from crewai import Crew, Process, Task
from secura_agents.contract_analyzer import ContractAnalyzerAgent
from secura_agents.report_generator import ReportGeneratorAgent


class SecuraCrew:
    def __init__(self):
        # Initialize all agents
        self.analyzer = ContractAnalyzerAgent()
        self.reporter = ReportGeneratorAgent()

        # Create standard tasks - RAG enhancement happens inside ContractAnalyzerAgent
        self.analysis_task = Task(
            description="Analyze smart contract for vulnerabilities using Slither, DistilRoBERTa, and RAG enhancement",
            agent=self.analyzer,
            expected_output="Comprehensive vulnerability analysis with RAG explanations and confidence scores"
        )

        self.report_task = Task(
            description="Generate professional audit report from enhanced analysis",
            agent=self.reporter,
            expected_output="Professional markdown report with RAG-enhanced explanations",
            context=[self.analysis_task]
        )

        # Create crew with sequential processing
        self.crew = Crew(
            agents=[self.analyzer, self.reporter],
            tasks=[self.analysis_task, self.report_task],
            process=Process.sequential,
            verbose=True
        )

    def audit_contract(self, contract_path: str) -> dict:
        """Run complete enhanced contract audit."""
        print(f"🚀 Starting enhanced audit for: {contract_path}")

        try:
            # Step 1: Static Analysis with RAG enhancement
            print("📊 Step 1: Running enhanced static analysis...")
            analysis_results = self.analyzer.analyze(contract_path)

            if "error" in analysis_results:
                return {"error": analysis_results["error"]}

            # Step 2: Report Generation
            print("📝 Step 2: Generating enhanced report...")
            report_results = self.reporter.generate(analysis_results)

            # Calculate enhancement statistics
            vulnerabilities = analysis_results.get("vulnerabilities", [])
            analysis_metadata = analysis_results.get("analysis_metadata", {})

            enhancement_stats = {
                "total_vulnerabilities": len(vulnerabilities),
                "rag_enhanced": analysis_metadata.get("rag_enhanced_count", 0),
                "classifier_enhanced": analysis_metadata.get("classifier_enhanced_count", 0),
                "enhancement_rate": analysis_metadata.get("rag_enhanced_count", 0) / max(len(vulnerabilities), 1)
            }

            print("✅ Enhanced audit completed successfully!")

            return {
                "analysis": analysis_results,
                "report": report_results,
                "enhancement_stats": enhancement_stats,
                "timestamp": report_results.get("timestamp"),
                "success": True,
                # Add compatibility fields for frontend
                "contract_name": analysis_results.get("contractName", "Unknown"),
                "vulnerabilities": vulnerabilities,
                "vulnerability_summary": analysis_results.get("vulnerability_summary", {}),
                "functions": analysis_results.get("functions", []),
                "contract_stats": analysis_results.get("contract_stats", {}),
                "report_content": report_results.get("report_content", "")
            }

        except Exception as e:
            print(f"❌ Error during enhanced audit: {str(e)}")
            return {"error": str(e), "success": False}


def run_audit(contract_path: str) -> dict:
    """Run enhanced audit with RAG integration."""
    crew = SecuraCrew()
    return crew.audit_contract(contract_path)