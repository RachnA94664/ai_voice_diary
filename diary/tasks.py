from celery import shared_task, chain
from diary.models import DiaryEntry
from diary.services.transcription import transcribe_audio
from diary.services.expense_detector import extract_expenses
from expenses.models import Expense

@shared_task
def transcribe_audio_task(entry_id):
    try:
        entry = DiaryEntry.objects.get(pk=entry_id)
        entry.status = 'transcribing'
        entry.save()
        if not entry.audio_file:
            entry.status = 'no_audio'
            entry.save()
            return None
        transcript = transcribe_audio(entry.audio_file.path)
        entry.transcription = transcript
        entry.status = 'transcribed'
        entry.save()
        return transcript
    except DiaryEntry.DoesNotExist:
        # Log it or alert
        return None
    except Exception as e:
        entry.status = 'failed_transcription'
        entry.save()
        print(f"Transcription error: {e}")
        return None

@shared_task
def extract_expenses_task(entry_id, mode='free'):
    try:
        entry = DiaryEntry.objects.get(pk=entry_id)
        entry.status = 'extracting_expenses'
        entry.save()
        if not entry.transcription:
            entry.status = 'notranscript'
            entry.save()
            return []
        expenses = extract_expenses(entry.transcription)
        for amount, context in expenses:
            Expense.objects.create(
                diary_entry=entry,
                amount=amount,
                category='other',
                detected_text=context
            )
        entry.status = 'expenses_extracted'
        entry.save()
        return expenses
    except DiaryEntry.DoesNotExist:
        return None
    except Exception as e:
        entry.status = 'failed_expenses'
        entry.save()
        print(f"Expense extraction error: {e}")
        return None

@shared_task
def process_diary_entry(entry_id, mode='free'):
    """
    Full pipeline: safe status updates at every step
    """
    try:
        entry = DiaryEntry.objects.get(id=entry_id)
        entry.status = 'processing'
        entry.save()
        task_chain = chain(
            transcribe_audio_task.s(entry_id),
            extract_expenses_task.s(entry_id, mode)
        )
        task_chain()
        entry.status = 'completed'
        entry.save()
        return "Pipeline completed"
    except Exception as e:
        try:
            entry = DiaryEntry.objects.get(id=entry_id)
            entry.status = 'failed_pipeline'
            entry.save()
        except Exception:
            pass
        print(f"Pipeline failed for DiaryEntry {entry_id}: {e}")
        return None
