import os
import subprocess
import re
from pathlib import Path
from crewai import Agent
from bug_classifier import classify_vulnerability


def analyze_contract_with_ml(contract_path):
    """Advanced contract analysis using Slither and ML classification"""
    # Set environment variable
    os.environ['SOLC_VERSION'] = '0.8.17'

    # Run Slither CLI with expanded detection capabilities
    print(f"Running Slither vulnerability detection on {contract_path}")
    result = subprocess.run(
        ["slither", contract_path, "--detect",
         "reentrancy-eth,low-level-calls,unchecked-transfer,unchecked-send,arbitrary-send,dangerous-strict-equalities,locked-ether"],
        capture_output=True,
        text=True
    )

    # Parse output for vulnerabilities
    vulnerabilities = []

    if result.stderr:
        # Pattern to extract vulnerabilities from Slither output
        vuln_pattern = re.compile(r'([^:]+):([\d]+):([^:]+):(.*?)(?=\n[^\s]|\Z)', re.DOTALL)
        matches = vuln_pattern.findall(result.stderr)

        for match in matches:
            file_path, line_num, vuln_type, description = match

            # Extract Slither's severity if available
            slither_severity = "Medium"  # Default
            if "high" in description.lower():
                slither_severity = "High"
            elif "low" in description.lower():
                slither_severity = "Low"

            # Clean up the description
            description = description.strip()

            # Use ML model to classify severity
            ml_classification = classify_vulnerability(description)

            # Create a comprehensive vulnerability entry
            vuln_entry = {
                "type": vuln_type.strip(),
                "description": description,
                "location": f"{file_path.strip()}:{line_num}",
                "slither_severity": slither_severity,
                "ml_severity": ml_classification["severity"],
                "ml_confidence": ml_classification["confidence"],
                "severity": ml_classification["severity"],  # Use ML severity as final determination
                "confidence": ml_classification["confidence"],
                "severity_probabilities": ml_classification["all_probabilities"]
            }

            vulnerabilities.append(vuln_entry)

    # Run a separate command to get function information
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

    # Get contract-level statistics
    print("Getting contract statistics...")
    stats_result = subprocess.run(
        ["slither", contract_path, "--print", "contract-summary"],
        capture_output=True,
        text=True
    )

    contract_stats = {}
    if stats_result.stdout:
        # Extract contract name
        contract_match = re.search(r'Contract ([a-zA-Z0-9_]+)', stats_result.stdout)
        if contract_match:
            contract_stats["name"] = contract_match.group(1)

        # Extract inheritance
        inheritance_match = re.search(r'Inheritance: (.*?)(?=\n)', stats_result.stdout)
        if inheritance_match:
            contract_stats["inheritance"] = inheritance_match.group(1).strip()

    return {
        "functions": functions,
        "vulnerabilities": vulnerabilities,
        "contract_stats": contract_stats,
        "vulnerability_summary": {
            "total": len(vulnerabilities),
            "by_severity": {
                "High": sum(1 for v in vulnerabilities if v["severity"] == "High"),
                "Medium": sum(1 for v in vulnerabilities if v["severity"] == "Medium"),
                "Low": sum(1 for v in vulnerabilities if v["severity"] == "Low")
            }
        }
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

    return analyze_contract_with_ml(contract_location)


class ContractAnalyzerAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Smart Contract Analyzer",
            goal="Analyze Solidity contracts for security issues using advanced ML classification",
            backstory="A sophisticated blockchain security expert using both static analysis and machine learning to detect and classify vulnerabilities with high accuracy.",
            verbose=True,
            llm=None
        )

    def analyze_contract(self, contract_path):
        """Analyze a smart contract for security vulnerabilities"""
        return analyze(contract_path)


# Create agent instance
contract_analyzer = ContractAnalyzerAgent()

if __name__ == "__main__":
    # For testing: Use absolute path from project root
    project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    contract_path = os.path.join(project_root, "data/test_contracts/Vulnerable.sol")

    print(f"Analyzing contract at: {contract_path}")

    # Verify the file exists
    if not os.path.exists(contract_path):
        print(f"ERROR: File {contract_path} not found")
        exit(1)

    # Set SOLC_VERSION environment variable
    os.environ['SOLC_VERSION'] = '0.8.17'

    # Run the analyzer
    print("\nRunning enhanced analyzer with ML classification...")
    analysis = analyze(contract_path)

    print("\nFunctions:", analysis["functions"])
    print(f"\nVulnerabilities found: {len(analysis['vulnerabilities'])}")

    # Display vulnerability summary
    if "vulnerability_summary" in analysis:
        summary = analysis["vulnerability_summary"]
        print("\nVulnerability Summary:")
        print(f"  Total vulnerabilities: {summary['total']}")
        print(f"  High severity: {summary['by_severity']['High']}")
        print(f"  Medium severity: {summary['by_severity']['Medium']}")
        print(f"  Low severity: {summary['by_severity']['Low']}")

    # Display detailed vulnerability information
    for i, vuln in enumerate(analysis["vulnerabilities"]):
        print(f"\n{i + 1}. {vuln['type']}")
        print(f"   Severity: {vuln['severity']} (ML confidence: {vuln['ml_confidence']:.2%})")
        print(f"   Slither severity: {vuln.get('slither_severity', 'Not specified')}")
        print(f"   Description: {vuln['description']}")
        print(f"   Location: {vuln['location']}")