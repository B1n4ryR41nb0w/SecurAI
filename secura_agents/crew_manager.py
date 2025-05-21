from crewai import Crew, Process

from secura_agents.contract_analyzer import ContractAnalyzerAgent
from secura_agents.report_generator import ReportGeneratorAgent

class SecuraCrew:
    def __init__(self):
        self.analyzer = ContractAnalyzerAgent()
        self.reporter = ReportGeneratorAgent()
        self.crew = Crew(
            agents=[self.analyzer, self.reporter],
            process=Process.sequential
        )

    def audit_contract(self, contract_path: str) -> dict:
        # Step 1: Analyze the contract
        analysis_results = self.analyzer.analyze(contract_path)

        # Step 2: Generate the report
        report_results = self.reporter.generate(analysis_results)

        # Combine results for API response
        return {
            "analysis": analysis_results,
            "report": report_results
        }

def run_audit(contract_path: str) -> dict:
    """Run a full audit on the given contract."""
    crew = SecuraCrew()
    return crew.audit_contract(contract_path)