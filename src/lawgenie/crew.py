from crewai import Task
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



def create_accumulating_task(original_task, key):
    def accumulating_task(agent, context):
        result = original_task.function(agent, context)
        if 'accumulated_results' not in context:
            context['accumulated_results'] = {}
        context['accumulated_results'][key] = result
        return context['accumulated_results']
    
    return Task(
        description=original_task.description,
        agent=original_task.agent,
        function=accumulating_task,
        expected_output=original_task.expected_output,  
        output_pydantic=original_task.output_pydantic,  
        context=original_task.context  
    )

tasks = [
    create_accumulating_task(ingest_documents_task, 'ingest_documents'),
    create_accumulating_task(identify_parties, 'parties'),
    create_accumulating_task(identify_obligations_of_receiving_party, 'obligations'),
    create_accumulating_task(identify_terms_and_termination, 'terms_and_termination'),
    create_accumulating_task(identify_remedies, 'remedies'),
    create_accumulating_task(identify_additional_information, 'additional_info')
]

crew = Crew(
    agents=[
        corporate_lawyer_agent,
        parties_corporate_lawyer,
        obligation_information_lawyer,
        terms_and_termination_lawyer,
        remedies_lawyer,
        additional_information_lawyer,
    ],
    tasks=tasks,
    process=Process.sequential,
    verbose=True,
)


def get_agent_output(document_from_frontend):
    result = crew.kickoff()
    print("\nFINAL RESULT\n")
    print(result)  # debug
    print("\nFINAL RESULT\n")
    
    if isinstance(result, dict) and 'accumulated_results' in result:
        return result['accumulated_results']
    else:
        # Fallback in case the modification didn't work as expected
        return {"final_recommendation": result}
