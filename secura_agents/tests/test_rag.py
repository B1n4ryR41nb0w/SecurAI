
import sys
import os

sys.path.insert(0, os.getcwd())


def test_rag():
    print("🧠 Testing RAG Expert")
    print("=" * 30)

    try:
        from secura_agents.rag_expert import RAGKnowledgeExpert

        # Test initialization
        print("Creating RAG Expert...")
        expert = RAGKnowledgeExpert()

        # Test vulnerability explanation
        print("Testing vulnerability explanation...")
        result = expert.explain_vulnerability('reentrancy', 'external call before state update')

        print(f"✅ Explanation length: {len(result['explanation'])}")
        print(f"✅ Enhanced: {result['enhanced']}")
        print(f"✅ Confidence: {result['confidence']}")
        print(f"✅ First 100 chars: {result['explanation'][:100]}...")

        if 'error' in result:
            print(f"⚠️ Error: {result['error']}")

        # Test enhance_vulnerabilities
        print("Testing vulnerability enhancement...")
        test_vulns = [
            {"type": "reentrancy", "description": "test reentrancy"},
            {"type": "access-control", "description": "missing modifier"}
        ]

        enhanced = expert.enhance_vulnerabilities(test_vulns)
        print(f"✅ Enhanced {len(enhanced)} vulnerabilities")

        for i, vuln in enumerate(enhanced):
            print(f"  Vuln {i + 1}: RAG enhanced = {vuln.get('rag_enhanced', False)}")

        print("🎉 RAG Expert test completed!")

    except Exception as e:
        print(f"❌ RAG Expert test failed: {e}")
        import traceback
        traceback.print