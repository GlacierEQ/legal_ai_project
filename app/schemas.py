from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_professional: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# Subscription schemas
class SubscriptionBase(BaseModel):
    plan: str
    
class SubscriptionCreate(SubscriptionBase):
    user_id: int
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    is_active: bool
    start_date: datetime
    end_date: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Query schemas
class QueryBase(BaseModel):
    query_text: str
    domain: str = "fiscal"  # Default to fiscal domain

class QueryCreate(QueryBase):
    user_id: int

class QueryResponse(QueryBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Response schemas
class ResponseBase(BaseModel):
    response_text: str
    sources: str  # JSON string of sources

class ResponseCreate(ResponseBase):
    query_id: int

class ResponseResponse(ResponseBase):
    id: int
    query_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Legal text schemas
class LegalTextBase(BaseModel):
    text_type: str
    title: str
    content: str
    source: str
    metadata: str  # JSON string of additional metadata
    
class LegalTextCreate(LegalTextBase):
    publication_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    vector_id: Optional[str] = None

class LegalTextResponse(LegalTextBase):
    id: int
    publication_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    vector_id: Optional[str] = None
    
    class Config:
        orm_mode = True

# Query request and response schemas for API
class LegalQueryRequest(BaseModel):
    query: str = Field(..., description="Question juridique posée par l'utilisateur")
    domain: str = Field("fiscal", description="Domaine juridique (fiscal, affaires, etc.)")
    user_type: str = Field("standard", description="Type d'utilisateur (professionnel ou non)")

class LegalQueryResponse(BaseModel):
    introduction: str = Field(..., description="Introduction contextuelle")
    cadre_legal: str = Field(..., description="Cadre légal applicable")
    application: str = Field(..., description="Application au cas spécifique")
    exceptions: str = Field(..., description="Exceptions et cas particuliers")
    recommandations: str = Field(..., description="Recommandations")
    sources: List[str] = Field(..., description="Sources et références")
