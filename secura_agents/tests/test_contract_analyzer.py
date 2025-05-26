from secura_agents.contract_analyzer import analyze


def test_contract_analyzer():
    print("🧪 Testing Contract Analyzer")
    print("=" * 40)

    # Test 1: Basic functionality
    result = analyze('data/test_contracts/reentrancy_test.sol')

    print(f"✅ Contract: {result.get('contractName')}")
    print(f"✅ Vulnerabilities: {len(result.get('vulnerabilities', []))}")

    if 'analysis_metadata' in result:
        metadata = result['analysis_metadata']
        print(f"✅ RAG Enhanced: {metadata['rag_enhanced']}")
        print(f"✅ RAG Count: {metadata['rag_enhanced_count']}")
        print(f"✅ Classifier Used: {metadata['classifier_used']}")

    if 'error' in result:
        print(f"❌ Error: {result['error']}")

    return result


def test_components():
    print("\n🔧 Testing Individual Components")
    print("=" * 40)

    # Test RAG Expert
    try:
        from secura_agents.rag_expert import RAGKnowledgeExpert
        rag = RAGKnowledgeExpert()
        result = rag.explain_vulnerability("reentrancy", "external call before state update")
        print(f"✅ RAG: {len(result['explanation'])} chars")
    except Exception as e:
        print(f"❌ RAG Error: {e}")

    # Test Bug Classifier
    try:
        from secura_agents.bug_classifier import classify_vulnerability
        result = classify_vulnerability("external call vulnerability", title="reentrancy")
        print(f"✅ Classifier: {result['severity']}")
    except Exception as e:
        print(f"❌ Classifier Error: {e}")

    # Test Slither
    import subprocess
    try:
        result = subprocess.run(["slither", "--version"], capture_output=True, text=True)
        print(f"✅ Slither: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Slither Error: {e}")


if __name__ == "__main__":
    test_components()
    test_contract_analyzer()