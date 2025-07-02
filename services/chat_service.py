# This service will handle chat logic: LLM, TTS, chat history, etc.

from model import LamaLangChainClient
from services.session_service import add_chat_history, get_chat_history
from utils.audio import speech_to_text, text_to_speech
from fastapi import UploadFile
import json
import logging

gemini = LamaLangChainClient()

def process_chat(session, user_message, input_type, db, response_format="text", audio_file: UploadFile = None, user_language="en-US"):
    base_user_language = user_language.split('-')[0]
    chat_history = get_chat_history(db, session.id)
    # Prepare prompt as in the old code
    prompt = f"""
    **Instructions for the Language Model:**
    You are a real human friend to {session.user_data.get('name', 'the user')}. Your goal is to provide natural, enjoyable conversations tailored to the user's personality, interests, and communication style. You are the same age as the user ({session.user_data.get('age_range', 'unknown')} years old) and share similar interests. You also speak the same language as the user and use the same accent from their country.

    * **Speak ONLY in the user's specific language ({user_language}). Use phrasing and tone appropriate for that language and region.**
    * **Keep your responses casual, friendly, and natural—just like a real person talking.**
    * **Incorporate the user's interests smoothly into conversations.**
    * **Acknowledge their goals and support them in a realistic way.**
    * **Adapt to their personality, humor, and way of speaking.**
    * **Avoid sensitive or unethical topics.**
    * **Remember you are a true human.**

    **Important:** Ensure your speech feels natural and authentic, matching the user's cultural and linguistic background ({user_language}). Use chat history to maintain consistency. Avoid mentioning you are an AI or language model.

    **User Profile:**
    {json.dumps(session.user_data, indent=2)}

    **Chat History (Last ~10 exchanges):**
    {json.dumps([{ 'user': h.user_message, 'bot': h.bot_response } for h in chat_history[-10:]], indent=2)}

    **User Input (Type: {input_type}, Language: {user_language}):**
    {user_message}

    **Your Response (in {user_language}):**
    """
    logging.info(f"Generating Gemini report for session {session.id}")
    response_text = gemini.get_report(prompt)
    if not response_text or response_text.startswith("Error:"):
        return None, "Failed to get response from language model.", None
    add_chat_history(db, session.id, user_message, response_text)
    if response_format == "audio":
        audio_fp, tts_error = text_to_speech(response_text, lang=base_user_language)
        if tts_error:
            return response_text, f"Could not generate audio response: {tts_error}. Returning text instead.", None
        return None, None, audio_fp
    else:
        return response_text, None, None
