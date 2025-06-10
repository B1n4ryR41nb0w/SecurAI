import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Shield,
  AlertTriangle,
  Clock,
  MessageCircle,
  Download,
  Check,
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
  enhancement_stats?: { total_vulnerabilities: number; rag_enhanced: number; classifier_enhanced: number; enhancement_rate: number };
}

function VulnerabilitySection({ vulnerabilities }: { vulnerabilities: Vulnerability[] }) {
  return (
    <div className="space-y-6">
      {vulnerabilities.map((vuln: Vulnerability) => {
        const severityColor = vuln.severity === "High" ? "red" : vuln.severity === "Medium" ? "yellow" : "green";
        return (
          <div key={vuln.id} className="border-l-4 border-gray-300 pl-4">
            <h3 className="text-lg font-bold text-gray-800 mb-2">{vuln.id}</h3>
            <p className="text-gray-600 mb-1"><strong>Type:</strong> {vuln.type}</p>
            <p className="text-gray-600 mb-1">
              <strong>Severity:</strong>{" "}
              <span className={`inline-block w-3 h-3 bg-${severityColor}-500 rounded-full mr-1`}></span>
              {vuln.severity?.toUpperCase()} (Confidence: {Math.round((vuln.confidence || 0) * 100)}%)
            </p>
            <p className="text-gray-600 mb-1"><strong>Location:</strong> <code className="bg-gray-100 px-1 rounded text-sm">{vuln.location}</code></p>
            <p className="text-gray-600 mb-1"><strong>Description:</strong> {vuln.description}</p>
            {vuln.rag_explanation && vuln.rag_enhanced && (
              <div className="mt-2">
                <h4 className="text-md font-bold text-gray-800 mb-1">Technical Analysis:</h4>
                <pre className="bg-gray-100 p-2 rounded text-sm font-mono text-gray-600 whitespace-pre-wrap">{vuln.rag_explanation}</pre>
              </div>
            )}
            {vuln.slither_confidence && (
              <p className="text-gray-600 mb-1"><strong>Slither Analysis:</strong> Confidence: {vuln.slither_confidence}, Impact: {vuln.slither_impact}</p>
            )}
            {vuln.all_probabilities && (
              <p className="text-gray-600 mb-1"><strong>Classifier Probabilities:</strong> Low: {Math.round(vuln.all_probabilities.Low * 100)}%, Medium: {Math.round(vuln.all_probabilities.Medium * 100)}%, High: {Math.round(vuln.all_probabilities.High * 100)}%</p>
            )}
            <p className="text-gray-600 mb-1"><strong>Impact:</strong> {vuln.severity === "High" ? "Critical exploitation risk." : "Moderate to low risk."}</p>
            <p className="text-gray-600"><strong>Remediation:</strong> {vuln.recommendation}</p>
          </div>
        );
      })}
    </div>
  );
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
        const response = await fetch(`/api/analysis/${analysisId}`);
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
          timestamp: data.timestamp || "2025-05-27T16:45:00+07:00",
          functions: functions.map((fn: any) => ({ name: fn.name })),
          vulnerabilities: vulnerabilities.map((v: any, index: number) => {
            let cleanedDescription = v.description || "";
            cleanedDescription = cleanedDescription.replace(/\(.*?\)/g, (match: string) => {
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
          report_content: data.report_content || "",
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
        <div className="max-w-3xl mx-auto bg-white rounded-lg p-8 text-center">
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
      <div className="bg-white rounded-lg p-6">
        {/* Header */}
        <h1 className="text-4xl font-bold text-gray-800 mb-4">Smart Contract Security Audit Report</h1>
        <div className="flex justify-between items-center mb-6 text-sm text-gray-500">
          <div>
            <Link to="/" className="hover:text-blue-500 flex items-center">
              <Shield className="h-4 w-4 mr-1" /> Dashboard
            </Link>
            <span className="mx-2">•</span>
            <button className="hover:text-blue-500 flex items-center">
              <Download className="h-4 w-4 mr-1" /> Download
            </button>
          </div>
        </div>

        {/* Executive Summary */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2 border-b border-gray-200 pb-2">Executive Summary</h2>
          <p className="text-gray-600 leading-relaxed">
            This audit report provides a comprehensive analysis of the <code className="bg-gray-100 px-1 rounded text-sm">{report.contract_name}</code> smart contract. The audit was conducted to identify potential vulnerabilities and assess the overall security posture of the contract. Our analysis revealed a total of {report.vulnerability_summary?.total || 0} vulnerabilities across {report.functions?.length || 0} analyzed functions. Immediate remediation is recommended for all identified vulnerabilities to ensure the security and integrity of the contract.
          </p>
        </section>

        {/* Contract Information */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2 border-b border-gray-200 pb-2">Contract Information</h2>
          <ul className="list-disc list-inside text-gray-600 space-y-1">
            <li><strong>Contract Name:</strong> {report.contract_name}</li>
            <li><strong>Analysis Date:</strong> {new Date(report.timestamp).toLocaleString("en-US", { timeZone: "Asia/Bangkok", hour12: true })}</li>
            <li><strong>Functions Analyzed:</strong> {report.functions?.length || 0}</li>
          </ul>
        </section>

        {/* Methodology */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2 border-b border-gray-200 pb-2">Methodology</h2>
          <p className="text-gray-600 mb-2">The audit was performed using a multi-faceted approach:</p>
          <ul className="list-disc list-inside text-gray-600 space-y-1">
            <li>Static analysis using Slither to identify common vulnerabilities and code quality issues.</li>
            <li>AI-powered vulnerability classification using DistilRoBERTa to enhance the accuracy of vulnerability detection.</li>
            <li>RAG-enhanced explanations from a vulnerability knowledge base to provide deeper insights into identified issues.</li>
            <li>Multi-layer security assessment to evaluate the contract against best practices and known security threats.</li>
          </ul>
        </section>

        {/* Vulnerability Summary */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2 border-b border-gray-200 pb-2">Vulnerability Summary</h2>
          <table className="w-full text-left border-collapse mb-4">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="p-2 text-gray-700">Severity</th>
                <th className="p-2 text-gray-700">Count</th>
                <th className="p-2 text-gray-700">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-200">
                <td className="p-2"><span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-1"></span> HIGH</td>
                <td className="p-2">{highVulnerabilities.length}</td>
                <td className="p-2 text-gray-600">Critical vulnerabilities that could lead to severe exploitation.</td>
              </tr>
              <tr className="border-b border-gray-200">
                <td className="p-2"><span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-1"></span> MEDIUM</td>
                <td className="p-2">{mediumVulnerabilities.length}</td>
                <td className="p-2 text-gray-600">Moderate vulnerabilities that may pose risks under specific conditions.</td>
              </tr>
              <tr className="border-b border-gray-200">
                <td className="p-2"><span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-1"></span> LOW</td>
                <td className="p-2">{lowVulnerabilities.length}</td>
                <td className="p-2 text-gray-600">Low-risk vulnerabilities with minimal impact.</td>
              </tr>
            </tbody>
          </table>
          {report.enhancement_stats && report.enhancement_stats.rag_enhanced > 0 && (
            <p className="text-blue-700"><strong>AI Enhancements:</strong> {report.enhancement_stats.rag_enhanced} RAG-enhanced, {report.enhancement_stats.classifier_enhanced} classified.</p>
          )}
        </section>

        {/* Detailed Findings */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2 border-b border-gray-200 pb-2">Detailed Findings</h2>
          {report.vulnerabilities.length === 0 ? (
            <div className="bg-green-50 p-4 rounded text-center">
              <Check className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <p className="text-green-700">No vulnerabilities found.</p>
            </div>
          ) : (
            <VulnerabilitySection vulnerabilities={report.vulnerabilities} />
          )}
        </section>

        {/* Code Quality Assessment */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2 border-b border-gray-200 pb-2">Code Quality Assessment</h2>
          <p className="text-gray-600">
            The overall code quality of <code className="bg-gray-100 px-1 rounded text-sm">{report.contract_name}</code> requires attention. {report.vulnerabilities.length > 0 ? "Issues such as unsafe calls or uninitialized variables were identified." : "No major issues detected, but best practices should be followed."}
          </p>
        </section>

        {/* Recommendations */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2 border-b border-gray-200 pb-2">Recommendations</h2>
          <ol className="list-decimal list-inside text-gray-600 space-y-2">
            <li>Address high-severity issues immediately using provided remediation steps.</li>
            <li>Monitor updates to Solidity best practices and libraries.</li>
            <li>Implement comprehensive error handling and regular code reviews.</li>
            <li>Adopt the checks-effects-interactions pattern and maintain updated documentation.</li>
          </ol>
        </section>

        {/* AI Analysis Summary */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2 border-b border-gray-200 pb-2">AI Analysis Summary</h2>
          <p className="text-gray-600 mb-4">
            This report was enhanced using AI-powered analysis, including {report.enhancement_stats?.rag_enhanced || 0} RAG-enhanced vulnerability explanations and {report.enhancement_stats?.classifier_enhanced || 0} AI-classified vulnerabilities. For further assistance, you can interact with our AI tools below.
          </p>
          <div className="flex gap-4">
            <Link to={`/chat/${analysisId}`} className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
              <MessageCircle className="h-5 w-5 mr-2 inline" /> Chat with AI
            </Link>
            <Link to={`/insights/${analysisId}`} className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300">
              <Lightbulb className="h-5 w-5 mr-2 inline" /> Developer Insights
            </Link>
          </div>
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