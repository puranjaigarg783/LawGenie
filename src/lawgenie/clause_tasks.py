from crewai import Task

from lawgenie.clause_agents import (
    additional_information_lawyer,
    confidential_information_lawyer,
    corporate_lawyer_agent,
    obligation_information_lawyer,
    parties_corporate_lawyer,
    remedies_lawyer,
    terms_and_termination_lawyer,
)
from lawgenie.models import AgentOutput
from lawgenie.nda_to_check import (
    additional_information_nda,
    confidential_information_nda,
    current_nda,
    obligations_nda,
    remedies_nda,
    terms_and_termination_nda,
)

ingest_documents_task = Task(
    description="""Ingest benchmark NDAs that will be used as a yardstick to compare NDAs we will judge later.
    Check all the files with NDA in their title in the current directory and ingest all the documents using the RAG tool.""",
    expected_output="Yes or No based on whether you've ingested the documents given to you with the RAG tool.",
    agent=corporate_lawyer_agent,
)

identify_parties = Task(
    description=f"""Take the current parties clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the parties in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    There is a party that offers services, and there's a party that consumes services. This should be well defined within the clauses.
    This is the parties clause of the current NDA: {current_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=parties_corporate_lawyer,
    output_pydantic=AgentOutput,
)

identify_condifential_information = Task(
    description=f"""Take the current confidential information clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the confidential information in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the confidential information clause of the current NDA: {confidential_information_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=confidential_information_lawyer,
    output_pydantic=AgentOutput,
)

identify_obligations_of_receiving_party = Task(
    description=f"""Take the current obligations of receiving party clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the obligations of receiving party in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the obligations of receiving party clause of the current NDA: {obligations_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=obligation_information_lawyer,
    output_pydantic=AgentOutput,
)

identify_terms_and_termination = Task(
    description=f"""Take the current terms and termination clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the terms and termination in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the terms and termination clause of the current NDA: {terms_and_termination_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=terms_and_termination_lawyer,
    output_pydantic=AgentOutput,
)

identify_remedies = Task(
    description=f"""Take the current remedies clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the remedies in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the remedies clause of the current NDA: {remedies_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=remedies_lawyer,
    output_pydantic=AgentOutput,
)

identify_additional_information = Task(
    description=f"""Take the current additional important information clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the additional important information in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the additional important information clause of the current NDA: {additional_information_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=additional_information_lawyer,
    output_pydantic=AgentOutput,
)
