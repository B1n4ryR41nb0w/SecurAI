import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, Any
import openai
from dotenv import load_dotenv
from crewai import Agent

# Load environment variables
load_dotenv()

class ContractAnalyzerAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Contract Analyzer",
            goal="Analyze Solidity contracts for vulnerabilities using Slither and interpret results.",
            backstory="Expert in smart contract security, proficient in Slither and static analysis."
        )

    def analyze(self, contract_path: str) -> Dict[str, Any]:
        """Analyze a Solidity contract using Slither and interpret results with GPT-4o Mini."""
        print(f"Debug: Analyzing contract at path: {contract_path}")

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Debug: OPENAI_API_KEY not found in environment variables")
            return {
                "contractName": "Unknown",
                "language": "Solidity",
                "version": "0.0.0",
                "functions": [],
                "vulnerabilities": [
                    {"type": "Configuration Error", "description": "OPENAI_API_KEY not found", "severity": "Critical", "affectedFunctions": [], "confidence": 1.0}
                ],
                "vulnerability_summary": {"total": 1, "by_severity": {"High": 0, "Medium": 0, "Low": 0, "Critical": 1}},
                "contract_stats": {"name": "Unknown"}
            }
        client = openai.OpenAI(api_key=api_key)

        # Read contract content for metadata
        try:
            with open(contract_path, 'r') as f:
                contract_content = f.read()
                contract_name_match = re.search(r'contract\s+(\w+)', contract_content)
                contract_name = contract_name_match.group(1) if contract_name_match else "Unknown"
                compiler_version_match = re.search(r'pragma solidity \^?([\d.]+)', contract_content)
                compiler_version = compiler_version_match.group(1) if compiler_version_match else "0.8.0"
        except Exception as e:
            print(f"Debug: Error reading contract: {e}")
            return {
                "contractName": "Unknown",
                "language": "Solidity",
                "version": "0.0.0",
                "functions": [],
                "vulnerabilities": [
                    {"type": "File Error", "description": f"Failed to read contract: {str(e)}", "severity": "Critical", "affectedFunctions": [], "confidence": 1.0}
                ],
                "vulnerability_summary": {"total": 1, "by_severity": {"High": 0, "Medium": 0, "Low": 0, "Critical": 1}},
                "contract_stats": {"name": "Unknown"}
            }

        # Run Slither
        slither_output_file = "slither_output.json"
        try:
            result = subprocess.run(
                ["slither", contract_path, "--json", slither_output_file],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Debug: Slither executed successfully: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Debug: Slither error: {e.stderr}")
            return {
                "contractName": contract_name,
                "language": "Solidity",
                "version": compiler_version,
                "functions": [],
                "vulnerabilities": [
                    {"type": "Slither Error", "description": f"Slither failed: {str(e)}", "severity": "Critical", "affectedFunctions": [], "confidence": 1.0}
                ],
                "vulnerability_summary": {"total": 1, "by_severity": {"High": 0, "Medium": 0, "Low": 0, "Critical": 1}},
                "contract_stats": {"name": contract_name}
            }

        # Parse Slither output
        try:
            with open(slither_output_file, 'r') as f:
                slither_output = json.load(f)
        except Exception as e:
            print(f"Debug: Error reading Slither output: {e}")
            return {
                "contractName": contract_name,
                "language": "Solidity",
                "version": compiler_version,
                "functions": [],
                "vulnerabilities": [
                    {"type": "Output Error", "description": f"Failed to read Slither output: {str(e)}", "severity": "Critical", "affectedFunctions": [], "confidence": 1.0}
                ],
                "vulnerability_summary": {"total": 1, "by_severity": {"High": 0, "Medium": 0, "Low": 0, "Critical": 1}},
                "contract_stats": {"name": contract_name}
            }

        # Extract functions
        functions = []
        function_matches = re.findall(
            r'function\s+(\w+)\s*\(([^)]*)\)\s*(public|private|internal|external)?\s*(view|pure|payable)?',
            contract_content)
        for func_match in function_matches:
            name, params, visibility, mutability = func_match
            param_list = []
            if params.strip():
                param_parts = params.split(',')
                for p in param_parts:
                    p = p.strip()
                    if not p:
                        continue
                    parts = p.split(' ')
                    if len(parts) >= 2:
                        param_list.append({"name": parts[1].strip(), "type": parts[0]})
            functions.append({
                "name": name,
                "visibility": visibility if visibility else "public",
                "modifiable_state": mutability != "view" and mutability != "pure",
                "inputs": param_list,
                "outputs": [],
                "stateMutability": mutability if mutability else "nonpayable"
            })

        # Mock Classifier output
        def mock_classifier(vuln: Dict[str, Any]) -> Dict[str, Any]:
            vuln_type = vuln.get("check", "").lower()
            if "reentrancy" in vuln_type:
                return {"severity": "High", "confidence": 0.95}
            elif "unchecked-low-level-calls" in vuln_type:
                return {"severity": "Medium", "confidence": 0.85}
            else:
                return {"severity": "Low", "confidence": 0.75}

        # Process Slither vulnerabilities
        vulnerabilities = []
        for detector in slither_output.get("results", {}).get("detectors", []):
            vuln = {
                "type": detector.get("check", "Unknown"),
                "description": detector.get("description", ""),
                "location": f"{contract_path}:{detector.get('first_markdown_element', {}).get('source_mapping', {}).get('lines', ['Unknown'])[0]}",
                "affectedFunctions": [elem.get("name", "") for elem in detector.get("elements", []) if elem.get("type") == "function"],
            }
            classifier_result = mock_classifier(vuln)
            vuln.update(classifier_result)
            vulnerabilities.append(vuln)

        # Interpret Slither output with GPT-4o Mini
        prompt = f"""
        You are an expert smart contract auditor. Interpret the following Slither analysis output for the Solidity contract '{contract_name}' and provide enhanced vulnerability details in JSON format. For each vulnerability, include:
        - type: Vulnerability type
        - description: Clear explanation for developers
        - severity: High, Medium, or Low (use provided Classifier severity)
        - confidence: Numeric value between 0 and 1 (use provided Classifier confidence)
        - affectedFunctions: List of affected function names
        - location: File and line number
        - recommendation: Specific mitigation steps

        Slither output:
        {json.dumps(vulnerabilities, indent=2)}

        Contract functions:
        {json.dumps(functions, indent=2)}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert smart contract auditor interpreting Slither output."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            enhanced_vulnerabilities = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Debug: OpenAI error: {e}")
            enhanced_vulnerabilities = vulnerabilities  # Fallback

        # Calculate vulnerability summary
        high = sum(1 for v in enhanced_vulnerabilities if v["severity"] == "High")
        medium = sum(1 for v in enhanced_vulnerabilities if v["severity"] == "Medium")
        low = sum(1 for v in enhanced_vulnerabilities if v["severity"] == "Low")
        vulnerability_summary = {
            "total": len(enhanced_vulnerabilities),
            "by_severity": {"High": high, "Medium": medium, "Low": low}
        }

        result = {
            "contractName": contract_name,
            "language": "Solidity",
            "version": compiler_version,
            "functions": functions,
            "vulnerabilities": enhanced_vulnerabilities,
            "vulnerability_summary": vulnerability_summary,
            "contract_stats": {"name": contract_name}
        }
        print(f"Debug: Analysis result: {json.dumps(result, indent=2)}")
        return result

def analyze(contract_path: str) -> Dict[str, Any]:
    """Wrapper for direct analysis calls."""
    agent = ContractAnalyzerAgent()
    return agent.analyze(contract_path)