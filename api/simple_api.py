import os
import sys
from pathlib import Path
import uuid
import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from secura_agents.crew_manager import run_audit

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis results
analysis_results: Dict[str, Any] = {}


def get_analysis_by_id(analysis_id: str) -> Dict[str, Any]:
    if analysis_id not in analysis_results:
        raise KeyError(f"Analysis not found: {analysis_id}")
    return analysis_results[analysis_id]


# Import routes
from routes import chat
from routes import insights  # Your existing insights route

# Set the analysis getter function in the modules
chat.set_analysis_getter(get_analysis_by_id)
insights.set_analysis_getter(get_analysis_by_id)

# Include the routers
app.include_router(chat.router)
app.include_router(insights.router)


@app.post("/api/upload")
async def upload_contract(file: UploadFile = File(...)):
    """Upload and analyze a Solidity contract."""
    try:
        temp_dir = Path(tempfile.mkdtemp())
        temp_path = temp_dir / file.filename

        with open(temp_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)

        print(f"Saved uploaded file to: {temp_path}")

        analysis_id = str(uuid.uuid4())

        # Run full audit (this should now include insights if using the updated crew)
        result = run_audit(str(temp_path))

        if "error" in result:
            raise Exception(result["error"])

        # Store comprehensive results
        analysis_results[analysis_id] = {
            "contract_name": file.filename,
            "contract_path": str(temp_path),
            "timestamp": result.get("timestamp", datetime.datetime.now().isoformat()),
            **result
        }

        return {
            "success": True,
            "analysis_id": analysis_id,
            "message": "Contract analyzed successfully"
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results by ID."""
    try:
        result = get_analysis_by_id(analysis_id)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Analysis not found")


@app.get("/api/test-analysis")
async def test_analysis():
    """Run analysis on the built-in Vulnerable.sol file."""
    try:
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        test_contract = project_root / "data" / "test_contracts" / "Vulnerable.sol"

        if not os.path.exists(test_contract):
            return {
                "success": False,
                "error": f"Test contract not found at {test_contract}"
            }

        analysis_id = "test-analysis"

        # Run full audit
        result = run_audit(str(test_contract))

        if "error" in result:
            raise Exception(result["error"])

        analysis_results[analysis_id] = {
            "contract_name": "Vulnerable.sol",
            "contract_path": str(test_contract),
            "timestamp": result.get("timestamp", datetime.datetime.now().isoformat()),
            **result
        }

        return {
            "success": True,
            "analysis_id": analysis_id,
            "message": "Contract analyzed successfully"
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)