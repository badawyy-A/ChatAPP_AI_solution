import speech_recognition as sr
from pydub import AudioSegment
import io
import os
import uuid
import logging
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()
tts_api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=tts_api_key)
recognizer = sr.Recognizer()

def speech_to_text(audio_file, language="en-US"):
    """Converts audio file to text using SpeechRecognition. Accepts file-like object."""
    temp_wav_path = f"temp_{uuid.uuid4()}.wav"
    temp_orig_path = temp_wav_path
    try:
        # Save uploaded file to disk
        with open(temp_orig_path, "wb") as f:
            f.write(audio_file.read())
        try:
            audio_segment = AudioSegment.from_file(temp_orig_path)
            audio_segment = audio_segment.set_channels(1).set_frame_rate(16000)
            audio_segment.export(temp_wav_path, format="wav")
            logging.info(f"Successfully converted {temp_orig_path} to {temp_wav_path}")
        except Exception as e:
            logging.error(f"Error converting audio format using pydub: {e}", exc_info=True)
            temp_wav_path = temp_orig_path
        with sr.AudioFile(temp_wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language=language)
                return text, None
            except sr.UnknownValueError:
                return None, "Speech Recognition could not understand audio"
            except sr.RequestError as e:
                return None, f"Could not request results from Google Speech Recognition service; {e}"
    except Exception as e:
        return None, f"Error processing audio file: {e}"
    finally:
        if os.path.exists(temp_wav_path):
            try: os.remove(temp_wav_path)
            except OSError: pass
        if temp_orig_path != temp_wav_path and os.path.exists(temp_orig_path):
            try: os.remove(temp_orig_path)
            except OSError: pass

def text_to_speech(text, lang="ar"):
    """Converts text to speech using ElevenLabs and returns an in-memory audio file object."""
    voice_settings = {
        "ar": "a1KZUXKFVFDOb33I1uqr",
        "en": "tQ4MEZFJOzsahSEEZtHK"
    }
    voice_id = voice_settings.get(lang)
    if not voice_id:
        return None, f"Unsupported language/voice selected for TTS: {lang}"
    try:
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        audio_bytes = b"".join(audio_stream)
        if not audio_bytes:
            return None, "TTS service returned empty audio."
        audio_fp = io.BytesIO(audio_bytes)
        audio_fp.seek(0)
        return audio_fp, None
    except Exception as e:
        return None, f"TTS API error: {e}" 