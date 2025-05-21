from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from typing import Dict, List, Any, Optional, Callable
import datetime

from secura_agents.chat_bot import ChatBotAgent

# Initialize the chatbot agent
chat_bot = ChatBotAgent()

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatSessionRequest(BaseModel):
    analysis_id: str


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    message: str
    session_id: str
    timestamp: str


class ChatSessionResponse(BaseModel):
    session_id: str
    contract_name: str
    created_at: str
    message_count: Optional[int] = 0


class ChatHistoryResponse(BaseModel):
    session_id: str
    contract_name: str
    messages: List[Dict[str, Any]]


# Global variable to be set from the outside
# Define the type hint for clarity
analysis_results_getter: Optional[Callable[[str], Dict[str, Any]]] = None


# Session creation endpoint
@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(request: ChatSessionRequest):
    """Create a new chat session for a specific audit."""
    global analysis_results_getter

    session_id = str(uuid.uuid4())

    # Get the analysis results using the provided function
    if analysis_results_getter is None:
        raise HTTPException(status_code=500, detail="Analysis results getter not initialized")

    try:
        analysis_results = analysis_results_getter(request.analysis_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

    # Initialize the chatbot with the audit context
    session_info = chat_bot.set_audit_context(session_id, analysis_results)

    return {
        "session_id": session_id,
        "contract_name": session_info.get("contract_name", "Unknown Contract"),
        "created_at": session_info.get("created_at", datetime.datetime.now().isoformat()),
        "message_count": 0
    }


# Get all chat sessions
@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions():
    """List all active chat sessions."""
    return chat_bot.list_sessions()


# Get specific session info
@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(session_id: str):
    """Get information about a specific chat session."""
    session_info = chat_bot.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session_info


# Send a message in a chat session
@router.post("/{session_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(session_id: str, request: ChatMessageRequest):
    """Send a message to the chatbot and get a response."""
    response = chat_bot.chat(session_id, request.message)

    if "error" in response:
        raise HTTPException(status_code=400, detail=response.get("error", "Unknown error"))

    return {
        "message": response.get("message", ""),
        "session_id": session_id,
        "timestamp": response.get("timestamp", datetime.datetime.now().isoformat())
    }


# Get chat history for a session
@router.get("/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Get the conversation history for a chat session."""
    history = chat_bot.get_conversation_history(session_id)

    if "error" in history:
        raise HTTPException(status_code=404, detail=history.get("error", "Unknown error"))

    return history


# Clear a chat session
@router.delete("/sessions/{session_id}", response_model=Dict[str, Any])
async def clear_chat_session(session_id: str):
    """Clear a chat session."""
    result = chat_bot.clear_session(session_id)

    if not result.get("success", False):
        raise HTTPException(status_code=404, detail=result.get("message", "Unknown error"))

    return result


def set_analysis_getter(getter_func: Callable[[str], Dict[str, Any]]):
    """Set the analysis results getter function."""
    global analysis_results_getter
    analysis_results_getter = getter_func