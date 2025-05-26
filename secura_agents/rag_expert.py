import os
import openai
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

try:
    import weaviate

    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

load_dotenv()


class RAGKnowledgeExpert:
    def __init__(self):
        self.role = "RAG Knowledge Expert"
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.knowledge_base = self._load_simple_knowledge()
        self.weaviate_client = None

        if WEAVIATE_AVAILABLE:
            self._try_weaviate_setup()

        print("✅ RAG Expert initialized")

    def _load_simple_knowledge(self) -> Dict[str, str]:
        knowledge = {
            "reentrancy": "Reentrancy occurs when external calls can recursively call back into the contract before state changes are finalized. Use checks-effects-interactions pattern and reentrancy guards.",
            "integer-overflow": "Integer overflow happens when arithmetic operations exceed maximum values. Use Solidity 0.8+ built-in checks or SafeMath library.",
            "access-control": "Access control issues occur when functions lack proper permission checks. Use OpenZeppelin's AccessControl and proper modifiers.",
            "oracle-manipulation": "Oracle attacks manipulate price feeds through flash loans. Use multiple oracles, TWAP, and circuit breakers.",
            "unchecked-return": "Unchecked return values can lead to silent failures. Always check return values of external calls."
        }

        data_path = Path("data/rag_data.txt")
        if data_path.exists():
            with open(data_path, 'r') as f:
                knowledge["file_data"] = f.read()

        return knowledge

    def _try_weaviate_setup(self):
        try:
            self.weaviate_client = weaviate.connect_to_local(skip_init_checks=True)
            print("✅ Weaviate connected")
        except Exception as e:
            print(f"⚠️ Weaviate unavailable: Using OpenAI only")

    def __del__(self):
        """Clean up Weaviate connection."""
        if hasattr(self, 'weaviate_client') and self.weaviate_client:
            try:
                self.weaviate_client.close()
            except:
                pass

    def explain_vulnerability(self, vulnerability_type: str, description: str) -> Dict[str, Any]:
        key = vulnerability_type.lower().replace(" ", "-").replace("_", "-")
        context = self.knowledge_base.get(key, self.knowledge_base.get("file_data", ""))

        prompt = f"""Explain this smart contract vulnerability:

Type: {vulnerability_type}
Description: {description}

Knowledge Base Context:
{context}

Provide: technical explanation, impact, and mitigation strategies."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a smart contract security expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )

            return {
                "explanation": response.choices[0].message.content,
                "enhanced": True,
                "confidence": 0.8
            }
        except Exception as e:
            return {
                "explanation": f"Basic explanation: {context[:200]}...",
                "enhanced": False,
                "confidence": 0.5,
                "error": str(e)
            }

    def enhance_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enhanced = []
        for vuln in vulnerabilities:
            vuln_type = vuln.get("type", "Unknown")
            description = vuln.get("description", "")

            explanation = self.explain_vulnerability(vuln_type, description)

            enhanced_vuln = vuln.copy()
            enhanced_vuln.update({
                "rag_explanation": explanation["explanation"],
                "rag_enhanced": explanation["enhanced"],
                "rag_confidence": explanation["confidence"]
            })

            enhanced.append(enhanced_vuln)

        return enhanced