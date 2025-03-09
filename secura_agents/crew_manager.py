from crewai import Task, Crew
from secura_agents.contract_analyzer import contract_analyzer

analyze_task = Task(
    agent=contract_analyzer,
    description="Analyze a Solidity contract using Slither.",
    expected_output="A JSON object with functions, vulnerabilities, and contract details detected by Slither",
    action=lambda inputs: contract_analyzer.analyze(inputs["contract_path"])  # Use the agent's method directly
)

crew = Crew(
    agents=[contract_analyzer],
    tasks=[analyze_task]
)

def run_audit(contract_path):
    print("🔍 Running smart contract audit...")
    outcome = crew.kickoff(inputs={"contract_path": contract_path})
    print("Audit Results:", outcome)
    return outcome

if __name__ == "__main__":
    result = run_audit("data/test_contracts/Vulnerable.sol")
    print("Test Results:", result)