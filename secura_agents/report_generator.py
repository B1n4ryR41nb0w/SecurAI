import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any
import openai
from dotenv import load_dotenv
from crewai import Agent

# Load environment variables
load_dotenv()

class ReportGeneratorAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Report Generator",
            goal="Generate professional audit reports from contract analysis results.",
            backstory="Expert in technical writing and smart contract audit reporting."
        )

    def generate(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive audit report from Slither and Classifier outputs."""
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Debug: OPENAI_API_KEY not found in environment variables")
            return {
                "error": "OPENAI_API_KEY not found",
                "contract_name": analysis_results.get("contract_stats", {}).get("name", "Unknown Contract"),
                "timestamp": datetime.datetime.now().isoformat()
            }
        client = openai.OpenAI(api_key=api_key)

        contract_name = analysis_results.get("contract_stats", {}).get("name", "Unknown Contract")
        vulnerability_count = analysis_results.get("vulnerability_summary", {}).get("total", 0)
        high_severity = analysis_results.get("vulnerability_summary", {}).get("by_severity", {}).get("High", 0)
        medium_severity = analysis_results.get("vulnerability_summary", {}).get("by_severity", {}).get("Medium", 0)
        low_severity = analysis_results.get("vulnerability_summary", {}).get("by_severity", {}).get("Low", 0)

        prompt = f"""
        You are an expert smart contract auditor. Generate a professional audit report in Markdown for the Solidity contract '{contract_name}' based on the following analysis results from Slither and a DistilRoBERTa classifier:

        Summary:
        - Total vulnerabilities found: {vulnerability_count}
        - High severity: {high_severity}
        - Medium severity: {medium_severity}
        - Low severity: {low_severity}

        Detailed findings:
        {json.dumps(analysis_results.get("vulnerabilities", []), indent=2)}

        Contract functions:
        {json.dumps(analysis_results.get("functions", []), indent=2)}

        The report should include:
        1. Executive Summary: Brief overview of findings and their criticality.
        2. Methodology: Explain that Slither was used for static analysis and a DistilRoBERTa classifier for severity/confidence scoring.
        3. Findings Overview: Summarize vulnerabilities by severity.
        4. Detailed Vulnerability Descriptions: For each vulnerability, include:
           - Type
           - Severity (from classifier)
           - Confidence (from classifier)
           - Probability distribution for Low, Medium, High (from classifier)
           - Location in code (if available)
           - Affected functions
           - Technical explanation
           - Impact assessment
           - Remediation recommendations
        5. General Recommendations: Best practices for the codebase.
        6. Conclusion: Summary and next steps.

        Format in Markdown with proper headings, tables, and code blocks. Do not include a numerical security score.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert smart contract auditor creating detailed, professional audit reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            report_content = response.choices[0].message.content
            report_path = self._save_report(contract_name, report_content)

            return {
                "report_content": report_content,
                "report_path": report_path,
                "timestamp": datetime.datetime.now().isoformat(),
                "contract_name": contract_name,
                "summary": {
                    "total_vulnerabilities": vulnerability_count,
                    "high_severity": high_severity,
                    "medium_severity": medium_severity,
                    "low_severity": low_severity
                }
            }

        except Exception as e:
            print(f"Error generating report: {e}")
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
        with open(report_path, "w") as f:
            f.write(report_content)
        return str(report_path)

def generate_report(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for direct report generation calls."""
    agent = ReportGeneratorAgent()
    return agent.generate(analysis_results)