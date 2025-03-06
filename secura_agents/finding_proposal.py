from crewai import Agent

finding_proposal = Agent(
    role="Finding Proposal Generator",
    goal="Suggest improvements or fixes for smart contract vulnerabilities",
    backstory="An AI assistant trained on best security practices in Solidity.",
    verbose=True
)
