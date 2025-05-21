import { useState, useRef, useEffect } from "react"
import { useParams } from "react-router-dom"
import { Send, ArrowLeft, Bot, User, Shield } from "lucide-react"
import { Link } from "react-router-dom"

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your smart contract audit assistant. I can help explain vulnerabilities found in your contract and answer any questions you have about security best practices. What would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date()
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    
    // Simulate AI response
    setTimeout(() => {
      // Sample responses based on message content
      let responseText = "I'll need to analyze that further. Could you provide more details?";
      
      if (input.toLowerCase().includes("reentrancy")) {
        responseText = "Reentrancy vulnerabilities occur when external contract calls are allowed to make new calls back to the calling contract before the first execution is complete. This allows an attacker to recursively call functions before state updates, potentially draining funds. To prevent this, always follow the checks-effects-interactions pattern and consider using a reentrancy guard.";
      } else if (input.toLowerCase().includes("unchecked") || input.toLowerCase().includes("return value")) {
        responseText = "Unchecked external call vulnerabilities happen when your contract makes external calls without checking the return values. This can lead to silent failures and unexpected behavior. Always check return values of functions like send() and transfer(), and handle failures appropriately.";
      } else if (input.toLowerCase().includes("timestamp")) {
        responseText = "Timestamp dependence becomes an issue when contracts rely on block.timestamp for critical timing decisions. Miners can manipulate timestamps slightly (by several seconds), which could affect the outcome in time-sensitive operations. For time-dependent logic, consider using block numbers instead, or ensure that the logic isn't vulnerable to small timestamp manipulations.";
      } else if (input.toLowerCase().includes("fix") || input.toLowerCase().includes("solution")) {
        responseText = "To fix the vulnerabilities in this contract:\n\n1. For the reentrancy issue, make sure to update state variables before making external calls.\n\n2. For unchecked external calls, verify the return values and handle failures.\n\n3. For timestamp dependence, avoid relying on precise timestamps for critical functions.";
      }
      
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: responseText,
        timestamp: new Date()
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };
  
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
            TokenSale.sol
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
              disabled={isLoading}
            />
            <button
              type="submit"
              className="bg-primary text-primary-foreground px-4 py-3 rounded-r-md hover:bg-primary/90 disabled:opacity-50"
              disabled={!input.trim() || isLoading}
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