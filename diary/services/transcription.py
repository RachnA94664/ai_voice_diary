import whisper

def transcribe_audio(audio_path, language='en'):
    """
    Transcribe audio using OpenAI Whisper.
    :param audio_path: Path to the audio file
    :param language: Language code (default 'en')
    :return: Recognized text string
    """
    model = whisper.load_model("base")  # Change to 'small', 'medium', etc as needed
    result = model.transcribe(audio_path, language=language)
    return result["text"]
