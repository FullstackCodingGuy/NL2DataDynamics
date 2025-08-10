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
import subprocess
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
    mode: str = Field("http", example="http")  # "http" or "cli"

class GraphAnalyticsRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., example=[{"x": 1, "y": 2}])

class PluginRegisterRequest(BaseModel):
    name: str = Field(..., example="custom_plugin")
    config: Dict[str, Any] = Field(..., example={"param": "value"})

class PluginExecuteRequest(BaseModel):
    name: str = Field(..., example="custom_plugin")
    input_data: Dict[str, Any] = Field(..., example={"input": "value"})

def ollama_llm_http(text: str, task: str = "summarization") -> Dict[str, Any]:
    endpoint = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:11434/api/generate")
    if not endpoint or endpoint.strip() == "":
        raise ValueError("Ollama endpoint is required and cannot be empty")
    if not text or text.strip() == "":
        raise ValueError("Text input cannot be empty")
    payload = {
        "model": "phi3",
        "prompt": f"Perform {task} on the following text: {text}",
        "stream": False
    }
    try:
        response = httpx.post(endpoint, json=payload, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        output = result.get("response") or result.get("result") or str(result)
        return {
            "task": task,
            "result": output,
            "provider": "ollama",
            "endpoint": endpoint,
            "mode": "http"
        }
    except httpx.HTTPStatusError as e:
        logger.exception("Ollama HTTP error")
        raise HTTPException(status_code=500, detail=f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.TimeoutException:
        logger.exception("Ollama HTTP request timed out")
        raise HTTPException(status_code=500, detail="Ollama HTTP request timed out")
    except Exception as e:
        logger.exception("Ollama HTTP request failed")
        raise HTTPException(status_code=500, detail=f"Ollama HTTP request failed: {str(e)}")

def ollama_llm_cli(text: str, task: str = "summarization") -> Dict[str, Any]:
    if not text or text.strip() == "":
        raise ValueError("Text input cannot be empty")
    prompt = f"Perform {task} on the following text: {text}"
    try:
        result = subprocess.run(
            ["ollama", "run", "phi3", prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            logger.error(f"Ollama CLI error: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"Ollama CLI error: {result.stderr}")
        output = result.stdout.strip()
        return {
            "task": task,
            "result": output,
            "provider": "ollama",
            "mode": "cli"
        }
    except subprocess.TimeoutExpired:
        logger.exception("Ollama CLI request timed out")
        raise HTTPException(status_code=500, detail="Ollama CLI request timed out")
    except Exception as e:
        logger.exception("Ollama CLI request failed")
        raise HTTPException(status_code=500, detail=f"Ollama CLI request failed: {str(e)}")

@router.post("/analytics/text", summary="Text Analytics", response_description="Text analytics result")
async def text_analytics(request: TextAnalyticsRequest, current_user: User = Depends(get_current_user)):
    try:
        if request.mode == "cli":
            return ollama_llm_cli(request.text, task=request.task)
        else:
            return ollama_llm_http(request.text, task=request.task)
    except Exception as e:
        logger.exception("Text analytics failed")
        raise HTTPException(status_code=500, detail=f"Text analytics failed: {str(e)}")

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