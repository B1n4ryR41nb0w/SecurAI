import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Send, ArrowLeft, Bot, User, Shield } from "lucide-react";
import { Link } from "react-router-dom";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatSession {
  session_id: string;
  contract_name: string;
  created_at: string;
  message_count?: number;
}

export default function ChatPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [contractName, setContractName] = useState<string>("Unknown Contract");
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize chat session when component mounts
  useEffect(() => {
    const initChatSession = async () => {
      if (!analysisId) return;
      
      try {
        // First, get the analysis results
        const analysisResponse = await fetch(`http://localhost:8000/api/analysis/${analysisId}`);
        
        if (!analysisResponse.ok) {
          throw new Error(`Failed to fetch analysis: ${analysisResponse.statusText}`);
        }
        
        const analysisData = await analysisResponse.json();
        
        // Create a chat session with the analysis context
        const sessionResponse = await fetch('http://localhost:8000/api/chat/sessions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            analysis_id: analysisId
          }),
        });
        
        if (!sessionResponse.ok) {
          throw new Error(`Failed to create chat session: ${sessionResponse.statusText}`);
        }
        
        const sessionData = await sessionResponse.json();
        
        setSessionId(sessionData.session_id);
        setContractName(sessionData.contract_name || analysisData.contract_name || "Unknown Contract");
        
        // Add initial welcome message
        setMessages([
          {
            id: "welcome",
            role: "assistant",
            content: `Hello! I'm your smart contract audit assistant. I've analyzed ${sessionData.contract_name}. I can help explain vulnerabilities found in your contract and answer any questions you have about security best practices. What would you like to know?`,
            timestamp: new Date()
          }
        ]);
        
      } catch (err) {
        console.error('Error initializing chat:', err);
        setError(`Failed to initialize chat: ${err instanceof Error ? err.message : String(err)}`);
      }
    };
    
    initChatSession();
  }, [analysisId]);
  
  // Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || !sessionId) return;
    
    // Add user message to UI immediately
    const messageId = Date.now().toString();
    const userMessage: Message = {
      id: messageId,
      role: "user",
      content: input,
      timestamp: new Date()
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    
    try {
      // Send message to API
      const response = await fetch(`http://localhost:8000/api/chat/${sessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Add assistant response to UI
      const assistantMessage: Message = {
        id: `response-${messageId}`,
        role: "assistant",
        content: data.message,
        timestamp: new Date(data.timestamp || Date.now())
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
      
    } catch (err) {
      console.error('Error sending message:', err);
      
      // Add error message to UI
      const errorMessage: Message = {
        id: `error-${messageId}`,
        role: "assistant",
        content: `I'm sorry, there was an error processing your request. ${err instanceof Error ? err.message : "Please try again later."}`,
        timestamp: new Date()
      };
      
      setMessages((prev) => [...prev, errorMessage]);
      
    } finally {
      setIsLoading(false);
    }
  };
  
  if (error) {
    return (
      <div className="container mx-auto py-10 px-4">
        <div className="max-w-4xl mx-auto bg-card border rounded-lg p-8 text-center">
          <div className="text-destructive mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mx-auto mb-2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
          <h2 className="text-2xl font-bold mb-2">Chat Initialization Error</h2>
          <p className="text-muted-foreground mb-6">{error}</p>
          <Link to={`/report/${analysisId}`} className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
            Return to Audit Report
          </Link>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-6 px-4">
      <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 pb-4 border-b">
          <div className="flex items-center">
            <Link to={`/report/${analysisId}`} className="mr-4">
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <Shield className="h-6 w-6 text-primary mr-2" />
            <h1 className="text-xl font-bold">Security Assistant Chat</h1>
          </div>
          <div className="text-sm text-muted-foreground">
            {contractName}
          </div>
        </div>
        
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4 pr-2">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div 
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === "user" 
                    ? "bg-primary text-primary-foreground rounded-tr-none" 
                    : "bg-muted rounded-tl-none"
                }`}
              >
                <div className="flex items-center mb-2">
                  {message.role === "assistant" ? (
                    <Bot className="h-4 w-4 mr-2" />
                  ) : (
                    <User className="h-4 w-4 mr-2" />
                  )}
                  <span className="text-xs opacity-70">
                    {message.role === "assistant" ? "AI Assistant" : "You"}
                  </span>
                </div>
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div className="text-right mt-1">
                  <span className="text-xs opacity-50">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg rounded-tl-none px-4 py-3 max-w-[80%]">
                <div className="flex items-center">
                  <Bot className="h-4 w-4 mr-2" />
                  <span className="text-xs opacity-70">AI Assistant</span>
                </div>
                <div className="flex items-center space-x-2 py-2">
                  <div className="h-2 w-2 rounded-full bg-muted-foreground/30 animate-bounce"></div>
                  <div className="h-2 w-2 rounded-full bg-muted-foreground/30 animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                  <div className="h-2 w-2 rounded-full bg-muted-foreground/30 animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input Form */}
        <form onSubmit={handleSendMessage} className="border-t pt-4">
          <div className="flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about vulnerabilities or security best practices..."
              className="flex-1 bg-muted rounded-l-md px-4 py-3 focus:outline-none"
              disabled={isLoading || !sessionId}
            />
            <button
              type="submit"
              className="bg-primary text-primary-foreground px-4 py-3 rounded-r-md hover:bg-primary/90 disabled:opacity-50"
              disabled={!input.trim() || isLoading || !sessionId}
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
          <div className="text-xs text-muted-foreground mt-2 text-center">
            Ask questions about the vulnerabilities found in your contract, 
            how to fix them, or general security best practices.
          </div>
        </form>
      </div>
    </div>
  );
}