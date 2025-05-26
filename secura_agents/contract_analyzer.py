import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List
import openai
from dotenv import load_dotenv
from crewai import Agent

from secura_agents.bug_classifier import classify_vulnerability

load_dotenv()


class ContractAnalyzerAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Enhanced Contract Analyzer",
            goal="Analyze Solidity contracts with Slither, DistilRoBERTa classification, and RAG enhancement",
            backstory="Elite smart contract security expert"
        )

    def analyze(self, contract_path: str) -> Dict[str, Any]:
        print(f"🔍 Analyzing contract: {contract_path}")

        # Step 1: Initialize RAG Expert
        rag_expert = None
        rag_available = False
        try:
            print("  📊 Step 1: Initializing RAG Expert...")
            from secura_agents.rag_expert import RAGKnowledgeExpert
            rag_expert = RAGKnowledgeExpert()
            rag_available = True
            print("  ✅ RAG Expert initialized successfully")
        except Exception as e:
            print(f"  ⚠️ RAG Expert initialization failed: {e}")

        # Step 2: Validate Environment
        print("  🔧 Step 2: Validating environment...")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._create_error_response("OPENAI_API_KEY not found in environment", "Unknown",
                                               "Environment Validation")

        try:
            client = openai.OpenAI(api_key=api_key)
            print("  ✅ OpenAI client initialized")
        except Exception as e:
            return self._create_error_response(f"OpenAI client initialization failed: {str(e)}", "Unknown",
                                               "Environment Validation")

        # Step 3: Read Contract
        print("  📖 Step 3: Reading contract file...")
        try:
            if not Path(contract_path).exists():
                return self._create_error_response(f"Contract file not found: {contract_path}", "Unknown",
                                                   "File Reading")

            with open(contract_path, 'r') as f:
                contract_content = f.read()

            if not contract_content.strip():
                return self._create_error_response("Contract file is empty", "Unknown", "File Reading")

            contract_name = self._extract_contract_name(contract_content)
            compiler_version = self._extract_compiler_version(contract_content)
            print(f"  ✅ Contract read successfully: {contract_name} (Solidity {compiler_version})")

        except Exception as e:
            return self._create_error_response(f"Failed to read contract: {str(e)}", "Unknown", "File Reading")

        # Step 4: Check Slither Installation
        print("  🔍 Step 4: Checking Slither installation...")
        try:
            slither_check = subprocess.run(["slither", "--version"], capture_output=True, text=True, timeout=10)
            if slither_check.returncode != 0:
                return self._create_error_response("Slither not properly installed", contract_name, "Slither Check")
            print(f"  ✅ Slither available: {slither_check.stdout.strip()}")
        except FileNotFoundError:
            return self._create_error_response("Slither not installed. Install with: pip install slither-analyzer",
                                               contract_name, "Slither Check")
        except subprocess.TimeoutExpired:
            return self._create_error_response("Slither check timed out", contract_name, "Slither Check")
        except Exception as e:
            return self._create_error_response(f"Slither check failed: {str(e)}", contract_name, "Slither Check")

        # Step 5: Check Solidity Compiler
        print("  ⚙️ Step 5: Checking Solidity compiler...")
        try:
            solc_check = subprocess.run(["solc", "--version"], capture_output=True, text=True, timeout=10)
            if solc_check.returncode != 0:
                return self._create_error_response(
                    "Solidity compiler not available. Install with: pip install solc-select && solc-select install 0.8.0 && solc-select use 0.8.0",
                    contract_name, "Solidity Compiler Check"
                )
            print(f"  ✅ Solidity compiler available")
        except FileNotFoundError:
            return self._create_error_response(
                "Solidity compiler not found. Install with: pip install solc-select && solc-select install 0.8.0 && solc-select use 0.8.0",
                contract_name, "Solidity Compiler Check"
            )
        except subprocess.TimeoutExpired:
            return self._create_error_response("Solidity compiler check timed out", contract_name,
                                               "Solidity Compiler Check")
        except Exception as e:
            return self._create_error_response(f"Solidity compiler check failed: {str(e)}", contract_name,
                                               "Solidity Compiler Check")

        # Step 6: Run Slither Analysis
        print("  🔍 Step 6: Running Slither analysis...")
        slither_result = self._run_slither(contract_path, contract_name, compiler_version)
        if "error" in slither_result:
            return slither_result

        # Step 7: Extract Functions and Raw Vulnerabilities
        print("  🔧 Step 7: Processing Slither output...")
        try:
            functions = self._extract_functions(contract_content)
            raw_vulnerabilities = self._process_slither_output(slither_result["slither_output"], contract_path)
            print(f"  ✅ Found {len(functions)} functions and {len(raw_vulnerabilities)} raw vulnerabilities")
        except Exception as e:
            return self._create_error_response(f"Failed to process Slither output: {str(e)}", contract_name,
                                               "Slither Output Processing")

        # Step 8: Enhanced Vulnerability Processing
        print("  🧠 Step 8: Enhancing vulnerabilities...")
        enhanced_vulnerabilities = []

        for i, vuln in enumerate(raw_vulnerabilities):
            print(f"    Processing vulnerability {i + 1}/{len(raw_vulnerabilities)}: {vuln.get('type', 'Unknown')}")

            # Sub-step 8.1: Classify with DistilRoBERTa
            try:
                classified_vuln = self._classify_vulnerability(vuln)
                print(f"      ✅ Classified as {classified_vuln.get('severity', 'Unknown')} severity")
            except Exception as e:
                print(f"      ⚠️ Classification failed: {e}")
                classified_vuln = vuln.copy()
                classified_vuln.update({
                    "severity": "Medium",
                    "confidence": 0.5,
                    "all_probabilities": {"Low": 0.3, "Medium": 0.4, "High": 0.3},
                    "classifier_enhanced": False,
                    "classifier_error": str(e)
                })

            # Sub-step 8.2: Enhance with RAG
            if rag_available and rag_expert:
                try:
                    print(f"      🧠 Getting RAG explanation...")
                    rag_enhancement = rag_expert.explain_vulnerability(
                        classified_vuln["type"], classified_vuln["description"]
                    )
                    classified_vuln.update({
                        "rag_explanation": rag_enhancement["explanation"],
                        "rag_enhanced": rag_enhancement["enhanced"],
                        "rag_confidence": rag_enhancement["confidence"]
                    })
                    print(f"      ✅ RAG enhancement added ({len(rag_enhancement['explanation'])} chars)")
                except Exception as e:
                    print(f"      ⚠️ RAG enhancement failed: {e}")
                    classified_vuln.update({
                        "rag_explanation": f"RAG enhancement failed: {str(e)}",
                        "rag_enhanced": False,
                        "rag_confidence": 0.5,
                        "rag_error": str(e)
                    })
            else:
                classified_vuln.update({
                    "rag_explanation": "RAG enhancement unavailable",
                    "rag_enhanced": False,
                    "rag_confidence": 0.5
                })

            enhanced_vulnerabilities.append(classified_vuln)

        # Step 9: Calculate Summary
        print("  📊 Step 9: Calculating vulnerability summary...")
        try:
            vulnerability_summary = self._calculate_vulnerability_summary(enhanced_vulnerabilities)

            # Count enhancements
            rag_enhanced_count = len([v for v in enhanced_vulnerabilities if v.get("rag_enhanced")])
            classifier_enhanced_count = len([v for v in enhanced_vulnerabilities if v.get("classifier_enhanced")])

            print(
                f"  ✅ Summary: {vulnerability_summary['total']} total, {rag_enhanced_count} RAG enhanced, {classifier_enhanced_count} classifier enhanced")
        except Exception as e:
            return self._create_error_response(f"Failed to calculate summary: {str(e)}", contract_name,
                                               "Summary Calculation")

        # Step 10: Build Final Result
        print("  📋 Step 10: Building final result...")
        try:
            result = {
                "contractName": contract_name,
                "language": "Solidity",
                "version": compiler_version,
                "functions": functions,
                "vulnerabilities": enhanced_vulnerabilities,
                "vulnerability_summary": vulnerability_summary,
                "contract_stats": {"name": contract_name},
                "analysis_metadata": {
                    "rag_enhanced": rag_available,
                    "total_vulnerabilities": len(enhanced_vulnerabilities),
                    "rag_enhanced_count": rag_enhanced_count,
                    "classifier_enhanced_count": classifier_enhanced_count,
                    "classifier_used": True,
                    "gpt_enhanced": False,
                    "analysis_steps_completed": [
                        "RAG Initialization",
                        "Environment Validation",
                        "File Reading",
                        "Slither Check",
                        "Solidity Compiler Check",
                        "Slither Analysis",
                        "Output Processing",
                        "Vulnerability Enhancement",
                        "Summary Calculation",
                        "Result Building"
                    ]
                }
            }

            print(f"✅ Enhanced analysis complete: {len(enhanced_vulnerabilities)} vulnerabilities found")
            return result

        except Exception as e:
            return self._create_error_response(f"Failed to build result: {str(e)}", contract_name, "Result Building")

    def _extract_contract_name(self, content: str) -> str:
        match = re.search(r'contract\s+(\w+)', content)
        return match.group(1) if match else "Unknown"

    def _extract_compiler_version(self, content: str) -> str:
        match = re.search(r'pragma solidity \^?([\d.]+)', content)
        return match.group(1) if match else "0.8.0"

    def _run_slither(self, contract_path: str, contract_name: str, compiler_version: str) -> Dict[str, Any]:
        slither_output_file = f"slither_output_{contract_name}.json"

        # Remove existing output file if it exists
        if Path(slither_output_file).exists():
            Path(slither_output_file).unlink()

        try:
            print(f"    Running: slither {contract_path} --json {slither_output_file}")
            result = subprocess.run(
                ["slither", contract_path, "--json", slither_output_file],
                capture_output=True, text=True, check=True, timeout=60
            )

            if result.stdout:
                print(f"    Slither stdout: {result.stdout[:200]}...")

            if not Path(slither_output_file).exists():
                return self._create_error_response("Slither output file not created", contract_name,
                                                   "Slither Execution")

            with open(slither_output_file, 'r') as f:
                slither_output = json.load(f)

            detectors_count = len(slither_output.get("results", {}).get("detectors", []))
            print(f"    ✅ Slither analysis complete: {detectors_count} detectors triggered")

            return {"slither_output": slither_output}

        except subprocess.CalledProcessError as e:
            # Check if it's just warnings/info but still produced output
            if Path(slither_output_file).exists():
                try:
                    with open(slither_output_file, 'r') as f:
                        slither_output = json.load(f)
                    detectors_count = len(slither_output.get("results", {}).get("detectors", []))
                    print(f"    ✅ Slither completed with warnings: {detectors_count} detectors triggered")
                    return {"slither_output": slither_output}
                except:
                    pass

            error_msg = f"Slither execution failed (exit code {e.returncode})"
            if e.stderr:
                error_msg += f"\nSTDERR: {e.stderr}"
            if e.stdout:
                error_msg += f"\nSTDOUT: {e.stdout}"
            return self._create_error_response(error_msg, contract_name, "Slither Execution")

        except subprocess.TimeoutExpired:
            return self._create_error_response("Slither analysis timed out (60s limit)", contract_name,
                                               "Slither Execution")

        except json.JSONDecodeError as e:
            return self._create_error_response(f"Slither output is not valid JSON: {str(e)}", contract_name,
                                               "Slither Output Parsing")

        except Exception as e:
            return self._create_error_response(f"Slither processing error: {str(e)}", contract_name,
                                               "Slither Execution")

    def _extract_functions(self, contract_content: str) -> List[Dict[str, Any]]:
        functions = []
        function_matches = re.findall(
            r'function\s+(\w+)\s*\(([^)]*)\)\s*(public|private|internal|external)?\s*(view|pure|payable)?',
            contract_content
        )
        for func_match in function_matches:
            name, params, visibility, mutability = func_match
            functions.append({
                "name": name,
                "visibility": visibility or "public",
                "modifiable_state": mutability not in ["view", "pure"],
                "inputs": [],
                "outputs": [],
                "stateMutability": mutability or "nonpayable"
            })
        return functions

    def _process_slither_output(self, slither_output: Dict, contract_path: str) -> List[Dict[str, Any]]:
        vulnerabilities = []
        detectors = slither_output.get("results", {}).get("detectors", [])

        if not detectors:
            print("    ℹ️ No vulnerabilities detected by Slither")
            return vulnerabilities

        for detector in detectors:
            vuln = {
                "type": detector.get("check", "Unknown"),
                "description": detector.get("description", ""),
                "location": f"{contract_path}:Unknown",
                "affectedFunctions": [],
                "slither_confidence": detector.get("confidence", "Unknown"),
                "slither_impact": detector.get("impact", "Unknown")
            }
            vulnerabilities.append(vuln)

        return vulnerabilities

    def _classify_vulnerability(self, vuln: Dict[str, Any]) -> Dict[str, Any]:
        try:
            swc_id = vuln["type"] if vuln["type"].startswith("SWC-") else None
            classifier_result = classify_vulnerability(
                description=vuln["description"],
                swc_id=swc_id,
                title=vuln["type"]
            )
            vuln.update({
                "severity": classifier_result["severity"],
                "confidence": classifier_result["confidence"],
                "all_probabilities": classifier_result["all_probabilities"],
                "classifier_enhanced": True
            })
        except Exception as e:
            print(f"      ⚠️ Classification error: {e}")
            vuln.update({
                "severity": "Medium",
                "confidence": 0.5,
                "all_probabilities": {"Low": 0.3, "Medium": 0.4, "High": 0.3},
                "classifier_enhanced": False,
                "classifier_error": str(e)
            })
        return vuln

    def _calculate_vulnerability_summary(self, vulnerabilities: List[Dict]) -> Dict:
        severity_counts = {"High": 0, "Medium": 0, "Low": 0, "Critical": 0}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "Medium")
            if severity in severity_counts:
                severity_counts[severity] += 1
        return {
            "total": len(vulnerabilities),
            "by_severity": severity_counts,
            "rag_enhanced": len([v for v in vulnerabilities if v.get("rag_enhanced")]),
            "classifier_enhanced": len([v for v in vulnerabilities if v.get("classifier_enhanced")]),
            "gpt_enhanced": 0
        }

    def _create_error_response(self, error_msg: str, contract_name: str, failed_step: str) -> Dict[str, Any]:
        print(f"  ❌ FAILED at {failed_step}: {error_msg}")
        return {
            "contractName": contract_name,
            "language": "Solidity",
            "version": "0.0.0",
            "functions": [],
            "vulnerabilities": [{
                "type": "Analysis Error",
                "description": error_msg,
                "severity": "Critical",
                "affectedFunctions": [],
                "confidence": 1.0,
                "failed_step": failed_step
            }],
            "vulnerability_summary": {"total": 1, "by_severity": {"Critical": 1, "High": 0, "Medium": 0, "Low": 0}},
            "contract_stats": {"name": contract_name},
            "analysis_metadata": {
                "rag_enhanced": False,
                "total_vulnerabilities": 1,
                "rag_enhanced_count": 0,
                "classifier_enhanced_count": 0,
                "classifier_used": False,
                "gpt_enhanced": False,
                "failed_step": failed_step,
                "analysis_steps_completed": []
            },
            "error": error_msg,
            "failed_step": failed_step
        }


def analyze(contract_path: str) -> Dict[str, Any]:
    agent = ContractAnalyzerAgent()
    return agent.analyze(contract_path)