import argparse
import os
import sys
import subprocess
import logging

# Add project root to sys.path
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from secura_agents.crew_manager import run_audit

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run a smart contract audit.")
    parser.add_argument("--contract", type=str, help="Path to a local Solidity contract file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--prepare", action="store_true", help="Run dataset preparation before audit")
    args = parser.parse_args()

    if args.prepare:
        logger.info("Running dataset preparation...")
        try:
            subprocess.run(["python", "scripts/prepare_dataset.py"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Dataset preparation failed: {e}")
            sys.exit(1)

    if not args.contract:
        logger.error("Please provide a --contract path.")
        sys.exit(1)
    elif not os.path.exists(args.contract):
        logger.error(f"Contract file '{args.contract}' not found.")
        sys.exit(1)

    logger.info(f"Starting audit for contract: {args.contract}")
    try:
        result = run_audit(args.contract)
        logger.info("Audit completed successfully.")
        # Optionally save results to a file
        with open("audit_result.json", "w") as f:
            import json
            json.dump(result, f, indent=2)
        logger.info("Audit results saved to audit_result.json")
    except Exception as e:
        logger.error(f"Error during audit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()