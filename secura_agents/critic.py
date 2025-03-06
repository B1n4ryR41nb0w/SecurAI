from crewai import Agent

critic = Agent(
    role="Security Critic",
    goal="Review and critique proposed fixes to ensure effectiveness",
    backstory="A highly experienced smart contract auditor who ensures proposed fixes are strong and secure.",
    verbose=True
)
