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

        const result: AnalysisResult = {
          contract_name: data.contract_name || "Unknown Contract",
          contract_path: data.contract_path || "",
          timestamp: data.timestamp || new Date().toISOString(),
          functions: Array.isArray(data.functions) ? data.functions.map((fn: any) => ({ name: fn.name })) : [],
          vulnerabilities: Array.isArray(data.vulnerabilities)
            ? data.vulnerabilities.map((v: any, index: number) => ({
                id: v.id || `VULN-${index + 1}`,
                type: v.type || "Unknown",
                description: v.description || "",
                location: v.affectedFunctions ? v.affectedFunctions.join(", ") : "Unknown",
                severity: v.severity || getSeverity(v.type),
                confidence: v.confidence || 0.8,
                details: v.details || v.description,
                recommendation: v.recommendation || getRecommendation(v.type),
                affectedFunctions: v.affectedFunctions || [],
              }))
            : [],
        };

        if (!data.vulnerability_summary) {
          const high = result.vulnerabilities.filter((v) => v.severity === "High").length;
          const medium = result.vulnerabilities.filter((v) => v.severity === "Medium").length;
          const low = result.vulnerabilities.filter((v) => v.severity === "Low").length;

          result.vulnerability_summary = {
            total: result.vulnerabilities.length,
            by_severity: { High: high, Medium: medium, Low: low },
          };
        } else {
          result.vulnerability_summary = data.vulnerability_summary;
        }

        if (data.contract_stats && data.contract_stats.name) {
          result.contract_name = data.contract_stats.name;
        }

        if (data.report_content) {
          result.report_content = data.report_content;
        }

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
    } else if (typeLC.includes("unchecked") || typeLC.includes("timestamp")) {
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
    }
    return "Review the code and follow security best practices to address this issue.";
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[70vh]">
        <div className="flex flex-col items-center">
          <div className="mb-4 h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <h3 className="text-xl font-medium mb-2">Generating Audit Report</h3>
          <p className="text-muted-foreground">Analyzing contract vulnerabilities...</p>
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

  const calculateSecurityScore = (): { score: number; label: string; color: string } => {
    const { total, by_severity } = report.vulnerability_summary || { total: 0, by_severity: { High: 0, Medium: 0, Low: 0 } };

    if (total === 0) return { score: 100, label: "Excellent", color: "text-green-500" };

    const weightedIssues = by_severity.High * 3 + by_severity.Medium * 2 + by_severity.Low;
    const maxScore = 100;
    const deduction = Math.min(weightedIssues * 5, 95);
    const score = Math.max(maxScore - deduction, 5);

    let label = "Critical";
    let color = "text-red-500";

    if (score >= 90) {
      label = "Excellent";
      color = "text-green-500";
    } else if (score >= 75) {
      label = "Good";
      color = "text-green-400";
    } else if (score >= 60) {
      label = "Fair";
      color = "text-yellow-500";
    } else if (score >= 40) {
      label = "Poor";
      color = "text-orange-500";
    }

    return { score, label, color };
  };

  const securityScore = calculateSecurityScore();

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
              <h1 className="text-3xl font-bold">Audit Report</h1>
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

        <div className="bg-card border rounded-lg p-6 mb-8">
          <div className="flex items-start">
            <FileCode className="h-6 w-6 text-primary mr-4 mt-1" />
            <div className="flex-1">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold mb-1">{report.contract_name}</h2>
                  <p className="text-sm text-muted-foreground">{report.contract_path}</p>
                </div>
                <div className="mt-2 md:mt-0 flex items-center bg-background px-4 py-2 rounded-md border">
                  <div className="mr-3">
                    <div className="text-sm text-muted-foreground">Security Score</div>
                    <div className={`text-2xl font-bold ${securityScore.color}`}>{securityScore.score}</div>
                  </div>
                  <div className={`text-sm font-medium ${securityScore.color}`}>{securityScore.label}</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div className="bg-background p-4 rounded-md border">
                  <h3 className="text-sm font-medium text-muted-foreground mb-1">Vulnerabilities</h3>
                  <p className="text-2xl font-bold">{report.vulnerability_summary?.total || 0}</p>
                </div>
                <div className="bg-background p-4 rounded-md border">
                  <h3 className="text-sm font-medium text-muted-foreground mb-1">Functions Analyzed</h3>
                  <p className="text-2xl font-bold">{report.functions?.length || 0}</p>
                </div>
                <div className="bg-background p-4 rounded-md border">
                  <h3 className="text-sm font-medium text-muted-foreground mb-1">Severity Distribution</h3>
                  <div className="flex items-center space-x-3 mt-1">
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-red-500 mr-1"></div>
                      <span>{report.vulnerability_summary?.by_severity.High || 0}</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-yellow-500 mr-1"></div>
                      <span>{report.vulnerability_summary?.by_severity.Medium || 0}</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-blue-500 mr-1"></div>
                      <span>{report.vulnerability_summary?.by_severity.Low || 0}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

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
              {highVulnerabilities.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium mb-3 flex items-center">
                    <div className="w-4 h-4 rounded-full bg-red-500 mr-2"></div>
                    High Severity Issues ({highVulnerabilities.length})
                  </h3>
                  <div className="space-y-4">
                    {highVulnerabilities.map((vuln, index) => (
                      <div key={vuln.id || index} className="bg-card border border-l-4 border-l-red-500 rounded-lg overflow-hidden">
                        <div className="p-6">
                          <div className="flex items-center justify-between mb-4">
                            <h4 className="text-lg font-semibold flex items-center">
                              {getSeverityIcon(vuln.severity || "High")}
                              <span className="ml-2">{vuln.type}</span>
                            </h4>
                            <div className="px-2 py-1 text-xs font-medium rounded-full bg-red-500/10 text-red-500">
                              {vuln.confidence
                                ? typeof vuln.confidence === "number"
                                  ? Math.round(vuln.confidence * 100)
                                  : Math.round(parseFloat(String(vuln.confidence)) * 100)
                                : "High Severity"}
                            </div>
                          </div>
                          <p className="text-muted-foreground mb-4">{vuln.description}</p>
                          {vuln.location && (
                            <div className="mb-4">
                              <h5 className="text-sm font-medium mb-1">Location</h5>
                              <code className="px-2 py-1 bg-background rounded text-sm">{vuln.location}</code>
                            </div>
                          )}
                          <div>
                            <h5 className="text-sm font-medium mb-1">Recommendation</h5>
                            <p className="text-sm text-muted-foreground">{vuln.recommendation}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {mediumVulnerabilities.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium mb-3 flex items-center">
                    <div className="w-4 h-4 rounded-full bg-yellow-500 mr-2"></div>
                    Medium Severity Issues ({mediumVulnerabilities.length})
                  </h3>
                  <div className="space-y-4">
                    {mediumVulnerabilities.map((vuln, index) => (
                      <div key={vuln.id || index} className="bg-card border border-l-4 border-l-yellow-500 rounded-lg overflow-hidden">
                        <div className="p-6">
                          <div className="flex items-center justify-between mb-4">
                            <h4 className="text-lg font-semibold flex items-center">
                              {getSeverityIcon(vuln.severity || "Medium")}
                              <span className="ml-2">{vuln.type}</span>
                            </h4>
                            <div className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-500/10 text-yellow-500">
                              {vuln.confidence
                                ? `${typeof vuln.confidence === "number"
                                    ? Math.round(vuln.confidence * 100)
                                    : Math.round(parseFloat(String(vuln.confidence)) * 100)}% Confidence`
                                : "Medium Severity"}
                            </div>
                          </div>
                          <p className="text-muted-foreground mb-4">{vuln.description}</p>
                          {vuln.location && (
                            <div className="mb-4">
                              <h5 className="text-sm font-medium mb-1">Location</h5>
                              <code className="px-2 py-1 bg-background rounded text-sm">{vuln.location}</code>
                            </div>
                          )}
                          <div>
                            <h5 className="text-sm font-medium mb-1">Recommendation</h5>
                            <p className="text-sm text-muted-foreground">{vuln.recommendation}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {lowVulnerabilities.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium mb-3 flex items-center">
                    <div className="w-4 h-4 rounded-full bg-blue-500 mr-2"></div>
                    Low Severity Issues ({lowVulnerabilities.length})
                  </h3>
                  <div className="space-y-4">
                    {lowVulnerabilities.map((vuln, index) => (
                      <div key={vuln.id || index} className="bg-card border border-l-4 border-l-blue-500 rounded-lg overflow-hidden">
                        <div className="p-6">
                          <div className="flex items-center justify-between mb-4">
                            <h4 className="text-lg font-semibold flex items-center">
                              {getSeverityIcon(vuln.severity || "Low")}
                              <span className="ml-2">{vuln.type}</span>
                            </h4>
                            <div className="px-2 py-1 text-xs font-medium rounded-full bg-blue-500/10 text-blue-500">
                              {vuln.confidence
                                ? `${typeof vuln.confidence === "number"
                                    ? Math.round(vuln.confidence * 100)
                                    : Math.round(parseFloat(String(vuln.confidence)) * 100)}% Confidence`
                                : "Low Severity"}
                            </div>
                          </div>
                          <p className="text-muted-foreground mb-4">{vuln.description}</p>
                          {vuln.location && (
                            <div className="mb-4">
                              <h5 className="text-sm font-medium mb-1">Location</h5>
                              <code className="px-2 py-1 bg-background rounded text-sm">{vuln.location}</code>
                            </div>
                          )}
                          <div>
                            <h5 className="text-sm font-medium mb-1">Recommendation</h5>
                            <p className="text-sm text-muted-foreground">{vuln.recommendation}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

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

        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <MessageCircle className="h-5 w-5 mr-2" />
            AI Analysis Report
          </h2>
          {report.report_content ? (
            <div className="bg-card border rounded-lg p-6">
              <div className="prose prose-sm max-w-none">
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
                      .replace(/\n\n/g, '<p class="mb-4"></p>'),
                  }}
                />
              </div>
            </div>
          ) : (
            <div className="bg-card border rounded-lg p-6">
              <p className="text-muted-foreground mb-6">
                Have questions about the vulnerabilities in your contract? Need guidance on implementing the recommended fixes?
              </p>
              <button className="inline-flex items-center justify-center bg-primary text-primary-foreground px-6 py-3 rounded-md font-medium hover:bg-primary/90">
                <MessageCircle className="mr-2 h-5 w-5" />
                Chat with AI Assistant
              </button>
            </div>
          )}
        </div>

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