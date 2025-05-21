import os
import json
import datetime
from typing import Dict, Any
from dotenv import load_dotenv
from crewai import Crew, Task
from secura_agents.contract_analyzer import ContractAnalyzerAgent
from secura_agents.report_generator import ReportGeneratorAgent

# Load environment variables
load_dotenv()

def run_audit(contract_path: str) -> Dict[str, Any]:
    """Run a smart contract audit using CrewAI with Slither and GPT-4o Mini."""
    if not os.path.isabs(contract_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        contract_path = os.path.join(project_root, contract_path)

    print(f"Debug: Running audit for contract path: {contract_path}")
    print(f"Debug: File exists check: {os.path.exists(contract_path)}")

    try:
        with open(contract_path, 'r') as f:
            contract_content = f.read()
            print(f"Debug: First 100 characters of contract:\n{contract_content[:100]}...")
    except Exception as e:
        print(f"Debug: Error reading contract file: {e}")
        return {"error": f"Failed to read contract file: {str(e)}"}

    print("🔍 Running smart contract audit...")
    try:
        # Instantiate agents
        contract_analyzer = ContractAnalyzerAgent()
        report_generator = ReportGeneratorAgent()

        # Define tasks
        analyze_task = Task(
            agent=contract_analyzer,
            description="Analyze a Solidity contract using Slither.",
            expected_output="A JSON object with functions, vulnerabilities, and contract details detected by Slither",
            action=lambda inputs: contract_analyzer.analyze(inputs["contract_path"])
        )

        report_task = Task(
            agent=report_generator,
            description="Generate a professional audit report from contract analysis results.",
            expected_output="A JSON object with Markdown report content, report path, and summary",
            action=lambda inputs: report_generator.generate(inputs["analysis_result"])
        )

        # Create and run Crew
        crew = Crew(
            agents=[contract_analyzer, report_generator],
            tasks=[analyze_task, report_task]
        )

        # Run audit
        crew.kickoff(inputs={"contract_path": contract_path})
        print("Debug: CrewAI tasks completed")

        # Combine analysis and report results
        analysis_result = contract_analyzer.analyze(contract_path)
        report_result = report_generator.generate(analysis_result)
        result = {
            **analysis_result,
            "report_content": report_result.get("report_content", ""),
            "report_path": report_result.get("report_path", ""),
            "timestamp": report_result.get("timestamp", datetime.datetime.now().isoformat())
        }
        print(f"Debug: Final audit result: {json.dumps(result, indent=2)}")
        return result

    except Exception as e:
        print(f"Debug: Audit error: {e}")
        return {"error": f"Audit failed: {str(e)}"}

if __name__ == "__main__":
    print(f"Debug: Starting main execution at {os.path.abspath(__file__)}")
    result = run_audit("data/test_contracts/Vulnerable.sol")
    print("Test Results:", json.dumps(result, indent=2))