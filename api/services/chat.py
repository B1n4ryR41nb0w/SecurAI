import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid
import datetime

# Add project root to path
project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(str(project_root))

# Import agents
from secura_agents.chat_bot import chat_bot


class ChatService:
    """Service for interactive chat with the audit agent"""

    def __init__(self):
        """Initialize the chat service"""
        # Nothing to initialize - chat_bot manages its own state
        pass

    async def create_session(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chat session

        Args:
            analysis_results: Results of the analysis

        Returns:
            Dictionary with session information
        """
        try:
            # Generate unique session ID
            session_id = str(uuid.uuid4())

            # Set up the session
            session_info = chat_bot.set_audit_context(session_id, analysis_results)

            return {
                "success": True,
                "session_id": session_id,
                "contract_name": session_info.get("contract_name", "Unknown"),
                "created_at": session_info.get("created_at", datetime.datetime.now().isoformat())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create chat session: {str(e)}"
            }

    async def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Send a message to the chat session

        Args:
            session_id: ID of the chat session
            message: Message to send

        Returns:
            Dictionary with response information
        """
        try:
            # Get response from the chat bot
            response = chat_bot.chat(session_id, message)

            if "error" in response:
                return {
                    "success": False,
                    "error": response["error"],
                    "session_id": session_id
                }

            return {
                "success": True,
                "session_id": session_id,
                "message": response.get("message", ""),
                "timestamp": response.get("timestamp", datetime.datetime.now().isoformat())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send message: {str(e)}",
                "session_id": session_id
            }

    def get_history(self, session_id: str) -> Dict[str, Any]:
        """Get the chat history for a session

        Args:
            session_id: ID of the chat session

        Returns:
            Dictionary with chat history
        """
        try:
            # Get history from the chat bot
            history = chat_bot.get_conversation_history(session_id)

            if "error" in history:
                return {
                    "success": False,
                    "error": history["error"],
                    "session_id": session_id
                }

            return {
                "success": True,
                "session_id": session_id,
                "contract_name": history.get("contract_name", "Unknown"),
                "messages": history.get("messages", [])
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get chat history: {str(e)}",
                "session_id": session_id
            }

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all chat sessions

        Returns:
            List of dictionaries with session information
        """
        try:
            # Get sessions from the chat bot
            sessions = chat_bot.list_sessions()

            return sessions

        except Exception as e:
            print(f"Error listing chat sessions: {e}")
            return []

    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a chat session

        Args:
            session_id: ID of the chat session

        Returns:
            Dictionary with deletion information
        """
        try:
            # Delete session from the chat bot
            result = chat_bot.clear_session(session_id)

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": result.get("message", "Failed to delete session"),
                    "session_id": session_id
                }

            return {
                "success": True,
                "message": f"Session {session_id} deleted successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete session: {str(e)}",
                "session_id": session_id
            }