import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Shield,
  AlertTriangle,
  Clock,
  MessageCircle,
  Download,
  FileCode,
  Check,
  Info,
  AlertCircle,
  Flame,
  Code,
  Lightbulb,
} from "lucide-react";

interface Vulnerability {
  id?: string;
  type: string;
  description: string;
  location?: string;
  severity?: string;
  confidence?: number;
  details?: string;
  recommendation?: string;
  affectedFunctions?: string[];
  // RAG Enhancement fields
  rag_explanation?: string;
  rag_enhanced?: boolean;
  rag_confidence?: number;
  // Classifier fields
  all_probabilities?: {
    Low: number;
    Medium: number;
    High: number;
  };
  classifier_enhanced?: boolean;
}

interface AnalysisResult {
  contract_name: string;
  contract_path: string;
  timestamp: string;
  functions?: { name: string }[];
  vulnerabilities: Vulnerability[];
  vulnerability_summary?: {
    total: number;
    by_severity: {
      High: number;
      Medium: number;
      Low: number;
    };
  };
  report_content?: string;
  contract_stats?: {
    name: string;
    inheritance?: string;
  };
  analysis?: {
    vulnerabilities: Vulnerability[];
    functions: { name: string }[];
    vulnerability_summary?: {
      total: number;
      by_severity: {
        High: number;
        Medium: number;
        Low: number;
      };
    };
  };
  report?: {
    report_content: string;
  };
  enhancement_stats?: {
    total_vulnerabilities: number;
    rag_enhanced: number;
    classifier_enhanced: number;
    enhancement_rate: number;
  };
}

export default function ReportPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/analysis/${analysisId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch report: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log("API Response:", data);
        
        // Check if vulnerabilities are in nested analysis object
        const vulnerabilities = data.analysis?.vulnerabilities || data.vulnerabilities || [];
        const functions = data.analysis?.functions || data.functions || [];
        
        // Get vulnerability summary from appropriate location
        let vulnSummary = data.vulnerability_summary || data.analysis?.vulnerability_summary;
        
        // If no summary exists, calculate it
        if (!vulnSummary) {
          const high = vulnerabilities.filter((v: any) => v.severity === "High").length;
          const medium = vulnerabilities.filter((v: any) => v.severity === "Medium").length;
          const low = vulnerabilities.filter((v: any) => v.severity === "Low").length;
          vulnSummary = {
            total: vulnerabilities.length,
            by_severity: { High: high, Medium: medium, Low: low },
          };
        }
        
        // Get report content from appropriate location
        const reportContent = data.report_content || data.report?.report_content || "";
        
        // Create standardized result object
        const result: AnalysisResult = {
          contract_name: data.contract_name || data.contractName || data.contract_stats?.name || "Unknown Contract",
          contract_path: data.contract_path || "",
          timestamp: data.timestamp || new Date().toISOString(),
          functions: functions.map((fn: any) => ({ name: fn.name })),
          vulnerabilities: vulnerabilities.map((v: any, index: number) => ({
            id: v.id || `VULN-${index + 1}`,
            type: v.type || "Unknown",
            description: v.description || "",
            location: v.location || (v.affectedFunctions ? v.affectedFunctions.join(", ") : "Unknown"),
            severity: v.severity || getSeverity(v.type),
            confidence: v.confidence || 0.8,
            details: v.details || v.description,
            recommendation: v.recommendation || getRecommendation(v.type),
            affectedFunctions: v.affectedFunctions || [],
            // RAG fields
            rag_explanation: v.rag_explanation || "",
            rag_enhanced: v.rag_enhanced || false,
            rag_confidence: v.rag_confidence || 0,
            // Classifier fields
            all_probabilities: v.all_probabilities || null,
            classifier_enhanced: v.classifier_enhanced || false,
          })),
          vulnerability_summary: vulnSummary,
          report_content: reportContent,
          enhancement_stats: data.enhancement_stats || {
            total_vulnerabilities: vulnerabilities.length,
            rag_enhanced: vulnerabilities.filter((v: any) => v.rag_enhanced).length,
            classifier_enhanced: vulnerabilities.filter((v: any) => v.classifier_enhanced).length,
            enhancement_rate: 0
          }
        };
        
        setReport(result);
      } catch (error) {
        console.error("Error fetching report:", error);
        setError("Failed to load the audit report. Please try again.");
        setReport(null);
      } finally {
        setLoading(false);
      }
    };
    
    if (analysisId) {
      fetchReport();
    }
  }, [analysisId]);

  const getSeverity = (type: string): string => {
    const typeLC = type.toLowerCase();
    if (typeLC.includes("reentrancy") || typeLC.includes("overflow") || typeLC.includes("access control")) {
      return "High";
    } else if (typeLC.includes("unchecked") || typeLC.includes("timestamp") || typeLC.includes("version")) {
      return "Medium";
    }
    return "Low";
  };

  const getRecommendation = (type: string): string => {
    const typeLC = type.toLowerCase();
    if (typeLC.includes("reentrancy")) {
      return "Implement the checks-effects-interactions pattern and consider using ReentrancyGuard.";
    } else if (typeLC.includes("unchecked")) {
      return "Always check return values of external calls and handle failures appropriately.";
    } else if (typeLC.includes("access control")) {
      return "Implement proper access controls using modifiers like onlyOwner or role-based permissions.";
    } else if (typeLC.includes("gas")) {
      return "Optimize gas usage by avoiding loops with unbounded iterations and minimizing storage operations.";
    } else if (typeLC.includes("timestamp")) {
      return "Avoid relying on block.timestamp for critical timing decisions, as it can be manipulated by miners.";
    } else if (typeLC.includes("version")) {
      return "Update to a more recent and stable compiler version without known issues.";
    } else if (typeLC.includes("low level") || typeLC.includes("call")) {
      return "Consider using safer alternatives like transfer() or send(), or implement thorough checks when using low-level calls.";
    }
    return "Review the code and follow security best practices to address this issue.";
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[70vh]">
        <div className="flex flex-col items-center">
          <div className="mb-4 h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <h3 className="text-xl font-medium mb-2">Generating Enhanced Audit Report</h3>
          <p className="text-muted-foreground">Analyzing contract with AI enhancements...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="container mx-auto py-10 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-card border rounded-lg p-8 text-center">
            <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Report Not Found</h2>
            <p className="text-muted-foreground mb-6">
              {error || "We couldn't find an audit report for the specified analysis ID."}
            </p>
            <Link to="/" className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
              Return to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const highVulnerabilities = report.vulnerabilities.filter((v) => v.severity === "High");
  const mediumVulnerabilities = report.vulnerabilities.filter((v) => v.severity === "Medium");
  const lowVulnerabilities = report.vulnerabilities.filter((v) => v.severity === "Low");

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "High":
        return <Flame className="h-5 w-5 text-red-500" />;
      case "Medium":
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case "Low":
        return <Info className="h-5 w-5 text-blue-500" />;
      default:
        return <Info className="h-5 w-5 text-blue-500" />;
    }
  };

  return (
    <div className="container mx-auto py-10 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between">
          <div className="flex items-center mb-4 md:mb-0">
            <Shield className="h-8 w-8 text-primary mr-3" />
            <div>
              <h1 className="text-3xl font-bold">Enhanced Audit Report</h1>
              <p className="text-muted-foreground">{new Date(report.timestamp).toLocaleString()}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Link to="/" className="text-sm text-muted-foreground hover:text-foreground flex items-center">
              <Shield className="h-4 w-4 mr-1" />
              <span>Dashboard</span>
            </Link>
            <span className="text-muted-foreground">•</span>
            <button className="text-sm text-muted-foreground hover:text-foreground flex items-center">
              <Download className="h-4 w-4 mr-1" />
              <span>Download</span>
            </button>
          </div>
        </div>

        {/* Contract Info */}
        <div className="bg-card border rounded-lg p-6 mb-8">
          <div className="flex items-start">
            <FileCode className="h-6 w-6 text-primary mr-4 mt-1" />
            <div className="flex-1">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold mb-1">{report.contract_name}</h2>
                  <p className="text-sm text-muted-foreground">{report.contract_path}</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                <div className="bg-background p-4 rounded-md border">
                  <h3 className="text-sm font-medium text-muted-foreground mb-1">Vulnerabilities</h3>
                  <p className="text-2xl font-bold">{report.vulnerability_summary?.total || 0}</p>
                </div>
                <div className="bg-background p-4 rounded-md border">
                  <h3 className="text-sm font-medium text-muted-foreground mb-1">Functions Analyzed</h3>
                  <p className="text-2xl font-bold">{report.functions?.length || 0}</p>
                </div>
                <div className="bg-background p-4 rounded-md border">
                  <h3 className="text-sm font-medium text-muted-foreground mb-1">AI Enhanced</h3>
                  <p className="text-2xl font-bold text-blue-600">{report.enhancement_stats?.rag_enhanced || 0}</p>
                </div>
                <div className="bg-background p-4 rounded-md border">
                  <h3 className="text-sm font-medium text-muted-foreground mb-1">Enhancement Rate</h3>
                  <p className="text-2xl font-bold text-green-600">
                    {Math.round((report.enhancement_stats?.enhancement_rate || 0) * 100)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Enhancement Stats */}
        {report.enhancement_stats && report.enhancement_stats.rag_enhanced > 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-8">
            <div className="flex items-center mb-4">
              <MessageCircle className="h-6 w-6 text-blue-600 mr-3" />
              <h2 className="text-xl font-semibold text-blue-800 dark:text-blue-200">AI Enhancement Summary</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{report.enhancement_stats.rag_enhanced}</div>
                <div className="text-sm text-blue-700 dark:text-blue-300">RAG Enhanced</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{report.enhancement_stats.classifier_enhanced}</div>
                <div className="text-sm text-green-700 dark:text-green-300">AI Classified</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(report.enhancement_stats.enhancement_rate * 100)}%
                </div>
                <div className="text-sm text-purple-700 dark:text-purple-300">Enhancement Rate</div>
              </div>
            </div>
          </div>
        )}

        {/* Vulnerabilities Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2" />
            Vulnerabilities
          </h2>
          {report.vulnerabilities.length === 0 ? (
            <div className="bg-card border rounded-lg p-6 text-center">
              <Check className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-medium mb-2">No Vulnerabilities Found</h3>
              <p className="text-muted-foreground">Great job! Your contract passed all security checks.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* High Severity */}
              {highVulnerabilities.length > 0 && (
                <VulnerabilitySection 
                  vulnerabilities={highVulnerabilities} 
                  severity="High" 
                  color="red" 
                  getSeverityIcon={getSeverityIcon}
                />
              )}
              
              {/* Medium Severity */}
              {mediumVulnerabilities.length > 0 && (
                <VulnerabilitySection 
                  vulnerabilities={mediumVulnerabilities} 
                  severity="Medium" 
                  color="yellow" 
                  getSeverityIcon={getSeverityIcon}
                />
              )}
              
              {/* Low Severity */}
              {lowVulnerabilities.length > 0 && (
                <VulnerabilitySection 
                  vulnerabilities={lowVulnerabilities} 
                  severity="Low" 
                  color="blue" 
                  getSeverityIcon={getSeverityIcon}
                />
              )}
            </div>
          )}
        </div>

        {/* Functions Section */}
        {report.functions && report.functions.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <Code className="h-5 w-5 mr-2" />
              Analyzed Functions
            </h2>
            <div className="bg-card border rounded-lg p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {report.functions.map((fn, index) => (
                  <div key={index} className="p-3 bg-background rounded-md border">
                    <code className="text-sm">{fn.name}</code>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Best Practices Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Lightbulb className="h-5 w-5 mr-2" />
            Best Practices
          </h2>
          <div className="bg-card border rounded-lg p-6">
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center mr-3 mt-0.5">
                  <Check className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <h4 className="text-lg font-medium mb-1">Implement Security Patterns</h4>
                  <p className="text-muted-foreground">
                    Follow established security patterns like Checks-Effects-Interactions, and use well-tested libraries like
                    OpenZeppelin for common contract functionality.
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center mr-3 mt-0.5">
                  <Check className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <h4 className="text-lg font-medium mb-1">Comprehensive Testing</h4>
                  <p className="text-muted-foreground">
                    Develop thorough test suites that cover all edge cases and potential attack vectors. Use formal verification
                    tools where possible.
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center mr-3 mt-0.5">
                  <Check className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <h4 className="text-lg font-medium mb-1">Gas Optimization</h4>
                  <p className="text-muted-foreground">
                    Optimize for gas usage without sacrificing security. Consider storage patterns, loop optimizations, and
                    efficient data structures.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Analysis Report Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <MessageCircle className="h-5 w-5 mr-2" />
            AI Analysis Report
          </h2>
          {report.report_content ? (
            <div className="bg-card border rounded-lg p-6">
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <div
                  dangerouslySetInnerHTML={{
                    __html: report.report_content
                      .replace(/^# /gm, '<h1 class="text-2xl font-bold mb-4">')
                      .replace(/^## /gm, '<h2 class="text-xl font-bold mt-6 mb-3">')
                      .replace(/^### /gm, '<h3 class="text-lg font-bold mt-5 mb-2">')
                      .replace(/^#### /gm, '<h4 class="text-md font-bold mt-4 mb-2">')
                      .replace(/```([^`]+)```/gs, '<pre class="bg-background p-4 rounded-md my-4 overflow-x-auto"><code>$1</code></pre>')
                      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                      .replace(/\*([^*]+)\*/g, '<em>$1</em>')
                      .replace(/🔴/g, '<span class="inline-block w-3 h-3 bg-red-500 rounded-full mr-1"></span>')
                      .replace(/🟡/g, '<span class="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-1"></span>')
                      .replace(/🟢/g, '<span class="inline-block w-3 h-3 bg-green-500 rounded-full mr-1"></span>')
                      .replace(/\n\n/g, '</p><p class="mb-4">')
                  }}
                />
              </div>
              <div className="mt-6 pt-4 border-t flex flex-col sm:flex-row gap-4 items-center sm:justify-end">
                <Link
                  to={`/chat/${analysisId}`}
                  className="w-full sm:w-auto inline-flex items-center justify-center bg-primary text-primary-foreground px-6 py-3 rounded-md font-medium hover:bg-primary/90"
                >
                  <MessageCircle className="mr-2 h-5 w-5" />
                  Chat with AI Assistant
                </Link>
                <Link
                  to={`/insights/${analysisId}`}
                  className="w-full sm:w-auto inline-flex items-center justify-center bg-secondary text-secondary-foreground px-6 py-3 rounded-md font-medium hover:bg-secondary/80"
                >
                  <Lightbulb className="mr-2 h-5 w-5" />
                  View Developer Insights
                </Link>
              </div>
            </div>
          ) : (
            <div className="bg-card border rounded-lg p-6">
              <p className="text-muted-foreground mb-6">
                Have questions about the vulnerabilities in your contract? Need guidance on implementing the recommended fixes?
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  to={`/chat/${analysisId}`}
                  className="w-full sm:w-auto inline-flex items-center justify-center bg-primary text-primary-foreground px-6 py-3 rounded-md font-medium hover:bg-primary/90"
                >
                  <MessageCircle className="mr-2 h-5 w-5" />
                  Chat with AI Assistant
                </Link>
                <Link
                  to={`/insights/${analysisId}`}
                  className="w-full sm:w-auto inline-flex items-center justify-center bg-secondary text-secondary-foreground px-6 py-3 rounded-md font-medium hover:bg-secondary/80"
                >
                  <Lightbulb className="mr-2 h-5 w-5" />
                  View Developer Insights
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-4">
          <Link
            to="/"
            className="w-full md:w-auto inline-flex items-center justify-center bg-secondary text-secondary-foreground px-6 py-3 rounded-md font-medium hover:bg-secondary/80"
          >
            <Shield className="mr-2 h-5 w-5" />
            Back to Dashboard
          </Link>
          <button className="w-full md:w-auto inline-flex items-center justify-center bg-primary text-primary-foreground px-6 py-3 rounded-md font-medium hover:bg-primary/90">
            <Download className="mr-2 h-5 w-5" />
            Download Full Report
          </button>
          <button className="w-full md:w-auto inline-flex items-center justify-center bg-card border text-foreground px-6 py-3 rounded-md font-medium hover:bg-accent">
            <Clock className="mr-2 h-5 w-5" />
            Schedule Follow-Up Audit
          </button>
        </div>
      </div>
    </div>
  );
}

// Enhanced VulnerabilitySection component with RAG support
function VulnerabilitySection({ vulnerabilities, severity, color, getSeverityIcon }) {
  return (
    <div>
      <h3 className="text-lg font-medium mb-3 flex items-center">
        <div className={`w-4 h-4 rounded-full bg-${color}-500 mr-2`}></div>
        {severity} Severity Issues ({vulnerabilities.length})
      </h3>
      <div className="space-y-4">
        {vulnerabilities.map((vuln, index) => (
          <div key={vuln.id || index} className={`bg-card border border-l-4 border-l-${color}-500 rounded-lg overflow-hidden`}>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold flex items-center">
                  {getSeverityIcon(vuln.severity || severity)}
                  <span className="ml-2">{vuln.type}</span>
                </h4>
                <div className="flex items-center gap-2">
                  {/* RAG Enhancement Badge */}
                  {vuln.rag_enhanced && (
                    <div className="px-2 py-1 text-xs font-medium rounded-full bg-blue-500/10 text-blue-500 flex items-center">
                      <MessageCircle className="h-3 w-3 mr-1" />
                      AI Enhanced
                    </div>
                  )}
                  <div className={`px-2 py-1 text-xs font-medium rounded-full bg-${color}-500/10 text-${color}-500`}>
                    {vuln.confidence
                      ? `${typeof vuln.confidence === "number"
                          ? Math.round(vuln.confidence * 100)
                          : Math.round(parseFloat(String(vuln.confidence)) * 100)}% Confidence`
                      : `${severity} Severity`}
                  </div>
                </div>
              </div>
              
              {/* Basic Description */}
              <p className="text-muted-foreground mb-4">{vuln.description}</p>
              
              {/* RAG Enhanced Explanation */}
              {vuln.rag_explanation && vuln.rag_explanation !== "RAG enhancement unavailable" && (
                <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                  <div className="flex items-center mb-2">
                    <MessageCircle className="h-4 w-4 text-blue-500 mr-2" />
                    <h5 className="text-sm font-medium text-blue-700 dark:text-blue-300">AI Security Analysis</h5>
                  </div>
                  <div className="text-sm text-blue-800 dark:text-blue-200">
                    {vuln.rag_explanation.length > 500 ? (
                      <details className="cursor-pointer">
                        <summary className="font-medium hover:text-blue-600">
                          {vuln.rag_explanation.substring(0, 200)}... (Click to expand)
                        </summary>
                        <div className="mt-2 whitespace-pre-wrap">
                          {vuln.rag_explanation}
                        </div>
                      </details>
                    ) : (
                      <div className="whitespace-pre-wrap">{vuln.rag_explanation}</div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Location */}
              {vuln.location && (
                <div className="mb-4">
                  <h5 className="text-sm font-medium mb-1">Location</h5>
                  <code className="px-2 py-1 bg-background rounded text-sm">{vuln.location}</code>
                </div>
              )}
              
              {/* Affected Functions */}
              {vuln.affectedFunctions && vuln.affectedFunctions.length > 0 && (
                <div className="mb-4">
                  <h5 className="text-sm font-medium mb-1">Affected Functions</h5>
                  <div className="flex flex-wrap gap-1">
                    {vuln.affectedFunctions.map((func, idx) => (
                      <code key={idx} className="px-2 py-1 bg-background rounded text-xs">
                        {func}
                      </code>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Recommendation */}
              <div>
                <h5 className="text-sm font-medium mb-1">Recommendation</h5>
                <p className="text-sm text-muted-foreground">{vuln.recommendation}</p>
              </div>
              
              {/* Confidence Score Details */}
              {vuln.all_probabilities && (
                <div className="mt-4 pt-4 border-t">
                  <h5 className="text-sm font-medium mb-2">Confidence Breakdown</h5>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="text-center">
                      <div className="text-green-600">Low</div>
                      <div className="font-mono">{Math.round((vuln.all_probabilities.Low || 0) * 100)}%</div>
                    </div>
                    <div className="text-center">
                      <div className="text-yellow-600">Medium</div>
                      <div className="font-mono">{Math.round((vuln.all_probabilities.Medium || 0) * 100)}%</div>
                    </div>
                    <div className="text-center">
                      <div className="text-red-600">High</div>
                      <div className="font-mono">{Math.round((vuln.all_probabilities.High || 0) * 100)}%</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}