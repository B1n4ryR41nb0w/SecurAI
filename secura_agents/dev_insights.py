import os
import json
import re
import datetime
from typing import Dict, Any, List
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_dev_insights(contract_path: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate developer-focused insights for a Solidity contract using GPT-4o Mini."""
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found in environment variables")

    # Initialize OpenAI client
    client = openai.OpenAI(api_key=api_key)

    # Read the contract content
    try:
        with open(contract_path, 'r') as f:
            contract_content = f.read()
            contract_name_match = re.search(r'contract\s+(\w+)', contract_content)
            contract_name = contract_name_match.group(1) if contract_name_match else "Unknown"
    except Exception as e:
        print(f"Debug: Error reading contract: {e}")
        return {
            "contract_name": "Unknown",
            "insights": f"Failed to read contract: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }

    # Extract and prepare detailed contract structure manually
    function_patterns = r"function\s+(\w+)\s*\(([^)]*)\)\s*(public|private|internal|external)?\s*(view|pure|payable)?\s*(\{|returns)"
    functions_found = re.findall(function_patterns, contract_content)

    function_details = []
    for func in functions_found:
        name, params, visibility, mutability, _ = func
        function_details.append({
            "name": name,
            "visibility": visibility or "internal",
            "mutability": mutability or "nonpayable"
        })

    # Check for modifier patterns
    modifiers_found = re.findall(r"modifier\s+(\w+)", contract_content)

    # Check for inheritance patterns
    inheritance = re.search(r"contract\s+\w+\s+is\s+([^{]+)", contract_content)
    inherited_contracts = []
    if inheritance:
        inherited_contracts = [c.strip() for c in inheritance.group(1).split(',')]

    # Get vulnerabilities from analysis results
    vulnerabilities = analysis_results.get("vulnerabilities", [])

    # Format functions from analysis for comparison
    analysis_functions = analysis_results.get("functions", [])

    # Get vulnerability summary
    vulnerability_summary = analysis_results.get("vulnerability_summary", {})
    high_count = vulnerability_summary.get("by_severity", {}).get("High", 0)
    medium_count = vulnerability_summary.get("by_severity", {}).get("Medium", 0)
    low_count = vulnerability_summary.get("by_severity", {}).get("Low", 0)

    # Create a factual based template for insights rather than free-form generation
    insights_sections = []

    # Generate contract overview section
    insights_sections.append(f"# Developer Insights for {contract_name}")
    insights_sections.append("\n## Contract Overview")
    insights_sections.append(f"- **Contract Name**: {contract_name}")
    insights_sections.append(f"- **Total Functions**: {len(function_details)}")
    if inherited_contracts:
        insights_sections.append(f"- **Inherits From**: {', '.join(inherited_contracts)}")
    if modifiers_found:
        insights_sections.append(f"- **Modifiers Defined**: {', '.join(modifiers_found)}")

    # Generate vulnerability section
    insights_sections.append("\n## Vulnerability Summary")
    insights_sections.append(f"- **Total Vulnerabilities**: {vulnerability_summary.get('total', 0)}")
    insights_sections.append(f"- **High Severity**: {high_count}")
    insights_sections.append(f"- **Medium Severity**: {medium_count}")
    insights_sections.append(f"- **Low Severity**: {low_count}")

    # If vulnerabilities exist, list them
    if vulnerabilities:
        insights_sections.append("\n## Detailed Vulnerabilities")

        # Group by severity for better organization
        high_vulns = [v for v in vulnerabilities if v.get("severity") == "High"]
        medium_vulns = [v for v in vulnerabilities if v.get("severity") == "Medium"]
        low_vulns = [v for v in vulnerabilities if v.get("severity") == "Low"]

        if high_vulns:
            insights_sections.append("\n### High Severity")
            for v in high_vulns:
                insights_sections.append(f"- **{v.get('type', 'Unknown')}**")
                insights_sections.append(f"  - Description: {v.get('description', 'No description')}")
                insights_sections.append(f"  - Location: {v.get('location', 'Unknown')}")
                if v.get('affectedFunctions'):
                    insights_sections.append(f"  - Affected Functions: {', '.join(v.get('affectedFunctions'))}")
                if v.get('recommendation'):
                    insights_sections.append(f"  - Recommendation: {v.get('recommendation')}")

        if medium_vulns:
            insights_sections.append("\n### Medium Severity")
            for v in medium_vulns:
                insights_sections.append(f"- **{v.get('type', 'Unknown')}**")
                insights_sections.append(f"  - Description: {v.get('description', 'No description')}")
                insights_sections.append(f"  - Location: {v.get('location', 'Unknown')}")
                if v.get('affectedFunctions'):
                    insights_sections.append(f"  - Affected Functions: {', '.join(v.get('affectedFunctions'))}")
                if v.get('recommendation'):
                    insights_sections.append(f"  - Recommendation: {v.get('recommendation')}")

        if low_vulns:
            insights_sections.append("\n### Low Severity")
            for v in low_vulns:
                insights_sections.append(f"- **{v.get('type', 'Unknown')}**")
                insights_sections.append(f"  - Description: {v.get('description', 'No description')}")
                insights_sections.append(f"  - Location: {v.get('location', 'Unknown')}")
                if v.get('affectedFunctions'):
                    insights_sections.append(f"  - Affected Functions: {', '.join(v.get('affectedFunctions'))}")
                if v.get('recommendation'):
                    insights_sections.append(f"  - Recommendation: {v.get('recommendation')}")

    # Now use the LLM only for general recommendations based on factual data
    prompt = f"""
    You are an expert smart contract developer. Based ONLY on the following FACTS about a Solidity contract named {contract_name}, provide specific, actionable advice for improving the contract. 

    Do NOT make up or assume any features that are not explicitly mentioned below.

    ## Contract Facts:
    - Has {len(function_details)} functions
    - Function names: {", ".join([f["name"] for f in function_details])}
    - Inherits from: {", ".join(inherited_contracts) if inherited_contracts else "No inheritance"}
    - Modifiers: {", ".join(modifiers_found) if modifiers_found else "No custom modifiers"}

    ## Vulnerabilities Found:
    - Total: {vulnerability_summary.get('total', 0)}
    - High severity: {high_count}
    - Medium severity: {medium_count}
    - Low severity: {low_count}

    ## Specific Vulnerability Types:
    {", ".join([v.get("type", "Unknown") for v in vulnerabilities]) if vulnerabilities else "None detected"}

    Provide 3-5 specific, concrete recommendations for improving this contract. Focus ONLY on general best practices for Solidity and addressing the specific vulnerability types mentioned above. Do NOT invent or assume any contract features beyond what is stated.

    Format your response as a Markdown section titled "## Improvement Recommendations" with numbered bullet points.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "You are a factual smart contract developer providing strictly objective insights based only on the provided information. Do not make up or assume any details not explicitly provided."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Very low temperature for factual outputs
            max_tokens=1000
        )

        recommendations = response.choices[0].message.content

        # Add the recommendations to our insights
        insights_sections.append("\n" + recommendations)

        # Compile final insights
        insights_content = "\n".join(insights_sections)

        return {
            "contract_name": contract_name,
            "insights": insights_content,
            "timestamp": datetime.datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error generating insights: {e}")
        return {
            "contract_name": contract_name,
            "insights": f"Error generating insights: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }