from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

from app.routers import users, auth, query

app = FastAPI(
    title="Assistant Juridique IA",
    description="API pour l'assistant juridique IA spécialisé en droit des affaires et fiscal français",
    version="0.1.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À remplacer par les domaines spécifiques en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(query.router)

@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API de l'Assistant Juridique IA",
        "status": "online",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "online",
            "database": "pending",
            "vector_db": "pending",
            "llm": "pending"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
