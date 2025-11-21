from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from diary.models import DiaryEntry
from accounts.utils import can_create_entry
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils.dateparse import parse_date
from accounts.decorators import premium_required
from diary.tasks import transcribe_audio_task
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .tasks import extract_expenses_task
from .utils import can_create_entry
from .tasks import transcribe_audio_task


def home(request):
    """Redirect users to dashboard if authenticated, otherwise to login."""
    if request.user.is_authenticated:
        return redirect('diary:dashboard')
    return redirect('login')


@login_required
def dashboard(request):
    """Render the diary dashboard."""
    return render(request, 'diary/dashboard.html')


@login_required
def create_diary_entry(request):
    """Handle creation of a new diary entry."""
    if not can_create_entry(request.user):
        messages.error(request, "Entry limit reached. Upgrade to premium for unlimited entries.")
        return redirect('diary:dashboard')

    if request.method == 'POST':
        entry_type = request.POST.get('entry_type', 'text')
        content = request.POST.get('content', '').strip()
        audio_file = request.FILES.get('audio_file', None)
        processing_mode = 'premium' if request.user.userprofile.is_premium else 'free'

        diary_entry = DiaryEntry.objects.create(
            user=request.user,
            entry_type=entry_type,
            transcription=content if entry_type == 'text' else '',
            audio_file=audio_file if entry_type == 'voice' else None,
            processing_mode=processing_mode,
            status='processing'
        )

        if entry_type == "voice" and diary_entry.audio_file:
            transcribe_audio_task.delay(diary_entry.id)

        profile = request.user.userprofile
        if not profile.is_premium:
            profile.entry_count += 1
            profile.save()

        messages.success(request, "Diary entry created successfully!")
        return redirect('diary:dashboard')

    return render(request, 'diary/create_entry.html')


@login_required
def entry_detail(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    return render(request, 'diary/entry_detail.html', {'entry': entry})


@login_required
def entry_update(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        entry_type = request.POST.get('entry_type', entry.entry_type)
        entry.entry_type = entry_type
        entry.transcription = request.POST.get('content', entry.transcription).strip()

        if entry_type == "voice":
            audio_file = request.FILES.get('audio_file')
            if audio_file:
                entry.audio_file = audio_file

        entry.save()
        messages.success(request, "Entry updated successfully!")
        return redirect('diary:entry_detail', pk=entry.pk)

    return render(request, 'diary/entry_update.html', {'entry': entry})


@login_required
def entry_delete(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        entry.delete()
        messages.success(request, "Entry deleted successfully!")
        return redirect('diary:entry_list')

    return render(request, 'diary/entry_delete.html', {'entry': entry})


# ------------------------------
#  FINAL SINGLE entry_list VIEW
# ------------------------------

@login_required
def entry_list(request):
    user = request.user
    entries = DiaryEntry.objects.filter(user=user).order_by('-created_at')

    search_query = request.GET.get('search', '').strip()
    entry_type = request.GET.get('type')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if search_query:
        entries = entries.filter(transcription__icontains=search_query)

    if entry_type in ['text', 'voice']:
        entries = entries.filter(entry_type=entry_type)

    if start_date:
        entries = entries.filter(created_at__date__gte=parse_date(start_date))

    if end_date:
        entries = entries.filter(created_at__date__lte=parse_date(end_date))

    per_page = 1000 if getattr(user.userprofile, 'is_premium', False) else 50
    paginator = Paginator(entries, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'entry_type': entry_type,
        'start_date': start_date,
        'end_date': end_date,
        'is_premium': getattr(user.userprofile, 'is_premium', False),
    }

    return render(request, 'diary/entry_list.html', context)


@premium_required
def some_premium_feature_view(request):
    pass


@csrf_exempt
def voice_upload(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        entry = DiaryEntry.objects.create(audio_file=request.FILES['audio_file'])
        transcribe_audio_task.delay(entry.id)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)



@csrf_exempt
@login_required
def text_entry_upload(request):
    if request.method == "POST":
        if not can_create_entry(request.user):
            return JsonResponse({"error": "Upgrade to premium to create more entries."}, status=403)
        content = request.POST.get('content', '')
        if not content.strip():
            return JsonResponse({"error": "Content cannot be empty."}, status=400)
        entry = DiaryEntry.objects.create(user=request.user, entry_type='text', processing_mode='free', status='processing')
        entry.transcription = content
        entry.save()
        extract_expenses_task.delay(entry.id, content, "free")
        return JsonResponse({"success": True, "entry_id": entry.id, "status": entry.status})
    return JsonResponse({"error": "Invalid method"}, status=405)



@csrf_exempt
@login_required
def voice_entry_upload(request):
    if request.method == "POST":
        if not can_create_entry(request.user):
            return JsonResponse({"error": "Upgrade to premium to create more entries."}, status=403)
        audio_file = request.FILES.get('audio_file')
        if not audio_file:
            return JsonResponse({"error": "No audio file uploaded."}, status=400)
        entry = DiaryEntry.objects.create(
            user=request.user,
            entry_type='voice',
            audio_file=audio_file,
            processing_mode='free',
            status='processing'
        )
        transcribe_audio_task.delay(entry.id)
        return JsonResponse({"success": True, "entry_id": entry.id, "status": entry.status})
    return JsonResponse({"error": "Invalid method"}, status=405)
