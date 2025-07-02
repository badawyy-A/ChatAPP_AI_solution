from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
from services.translator_service import translate_service

router = APIRouter(prefix="/api", tags=["translator"])

class TranslatorRequest(BaseModel):
    text: Optional[str] = None
    target_lang: str
    source_lang: Optional[str] = None

class TranslatorResponse(BaseModel):
    translated_text: Optional[str] = None
    source_language_detected: Optional[str] = None
    warning: Optional[str] = None

@router.post("/translator/")
async def do_translation(
    request: Request,
    text: Optional[str] = Form(None),
    target_lang: Optional[str] = Form(None),
    source_lang: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    format: Optional[str] = None
):
    # Try to get JSON body if not form
    data = None
    if not text and not audio:
        try:
            data = await request.json()
        except Exception:
            data = None
    if data:
        text = data.get('text')
        target_lang = data.get('target_lang')
        source_lang = data.get('source_lang')
    if not target_lang:
        return JSONResponse(status_code=400, content={"error": "'target_lang' is required in JSON or form data."})
    input_type = "audio" if audio else "text"
    input_error = None
    if audio:
        from utils.audio import speech_to_text
        text, input_error = speech_to_text(audio.file, language=source_lang or 'en-US')
        if input_error:
            return JSONResponse(status_code=400, content={"error": f"Audio processing failed: {input_error}"})
    if not text:
        return JSONResponse(status_code=400, content={"error": "Input required: JSON with 'text', or form-data with 'text' or 'audio'."})
    output_format = format.lower() if format else "text"
    translated_text, actual_src_lang, warning, audio_fp = translate_service(
        text, target_lang, source_lang, output_format=output_format
    )
    if output_format == "audio":
        if audio_fp:
            return StreamingResponse(audio_fp, media_type="audio/mpeg")
        else:
            return JSONResponse(content={
                "warning": warning,
                "translated_text": translated_text,
                "source_language_detected": actual_src_lang
            })
    else:
        return JSONResponse(content={
            "translated_text": translated_text,
            "source_language_detected": actual_src_lang,
            "warning": warning
        })
