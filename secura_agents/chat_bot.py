import os
from crewai import Agent
from dotenv import load_dotenv
import json
import openai
import datetime
from typing import Dict, Any, List, Optional
from pydantic import Field

# Load environment variables
load_dotenv()


class ChatBotAgent(Agent):
    """Interactive chatbot for answering questions about smart contract audits."""

    # Add fields that need to be set in __init__
    client: Any = Field(default=None, description="OpenAI client")
    conversation_context: Dict = Field(default_factory=dict, description="Conversation history")

    def __init__(self):
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY not found in environment variables")

        # Initialize the agent
        super().__init__(
            role="Smart Contract Audit Chatbot",
            goal="Answer user questions about smart contract vulnerabilities and audit results",
            backstory="An intelligent assistant with expertise in blockchain security, "
                      "capable of explaining complex vulnerabilities in simple terms and "
                      "providing educational insights about smart contract security.",
            verbose=True,
            llm=None  # We'll handle the LLM calls directly for more control
        )

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def set_audit_context(self, session_id, analysis_results):
        """Set the current audit results as context for the chatbot."""
        contract_name = analysis_results.get("contract_stats", {}).get("name", "Unknown Contract")

        # Create system prompt with analysis context
        system_prompt = f"""
        You are an expert smart contract security chatbot. You are discussing an audit of the contract '{contract_name}'.

        Here is a summary of the audit findings:
        - Total vulnerabilities: {analysis_results.get('vulnerability_summary', {}).get('total', 0)}
        - High severity: {analysis_results.get('vulnerability_summary', {}).get('by_severity', {}).get('High', 0)}
        - Medium severity: {analysis_results.get('vulnerability_summary', {}).get('by_severity', {}).get('Medium', 0)}
        - Low severity: {analysis_results.get('vulnerability_summary', {}).get('by_severity', {}).get('Low', 0)}

        The detailed findings are: {json.dumps(analysis_results.get('vulnerabilities', []), indent=2)}

        The contract includes these functions: {', '.join(f["name"] for f in analysis_results.get('functions', []))}

        Answer questions about this audit in a helpful, educational manner. If asked about vulnerabilities
        not found in this audit, you can provide general information but clarify that they weren't detected
        in this specific contract.
        """

        # Initialize conversation context for this session
        self.conversation_context[session_id] = {
            "messages": [{"role": "system", "content": system_prompt}],
            "contract_name": contract_name,
            "analysis_results": analysis_results,
            "created_at": datetime.datetime.now().isoformat()
        }

        return {
            "session_id": session_id,
            "contract_name": contract_name,
            "created_at": self.conversation_context[session_id]["created_at"]
        }

    def get_session_info(self, session_id):
        """Get information about a chat session."""
        if session_id not in self.conversation_context:
            return None

        session = self.conversation_context[session_id]
        return {
            "session_id": session_id,
            "contract_name": session.get("contract_name", "Unknown"),
            "created_at": session.get("created_at"),
            "message_count": len(session.get("messages", [])) - 1  # Don't count system message
        }

    def list_sessions(self):
        """List all active chat sessions."""
        return [
            self.get_session_info(session_id)
            for session_id in self.conversation_context.keys()
        ]

    def chat(self, session_id, user_message):
        """Handle a user message and generate a response."""
        if session_id not in self.conversation_context:
            return {
                "error": "Session not found",
                "message": "No active chat session found. Please start a new session."
            }

        # Get the conversation context
        context = self.conversation_context[session_id]

        # Add the user message to context
        context["messages"].append({"role": "user", "content": user_message})

        # Keep conversation context to a reasonable size (last 20 messages including system)
        if len(context["messages"]) > 21:  # 1 system + 20 conversation messages
            # Keep system message and last 20 conversation messages
            context["messages"] = [context["messages"][0]] + context["messages"][-20:]

        try:
            # Generate response using the chat model
            response = self.client.chat.completions.create(
                model="gpt-4",  # Using a strong model for better security insights
                messages=context["messages"],
                temperature=0.7,
                max_tokens=1500
            )

            # Extract the assistant's response
            assistant_response = response.choices[0].message.content

            # Add the response to the conversation history
            context["messages"].append({"role": "assistant", "content": assistant_response})

            return {
                "message": assistant_response,
                "session_id": session_id,
                "timestamp": datetime.datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error generating chat response: {e}")
            return {
                "error": str(e),
                "message": f"I'm sorry, I encountered an error: {str(e)}",
                "session_id": session_id
            }

    def get_conversation_history(self, session_id):
        """Get the conversation history for a session."""
        if session_id not in self.conversation_context:
            return {"error": "Session not found", "messages": []}

        # Return all messages except the system prompt
        return {
            "session_id": session_id,
            "contract_name": self.conversation_context[session_id].get("contract_name", "Unknown"),
            "messages": self.conversation_context[session_id]["messages"][1:]  # Skip system message
        }

    def clear_session(self, session_id):
        """Clear a chat session."""
        if session_id in self.conversation_context:
            del self.conversation_context[session_id]
            return {"success": True, "message": f"Session {session_id} cleared"}
        return {"success": False, "message": "Session not found"}


# Create agent instance
chat_bot = ChatBotAgent()