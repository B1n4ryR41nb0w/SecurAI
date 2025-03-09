import argparse
import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from secura_agents.crew_manager import run_audit

def main():
    parser = argparse.ArgumentParser(description="Run a smart contract audit.")
    parser.add_argument("--contract", type=str, help="Path to a local Solidity contract file")
    args = parser.parse_args()

    if args.contract:
        run_audit(args.contract)
    else:
        print("Please provide a --contract path.")

if __name__ == "__main__":
    main()