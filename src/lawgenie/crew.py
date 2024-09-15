from crewai import Crew, Process
from dotenv import load_dotenv

from lawgenie.clause_agents import (
    additional_information_lawyer,
    corporate_lawyer_agent,
    obligation_information_lawyer,
    parties_corporate_lawyer,
    remedies_lawyer,
    terms_and_termination_lawyer,
)
from lawgenie.clause_tasks import (
    identify_additional_information,
    identify_obligations_of_receiving_party,
    identify_parties,
    identify_remedies,
    identify_terms_and_termination,
    ingest_documents_task,
)

load_dotenv()

crew = Crew(
    agents=[
        corporate_lawyer_agent,
        parties_corporate_lawyer,
        obligation_information_lawyer,
        terms_and_termination_lawyer,
        remedies_lawyer,
        additional_information_lawyer,
    ],
    tasks=[
        ingest_documents_task,
        identify_parties,
        identify_obligations_of_receiving_party,
        identify_terms_and_termination,
        identify_remedies,
        identify_additional_information,
    ],
    process=Process.sequential,
    verbose=True,
)


def get_agent_output(document_from_frontend):
    result = crew.kickoff()
    print(result)  # debug
    return result.pydantic
