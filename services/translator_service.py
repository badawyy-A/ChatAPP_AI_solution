# This service will handle translation and TTS logic

from deep_translator import GoogleTranslator
from utils.audio import speech_to_text, text_to_speech
import logging

def translate_service(input_text, target_lang, source_lang=None, output_format="text", audio_file=None):
    # Translate text using GoogleTranslator
    try:
        base_source = source_lang.split('-')[0] if source_lang else None
        translator = GoogleTranslator(source=source_lang or 'auto', target=target_lang)
        translated_text = translator.translate(input_text)
        actual_src_lang = source_lang or "auto-detect"
    except Exception as e:
        logging.error(f"Translate | Error: {e}", exc_info=True)
        return None, None, f"Translation failed: {e}", None
    # Handle output format
    if not isinstance(target_lang, str):
        return None, None, "Internal error: Target language missing or invalid.", None
    base_target_lang = target_lang.split('-')[0].lower()
    if output_format == 'audio':
        if translated_text is None:
            return None, None, "Internal error: Translation result is missing.", None
        audio_fp, tts_error = text_to_speech(translated_text, lang=base_target_lang)
        if tts_error:
            return translated_text, actual_src_lang, f"Audio generation failed: {tts_error}. Returning text instead.", None
        return None, actual_src_lang, None, audio_fp
    else:
        return translated_text, actual_src_lang, None, None

def handle_translation_input(request, form, files):
    # Helper to extract input_text, target_lang, source_lang, input_type, and error from request/form/files
    input_text = None
    input_error = None
    target_lang = None
    source_lang = None
    input_type = "unknown"
    audio_file = None
    if request:
        try:
            data = request
            input_text = data.get('text')
            target_lang = data.get('target_lang')
            source_lang = data.get('source_lang')
            if input_text:
                input_type = "text"
        except Exception as e:
            input_error = f"Invalid JSON format in request body. {e}"
    if form:
        target_lang = form.get('target_lang') or target_lang
        source_lang = form.get('source_lang') or source_lang
        if 'audio' in files:
            audio_file = files['audio']
            if audio_file and audio_file.filename:
                input_type = "audio"
                stt_lang_hint = source_lang or 'en-US'
                input_text, input_error = speech_to_text(audio_file.file, language=stt_lang_hint)
            else:
                input_error = "Audio file provided but no file uploaded or filename missing."
        if input_text is None and not input_error:
            form_text = form.get('text')
            if form_text:
                input_text = form_text
                input_type = "text"
            elif input_type != "audio":
                input_error = "No text or audio provided in form-data."
    return input_text, target_lang, source_lang, input_type, input_error, audio_file
