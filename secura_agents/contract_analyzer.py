import os
import subprocess
import re
from crewai import Agent



def analyze_contract_fast_cli(contract_path):
    """Fast contract analysis using only Slither CLI"""
    # Set environment variable
    os.environ['SOLC_VERSION'] = '0.8.17'

    # Run Slither CLI with minimal options for vulnerabilities
    print(f"Running Slither vulnerability detection on {contract_path}")
    result = subprocess.run(
        ["slither", contract_path, "--detect", "reentrancy-eth,low-level-calls"],
        capture_output=True,
        text=True
    )

    # Parse output for vulnerabilities
    vulnerabilities = []
    if result.stderr:
        # Look for reentrancy patterns
        reentrancy_matches = re.findall(r'Reentrancy in ([^(]+)', result.stderr)
        for match in reentrancy_matches:
            vulnerabilities.append({
                "type": "Reentrancy",
                "description": "State variables are modified after external calls, allowing potential reentrancy attacks",
                "location": match.strip(),
                "severity": "High",
                "confidence": "Medium"
            })

        # Look for low-level calls
        lowlevel_matches = re.findall(r'Low level call in ([^(]+)', result.stderr)
        for match in lowlevel_matches:
            vulnerabilities.append({
                "type": "Low_Level_Call",
                "description": "Contract uses low-level calls which may lead to unexpected behavior",
                "location": match.strip(),
                "severity": "Informational",
                "confidence": "High"
            })

    # Run a separate command to get function names
    print("Getting function information...")
    functions_result = subprocess.run(
        ["slither", contract_path, "--print", "function-summary"],
        capture_output=True,
        text=True
    )

    # Parse output for function names
    functions = []
    if functions_result.stdout:
        # Use regex to find function names
        func_matches = re.findall(r'Function ([a-zA-Z0-9_]+)\(', functions_result.stdout)
        functions = list(set(func_matches))  # Remove duplicates

    return {
        "functions": functions,
        "vulnerabilities": vulnerabilities
    }


def analyze(contract_location):
    """Main analysis function with path resolution"""
    if not os.path.isabs(contract_location):
        directory_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        contract_location = os.path.join(directory_root, contract_location)

    if not os.path.exists(contract_location):
        return {
            "functions": [],
            "vulnerabilities": [
                {"type": "File Error", "description": f"File {contract_location} does not exist",
                 "location": "N/A", "severity": "Critical"}
            ]
        }

    return analyze_contract_fast_cli(contract_location)


class ContractAnalyzerAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Smart Contract Analyzer",
            goal="Analyze Solidity contracts for security issues using Slither",
            backstory="A skilled blockchain security expert specializing in detecting vulnerabilities with Slither.",
            verbose=True,
            llm=None
        )


# Create agent instance
contract_analyzer = ContractAnalyzerAgent()

if __name__ == "__main__":
    # For testing: Use absolute path from project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    contract_path = os.path.join(project_root, "data/test_contracts/Vulnerable.sol")

    print(f"Analyzing contract at: {contract_path}")
    print(f"File exists: {os.path.exists(contract_path)}")

    # Set SOLC_VERSION environment variable
    os.environ['SOLC_VERSION'] = '0.8.17'
    print(f"SOLC_VERSION set to: {os.environ.get('SOLC_VERSION')}")

    # Verify solc version directly (faster)
    try:
        result = subprocess.run(["solc", "--version"], capture_output=True, text=True)
        print(f"Using solc: {result.stdout.strip() if result.stdout else 'Unknown'}")
    except Exception as e:
        print(f"Error checking solc: {e}")

    # Run the analyzer
    print("\nRunning analyzer...")
    analysis = analyze(contract_path)

    print("\nFunctions:", analysis["functions"])
    print(f"\nVulnerabilities found: {len(analysis['vulnerabilities'])}")
    for i, vuln in enumerate(analysis["vulnerabilities"]):
        print(f"\n{i + 1}. {vuln['type']} ({vuln['severity']} severity, {vuln['confidence']} confidence)")
        print(f"   Description: {vuln['description']}")
        print(f"   Location: {vuln['location']}")