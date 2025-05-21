import os
import json
from datetime import datetime
from typing import Dict, Any
import openai
from dotenv import load_dotenv
from mpmath import re

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

    # Create a prompt for developer insights
    prompt = f"""
    You are an expert smart contract developer and auditor. Analyze the following Solidity contract and its Slither/Classifier analysis results. Provide developer-focused insights in Markdown, including:

    - Code quality assessment (e.g., readability, structure, adherence to best practices)
    - Potential improvements (e.g., gas optimization, security enhancements)
    - Explanations of vulnerabilities in simple terms for developers
    - Recommendations for better coding practices
    - Any other actionable insights for improving the contract

    Contract content (first 2000 characters):
    {contract_content[:2000]}

    Analysis results (Slither and Classifier outputs):
    {json.dumps(analysis_results, indent=2)}

    Format in Markdown with clear headings and code blocks where appropriate.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert smart contract developer providing actionable insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        insights_content = response.choices[0].message.content

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

if __name__ == "__main__":
    # For testing
    sample_analysis = {
        "contract_stats": {"name": "Vulnerable"},
        "vulnerability_summary": {
            "total": 1,
            "by_severity": {"High": 1, "Medium": 0, "Low": 0}
        },
        "vulnerabilities": [
            {
                "type": "Reentrancy",
                "description": "The withdraw function performs an external call before updating state variables.",
                "location": "Vulnerable.sol:42",
                "severity": "High",
                "confidence": 0.95,
                "affectedFunctions": ["withdraw"]
            }
        ],
        "functions": [
            {"name": "deposit", "visibility": "public", "modifiable_state": True, "inputs": [], "stateMutability": "payable"},
            {"name": "withdraw", "visibility": "public", "modifiable_state": True, "inputs": [], "stateMutability": "nonpayable"},
            {"name": "getBalance", "visibility": "public", "modifiable_state": False, "inputs": [], "stateMutability": "view"}
        ]
    }

    insights = generate_dev_insights("data/test_contracts/Vulnerable.sol", sample_analysis)
    print(f"Insights generated: {insights.get('insights', 'unknown')}")