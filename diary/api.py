from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from diary.models import DiaryEntry
from django.utils import timezone


# ============================================================
#   ENTRY LIST API  (UNCHANGED, JUST CLEAN)
# ============================================================

@login_required
def entry_list_api(request):
    if request.method == 'GET':
        entries = DiaryEntry.objects.filter(user=request.user).order_by('-created_at')
        data = [
            {
                'id': entry.id,
                'created_at': entry.created_at.isoformat(),
                'entry_type': entry.entry_type,
                'status': entry.status,
                'total_expense': float(entry.total_expense),
                'transcription': entry.transcription,
            }
            for entry in entries
        ]
        return JsonResponse({'entries': data})

    return HttpResponseNotAllowed(['GET'])



# ============================================================
#   ENTRY DELETE API (UNCHANGED)
# ============================================================

@csrf_exempt
@login_required
def entry_delete_api(request, pk):
    if request.method == 'DELETE':
        try:
            entry = DiaryEntry.objects.get(pk=pk, user=request.user)
            entry.delete()
            return JsonResponse({'status': 'success'})
        except DiaryEntry.DoesNotExist:
            return JsonResponse({'status': 'not found'}, status=404)

    return HttpResponseNotAllowed(['DELETE'])



# ============================================================
#   UPDATED VOICE ENTRY API (RECOMMENDED IMPROVEMENTS APPLIED)
# ============================================================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def voice_entry_api(request):

    audio_file = request.FILES.get('audio_file')

    if not audio_file:
        return JsonResponse({'status': 'error', 'message': 'No audio file uploaded!'}, status=400)

    # Dynamic size limit based on user premium status
    max_size = 50 * 1024 * 1024 if request.user.userprofile.is_premium else 10 * 1024 * 1024
    if audio_file.size > max_size:
        return JsonResponse({'status': 'error', 'message': 'File too large!'}, status=400)

    # Validate audio extension
    allowed_ext = ('.mp3', '.wav', '.m4a', '.webm')
    if not audio_file.name.lower().endswith(allowed_ext):
        return JsonResponse({'status': 'error', 'message': 'Unsupported file type!'}, status=400)

    try:
        entry = DiaryEntry.objects.create(
            user=request.user,
            entry_type='voice',
            audio_file=audio_file,
            processing_mode='premium' if request.user.userprofile.is_premium else 'free',
            status='processing'
        )

        return JsonResponse({'status': 'success', 'entry_id': entry.id})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
