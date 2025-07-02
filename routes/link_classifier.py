from fastapi import APIRouter, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Optional
from services.link_classifier_service import classify_url_service

router = APIRouter(prefix="/api", tags=["link_classifier"])

class LinkClassifierRequest(BaseModel):
    url: str

class LinkClassifierResponse(BaseModel):
    label: str

@router.post("/link_classifier/")
async def predict_url_safety(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Request body must be JSON."})
    url = data.get('url')
    label, error = classify_url_service(url)
    if error:
        return JSONResponse(status_code=400, content={"error": error})
    return JSONResponse(content={"label": label})
