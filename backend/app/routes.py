from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from passlib.context import CryptContext
import os
import asyncio
from .database import get_db
from .models import User
from .auth import authenticate_user, create_access_token, get_current_user
from .analytics_providers import get_text_analytics_provider

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterRequest(BaseModel):
    username: str = Field(..., example="johndoe")
    email: str = Field(..., example="john@example.com")
    password: str = Field(..., example="strongpassword")

class QueryRequest(BaseModel):
    query: str = Field(..., example="SELECT * FROM users")

class TextAnalyticsRequest(BaseModel):
    text: str = Field(..., example="Analyze this text for sentiment.")
    task: str = Field("summarization", example="summarization")

class GraphAnalyticsRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., example=[{"x": 1, "y": 2}])

class PluginRegisterRequest(BaseModel):
    name: str = Field(..., example="custom_plugin")
    config: Dict[str, Any] = Field(..., example={"param": "value"})

class PluginExecuteRequest(BaseModel):
    name: str = Field(..., example="custom_plugin")
    input_data: Dict[str, Any] = Field(..., example={"input": "value"})

@router.get("/health", summary="Health Check", response_description="API health status")
def health_check():
    """
    Returns API health status.
    """
    return {"status": "ok"}

@router.post("/register", summary="Register User", response_description="User registration status")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user with hashed password.
    """
    user = db.query(User).filter((User.username == request.username) | (User.email == request.email)).first()
    if user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    hashed_password = pwd_context.hash(request.password)
    new_user = User(username=request.username, email=request.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully"}

@router.post("/token", summary="Login", response_description="JWT access token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates user and returns JWT access token.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", summary="Get Current User", response_description="Current user info")
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Returns current authenticated user's info.
    """
    return {"username": current_user.username, "email": current_user.email, "role": current_user.role}

@router.post("/db/query", summary="Execute SQL Query", response_description="Query result")
def execute_query(request: QueryRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Executes a raw SQL query and returns the result.
    """
    try:
        result = db.execute(text(request.query))
        rows = result.fetchall()
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in rows]
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analytics/text", summary="Text Analytics", response_description="Text analytics result")
async def text_analytics(request: TextAnalyticsRequest, current_user: User = Depends(get_current_user)):
    """
    Performs advanced text analytics using a configurable provider (e.g., OpenAI).
    """
    provider_name = os.getenv("TEXT_ANALYTICS_PROVIDER", "openai")
    api_key = os.getenv("OPENAI_API_KEY", "")
    provider = get_text_analytics_provider(provider_name, api_key=api_key)
    try:
        result = await provider.analyze(request.text, task=request.task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analytics failed: {str(e)}")

@router.post("/analytics/graph", summary="Graphical Analytics", response_description="Graphical analytics result")
def graph_analytics(request: GraphAnalyticsRequest, current_user: User = Depends(get_current_user)):
    """
    Performs graphical analytics on input data.
    """
    return {"graph": "Graphical analytics result"}

@router.post("/plugin/register", summary="Register Plugin", response_description="Plugin registration status")
def register_plugin(request: PluginRegisterRequest, current_user: User = Depends(get_current_user)):
    """
    Registers a new analytics plugin.
    """
    return {"msg": f"Plugin '{request.name}' registered", "config": request.config}

@router.post("/plugin/execute", summary="Execute Plugin", response_description="Plugin execution result")
def execute_plugin(request: PluginExecuteRequest, current_user: User = Depends(get_current_user)):
    """
    Executes a registered plugin with input data.
    """
    return {"result": f"Executed plugin '{request.name}' with input {request.input_data}"}

@router.get("/user/roles", summary="Get User Role", response_description="Current user role")
def get_roles(current_user: User = Depends(get_current_user)):
    """
    Returns the role of the current authenticated user.
    """
    return {"role": current_user.role}