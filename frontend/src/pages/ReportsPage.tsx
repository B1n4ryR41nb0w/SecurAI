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
  rag_explanation?: string;
  rag_enhanced?: boolean;
  rag_confidence?: number;
  all_probabilities?: { Low: number; Medium: number; High: number };
  classifier_enhanced?: boolean;
  slither_confidence?: string;
  slither_impact?: string;
}

interface AnalysisResult {
  contract_name: string;
  contract_path: string;
  timestamp: string;
  functions?: { name: string }[];
  vulnerabilities: Vulnerability[];
  vulnerability_summary?: { total: number; by_severity: { High: number; Medium: number; Low: number } };
  report_content?: string;
  contract_stats?: { name: string; inheritance?: string };
  analysis?: {
    vulnerabilities: Vulnerability[];
    functions: { name: string }[];
    vulnerability_summary?: { total: number; by_severity: { High: number; Medium: number; Low: number } };
  };
  report?: { report_content: string };
  enhancement_stats?: { total_vulnerabilities: number; rag_enhanced: number; classifier_enhanced: number; enhancement_rate: number };
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
        if (!response.ok) throw new Error(`Failed to fetch report: ${response.statusText}`);
        const data = await response.json();

        const vulnerabilities = data.analysis?.vulnerabilities || data.vulnerabilities || [];
        const functions = data.analysis?.functions || data.functions || [];
        let vulnSummary = data.vulnerability_summary || data.analysis?.vulnerability_summary;

        if (!vulnSummary) {
          const high = vulnerabilities.filter((v: any) => v.severity === "High").length;
          const medium = vulnerabilities.filter((v: any) => v.severity === "Medium").length;
          const low = vulnerabilities.filter((v: any) => v.severity === "Low").length;
          vulnSummary = { total: vulnerabilities.length, by_severity: { High: high, Medium: medium, Low: low } };
        }

        const result: AnalysisResult = {
          contract_name: data.contract_name || data.contractName || data.contract_stats?.name || "Unknown Contract",
          contract_path: data.contract_path || "",
          timestamp: data.timestamp || new Date().toISOString(),
          functions: functions.map((fn: any) => ({ name: fn.name })),
          vulnerabilities: vulnerabilities.map((v: any, index: number) => {
            // Clean up description by extracting key details
            let cleanedDescription = v.description || "";
            cleanedDescription = cleanedDescription.replace(/\(.*?\)/g, match => {
              const parts = match.slice(1, -1).split('#');
              return parts.length > 1 ? `#${parts[1]}` : match;
            }).replace(/^[^\(]+\(/, '').replace(/\)$/, '');
            return {
              id: v.id || `VULN-${index + 1}`,
              type: v.type || "Unknown",
              description: cleanedDescription || v.description,
              location: v.location || (v.affectedFunctions ? v.affectedFunctions.join(", ") : "Unknown"),
              severity: v.severity || "Medium",
              confidence: v.confidence || 0.5,
              details: v.details || v.description,
              recommendation: v.recommendation || "Review and apply best practices.",
              affectedFunctions: v.affectedFunctions || [],
              rag_explanation: v.rag_explanation || "",
              rag_enhanced: v.rag_enhanced || false,
              rag_confidence: v.rag_confidence || 0,
              all_probabilities: v.all_probabilities || null,
              classifier_enhanced: v.classifier_enhanced || false,
              slither_confidence: v.slither_confidence || "Unknown",
              slither_impact: v.slither_impact || "Unknown",
            };
          }),
          vulnerability_summary: vulnSummary,
          report_content: data.report_content || data.report?.report_content || "",
          enhancement_stats: data.enhancement_stats || {
            total_vulnerabilities: vulnerabilities.length,
            rag_enhanced: vulnerabilities.filter((v: any) => v.rag_enhanced).length,
            classifier_enhanced: vulnerabilities.filter((v: any) => v.classifier_enhanced).length,
            enhancement_rate: 0,
          },
        };

        setReport(result);
      } catch (error) {
        setError("Failed to load the audit report.");
      } finally {
        setLoading(false);
      }
    };

    if (analysisId) fetchReport();
  }, [analysisId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[70vh]">
        <div className="flex flex-col items-center">
          <div className="mb-4 h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <h3 className="text-xl font-semibold text-gray-800">Generating Audit Report</h3>
          <p className="text-gray-600">Analyzing contract with AI enhancements...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="container mx-auto py-10 px-4">
        <div className="max-w-3xl mx-auto bg-white shadow-md rounded-lg p-8 text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Report Not Found</h2>
          <p className="text-gray-600 mb-6">{error || "Unable to find the audit report."}</p>
          <Link to="/" className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            Return to Home
          </Link>
        </div>
      </div>
    );
  }

  const highVulnerabilities = report.vulnerabilities.filter((v) => v.severity === "High");
  const mediumVulnerabilities = report.vulnerabilities.filter((v) => v.severity === "Medium");
  const lowVulnerabilities = report.vulnerabilities.filter((v) => v.severity === "Low");

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="bg-white shadow-md rounded-lg p-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center">
            <Shield className="h-8 w-8 text-blue-500 mr-2" />
            Smart Contract Security Audit Report
          </h1>
          <div className="flex space-x-2">
            <Link to="/" className="text-gray-600 hover:text-blue-500 flex items-center text-sm">
              <Shield className="h-4 w-4 mr-1" /> Dashboard
            </Link>
            <span className="text-gray-600">•</span>
            <button className="text-gray-600 hover:text-blue-500 flex items-center text-sm">
              <Download className="h-4 w-4 mr-1" /> Download
            </button>
          </div>
        </div>

        {/* Executive Summary */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Executive Summary</h2>
          <p className="text-gray-600">
            This audit analyzes <code className="bg-gray-100 px-1 rounded">{report.contract_name}</code>, identifying {report.vulnerability_summary?.total || 0} vulnerabilities, including {highVulnerabilities.length} high-severity issues. Immediate action is recommended.
          </p>
        </section>

        {/* Contract Information */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Contract Information</h2>
          <ul className="list-disc list-inside text-gray-600 space-y-1">
            <li><strong>Contract Name:</strong> {report.contract_name}</li>
            <li><strong>Analysis Date:</strong> {new Date(report.timestamp).toISOString().split('T')[0]}</li>
            <li><strong>Functions Analyzed:</strong> {report.functions?.length || 0}</li>
          </ul>
        </section>

        {/* Methodology */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Methodology</h2>
          <ul className="list-disc list-inside text-gray-600 space-y-1">
            <li>Static analysis with Slither.</li>
            <li>AI classification using DistilRoBERTa.</li>
            <li>RAG-enhanced insights from a knowledge base.</li>
            <li>Multi-layer security assessment.</li>
          </ul>
        </section>

        {/* Vulnerability Summary */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Vulnerability Summary</h2>
          <table className="w-full border-collapse mb-4">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2 text-left">Severity</th>
                <th className="border p-2 text-left">Count</th>
                <th className="border p-2 text-left">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border p-2"><span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-1"></span> HIGH</td>
                <td className="border p-2">{highVulnerabilities.length}</td>
                <td className="border p-2">{highVulnerabilities.length > 0 ? "Critical risks detected." : "None"}</td>
              </tr>
              <tr>
                <td className="border p-2"><span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-1"></span> MEDIUM</td>
                <td className="border p-2">{mediumVulnerabilities.length}</td>
                <td className="border p-2">{mediumVulnerabilities.length > 0 ? "Moderate risks detected." : "None"}</td>
              </tr>
              <tr>
                <td className="border p-2"><span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-1"></span> LOW</td>
                <td className="border p-2">{lowVulnerabilities.length}</td>
                <td className="border p-2">{lowVulnerabilities.length > 0 ? "Low risks detected." : "None"}</td>
              </tr>
            </tbody>
          </table>
          {report.enhancement_stats && report.enhancement_stats.rag_enhanced > 0 && (
            <div className="bg-blue-50 p-4 rounded border border-blue-200">
              <p className="text-blue-800"><strong>AI Enhancements:</strong> {report.enhancement_stats.rag_enhanced} RAG, {report.enhancement_stats.classifier_enhanced} classified.</p>
            </div>
          )}
        </section>

        {/* Detailed Findings */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Detailed Findings</h2>
          {report.vulnerabilities.length === 0 ? (
            <div className="bg-green-50 p-4 rounded border border-green-200 text-center">
              <Check className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <p className="text-green-800">No vulnerabilities found.</p>
            </div>
          ) : (
            <VulnerabilitySection vulnerabilities={report.vulnerabilities} />
          )}
        </section>

        {/* Code Quality Assessment */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Code Quality Assessment</h2>
          <p className="text-gray-600">
            {report.contract_name} code quality needs improvement. {report.vulnerabilities.length > 0 ? "Issues like unsafe calls or outdated versions were found." : "No major issues, but follow best practices."}
          </p>
        </section>

        {/* Recommendations */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Recommendations</h2>
          <ol className="list-decimal list-inside text-gray-600 space-y-2">
            <li>Fix high-severity issues with provided remediation steps.</li>
            <li>Monitor for Solidity best practice updates.</li>
            <li>Enhance error handling and conduct code reviews.</li>
            <li>Use checks-effects-interactions pattern and update documentation.</li>
          </ol>
        </section>

        {/* AI Analysis Report */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">AI Analysis Report</h2>
          {report.report_content ? (
            <div className="bg-white p-6 rounded-lg border">
              <div className="prose max-w-none text-gray-600" dangerouslySetInnerHTML={{
                __html: report.report_content
                  .replace(/^# /, '<h2 class="text-xl font-bold mb-4">')
                  .replace(/^## /, '<h3 class="text-lg font-bold mt-4 mb-2">')
                  .replace(/```([^`]+)```/g, '<pre class="bg-gray-100 p-2 rounded mt-2 mb-2"><code>$1</code></pre>')
                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/\*(.*?)\*/g, '<em>$1</em>')
                  .replace(/🔴/g, '<span class="inline-block w-3 h-3 bg-red-500 rounded-full mr-1"></span>')
                  .replace(/🟡/g, '<span class="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-1"></span>')
                  .replace(/🟢/g, '<span class="inline-block w-3 h-3 bg-green-500 rounded-full mr-1"></span>')
                  .replace(/\n\n/g, '</p><p class="mt-2">'),
              }} />
              <div className="mt-4 flex gap-4">
                <Link to={`/chat/${analysisId}`} className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                  <MessageCircle className="h-5 w-5 mr-2 inline" /> Chat with AI
                </Link>
                <Link to={`/insights/${analysisId}`} className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300">
                  <Lightbulb className="h-5 w-5 mr-2 inline" /> Developer Insights
                </Link>
              </div>
            </div>
          ) : (
            <div className="bg-white p-6 rounded-lg border">
              <p className="text-gray-600 mb-4">Need help with vulnerabilities or fixes?</p>
              <div className="flex gap-4">
                <Link to={`/chat/${analysisId}`} className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                  <MessageCircle className="h-5 w-5 mr-2 inline" /> Chat with AI
                </Link>
                <Link to={`/insights/${analysisId}`} className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300">
                  <Lightbulb className="h-5 w-5 mr-2 inline" /> Developer Insights
                </Link>
              </div>
            </div>
          )}
        </section>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4">
          <Link to="/" className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300 flex items-center">
            <Shield className="h-5 w-5 mr-2" /> Back to Dashboard
          </Link>
          <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 flex items-center">
            <Download className="h-5 w-5 mr-2" /> Download Full Report
          </button>
          <button className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300 flex items-center">
            <Clock className="h-5 w-5 mr-2" /> Schedule Follow-Up Audit
          </button>
        </div>
      </div>
    </div>
  );
}

function VulnerabilitySection({ vulnerabilities }) {
  return (
    <div className="space-y-6">
      {vulnerabilities.map((vuln) => {
        const severityColor = vuln.severity === "High" ? "red" : vuln.severity === "Medium" ? "yellow" : "green";
        return (
          <div key={vuln.id} className={`border-l-4 border-${severityColor}-500 bg-white shadow-sm rounded p-6`}>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">{vuln.id}: {vuln.type}</h3>
            <p className="text-gray-600 mb-2"><strong>Severity:</strong> <span className={`inline-block w-3 h-3 bg-${severityColor}-500 rounded-full mr-1`}></span>{vuln.severity.toUpperCase()} (Confidence: {Math.round(vuln.confidence * 100)}%)</p>
            <p className="text-gray-600 mb-2"><strong>Location:</strong> <code className="bg-gray-100 px-1 rounded">{vuln.location}</code></p>
            <p className="text-gray-600 mb-2"><strong>Description:</strong> {vuln.description}</p>
            {vuln.rag_explanation && vuln.rag_enhanced && (
              <div className="mb-2">
                <p className="text-gray-600"><strong>Technical Analysis (RAG):</strong></p>
                <details className="text-gray-600">
                  <summary className="cursor-pointer hover:text-blue-500">{vuln.rag_explanation.substring(0, 100)}...</summary>
                  <p className="mt-2">{vuln.rag_explanation}</p>
                </details>
              </div>
            )}
            {vuln.slither_confidence && (
              <p className="text-gray-600 mb-2"><strong>Slither:</strong> Confidence: {vuln.slither_confidence}, Impact: {vuln.slither_impact}</p>
            )}
            {vuln.all_probabilities && (
              <p className="text-gray-600 mb-2"><strong>Classifier:</strong> Low: {Math.round(vuln.all_probabilities.Low * 100)}%, Medium: {Math.round(vuln.all_probabilities.Medium * 100)}%, High: {Math.round(vuln.all_probabilities.High * 100)}%</p>
            )}
            <p className="text-gray-600 mb-2"><strong>Impact:</strong> {vuln.severity === "High" ? "Potential fund loss." : "Moderate to low risk."}</p>
            <p className="text-gray-600"><strong>Remediation:</strong> {vuln.recommendation}</p>
          </div>
        );
      })}
    </div>
  );
}