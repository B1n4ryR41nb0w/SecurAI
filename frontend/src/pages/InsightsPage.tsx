import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Shield,
  ArrowLeft,
  Code,
  Download,
  Lightbulb,
  FileCode,
  AlertTriangle,
  MessageCircle,
  RefreshCw,
} from "lucide-react";

interface InsightsData {
  contract_name: string;
  insights: string;
  timestamp: string;
  error?: boolean;
}

export default function InsightsPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState<InsightsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [regenerating, setRegenerating] = useState(false);

  const fetchInsights = async (forceRegenerate = false) => {
    if (!analysisId) return;
    
    setLoading(!forceRegenerate); // Don't show full loading if regenerating
    setRegenerating(forceRegenerate);
    setError(null);
    
    try {
      let response;
      
      if (forceRegenerate) {
        // Force regeneration by calling POST directly
        response = await fetch("http://localhost:8000/api/insights", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            analysis_id: analysisId,
          }),
        });
      } else {
        // Try to get existing insights first
        response = await fetch(`http://localhost:8000/api/insights/${analysisId}`);
        
        // If not found, create new insights
        if (response.status === 404) {
          response = await fetch("http://localhost:8000/api/insights", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              analysis_id: analysisId,
            }),
          });
        }
      }
      
      if (!response.ok) {
        throw new Error(`Failed to ${forceRegenerate ? 'regenerate' : 'fetch'} insights: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error("Failed to generate insights");
      }
      
      setInsights(data);
    } catch (err) {
      console.error("Error with insights:", err);
      setError(`Failed to ${forceRegenerate ? 'regenerate' : 'load'} developer insights: ${err instanceof Error ? err.message : String(err)}`);
      if (!forceRegenerate) {
        setInsights(null);
      }
    } finally {
      setLoading(false);
      setRegenerating(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, [analysisId]);

  const handleRegenerate = () => {
    fetchInsights(true);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[70vh]">
        <div className="flex flex-col items-center">
          <div className="mb-4 h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <h3 className="text-xl font-medium mb-2">Generating Developer Insights</h3>
          <p className="text-muted-foreground">Analyzing code patterns and best practices...</p>
        </div>
      </div>
    );
  }

  if (error && !insights) {
    return (
      <div className="container mx-auto py-10 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-card border rounded-lg p-8 text-center">
            <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Insights Not Available</h2>
            <p className="text-muted-foreground mb-6">
              {error || "We couldn't generate developer insights for this contract."}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => fetchInsights()}
                className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
              >
                Try Again
              </button>
              <Link 
                to={`/report/${analysisId}`} 
                className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md hover:bg-secondary/80"
              >
                Return to Audit Report
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between">
          <div className="flex items-center mb-4 md:mb-0">
            <Link 
              to={`/report/${analysisId}`} 
              className="mr-4 p-2 hover:bg-accent rounded-md transition-colors"
              title="Back to Report"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <Lightbulb className="h-8 w-8 text-primary mr-3" />
            <div>
              <h1 className="text-3xl font-bold">Developer Insights</h1>
              <p className="text-muted-foreground">
                {insights && new Date(insights.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button 
              onClick={handleRegenerate}
              disabled={regenerating}
              className="inline-flex items-center justify-center px-4 py-2 bg-secondary text-secondary-foreground rounded-md font-medium hover:bg-secondary/80 disabled:opacity-50"
              title="Regenerate insights"
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${regenerating ? 'animate-spin' : ''}`} />
              <span>{regenerating ? 'Regenerating...' : 'Regenerate'}</span>
            </button>
            <button className="inline-flex items-center justify-center px-4 py-2 bg-primary text-primary-foreground rounded-md font-medium hover:bg-primary/90">
              <Download className="mr-2 h-4 w-4" />
              <span>Download</span>
            </button>
          </div>
        </div>

        {/* Error banner (if regeneration failed but we still have old insights) */}
        {error && insights && (
          <div className="mb-6 bg-destructive/10 border border-destructive/20 rounded-lg p-4">
            <div className="flex items-center">
              <AlertTriangle className="h-5 w-5 text-destructive mr-2" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          </div>
        )}

        {/* Contract Info */}
        <div className="bg-card border rounded-lg p-6 mb-8">
          <div className="flex items-start">
            <FileCode className="h-6 w-6 text-primary mr-4 mt-1" />
            <div>
              <h2 className="text-xl font-semibold mb-2">
                {insights?.contract_name || "Contract Analysis"}
              </h2>
              <div className="flex items-center">
                <Code className="h-4 w-4 text-muted-foreground mr-2" />
                <span className="text-sm text-muted-foreground">
                  Developer-focused insights and optimization recommendations
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Insights Content */}
        {insights && (
          <div className="bg-card border rounded-lg p-6 mb-8">
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <div
                dangerouslySetInnerHTML={{
                  __html: insights.insights
                    .replace(/^# /gm, '<h1 class="text-2xl font-bold mb-4 text-foreground">')
                    .replace(/^## /gm, '<h2 class="text-xl font-bold mt-6 mb-3 text-foreground">')
                    .replace(/^### /gm, '<h3 class="text-lg font-bold mt-5 mb-2 text-foreground">')
                    .replace(/^#### /gm, '<h4 class="text-md font-bold mt-4 mb-2 text-foreground">')
                    .replace(/```([^`]+)```/gs, '<pre class="bg-background p-4 rounded-md my-4 overflow-x-auto border"><code class="text-sm">$1</code></pre>')
                    .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold">$1</strong>')
                    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
                    .replace(/\n\n/g, '</p><p class="mb-4 text-muted-foreground">')
                    .replace(/^/, '<p class="mb-4 text-muted-foreground">')
                    .replace(/$/, '</p>')
                }}
              />
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Link
            to={`/report/${analysisId}`}
            className="inline-flex items-center justify-center px-6 py-3 bg-secondary text-secondary-foreground rounded-md font-medium hover:bg-secondary/80"
          >
            <Shield className="mr-2 h-5 w-5" />
            Back to Audit Report
          </Link>
          <Link
            to={`/chat/${analysisId}`}
            className="inline-flex items-center justify-center px-6 py-3 bg-primary text-primary-foreground rounded-md font-medium hover:bg-primary/90"
          >
            <MessageCircle className="mr-2 h-5 w-5" />
            Chat with AI Assistant
          </Link>
        </div>
      </div>
    </div>
  );
}