from crewai import Task
from dotenv import load_dotenv

from lawgenie.clause_agents import (
    additional_information_lawyer,
    corporate_lawyer_agent,
    obligation_information_lawyer,
    parties_corporate_lawyer,
    remedies_lawyer,
    terms_and_termination_lawyer,
)
from lawgenie.models import AgentOutput

load_dotenv()

EXPECTED_TASK_OUTPUT = """
A JSON that has two keys: an `analysis` of the current clause in laymen terms (in short, numbered points) as well as a `recommendation` of how the current clause deviates from the benchmark clauses."""


def create_accumulating_task(original_task, key):
    def accumulating_task(agent, context):
        result = original_task.function(agent, context)
        if "accumulated_results" not in context:
            context["accumulated_results"] = {}
        context["accumulated_results"][key] = result
        return context["accumulated_results"]

    return Task(
        description=original_task.description,
        agent=original_task.agent,
        function=accumulating_task,
        expected_output=original_task.expected_output,
        output_pydantic=original_task.output_pydantic,
        context=original_task.context,
    )


def get_tasks(input_document):
    tasks = []

    ingest_documents_task = Task(
        description="""Ingest benchmark NDAs that will be used as a yardstick to compare NDAs we will judge later.
        Check all the files with NDA in their title in the ndas folder inside the current directory and ingest all the documents using the RAG tool.
        Don't bother with the files inside the uploads folder.
        Only ingest files with docx, doc, and pdf extensions. You don't need to analyze these documents.
        If you pass the path of the documents to the RAG tool, it should be able to parse the documents.""",
        expected_output=EXPECTED_TASK_OUTPUT,
        agent=corporate_lawyer_agent,
    )
    tasks.append(create_accumulating_task(ingest_documents_task, "ingest_documents"))

    identify_parties = Task(
        description=f"""Take the current parties clause, which is inside this: `{input_document}`, and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the parties in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    There is a party that offers services, and there's a party that consumes services. This should be well defined within the clauses.""",
        expected_output=EXPECTED_TASK_OUTPUT,
        agent=parties_corporate_lawyer,
        output_pydantic=AgentOutput,
    )
    tasks.append(create_accumulating_task(identify_parties, "identify_parties"))

    identify_obligations_of_receiving_party = Task(
        description=f"""Take the current obligations of receiving party clause, which is inside this: `{input_document}`, and compare it with similar clauses in our RAG database to check how good it is.
        Your task is to identify the obligations of receiving party in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.""",
        expected_output=EXPECTED_TASK_OUTPUT,
        agent=obligation_information_lawyer,
        output_pydantic=AgentOutput,
    )
    tasks.append(
        create_accumulating_task(identify_obligations_of_receiving_party, "obligations")
    )

    identify_terms_and_termination = Task(
        description=f"""Take the current terms and termination clause, which is inside this: `{input_document}`, and compare it with similar clauses in our RAG database to check how good it is.
        Your task is to identify the terms and termination in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.""",
        expected_output=EXPECTED_TASK_OUTPUT,
        agent=terms_and_termination_lawyer,
        output_pydantic=AgentOutput,
    )
    tasks.append(
        create_accumulating_task(
            identify_terms_and_termination, "terms_and_termination"
        )
    )

    identify_remedies = Task(
        description=f"""Take the current remedies clause, which is inside this: `{input_document}`, and compare it with similar clauses in our RAG database to check how good it is.
        Your task is to identify the remedies in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.""",
        expected_output=EXPECTED_TASK_OUTPUT,
        agent=remedies_lawyer,
        output_pydantic=AgentOutput,
    )
    tasks.append(create_accumulating_task(identify_remedies, "remedies"))

    identify_additional_information = Task(
        description=f"""Take the current additional important information clause, which is inside this: `{input_document}`, and compare it with similar clauses in our RAG database to check how good it is.
        Your task is to identify the additional important information in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.""",
        expected_output=EXPECTED_TASK_OUTPUT,
        agent=additional_information_lawyer,
        output_pydantic=AgentOutput,
    )
    tasks.append(
        create_accumulating_task(identify_additional_information, "additional_info")
    )

    return tasks
