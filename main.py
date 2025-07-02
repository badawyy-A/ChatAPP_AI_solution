from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.db import Base, engine
from routes import chat, session, translator, link_classifier

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(session.router)
app.include_router(chat.router)
app.include_router(translator.router)
app.include_router(link_classifier.router)
