from crewai import Crew, Process
from dotenv import load_dotenv

from lawgenie.clause_agents import (
    additional_information_lawyer,
    corporate_lawyer_agent,
    obligation_information_lawyer,
    remedies_lawyer,
    terms_and_termination_lawyer,
)
from lawgenie.clause_tasks import get_tasks

load_dotenv()


def get_crew(input_doc):
    crew = Crew(
        agents=[
            corporate_lawyer_agent,
            obligation_information_lawyer,
            terms_and_termination_lawyer,
            remedies_lawyer,
            additional_information_lawyer,
        ],
        tasks=get_tasks(input_doc),
        process=Process.sequential,
        verbose=True,
    )

    return crew


def get_agent_output(document_from_frontend):
    crew = get_crew(document_from_frontend)
    result = crew.kickoff()
    print("\n\n\n\n\n")
    print("CREW RESULT HERE!!!!!!!!!!!")
    print("\n\n\n\n\n")
    print(result)  # debug

    if isinstance(result, dict) and "accumulated_results" in result:
        return result["accumulated_results"]
    else:
        # Fallback in case the modification didn't work as expected
        return {"final_recommendation": result}
