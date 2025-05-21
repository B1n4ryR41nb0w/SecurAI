import os
import json
from dotenv import load_dotenv
from crewai import Task, Crew
from secura_agents.contract_analyzer import ContractAnalyzerAgent

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
if not os.environ["OPENAI_API_KEY"]:
    print("Error: OPENAI_API_KEY not found in .env file")
    exit(1)

# Instantiate the agent
contract_analyzer = ContractAnalyzerAgent()

print(f"Debug: Loading contract_analyzer from {contract_analyzer.__module__} with type {type(contract_analyzer)}")

analyze_task = Task(
    agent=contract_analyzer,
    description="Analyze a Solidity contract using Slither.",
    expected_output="A JSON object with functions, vulnerabilities, and contract details detected by Slither",
    action=lambda inputs: contract_analyzer.analyze(inputs["contract_path"])
)

crew = Crew(
    agents=[contract_analyzer],
    tasks=[analyze_task]
)

def run_audit(contract_path):
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
        from secura_agents.contract_analyzer import analyze
        direct_outcome = analyze(contract_path)
        print(f"Debug: Direct analysis outcome: {json.dumps(direct_outcome, indent=2)}")

        if "error" in direct_outcome:
            print("Debug: Direct analysis failed, falling back to CrewAI")
            outcome = crew.kickoff(inputs={"contract_path": contract_path})
        else:
            outcome = direct_outcome
    except Exception as e:
        print(f"Debug: Direct analysis error: {e}")
        outcome = crew.kickoff(inputs={"contract_path": contract_path})

    print(f"Debug: Raw outcome from analysis: {json.dumps(outcome, indent=2)}")
    print("Audit Results:", json.dumps(outcome, indent=2))
    return outcome

if __name__ == "__main__":
    print(f"Debug: Starting main execution at {os.path.abspath(__file__)}")
    result = run_audit("data/test_contracts/Vulnerable.sol")
    print("Test Results:", json.dumps(result, indent=2))