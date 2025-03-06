from crewai import Agent

class ContractAnalyzer(Agent):
    def analyze(self, contract_code):
        functions = [line.strip() for line in contract_code.split("\n") if line.strip().startswith("function")]
        return functions

contract_analyzer = Agent(
    role="Smart Contract Analyzer",
    goal="Analyze Solidity contracts for security issues",
    backstory="A skilled blockchain security expert who specializes in detecting vulnerabilities.",
    verbose=True
)
