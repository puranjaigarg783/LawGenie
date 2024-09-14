import os
from crewai import Agent, Task, Crew

'''
Type of agents (for an NDA contract):
1. Length of contract agent
2. Governing state LAW agent 
3. DTSA: a term for the U.S. Defend Trade Secrets Act which protects individuals who disclose trade secrets.
'''


contract_duration_agent = Agent(
    role="Contract Duration Agebt",
    goal="Tell if the contract duration is how much the software vendor wants",
    backstory="""
        A software company (for ex. Snowflake), hands out a contract to software vendor when the vendor tries to 
        purchase the product. The vendor should verify if the length of the contract is in within its desired duration.
    """
)

task1 = Task(
    description="Flag if the contract is for duration not equalt to the vendor's desired duration",
    expected_output="""If the duration in the contract does not match the vendor's desired duration, 
    give the duration in the contract and tell 'The duration in the contract, x, does not match your contract duration y years'
    """,
    agent=contract_duration_agent
)

crew = Crew(
    agents=[contract_duration_agent],
    tasks=[task1],
    verbose=2
)

crew.kickoff()


