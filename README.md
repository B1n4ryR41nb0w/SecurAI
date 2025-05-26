# SecurAI: Smart Contract Audit Agent 



**SecurAI** is an AI-powered smart contract auditing tool designed to detect vulnerabilities, classify their severity, explain issues with real-world examples, suggest fixes, and generate comprehensive reports. Built with a multi-agent system using [CrewAI](https://github.com/joaomdmoura/crewAI), SecurAI aims to compete with professional auditors in platforms like Sherlock and Code4rena by May 2025.

Contract → Slither/Mythril → Bug Classifier (DistilRoBERTa) → RAG Expert → Fix Proposal Generator (DeepSeek) → Critic (Claude 3.5 Sonnet) → Report Generator (GPT-4o Mini) → Enhanced Report
                                          ↓                        ↓                           ↓                            ↓
                                   Adds context,           Generates secure         Reviews and validates        Creates polished
                                   examples,               code fixes and           proposed fixes,              reports with fixes,
                                   real-world impact       mitigation               suggests improvements,       explanations, and
                                   data, specific          strategies               ensures best practices       recommendations
                                   mitigations
### Flow Summary:

Using [CrewAI](https://github.com/joaomdmoura/crewAI) with the following roles:

Contract Analysis - Slither/Mythril detect vulnerabilities
Bug Classification - DistilRoBERTa prioritizes by severity
Knowledge Enhancement - RAG Expert adds context and examples
Developer Insight - Gpt-4o-mini to assess code quality 
Fix Generation - DeepSeek proposes secure code fixes
Fix Review - Claude 3.5 Sonnet critiques and validates proposed fixes
Report Creation - GPT-4o Mini generates comprehensive audit report
Enhanced Output - Final report with validated vulnerabilities and reviewed fixes

## 🌟 Features (Current & Planned)

### Current 
- **Smart Contract Analysis**: Uses [Slither](https://github.com/crytic/slither) to detect vulnerabilities in Solidity contracts (e.g., reentrancy, unchecked calls).
- **Multi-Agent System**: Leverages CrewAI to orchestrate agents for analysis, classification, explanation, fix proposals, and reporting.
- **Foundation for RAG & Classification**: Preparing to integrate DistilRoBERTa for severity classification and LlamaIndex for Retrieval-Augmented Generation (RAG) explanations.

### Planned 
- **Vulnerability Classification**: Prioritize findings (Critical, High, Medium, Low) using DistilRoBERTa.
- **RAG-Powered Explanations**: Explain vulnerabilities with real-world examples using Llama-70B + LlamaIndex + Weaviate.
- **Audit Reports**: Generate structured reports with GPT-4o Mini.
- **End-to-End Workflow**: Upload a contract → Detect vulnerabilities → Classify → Explain → Report.

### Future 
- **Advanced Analysis**: Integrate Mythril (symbolic execution) and Echidna (fuzzing) for deeper vulnerability detection.
- **Fix Proposals**: Suggest secure fixes with DeepSeek-Coder-33B, reviewed by Claude 3.5 Sonnet.
- **Interactive Chatbot**: Answer user queries with Mixtral 8x22B.
- **API & Deployment**: Deploy on AWS/GCP with a FastAPI endpoint for contract uploads.
- **Competition-Ready**: Compete in Sherlock/Code4rena with confidence scoring and exportable reports, integrate with Nethemind's Audit4rena 

## 📋 Usage

### Set up & Audit run 

Before running audit, install required dependencies for python with: 

```bash
pip install 
```

First you need to train your DistilRoBERTa model

```bash
python secura_agents/bug_classifier.py
```

Analyze a Contract:

```bash
python -c "from secura_agents.contract_analyzer import analyze; result = analyze('data/test_contracts/reentrancy_test.sol'); print('FAILED AT:', result.get('failed_step', 'Success'))"
```
This uses the ContractAnalyzer agent to run Slither/Bug Classifier/Rag Expert and extract functions/vulnerabilities.

(you have to put contract in data folder where Vulnerable.sol is).


For running backend go to api folder and run a simple backend 
```bash
python api/simple_api.py
```

For running frontend, go to frontend folder and do:

```bash
npm install 
npm run dev 
```

Note: at the moment of writing this readme frontend is very basic and just covers needed elements without much styling. 

## 🤝 Contributing

We welcome contributions! To get started:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push to your branch: `git push origin feature/your-feature`.
5. Open a Pull Request.

### Current Needs
- Expand `classifier_data.csv` and `rag_data.txt` datasets.
- Implement FindingProposal and Critic agents.
- Write unit tests in `tests/`.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📬 Contact

For questions or collaboration, reach out on telegram @murluki_prg
