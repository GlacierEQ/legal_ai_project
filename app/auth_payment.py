#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'authentification et de gestion des abonnements pour l'assistant juridique IA
Ce script implémente le système d'authentification utilisateur et l'intégration avec Stripe
"""

import os
import json
import logging
import secrets
import hashlib
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt
import stripe
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auth_payment.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("auth_payment")

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./legal_assistant.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuration de JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration de Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

# Modèles de base de données
class User(Base):
    """Modèle de table utilisateur"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    queries = relationship("Query", back_populates="user")


class Subscription(Base):
    """Modèle de table abonnement"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    plan_type = Column(String)  # "freemium", "standard", "pro"
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    queries_limit = Column(Integer)
    queries_used = Column(Integer, default=0)
    
    user = relationship("User", back_populates="subscription")


class Query(Base):
    """Modèle de table requête"""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query_text = Column(String)
    domain = Column(String)  # "business", "tax"
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="queries")


# Créer les tables
Base.metadata.create_all(bind=engine)

# Modèles Pydantic pour l'API
class UserCreate(BaseModel):
    """Modèle pour la création d'utilisateur"""
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    """Modèle pour la réponse utilisateur"""
    id: int
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    """Modèle pour le token d'accès"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Modèle pour les données du token"""
    email: Optional[str] = None


class SubscriptionCreate(BaseModel):
    """Modèle pour la création d'abonnement"""
    plan_type: str
    payment_method_id: str


class SubscriptionResponse(BaseModel):
    """Modèle pour la réponse d'abonnement"""
    id: int
    plan_type: str
    is_active: bool
    start_date: datetime
    end_date: Optional[datetime]
    queries_limit: int
    queries_used: int
    
    class Config:
        orm_mode = True


class QueryCreate(BaseModel):
    """Modèle pour la création de requête"""
    query_text: str
    domain: str


class QueryResponse(BaseModel):
    """Modèle pour la réponse de requête"""
    id: int
    query_text: str
    domain: str
    timestamp: datetime
    
    class Config:
        orm_mode = True


# Fonctions utilitaires
def get_db():
    """Obtient une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash"""
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = bytes.fromhex(hashed_password)
    salt = hash_bytes[:16]
    stored_hash = hash_bytes[16:]
    
    # Recalculer le hash avec le sel stocké
    pwdhash = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
    
    return pwdhash == stored_hash


def get_password_hash(password: str) -> str:
    """Génère un hash sécurisé pour le mot de passe"""
    salt = os.urandom(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return (salt + pwdhash).hex()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authentifie un utilisateur"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Dépendance OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Obtient l'utilisateur actuel à partir du token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Vérifie si l'utilisateur est actif"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user


# Classe de gestion des abonnements
class SubscriptionManager:
    """Gestionnaire d'abonnements avec intégration Stripe"""
    
    # Définition des plans
    PLANS = {
        "freemium": {
            "name": "Freemium",
            "price_id": os.getenv("STRIPE_FREEMIUM_PRICE_ID"),
            "queries_limit": 10,
            "amount": 0,
            "currency": "eur",
            "interval": "month"
        },
        "standard": {
            "name": "Standard",
            "price_id": os.getenv("STRIPE_STANDARD_PRICE_ID"),
            "queries_limit": 100,
            "amount": 1999,  # 19.99 EUR
            "currency": "eur",
            "interval": "month"
        },
        "pro": {
            "name": "Pro",
            "price_id": os.getenv("STRIPE_PRO_PRICE_ID"),
            "queries_limit": 1000,
            "amount": 4999,  # 49.99 EUR
            "currency": "eur",
            "interval": "month"
        }
    }
    
    @staticmethod
    def create_stripe_customer(email: str, name: str) -> str:
        """
        Crée un client Stripe
        
        Args:
            email: Email du client
            name: Nom complet du client
            
        Returns:
            str: ID du client Stripe
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            return customer.id
        except Exception as e:
            logger.error(f"Erreur lors de la création du client Stripe: {str(e)}")
            raise
    
    @staticmethod
    def create_subscription(customer_id: str, plan_type: str, payment_method_id: str) -> Dict:
        """
        Crée un abonnement Stripe
        
        Args:
            customer_id: ID du client Stripe
            plan_type: Type de plan ("freemium", "standard", "pro")
            payment_method_id: ID de la méthode de paiement
            
        Returns:
            Dict: Informations sur l'abonnement
        """
        try:
            plan = SubscriptionManager.PLANS.get(plan_type)
            if not plan:
                raise ValueError(f"Type de plan invalide: {plan_type}")
            
            # Pour le plan freemium, pas besoin de paiement
            if plan_type == "freemium":
                return {
                    "id": "free_" + secrets.token_hex(8),
                    "status": "active",
                    "current_period_end": (datetime.utcnow() + timedelta(days=30)).timestamp()
                }
            
            # Attacher la méthode de paiement au client
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            # Définir comme méthode de paiement par défaut
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            
            # Créer l'abonnement
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {"price": plan["price_id"]}
                ],
                expand=["latest_invoice.payment_intent"]
            )
            
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'abonnement Stripe: {str(e)}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """
        Annule un abonnement Stripe
        
        Args:
            subscription_id: ID de l'abonnement Stripe
            
        Returns:
            bool: True si l'annulation a réussi
        """
        try:
            # Pour les abonnements freemium
            if subscription_id.startswith("free_"):
                return True
            
            stripe.Subscription.delete(subscription_id)
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation de l'abonnement Stripe: {str(e)}")
            return False
    
    @staticmethod
    def check_subscription_status(subscription_id: str) -> str:
        """
        Vérifie le statut d'un abonnement Stripe
        
        Args:
            subscription_id: ID de l'abonnement Stripe
            
        Returns:
            str: Statut de l'abonnement
        """
        try:
            # Pour les abonnements freemium
            if subscription_id.startswith("free_"):
                return "active"
            
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription.status
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du statut de l'abonnement: {str(e)}")
            return "error"


# Initialisation de l'application FastAPI
app = FastAPI(title="Assistant Juridique IA - API", version="1.0.0")


# Routes d'authentification
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Route pour obtenir un token d'accès"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Route pour créer un utilisateur"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Créer un abonnement Freemium par défaut
    try:
        # Créer un client Stripe
        stripe_customer_id = SubscriptionManager.create_stripe_customer(
            email=user.email,
            name=user.full_name
        )
        
        # Créer un abonnement Freemium
        subscription_data = SubscriptionManager.create_subscription(
            customer_id=stripe_customer_id,
            plan_type="freemium",
            payment_method_id=""
        )
        
        # Calculer la date de fin
        end_date = datetime.fromtimestamp(subscription_data["current_period_end"])
        
        # Enregistrer l'abonnement
        db_subscription = Subscription(
            user_id=db_user.id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=subscription_data["id"],
            plan_type="freemium",
            is_active=True,
            start_date=datetime.utcnow(),
            end_date=end_date,
            queries_limit=SubscriptionManager.PLANS["freemium"]["queries_limit"]
        )
        db.add(db_subscription)
        db.commit()
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'abonnement Freemium: {str(e)}")
    
    return db_user


@app.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Route pour obtenir les informations de l'utilisateur actuel"""
    return current_user


# Routes d'abonnement
@app.post("/subscriptions/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Route pour créer ou mettre à jour un abonnement"""
    # Vérifier si l'utilisateur a déjà un abonnement
    db_subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    
    try:
        # Si l'utilisateur a déjà un abonnement, annuler l'ancien
        if db_subscription:
            SubscriptionManager.cancel_subscription(db_subscription.stripe_subscription_id)
            
            # Créer un nouvel abonnement
            subscription_data_stripe = SubscriptionManager.create_subscription(
                customer_id=db_subscription.stripe_customer_id,
                plan_type=subscription_data.plan_type,
                payment_method_id=subscription_data.payment_method_id
            )
            
            # Mettre à jour l'abonnement existant
            db_subscription.stripe_subscription_id = subscription_data_stripe["id"]
            db_subscription.plan_type = subscription_data.plan_type
            db_subscription.is_active = subscription_data_stripe["status"] == "active"
            db_subscription.start_date = datetime.utcnow()
            db_subscription.end_date = datetime.fromtimestamp(subscription_data_stripe["current_period_end"])
            db_subscription.queries_limit = SubscriptionManager.PLANS[subscription_data.plan_type]["queries_limit"]
            db_subscription.queries_used = 0
            
            db.commit()
            db.refresh(db_subscription)
            
        else:
            # Créer un client Stripe
            stripe_customer_id = SubscriptionManager.create_stripe_customer(
                email=current_user.email,
                name=current_user.full_name
            )
            
            # Créer un abonnement
            subscription_data_stripe = SubscriptionManager.create_subscription(
                customer_id=stripe_customer_id,
                plan_type=subscription_data.plan_type,
                payment_method_id=subscription_data.payment_method_id
            )
            
            # Enregistrer l'abonnement
            db_subscription = Subscription(
                user_id=current_user.id,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=subscription_data_stripe["id"],
                plan_type=subscription_data.plan_type,
                is_active=subscription_data_stripe["status"] == "active",
                start_date=datetime.utcnow(),
                end_date=datetime.fromtimestamp(subscription_data_stripe["current_period_end"]),
                queries_limit=SubscriptionManager.PLANS[subscription_data.plan_type]["queries_limit"]
            )
            db.add(db_subscription)
            db.commit()
            db.refresh(db_subscription)
        
        return db_subscription
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'abonnement: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/subscriptions/me/", response_model=SubscriptionResponse)
async def read_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Route pour obtenir les informations de l'abonnement de l'utilisateur actuel"""
    db_subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    # Vérifier le statut de l'abonnement
    if db_subscription.stripe_subscription_id:
        status = SubscriptionManager.check_subscription_status(db_subscription.stripe_subscription_id)
        if status != "active" and db_subscription.is_active:
            db_subscription.is_active = False
            db.commit()
    
    return db_subscription


@app.delete("/subscriptions/me/", response_model=dict)
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Route pour annuler l'abonnement de l'utilisateur actuel"""
    db_subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    # Annuler l'abonnement Stripe
    success = SubscriptionManager.cancel_subscription(db_subscription.stripe_subscription_id)
    
    if success:
        # Mettre à jour l'abonnement dans la base de données
        db_subscription.is_active = False
        db.commit()
        
        # Créer un abonnement Freemium
        subscription_data_stripe = SubscriptionManager.create_subscription(
            customer_id=db_subscription.stripe_customer_id,
            plan_type="freemium",
            payment_method_id=""
        )
        
        # Mettre à jour l'abonnement
        db_subscription.stripe_subscription_id = subscription_data_stripe["id"]
        db_subscription.plan_type = "freemium"
        db_subscription.is_active = True
        db_subscription.start_date = datetime.utcnow()
        db_subscription.end_date = datetime.fromtimestamp(subscription_data_stripe["current_period_end"])
        db_subscription.queries_limit = SubscriptionManager.PLANS["freemium"]["queries_limit"]
        db_subscription.queries_used = 0
        
        db.commit()
        
        return {"message": "Abonnement annulé avec succès et rétrogradé vers Freemium"}
    else:
        raise HTTPException(status_code=400, detail="Erreur lors de l'annulation de l'abonnement")


# Routes pour les requêtes juridiques
@app.post("/queries/", response_model=dict)
async def create_query(
    query_data: QueryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Route pour créer une requête juridique"""
    # Vérifier l'abonnement de l'utilisateur
    db_subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    # Vérifier si l'abonnement est actif
    if not db_subscription.is_active:
        raise HTTPException(status_code=400, detail="Abonnement inactif")
    
    # Vérifier si l'utilisateur a dépassé sa limite de requêtes
    if db_subscription.queries_used >= db_subscription.queries_limit:
        raise HTTPException(status_code=400, detail="Limite de requêtes atteinte pour ce mois")
    
    # Créer la requête
    db_query = Query(
        user_id=current_user.id,
        query_text=query_data.query_text,
        domain=query_data.domain
    )
    db.add(db_query)
    
    # Incrémenter le compteur de requêtes
    db_subscription.queries_used += 1
    
    db.commit()
    db.refresh(db_query)
    
    # Ici, on appellerait le service de génération de réponse
    # Pour l'exemple, on retourne une réponse fictive
    
    return {
        "query_id": db_query.id,
        "response": "Ceci est une réponse juridique fictive. Dans l'implémentation réelle, cette réponse serait générée par le module de génération de réponses.",
        "remaining_queries": db_subscription.queries_limit - db_subscription.queries_used
    }


@app.get("/queries/", response_model=List[QueryResponse])
async def read_queries(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Route pour obtenir l'historique des requêtes de l'utilisateur"""
    queries = db.query(Query).filter(Query.user_id == current_user.id).offset(skip).limit(limit).all()
    return queries


@app.get("/queries/stats/", response_model=dict)
async def read_query_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Route pour obtenir les statistiques des requêtes de l'utilisateur"""
    # Obtenir l'abonnement
    db_subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    # Compter les requêtes par domaine
    business_count = db.query(Query).filter(
        Query.user_id == current_user.id,
        Query.domain == "business"
    ).count()
    
    tax_count = db.query(Query).filter(
        Query.user_id == current_user.id,
        Query.domain == "tax"
    ).count()
    
    # Compter les requêtes du mois en cours
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_count = db.query(Query).filter(
        Query.user_id == current_user.id,
        Query.timestamp >= current_month_start
    ).count()
    
    return {
        "total_queries": business_count + tax_count,
        "business_queries": business_count,
        "tax_queries": tax_count,
        "current_month_queries": current_month_count,
        "queries_limit": db_subscription.queries_limit,
        "queries_used": db_subscription.queries_used,
        "queries_remaining": db_subscription.queries_limit - db_subscription.queries_used,
        "subscription_plan": db_subscription.plan_type,
        "subscription_active": db_subscription.is_active,
        "subscription_end_date": db_subscription.end_date
    }


# Webhook pour les événements Stripe
@app.post("/webhook/stripe/")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook pour les événements Stripe"""
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        logger.error(f"Erreur de validation du webhook: {str(e)}")
        raise HTTPException(status_code=400, detail="Payload invalide")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Erreur de signature du webhook: {str(e)}")
        raise HTTPException(status_code=400, detail="Signature invalide")
    
    # Gérer les événements
    if event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        subscription_id = invoice["subscription"]
        
        # Mettre à jour l'abonnement
        db_subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()
        
        if db_subscription:
            # Obtenir les détails de l'abonnement
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Mettre à jour l'abonnement
            db_subscription.is_active = subscription.status == "active"
            db_subscription.end_date = datetime.fromtimestamp(subscription.current_period_end)
            db_subscription.queries_used = 0  # Réinitialiser le compteur de requêtes
            
            db.commit()
            
            logger.info(f"Abonnement {subscription_id} renouvelé avec succès")
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        
        # Mettre à jour l'abonnement
        db_subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()
        
        if db_subscription:
            db_subscription.is_active = False
            db.commit()
            
            logger.info(f"Abonnement {subscription_id} supprimé avec succès")
    
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
