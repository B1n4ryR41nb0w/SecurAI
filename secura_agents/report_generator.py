import os
from crewai import Agent
from pathlib import Path
from dotenv import load_dotenv
import json
import openai
import datetime

# Load environment variables
load_dotenv()


class ReportGeneratorAgent(Agent):
    """Agent for generating comprehensive, human-readable audit reports."""

    def __init__(self):
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY not found in environment variables")

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize the agent
        super().__init__(
            role="Smart Contract Audit Report Generator",
            goal="Create comprehensive, clear audit reports from vulnerability findings",
            backstory="An expert technical writer with deep knowledge of smart contract security, "
                      "capable of explaining complex vulnerabilities in clear, actionable terms.",
            verbose=True,
            llm=None  # We'll handle the LLM calls directly for more control
        )

    def generate_report(self, analysis_results):
        """Generate a comprehensive audit report from analysis results."""

        # Extract key information for the prompt
        contract_name = analysis_results.get("contract_stats", {}).get("name", "Unknown Contract")
        vulnerability_count = analysis_results.get("vulnerability_summary", {}).get("total", 0)
        high_severity = analysis_results.get("vulnerability_summary", {}).get("by_severity", {}).get("High", 0)
        medium_severity = analysis_results.get("vulnerability_summary", {}).get("by_severity", {}).get("Medium", 0)
        low_severity = analysis_results.get("vulnerability_summary", {}).get("by_severity", {}).get("Low", 0)

        # Create a detailed prompt for the report generation
        prompt = f"""
        Generate a professional smart contract security audit report for '{contract_name}' based on the following findings:

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
        1. An executive summary
        2. Methodology section
        3. Findings overview with severity distribution
        4. Detailed vulnerability descriptions with:
           - Severity and confidence
           - Location in code
           - Technical explanation
           - Impact assessment
           - Remediation recommendations
        5. General recommendations for the codebase
        6. Conclusion

        Format the report in Markdown with proper headings, tables, and code blocks where appropriate.
        """

        # Generate the report using GPT-4o Mini
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use "gpt-4" for more comprehensive reports
                messages=[
                    {"role": "system",
                     "content": "You are an expert smart contract auditor creating detailed, professional audit reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=4000
            )

            # Extract the report from the response
            report_content = response.choices[0].message.content

            # Save the report to a file
            report_path = self._save_report(contract_name, report_content)

            # Add timestamp
            timestamp = datetime.datetime.now().isoformat()

            return {
                "report_content": report_content,
                "report_path": report_path,
                "timestamp": timestamp,
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

    def _save_report(self, contract_name, report_content):
        """Save the report to a file."""
        # Create reports directory if it doesn't exist
        reports_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "reports"
        reports_dir.mkdir(exist_ok=True)

        # Create a filename based on the contract name and timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{contract_name.replace(' ', '_')}_{timestamp}.md"

        # Save the report
        report_path = reports_dir / filename
        with open(report_path, "w") as f:
            f.write(report_content)

        return str(report_path)


# Create agent instance
report_generator = ReportGeneratorAgent()

if __name__ == "__main__":
    # For testing: Create a sample analysis result
    sample_analysis = {
        "contract_stats": {"name": "TestContract"},
        "vulnerability_summary": {
            "total": 3,
            "by_severity": {"High": 1, "Medium": 1, "Low": 1}
        },
        "vulnerabilities": [
            {
                "type": "Reentrancy",
                "description": "The contract does not follow the checks-effects-interactions pattern",
                "location": "TestContract.sol:42",
                "severity": "High",
                "confidence": 0.95
            },
            {
                "type": "Unchecked Send",
                "description": "The return value of send() is not checked",
                "location": "TestContract.sol:67",
                "severity": "Medium",
                "confidence": 0.87
            },
            {
                "type": "Timestamp Dependence",
                "description": "The contract uses block.timestamp as part of its logic",
                "location": "TestContract.sol:23",
                "severity": "Low",
                "confidence": 0.91
            }
        ],
        "functions": ["transfer", "withdraw", "deposit"]
    }

    # Generate a report
    report = report_generator.generate_report(sample_analysis)

    # Print the report path
    print(f"Report generated and saved to: {report.get('report_path', 'unknown')}")