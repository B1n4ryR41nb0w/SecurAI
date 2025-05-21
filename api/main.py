# api/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
import uuid

# Add project root to path to import secura_agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your secura_agents
from secura_agents.contract_analyzer import contract_analyzer
from secura_agents.crew_manager import run_audit

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
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
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".sol") as temp_file:
            # Write the uploaded file content to the temp file
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Generate a unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Run the contract analysis
        result = run_audit(temp_path)
        
        # Store the result
        analysis_results[analysis_id] = {
            "contract_name": file.filename,
            "contract_path": temp_path,
            "timestamp": datetime.datetime.now().isoformat(),
            **result
        }
        
        # Clean up t