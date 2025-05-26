import os
import re
import datetime
from typing import Dict, Any, List
import openai
from dotenv import load_dotenv
from crewai import Agent, Task

load_dotenv()


class DeveloperInsightsAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Developer Insights Specialist",
            goal="Generate factual, code-based insights and recommendations for smart contract developers without hallucinations.",
            backstory="Expert in smart contract development patterns, security analysis, and best practices. Focuses on providing only verifiable insights based on actual code analysis.",
            verbose=True,
            allow_delegation=False
        )

    def generate_insights(self, contract_path: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate developer-focused insights based ONLY on actual analysis results."""

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "contract_name": "Unknown",
                "insights": "OPENAI_API_KEY not found in environment variables",
                "timestamp": datetime.datetime.now().isoformat(),
                "error": True
            }

        client = openai.OpenAI(api_key=api_key)

        # Extract ONLY factual data from analysis results
        contract_name = analysis_results.get("contractName", analysis_results.get("contract_name", "Unknown"))
        vulnerabilities = analysis_results.get("vulnerabilities", [])
        functions = analysis_results.get("functions", [])
        vulnerability_summary = analysis_results.get("vulnerability_summary", {})

        # Read contract for basic factual analysis
        try:
            with open(contract_path, 'r') as f:
                contract_content = f.read()
        except Exception as e:
            return {
                "contract_name": contract_name,
                "insights": f"Error reading contract: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat(),
                "error": True
            }

        # Extract factual data
        facts = self._extract_factual_data(contract_content, vulnerabilities, functions)

        # Generate structured insights
        insights_content = self._generate_structured_insights(client, contract_name, facts, vulnerability_summary)

        return {
            "contract_name": contract_name,
            "insights": insights_content,
            "timestamp": datetime.datetime.now().isoformat(),
            "facts_analyzed": facts,
            "error": False
        }

    def _extract_factual_data(self, contract_content: str, vulnerabilities: List, functions: List) -> Dict[str, Any]:
        """Extract only verifiable facts from the contract code."""

        facts = {
            "contract_metrics": {
                "total_lines": len(contract_content.split('\n')),
                "total_functions": len(functions),
                "function_names": [f.get("name", "") for f in functions if f.get("name")],
                "non_empty_lines": len([line for line in contract_content.split('\n') if line.strip()]),
            },
            "vulnerability_facts": {
                "total_vulnerabilities": len(vulnerabilities),
                "vulnerability_types": [v.get("type", "") for v in vulnerabilities if v.get("type")],
                "severity_distribution": {},
                "affected_functions": []
            },
            "code_structure": {
                "imports": [],
                "inheritance": [],
                "modifiers": [],
                "events": [],
                "pragmas": []
            },
            "function_analysis": {
                "public_functions": [],
                "private_functions": [],
                "payable_functions": [],
                "view_functions": []
            }
        }

        # Count severity distribution and affected functions
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "Unknown")
            facts["vulnerability_facts"]["severity_distribution"][severity] = \
                facts["vulnerability_facts"]["severity_distribution"].get(severity, 0) + 1

            affected = vuln.get("affectedFunctions", [])
            facts["vulnerability_facts"]["affected_functions"].extend(affected)

        # Remove duplicates from affected functions
        facts["vulnerability_facts"]["affected_functions"] = list(
            set(facts["vulnerability_facts"]["affected_functions"]))

        # Extract code structure patterns
        facts["code_structure"]["inheritance"] = re.findall(r'contract\s+\w+\s+is\s+([^{]+)', contract_content)
        facts["code_structure"]["imports"] = re.findall(r'import\s+[^;]+;', contract_content)
        facts["code_structure"]["modifiers"] = re.findall(r'modifier\s+(\w+)', contract_content)
        facts["code_structure"]["events"] = re.findall(r'event\s+(\w+)', contract_content)
        facts["code_structure"]["pragmas"] = re.findall(r'pragma\s+[^;]+;', contract_content)

        # Analyze functions by visibility and mutability
        for func in functions:
            name = func.get("name", "")
            visibility = func.get("visibility", "")
            mutability = func.get("stateMutability", "")

            if visibility == "public":
                facts["function_analysis"]["public_functions"].append(name)
            elif visibility == "private":
                facts["function_analysis"]["private_functions"].append(name)

            if mutability == "payable":
                facts["function_analysis"]["payable_functions"].append(name)
            elif mutability == "view" or mutability == "pure":
                facts["function_analysis"]["view_functions"].append(name)

        return facts

    def _generate_structured_insights(self, client, contract_name: str, facts: Dict[str, Any],
                                      vulnerability_summary: Dict[str, Any]) -> str:
        """Generate insights based strictly on extracted facts."""

        sections = []

        # Header
        sections.append(f"# Developer Insights: {contract_name}")

        # Contract Overview
        sections.append("\n## 📊 Contract Overview")
        sections.append(
            f"- **Total Lines**: {facts['contract_metrics']['total_lines']} ({facts['contract_metrics']['non_empty_lines']} non-empty)")
        sections.append(f"- **Functions**: {facts['contract_metrics']['total_functions']} total")

        if facts['code_structure']['pragmas']:
            pragma_info = ', '.join(facts['code_structure']['pragmas'])
            sections.append(f"- **Compiler**: {pragma_info}")

        if facts['code_structure']['inheritance']:
            inheritance_info = ', '.join(
                [inh.strip() for sublist in facts['code_structure']['inheritance'] for inh in sublist.split(',')])
            sections.append(f"- **Inherits From**: {inheritance_info}")

        if facts['code_structure']['imports']:
            sections.append(f"- **External Dependencies**: {len(facts['code_structure']['imports'])} imports")

        # Function Breakdown
        if any(facts['function_analysis'].values()):
            sections.append("\n## 🔧 Function Analysis")
            if facts['function_analysis']['public_functions']:
                sections.append(
                    f"- **Public Functions** ({len(facts['function_analysis']['public_functions'])}): {', '.join(facts['function_analysis']['public_functions'])}")
            if facts['function_analysis']['private_functions']:
                sections.append(
                    f"- **Private Functions** ({len(facts['function_analysis']['private_functions'])}): {', '.join(facts['function_analysis']['private_functions'])}")
            if facts['function_analysis']['payable_functions']:
                sections.append(
                    f"- **Payable Functions** ({len(facts['function_analysis']['payable_functions'])}): {', '.join(facts['function_analysis']['payable_functions'])}")
            if facts['function_analysis']['view_functions']:
                sections.append(
                    f"- **View/Pure Functions** ({len(facts['function_analysis']['view_functions'])}): {', '.join(facts['function_analysis']['view_functions'])}")

        # Security Analysis
        sections.append("\n## 🛡️ Security Analysis")
        vuln_facts = facts['vulnerability_facts']
        sections.append(f"- **Total Issues**: {vuln_facts['total_vulnerabilities']}")

        if vuln_facts['severity_distribution']:
            sections.append("- **Severity Breakdown**:")
            for severity, count in vuln_facts['severity_distribution'].items():
                emoji = {"High": "🔴", "Medium": "🟡", "Low": "🔵"}.get(severity, "⚪")
                sections.append(f"  - {emoji} **{severity}**: {count}")

        if vuln_facts['vulnerability_types']:
            unique_types = list(set(vuln_facts['vulnerability_types']))
            sections.append(f"- **Issue Types**: {', '.join(unique_types)}")

        if vuln_facts['affected_functions']:
            sections.append(f"- **Functions with Issues**: {', '.join(vuln_facts['affected_functions'])}")

        # Code Quality Insights
        sections.append("\n## 📈 Code Quality Metrics")
        if facts['code_structure']['modifiers']:
            sections.append(f"- **Custom Modifiers**: {', '.join(facts['code_structure']['modifiers'])}")
        if facts['code_structure']['events']:
            sections.append(f"- **Events Defined**: {', '.join(facts['code_structure']['events'])}")

        # Calculate function density
        if facts['contract_metrics']['total_functions'] > 0:
            lines_per_function = facts['contract_metrics']['non_empty_lines'] / facts['contract_metrics'][
                'total_functions']
            sections.append(f"- **Average Lines per Function**: {lines_per_function:.1f}")

        # Generate specific recommendations using LLM (only for actual vulnerabilities)
        if vuln_facts['vulnerability_types']:
            recommendations = self._generate_specific_recommendations(client, contract_name, vuln_facts)
            sections.append(recommendations)
        else:
            sections.append(self._generate_general_recommendations())

        return "\n".join(sections)

    def _generate_specific_recommendations(self, client, contract_name: str, vuln_facts: Dict[str, Any]) -> str:
        """Generate specific recommendations based on actual vulnerabilities found."""

        unique_vulns = list(set(vuln_facts['vulnerability_types']))

        prompt = f"""
        As a smart contract security expert, provide specific recommendations for the following VERIFIED vulnerabilities found in {contract_name}:

        Vulnerability Types: {', '.join(unique_vulns)}
        Total Issues: {vuln_facts['total_vulnerabilities']}
        Severity Distribution: {vuln_facts['severity_distribution']}

        Provide:
        1. Specific fix for each vulnerability type
        2. Code patterns to implement
        3. Prevention strategies

        Format as markdown section "## 🔧 Specific Recommendations" with subsections for each vulnerability type.
        Be concrete and actionable. Do NOT assume code features not mentioned.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system",
                     "content": "You are a smart contract security expert. Provide specific, actionable recommendations only for the vulnerabilities mentioned. Do not assume any features not explicitly stated."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1200
            )

            return "\n" + response.choices[0].message.content

        except Exception as e:
            return f"\n## 🔧 Recommendations\n❌ Error generating recommendations: {str(e)}"

    def _generate_general_recommendations(self) -> str:
        """Generate general recommendations when no specific vulnerabilities are found."""

        return """
## 🔧 General Recommendations

✅ **Excellent!** No critical vulnerabilities detected. Consider these general best practices:

### Security Enhancements
- Implement comprehensive tests coverage (aim for >95%)
- Add NatSpec documentation for all public functions
- Consider formal verification for critical functions
- Implement proper access controls with role-based permissions

### Gas Optimization
- Use `uint256` instead of smaller uints where possible
- Cache storage variables in memory for repeated access
- Consider using `unchecked` blocks for safe arithmetic operations
- Optimize loops and avoid unbounded iterations

### Code Quality
- Add detailed error messages to require statements
- Implement proper event emission for state changes
- Consider upgradeability patterns if needed
- Regular security audits and code reviews
"""


# Wrapper function for backwards compatibility
def generate_dev_insights(contract_path: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for generating developer insights using the agent."""
    agent = DeveloperInsightsAgent()
    result = agent.generate_insights(contract_path, analysis_results)
    return result
