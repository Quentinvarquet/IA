from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Any, Dict
import uuid
from datetime import datetime, timezone
import json

from anonymizer import anonymize_json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class AnonymizeRequest(BaseModel):
    """Request model for JSON anonymization"""
    data: Any = Field(..., description="JSON data to anonymize")

class DetectedFieldInfo(BaseModel):
    """Information about a detected and anonymized field"""
    path: str
    type: str
    original: str
    anonymized: str

class AnonymizeResponse(BaseModel):
    """Response model for JSON anonymization"""
    success: bool
    anonymized_data: Any
    detected_fields: List[DetectedFieldInfo]
    stats: Dict[str, int]


# Routes
@api_router.get("/")
async def root():
    return {"message": "JSON Anonymizer API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

@api_router.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize_endpoint(request: AnonymizeRequest):
    """
    Anonymize JSON data by detecting and replacing sensitive fields
    
    Detected fields:
    - nom, prenom, nom_complet (names)
    - email (email addresses)
    - telephone (phone numbers)
    - adresse, code_postal, ville (addresses)
    - iban (bank account numbers)
    - secu (social security numbers)
    - date_naissance (birth dates)
    - carte_bancaire (credit card numbers)
    """
    try:
        anonymized_data, detected_fields = anonymize_json(request.data)
        
        # Calculate stats
        stats = {}
        for field in detected_fields:
            field_type = field["type"]
            stats[field_type] = stats.get(field_type, 0) + 1
        
        return AnonymizeResponse(
            success=True,
            anonymized_data=anonymized_data,
            detected_fields=[DetectedFieldInfo(**f) for f in detected_fields],
            stats=stats
        )
    except Exception as e:
        logging.error(f"Anonymization error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing JSON: {str(e)}")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
