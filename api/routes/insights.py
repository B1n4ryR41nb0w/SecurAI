# routes/insights.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from typing import Dict, Any, Optional, Callable
import datetime

from secura_agents.dev_insights import generate_dev_insights

router = APIRouter(prefix="/api/insights", tags=["insights"])


class InsightsRequest(BaseModel):
    analysis_id: str


class InsightsResponse(BaseModel):
    contract_name: str
    insights: str
    timestamp: str
    error: bool = False


# Global variable to be set from the outside
analysis_results_getter: Optional[Callable[[str], Dict[str, Any]]] = None


@router.post("", response_model=InsightsResponse)
async def create_insights(request: InsightsRequest):
    """Generate developer insights for a smart contract."""
    global analysis_results_getter

    if analysis_results_getter is None:
        raise HTTPException(status_code=500, detail="Analysis results getter not initialized")

    try:
        # Get the analysis results
        analysis_results = analysis_results_getter(request.analysis_id)

        # Extract contract path from analysis results
        contract_path = analysis_results.get("contract_path", "")
        if not contract_path:
            raise HTTPException(status_code=400, detail="Contract path not found in analysis")

        # Get analysis data (could be nested in 'analysis' key)
        analysis_data = analysis_results.get("analysis", analysis_results)

        # Generate insights using the agent
        insights_results = generate_dev_insights(contract_path, analysis_data)

        return InsightsResponse(
            contract_name=insights_results.get("contract_name", "Unknown Contract"),
            insights=insights_results.get("insights", "No insights generated"),
            timestamp=insights_results.get("timestamp", datetime.datetime.now().isoformat()),
            error=insights_results.get("error", False)
        )

    except KeyError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@router.get("/{analysis_id}", response_model=InsightsResponse)
async def get_insights(analysis_id: str):
    """Get developer insights by analysis ID."""
    global analysis_results_getter

    if analysis_results_getter is None:
        raise HTTPException(status_code=500, detail="Analysis results getter not initialized")

    try:
        # Check if insights already exist in the analysis results
        analysis_results = analysis_results_getter(analysis_id)

        # If insights already exist, return them
        if "insights" in analysis_results and analysis_results["insights"] and not analysis_results["insights"].get(
                "error", False):
            insights_data = analysis_results["insights"]
            return InsightsResponse(
                contract_name=insights_data.get("contract_name",
                                                analysis_results.get("contract_name", "Unknown Contract")),
                insights=insights_data.get("insights", "No insights available"),
                timestamp=insights_data.get("timestamp", datetime.datetime.now().isoformat()),
                error=insights_data.get("error", False)
            )

        # If no insights exist, generate them on the fly
        contract_path = analysis_results.get("contract_path", "")
        if not contract_path:
            raise HTTPException(status_code=400, detail="Contract path not found in analysis")

        # Get analysis data (could be nested in 'analysis' key)
        analysis_data = analysis_results.get("analysis", analysis_results)

        # Generate insights using the agent
        insights_results = generate_dev_insights(contract_path, analysis_data)

        return InsightsResponse(
            contract_name=insights_results.get("contract_name", "Unknown Contract"),
            insights=insights_results.get("insights", "No insights generated"),
            timestamp=insights_results.get("timestamp", datetime.datetime.now().isoformat()),
            error=insights_results.get("error", False)
        )

    except KeyError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving insights: {str(e)}")


def set_analysis_getter(getter_func: Callable[[str], Dict[str, Any]]):
    """Set the analysis results getter function."""
    global analysis_results_getter
    analysis_results_getter = getter_func