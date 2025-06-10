import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any
import openai
from dotenv import load_dotenv
from crewai import Agent

load_dotenv()


class ReportGeneratorAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Enhanced Report Generator",
            goal="Generate professional audit reports from contract analysis results with RAG enhancements.",
            backstory="Expert in technical writing and smart contract audit reporting with access to AI-enhanced vulnerability analysis."
        )

    def generate(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive audit report from enhanced analysis results."""
        print("📝 Generating enhanced audit report...")

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Debug: OPENAI_API_KEY not found in environment variables")
            return {
                "error": "OPENAI_API_KEY not found",
                "contract_name": analysis_results.get("contractName", "Unknown Contract"),
                "timestamp": datetime.datetime.now().isoformat()
            }

        client = openai.OpenAI(api_key=api_key)

        # Extract analysis data
        contract_name = analysis_results.get("contractName", "Unknown Contract")
        vulnerabilities = analysis_results.get("vulnerabilities", [])
        functions = analysis_results.get("functions", [])
        vulnerability_summary = analysis_results.get("vulnerability_summary", {})
        analysis_metadata = analysis_results.get("analysis_metadata", {})

        # Count vulnerabilities by severity
        high_severity = vulnerability_summary.get("by_severity", {}).get("High", 0)
        medium_severity = vulnerability_summary.get("by_severity", {}).get("Medium", 0)
        low_severity = vulnerability_summary.get("by_severity", {}).get("Low", 0)
        total_vulnerabilities = vulnerability_summary.get("total", len(vulnerabilities))

        # Enhanced prompt that includes RAG explanations
        prompt = f"""
        You are an expert smart contract auditor. Generate a comprehensive, professional audit report in Markdown for the Solidity contract '{contract_name}' based on the following enhanced analysis results:

        CONTRACT SUMMARY:
        - Contract Name: {contract_name}
        - Total Vulnerabilities: {total_vulnerabilities}
        - High Severity: {high_severity}
        - Medium Severity: {medium_severity}  
        - Low Severity: {low_severity}
        - Functions Analyzed: {len(functions)}

        ANALYSIS ENHANCEMENTS:
        - RAG Enhanced Vulnerabilities: {analysis_metadata.get('rag_enhanced_count', 0)}
        - Slither-Based Severity Assessment: {analysis_metadata.get('slither_based_severity', True)}
        - RAG System Available: {analysis_metadata.get('rag_enhanced', False)}

        DETAILED VULNERABILITY DATA:
        {json.dumps([{
            'type': v.get('type', 'Unknown'),
            'severity': v.get('severity', 'Medium'),
            'confidence': v.get('confidence', 0.8),
            'description': v.get('description', ''),
            'rag_explanation': v.get('rag_explanation', '')[:500] + '...' if v.get('rag_explanation', '') else 'N/A',
            'rag_enhanced': v.get('rag_enhanced', False),
            'slither_confidence': v.get('slither_confidence', 'Unknown'),
            'slither_impact': v.get('slither_impact', 'Unknown'),
            'location': v.get('location', 'Unknown'),
            'affected_functions': v.get('affectedFunctions', [])
        } for v in vulnerabilities], indent=2)}

        ANALYZED FUNCTIONS:
        {json.dumps([f.get('name', 'Unknown') for f in functions], indent=2)}

        Please generate a professional audit report with the following structure:

        # Smart Contract Security Audit Report

        ## Executive Summary
        Brief overview of the audit scope, methodology, and key findings. Highlight the most critical issues.

        ## Contract Information
        - Contract Name: {contract_name}
        - Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
        - Functions Analyzed: {len(functions)}

        ## Methodology
        Explain the comprehensive analysis approach:
        - Static analysis using Slither for vulnerability detection
        - Slither-based severity assessment using impact and confidence ratings
        - RAG-enhanced explanations from vulnerability knowledge base (when available)
        - Multi-layer security assessment

        ## Vulnerability Summary
        Overview of findings by severity level with counts and brief descriptions.

        ## Detailed Findings
        For each vulnerability, provide:
        - **Vulnerability ID**: VULN-001, VULN-002, etc.
        - **Type**: The vulnerability category
        - **Severity**: High/Medium/Low (based on Slither impact assessment)
        - **Location**: File and function if available
        - **Description**: Clear explanation of the issue
        - **Technical Analysis**: Detailed technical explanation (use RAG explanation if available)
        - **Impact Assessment**: Potential consequences
        - **Remediation**: Specific steps to fix the issue
        - **References**: Links to relevant security resources (SWC registry, etc.)

        ## Code Quality Assessment
        Assessment of overall code quality, best practices followed, and areas for improvement.

        ## Recommendations
        Prioritized list of actionable recommendations:
        1. Critical fixes (High severity issues)
        2. Security improvements (Medium severity issues)  
        3. Code quality enhancements (Low severity issues)
        4. Best practices implementation

        ## Conclusion
        Summary of the security posture and next steps.

        ---

        **IMPORTANT FORMATTING REQUIREMENTS:**
        - Use proper Markdown formatting with headers, lists, and code blocks
        - Include severity badges: `🔴 HIGH`, `🟡 MEDIUM`, `🟢 LOW`
        - Use code blocks for contract addresses and function names
        - Make the report professional and suitable for stakeholders
        - Include actionable remediation steps
        - Leverage the RAG explanations to provide deeper technical insights
        - Mention that severity assessment is based on Slither's static analysis
        - Do not include numerical security scores
        """

        try:
            print("  🤖 Generating report with AI...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system",
                     "content": "You are an expert smart contract auditor creating detailed, professional audit reports with Slither-based static analysis and RAG-enhanced vulnerability explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent, professional output
                max_tokens=4000
            )

            report_content = response.choices[0].message.content
            report_path = self._save_report(contract_name, report_content)

            print(f"  ✅ Report generated and saved to {report_path}")

            return {
                "report_content": report_content,
                "report_path": report_path,
                "timestamp": datetime.datetime.now().isoformat(),
                "contract_name": contract_name,
                "summary": {
                    "total_vulnerabilities": total_vulnerabilities,
                    "high_severity": high_severity,
                    "medium_severity": medium_severity,
                    "low_severity": low_severity,
                    "rag_enhanced_count": analysis_metadata.get("rag_enhanced_count", 0),
                    "functions_analyzed": len(functions),
                    "slither_based": analysis_metadata.get("slither_based_severity", True)
                }
            }

        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return {
                "error": str(e),
                "contract_name": contract_name,
                "timestamp": datetime.datetime.now().isoformat()
            }

    def _save_report(self, contract_name: str, report_content: str) -> str:
        """Save the report to a file."""
        reports_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "reports"
        reports_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{contract_name.replace(' ', '_')}_{timestamp}.md"
        report_path = reports_dir / filename

        try:
            with open(report_path, "w", encoding='utf-8') as f:
                f.write(report_content)
            print(f"  💾 Report saved to: {report_path}")
        except Exception as e:
            print(f"  ⚠️ Error saving report: {e}")

        return str(report_path)


def generate_report(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for direct report generation calls."""
    agent = ReportGeneratorAgent()
    return agent.generate(analysis_results)