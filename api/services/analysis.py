import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid
import datetime


# Add project root to path
project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(str(project_root))

# Import agents
from secura_agents.contract_analyzer import contract_analyzer
from secura_agents.crew_manager import run_audit
from secura_agents.report_generator import report_generator


class AnalysisService:
    """Service for analyzing smart contracts"""

    def __init__(self, reports_dir: str = None):
        """Initialize the analysis service

        Args:
            reports_dir: Directory for storing reports, defaults to 'reports'
        """
        if reports_dir is None:
            reports_dir = project_root / "reports"

        self.reports_dir = Path(reports_dir)
        os.makedirs(self.reports_dir, exist_ok=True)

        # In-memory storage for analysis results
        self.analysis_results = {}

    async def analyze_contract(self, contract_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze a smart contract

        Args:
            contract_path: Path to the contract file
            options: Analysis options

        Returns:
            Dictionary with analysis information
        """
        try:
            # Generate unique analysis ID
            analysis_id = str(uuid.uuid4())

            # Check if file exists
            if not os.path.exists(contract_path):
                return {
                    "success": False,
                    "error": f"File not found: {contract_path}",
                    "analysis_id": analysis_id
                }

            # Store initial info
            self.analysis_results[analysis_id] = {
                "analysis_id": analysis_id,
                "contract_path": contract_path,
                "status": "in_progress",
                "timestamp": datetime.datetime.now().isoformat(),
                "options": options or {}
            }

            # Run the audit
            result = run_audit(contract_path)

            # Add metadata
            result["analysis_id"] = analysis_id
            result["contract_path"] = contract_path
            result["timestamp"] = datetime.datetime.now().isoformat()
            result["status"] = "completed"

            # Generate report
            report = report_generator.generate_report(result)
            result["report"] = report

            # Store full results
            self.analysis_results[analysis_id] = result

            return {
                "success": True,
                "analysis_id": analysis_id,
                "contract_path": contract_path,
                "status": "completed",
                "summary": result.get("vulnerability_summary", {})
            }

        except Exception as e:
            # Store error
            if 'analysis_id' in locals():
                self.analysis_results[analysis_id] = {
                    "analysis_id": analysis_id,
                    "contract_path": contract_path,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.datetime.now().isoformat()
                }

            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "analysis_id": analysis_id if 'analysis_id' in locals() else None
            }

    def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """Get the status of an analysis

        Args:
            analysis_id: ID of the analysis

        Returns:
            Dictionary with analysis status information
        """
        if analysis_id not in self.analysis_results:
            return {
                "success": False,
                "error": "Analysis not found",
                "analysis_id": analysis_id
            }

        result = self.analysis_results[analysis_id]

        return {
            "success": True,
            "analysis_id": analysis_id,
            "status": result.get("status", "unknown"),
            "contract_path": result.get("contract_path"),
            "contract_name": result.get("contract_stats", {}).get("name", "Unknown"),
            "timestamp": result.get("timestamp"),
            "summary": result.get("vulnerability_summary", {})
        }

    def get_analysis_results(self, analysis_id: str) -> Dict[str, Any]:
        """Get the complete results of an analysis

        Args:
            analysis_id: ID of the analysis

        Returns:
            Dictionary with complete analysis results
        """
        if analysis_id not in self.analysis_results:
            return {
                "success": False,
                "error": "Analysis not found",
                "analysis_id": analysis_id
            }

        return {
            "success": True,
            **self.analysis_results[analysis_id]
        }

    def get_report(self, analysis_id: str) -> Dict[str, Any]:
        """Get the report for an analysis

        Args:
            analysis_id: ID of the analysis

        Returns:
            Dictionary with report information
        """
        if analysis_id not in self.analysis_results:
            return {
                "success": False,
                "error": "Analysis not found",
                "analysis_id": analysis_id
            }

        result = self.analysis_results[analysis_id]

        if "report" not in result:
            return {
                "success": False,
                "error": "Report not generated yet",
                "analysis_id": analysis_id
            }

        return {
            "success": True,
            "analysis_id": analysis_id,
            "report": result["report"]
        }

    def list_analyses(self) -> List[Dict[str, Any]]:
        """List all analyses

        Returns:
            List of dictionaries with analysis information
        """
        analyses = []

        for analysis_id, result in self.analysis_results.items():
            analyses.append({
                "analysis_id": analysis_id,
                "status": result.get("status", "unknown"),
                "contract_name": result.get("contract_stats", {}).get("name", "Unknown"),
                "timestamp": result.get("timestamp"),
                "vulnerability_count": result.get("vulnerability_summary", {}).get("total", 0)
            })

        return analyses

    def delete_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Delete an analysis

        Args:
            analysis_id: ID of the analysis

        Returns:
            Dictionary with deletion information
        """
        if analysis_id not in self.analysis_results:
            return {
                "success": False,
                "error": "Analysis not found",
                "analysis_id": analysis_id
            }

        # Remove from memory
        del self.analysis_results[analysis_id]

        return {
            "success": True,
            "message": f"Analysis {analysis_id} deleted successfully"
        }