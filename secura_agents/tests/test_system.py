#!/usr/bin/env python3
"""Test script for the enhanced contract analyzer system."""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_contract_analyzer():
    """Test the enhanced contract analyzer with different contracts."""
    print("🧪 Testing Enhanced Contract Analyzer System")
    print("=" * 50)
    
    # Test contracts (relative to project root)
    test_contracts = [
        "data/test_contracts/reentrancy_test.sol",
        "data/test_contracts/access_control_test.sol", 
        "data/test_contracts/multi_vuln_test.sol"
    ]
    
    for contract in test_contracts:
        if Path(contract).exists():
            print(f"\n📋 Testing: {contract}")
            try:
                from secura_agents.contract_analyzer import analyze
                result = analyze(contract)
                
                if 'error' not in result:
                    vulns = result.get('vulnerabilities', [])
                    metadata = result.get('analysis_metadata', {})
                    
                    print(f"  ✅ Analysis successful")
                    print(f"  📊 Vulnerabilities found: {len(vulns)}")
                    print(f"  🧠 RAG enhanced: {metadata.get('rag_enhanced_count', 0)}")
                else:
                    print(f"  ❌ Analysis failed: {result.get('error')}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        else:
            print(f"  ⚠️  Contract not found: {contract}")

def test_rag_expert():
    """Test RAG expert standalone."""
    print(f"\n🧠 Testing RAG Expert")
    print("=" * 25)
    
    try:
        from secura_agents.rag_expert import RAGKnowledgeExpert
        expert = RAGKnowledgeExpert()
        result = expert.explain_vulnerability('reentrancy', 'external call before state update')
        
        print(f"  ✅ RAG Expert working")
        print(f"  📝 Explanation length: {len(result['explanation'])}")
        print(f"  🎯 Enhanced: {result['enhanced']}")
        
    except Exception as e:
        print(f"  ❌ RAG Error: {e}")

def test_full_crew():
    """Test the full crew system."""
    print(f"\n🎭 Testing Full Crew System")
    print("=" * 30)
    
    try:
        from secura_agents.crew_manager import run_audit
        result = run_audit("data/test_contracts/reentrancy_test.sol")
        
        if result.get('success'):
            print("  ✅ Full crew audit successful") 
            analysis = result.get('analysis', {})
            print(f"  📊 Total vulnerabilities: {analysis.get('vulnerability_summary', {}).get('total', 0)}")
        else:
            print(f"  ❌ Crew audit failed: {result.get('error')}")
            
    except Exception as e:
        print(f"  ❌ Crew test error: {e}")

if __name__ == "__main__":
    # Change to project root
    os.chdir(Path(__file__).parent.parent.parent)
    
    test_rag_expert()
    test_contract_analyzer() 
    test_full_crew()
    
    print(f"\n🎉 Testing complete!")
