import { useState, useEffect } from "react"
import { useParams, Link } from "react-router-dom"
import { ArrowLeft, Shield, Star, Code2, Lock, Fuel, Lightbulb, Loader2 } from "lucide-react"

const mockInsights = {
  contractName: "TokenSale.sol",
  overallReview: "This contract shows solid fundamentals but has several concerning patterns that could lead to security issues. I particularly like your use of the Ownable pattern for access control, but the contract is missing critical protections against reentrancy and other common vulnerabilities.",
  sections: {
    codeQuality: {
      title: "Code Quality",
      icon: Code2,
      content: "The code is generally well-structured with clear function names and good variable naming. However, there's a lack of consistent documentation, with some functions missing NatSpec comments entirely. The use of constants for configuration is a good practice, but there are several magic numbers in the code that should be replaced with named constants. The contract could benefit from better modularization, with some functions being too large and handling multiple responsibilities."
    },
    securityConsiderations: {
      title: "Security Considerations",
      icon: Lock,
      content: "Beyond the vulnerabilities already identified, there are several other security considerations:\n\n1. The contract lacks input validation in several places, particularly around user-provided inputs.\n\n2. There's no protection against front-running attacks in the price-sensitive functions.\n\n3. The contract uses block.timestamp for time-sensitive operations, which can be manipulated slightly by miners.\n\n4. There are no rate limiting mechanisms to prevent abuse of certain functions."
    },
    gasOptimization: {
      title: "Gas Optimization",
      icon: Fuel,
      content: "There are several opportunities for gas optimization:\n\n1. Use uint256 instead of smaller integer types that don't save gas but increase complexity.\n\n2. Remove redundant storage reads by caching storage variables in memory when used multiple times within a function.\n\n3. Use unchecked blocks for arithmetic operations where overflow/underflow is not a concern, particularly in for-loops.\n\n4. Consider batching operations to reduce the number of state changes and thus save gas."
    },
    improvementSuggestions: {
      title: "Improvement Suggestions",
      icon: Lightbulb,
      content: "Here are some suggested improvements beyond fixing the identified vulnerabilities:\n\n1. Implement the checks-effects-interactions pattern to prevent reentrancy attacks.\n\n```solidity\nfunction withdraw() public {\n    uint balance = balances[msg.sender];\n    require(balance > 0);\n    \n    // Update state before interaction\n    balances[msg.sender] = 0;\n    \n    // Then perform external call\n    (bool success, ) = msg.sender.call{value: balance}(\"\");\n    require(success, \"Transfer failed\");\n}\n```\n\n2. Add proper events for all state changes to improve off-chain monitoring capabilities.\n\n3. Consider using the OpenZeppelin SafeERC20 library for safer token handling.\n\n4. Implement more granular access control using role-based permissions instead of just owner functions."
    }
  }
};

export default function InsightsPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState<typeof mockInsights | null>(null);
  
  // Simulate API call to fetch insights
  useEffect(() => {
    const fetchInsights = async () => {
      setLoading(true);
      
      // In a real app, fetch the insights from your API
      // const response = await fetch(`/api/insights/${analysisId}`);
      // const data = await response.json();
      
      // Using mock data for demonstration
      setTimeout(() => {
        setInsights(mockInsights);
        setLoading(false);
      }, 1500);
    };
    
    fetchInsights();
  }, [analysisId]);
  
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="flex flex-col items-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
          <p className="text-muted-foreground">Loading developer insights...</p>
        </div>
      </div>
    );
  }
  
  if (!insights) {
    return (
      <div className="container mx-auto py-10 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-card border rounded-lg p-8 text-center">
            <h2 className="text-2xl font-bold mb-2">Insights Not Available</h2>
            <p className="text-muted-foreground mb-6">
              We couldn't generate developer insights for this contract.
            </p>
            <Link 
              to={`/report/${analysisId}`}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
            >
              Back to Report
            </Link>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-10 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <Link to={`/report/${analysisId}`} className="mr-4">
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <Shield className="h-6 w-6 text-primary mr-2" />
            <h1 className="text-2xl font-bold">Developer Insights</h1>
          </div>
          <div className="text-sm text-muted-foreground">
            {insights.contractName}
          </div>
        </div>
        
        {/* Overall Review */}
        <div className="bg-card border rounded-lg p-6 mb-8">
          <div className="flex items-start">
            <Star className="h-6 w-6 text-yellow-500 mr-4 mt-1 flex-shrink-0" />
            <div>
              <h2 className="text-xl font-semibold mb-3">Overall Review</h2>
              <p className="text-lg leading-relaxed">{insights.overallReview}</p>
            </div>
          </div>
        </div>
        
        {/* Sections */}
        <div className="space-y-8">
          {Object.entries(insights.sections).map(([key, section]) => (
            <div key={key} className="bg-card border rounded-lg p-6">
              <div className="flex items-start">
                <section.icon className="h-6 w-6 text-primary mr-4 mt-1 flex-shrink-0" />
                <div>
                  <h2 className="text-xl font-semibold mb-3">{section.title}</h2>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    {section.content.split('\n\n').map((paragraph, i) => {
                      // Check if paragraph is a code block
                      if (paragraph.startsWith("```") && paragraph.endsWith("```")) {
                        const [, language, ...codeLines] = paragraph.split('\n');
                        const code = codeLines.slice(0, -1).join('\n');
                        
                        return (
                          <pre key={i} className="bg-background rounded-md p-4 my-4 overflow-auto">
                            <code className="text-sm">{code}</code>
                          </pre>
                        );
                      }
                      
                      return <p key={i} className="mb-4 leading-relaxed">{paragraph}</p>;
                    })}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {/* Actions */}
        <div className="flex justify-between mt-8">
          <Link 
            to={`/report/${analysisId}`}
            className="border border-input px-4 py-2 rounded-md hover:bg-accent"
          >
            Back to Report
          </Link>
          <Link 
            to={`/chat/${analysisId}`}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
          >
            Chat with AI Assistant
          </Link>
        </div>
      </div>
    </div>
  );
}