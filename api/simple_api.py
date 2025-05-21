# api/simple_api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
from pathlib import Path
import uuid
import datetime

# Add project root to path to import secura_agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your secura_agents
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
analysis_results = {}


@app.post("/api/upload")
async def upload_contract(file: UploadFile = File(...)):
    """Upload and analyze a Solidity contract"""
    try:
        # Create a temporary directory to store the uploaded content
        temp_dir = Path(tempfile.mkdtemp())
        temp_path = temp_dir / file.filename

        # Write the uploaded file content to the temp file
        with open(temp_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)

        print(f"Saved uploaded file to: {temp_path}")

        # Generate a unique ID for this analysis
        analysis_id = str(uuid.uuid4())

        # Run the contract analysis
        result = run_audit(str(temp_path))

        # Store the result
        analysis_results[analysis_id] = {
            "contract_name": file.filename,
            "contract_path": str(temp_path),
            "timestamp": datetime.datetime.now().isoformat(),
            **result
        }

        return {
            "success": True,
            "analysis_id": analysis_id,
            "message": "Contract analyzed successfully"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results by ID"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis_results[analysis_id]


# For testing, add an endpoint to run analysis on the built-in Vulnerable.sol file
@app.get("/api/test-analysis")
async def test_analysis():
    """Run analysis on the built-in Vulnerable.sol file"""
    try:
        # Find the Vulnerable.sol file
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        test_contract = project_root / "data" / "test_contracts" / "Vulnerable.sol"

        if not os.path.exists(test_contract):
            return {
                "success": False,
                "error": f"Test contract not found at {test_contract}"
            }

        # Run the analysis
        result = run_audit(str(test_contract))
        # Convert CrewOutput to a dictionary if it's not already one
        if not isinstance(result, dict):
            # Try to convert to a dictionary
            try:
                result_dict = dict(result)
            except:
                # If that fails, create a new dictionary with the result
                result_dict = {
                    "analysis_result": result,
                    "raw_output": str(result)
                }
            result = result_dict

        # Generate a unique ID for this analysis
        analysis_id = "test-analysis"

        # Store the result
        analysis_results[analysis_id] = {
            "contract_name": "Vulnerable.sol",
            "contract_path": str(test_contract),
            "timestamp": datetime.datetime.now().isoformat(),
            **result
        }

        return {
            "success": True,
            "analysis_id": analysis_id,
            "message": "Contract analyzed successfully"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)