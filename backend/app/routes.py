from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from passlib.context import CryptContext
import os
import httpx
import logging
from .database import get_db
from .models import User
from .auth import authenticate_user, create_access_token, get_current_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("analytics")

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
    return {"status": "ok"}

@router.post("/register", summary="Register User", response_description="User registration status")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
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
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", summary="Get Current User", response_description="Current user info")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email, "role": current_user.role}

@router.post("/db/query", summary="Execute SQL Query", response_description="Query result")
def execute_query(request: QueryRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
    endpoint = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:11434/api/generate")
    if not endpoint or endpoint.strip() == "":
        raise HTTPException(status_code=400, detail="Ollama endpoint is required and cannot be empty")
    if not request.text or request.text.strip() == "":
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    payload = {
        "model": "phi3",
        "prompt": f"Perform {request.task} on the following text: {request.text}",
        "stream": False
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            output = result.get("response") or result.get("result") or str(result)
            return {
                "task": request.task,
                "result": output,
                "provider": "ollama",
                "endpoint": endpoint
            }
    except httpx.HTTPStatusError as e:
        logger.exception("Ollama error")
        raise HTTPException(status_code=500, detail=f"Ollama error: {e.response.status_code} - {e.response.text}")
    except httpx.TimeoutException:
        logger.exception("Ollama request timed out")
        raise HTTPException(status_code=500, detail="Ollama request timed out")
    except Exception as e:
        logger.exception("Ollama request failed")
        raise HTTPException(status_code=500, detail=f"Ollama request failed: {str(e)}")

@router.post("/analytics/graph", summary="Graphical Analytics", response_description="Graphical analytics result")
def graph_analytics(request: GraphAnalyticsRequest, current_user: User = Depends(get_current_user)):
    return {"graph": "Graphical analytics result"}

@router.post("/plugin/register", summary="Register Plugin", response_description="Plugin registration status")
def register_plugin(request: PluginRegisterRequest, current_user: User = Depends(get_current_user)):
    return {"msg": f"Plugin '{request.name}' registered", "config": request.config}

@router.post("/plugin/execute", summary="Execute Plugin", response_description="Plugin execution result")
def execute_plugin(request: PluginExecuteRequest, current_user: User = Depends(get_current_user)):
    return {"result": f"Executed plugin '{request.name}' with input {request.input_data}"}

@router.get("/user/roles", summary="Get User Role", response_description="Current user role")
def get_roles(current_user: User = Depends(get_current_user)):
    return {"role": current_user.role}