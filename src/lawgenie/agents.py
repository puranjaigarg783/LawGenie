from composio_crewai import Action, ComposioToolSet
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    """Output of each clause agent"""

    analysis: str = Field(description="An analysis of the section in laymen terms")
    recommendation: str = Field(
        description="How the current clause deviates from the benchmark documents"
    )


load_dotenv()

tool_set = ComposioToolSet()
rag_tools = tool_set.get_tools(
    actions=[
        Action.FILETOOL_LIST_FILES,
        Action.RAGTOOL_ADD_CONTENT_TO_RAG_TOOL,
        Action.RAGTOOL_RAG_TOOL_QUERY,
    ]
)

rag_query_tools = tool_set.get_tools(actions=[Action.RAGTOOL_RAG_TOOL_QUERY])

# this is just an example of how the json for ONE of the clauses might look
current_nda = {
    "Parties and Execution": {
        "summary": "This section identifies the parties entering into the agreement and includes their details, signatures, and the date of signing.",
        "full_text": "oneNDA Version 2.0 ONE \nNDA \nPARTIES AND EXECUTION \nParty 1 Party 2 \nEntity details: Entity details: \nSignature: Signature: \nName: Name: \nTitle: Title: \nEmail: Email: \nDate: Date: \nParty 3 Party 4 \nEntity details: Entity details: \nSignature: Signature: \nName: Name: \nTitle: Title: \nEmail: Email: \nDate: Date: ",
    }
}

confidential_information_nda = {
     "Definition of Confidential Information": {
    "summary": "This section defines how 'Confidential Information' is determined in the agreement.",
    "full_text": "1 1.2. What is Confidential Information? (a) Confidential Information means information that is disclosed: (i) by a party to this Agreement (the Discloser) or on the Discloser's behalf by its authorised representatives or its Affiliates, (ii) to the other party to this Agreement (the Receiver), its Affiliates or Permitted Receivers, and (iii) in connection with the Purpose. (b) Affiliates means any: (i) entity that directly or indirectly controls, is controlled by, is under common control with or is otherwise in the same group of entities as a party to this Agreement, or (ii) fund or limited partnership that is managed or advised, or whose general partner or manager is managed or advised, by the Receiver or its Affiliate or which the Receiver or its Affiliate controls. (c) Permitted Receivers means the Receiver's Affiliates and the Receiver's or its Affiliates' officers, employees, members, representatives, professional advisors, agents and subcontractors. (d) Confidential Information does not include information that is: (i) in the public domain not by breach of this Agreement, (ii) known by the Receiver or its Permitted Receivers at the time of disclosure, (iii) lawfully obtained by the Receiver or its Permitted Receivers from a third party other than through a breach of confidence, (iv) independently developed by the Receiver, or (V) expressly indicated by the Discloser as not confidential."
  },
}

obligations_nda = {
     "Obligations of Receiving Party": {
    "summary": "This section outlines the duties of the party receiving confidential information, including who they can share it with and how they must handle it.",
    "full_text": "2 1.3. Who can I share it with? (a) The Receiver may share the Confidential Information with its Permitted Receivers, but only if they: (i) need to know it, and only use it, for the Purpose, and (ii) have agreed to keep it confidential and restrict its use to the same extent that the Receiver has. (b) The Receiver is liable for its breach of this Agreement and any act or omission by a Permitted Receiver which would constitute a breach of this Agreement if it were a party to it. (c) The Receiver may share the Confidential Information if required by law or regulation but must promptly notify the Discloser of the requirement if allowed by law or regulation. 3 1.4. What are my obligations? The Receiver must: (a) only use the Confidential Information for the Purpose, (b) keep the Confidential Information secure and confidential and only disclose it as allowed by this Agreement, (c) promptly notify the Discloser if it becomes aware of a breach of this Agreement, and (d) within thirty days of the Discloser's request, take reasonable steps to destroy or erase any Confidential Information it holds, except the Receiver may retain copies of Confidential Information: (i) that are securely stored in archival or computer back-up systems, (ii) to meet legal or regulatory obligations, or (iii) in accordance with bona fide record retention policies, subject to this Agreement's terms."
  }
}

terms_and_termination_nda = {
   "Term and Termination": {
    "summary": "This section describes the duration of the agreement and how it can be terminated.",
    "full_text": "4 1.5. How long do my obligations last? (a) The Receiver's obligations in relation to Confidential Information start on the date Confidential Information is disclosed and last until the end of the Confidentiality Period. (b) A party may terminate this Agreement with thirty days' prior written notice, but termination will not affect the parties' obligations in relation to Confidential Information disclosed before termination, which continue until the Confidentiality Period expires."
  }
}

remedies_nda = {
    "Remedies": {
    "summary": "This section is not present in the provided NDA text.",
    "full_text": ""
  }
}

return_of_confidential_information_nda = {
   "Return of Confidential Information": {
    "summary": "This section is not present in the provided NDA text.",
    "full_text": ""
  },
}

additional_information_nda = {
     "Additional Important Information": {
    "summary": "This section includes additional important information not covered in other sections, such as notice requirements, third-party rights, and governing law.",
    "full_text": "7. 5.8. Other important information (a) Notices. Formal notices under this Agreement must be in writing and sent to the email addresses on the Agreement's front page as may be updated by a party to the other in writing. (b) Third parties. Except for the Discloser's Affiliates, no one other than a party to this Agreement has the right to enforce any of its terms. (c) Entire agreement. This Agreement supersedes all prior discussions and agreements and constitutes the entire agreement between the parties with respect to its subject matter and no party has relied on any statement or representation of any person in entering into this Agreement. (d) Amendments. Any amendments to this Agreement must be agreed in writing. (e) Assignment. No party can assign this Agreement to anyone else without the other parties' consent. (f) Waiver. If a party fails to enforce a right under this Agreement, that is not a waiver of that right at any time. (g) Equitable relief. The Discloser may seek injunctive relief or specific performance to enforce its rights under this Agreement. (h) Counterparts. This Agreement may be executed in any number of counterparts and this has the same effect as if the signatures on the counterparts were on a single copy of this Agreement. (i) Governing Law. The Governing Law (excluding any conflicts of laws principles) applies to this Agreement and related issues. (j) Dispute Resolution. Any dispute arising in connection with this Agreement must only be resolved by the Dispute Resolution Method."
  }
}



### Manager/Scaffolding agents here
corporate_lawyer_agent = Agent(
    role="Corporate Lawyer",
    goal="Use the documents you're given and the RAG tool to build a knowledge base of NDAs that you can refer later.",
    backstory="""You are a corporate lawyer who has vast knowledge of NDAs, different sections within them, and how they are supposed to work.
    You also have the ability to call the RAG tool to ingest new documents that using the paths of files given to you and building a knowledge base of NDAs.""",
    tools=rag_tools,
    verbose=True,
)

ingest_documents_task = Task(
    description="""Ingest benchmark NDAs that will be used as a yardstick to compare NDAs we will judge later.
    Check all the files with NDA in their title in the current directory and ingest all the documents using the RAG tool.""",
    expected_output="Yes or No based on whether you've ingested the documents given to you with the RAG tool.",
    agent=corporate_lawyer_agent,
)


### Clause agents and tasks here - try to check if one agent can be used for multiple clauses, since handoff between agents takes time
parties_corporate_lawyer = Agent(
    role="Parties Corporate Lawyer",
    goal="To compare the current NDA parties clause to the ones in our RAG database and identify how good it is.",
    backstory="""You are a corporate lawyer who specialises in identifying who the parties in a certain NDA are.
    There's no one who does it as well as you do. Things that others miss, you don't.""",
    tools=rag_query_tools,
    verbose=True,
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


# confidential information lawyer
confidential_information_lawyer = Agent(
    role="Confidential Information Lawyer",
    goal="To compare the current NDA confidential information clause to the ones in our RAG database and identify how good it is.",
    backstory="""You are a confidential information lawyer who specialises in identifying what the confidential information is in a certain NDA.
    Identifying confidential information is like second nature to you. You can even tell the confidential information in an NDA even while sleeping.""",
    tools=rag_query_tools,
    verbose=True,
)
identify_condifential_information = Task(
    description=f"""Take the current confidential information clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the confidential information in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the confidential information clause of the current NDA: {confidential_information_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=confidential_information_lawyer,
    output_pydantic=AgentOutput,
)

#obligations of receiving party
obligation_information_lawyer = Agent(
    role="Obligations of Receiving Party Lawyer",
    goal="To compare the current NDA obligations of receiving party clause to the ones in our RAG database and identify how good it is.",
    backstory="""You are an obligations of receiving party lawyer who is an expert in identifying what the obligations of receiving party is in a certain NDA.
    You have never failed to identify obligations of receiving party in an NDA. You are a lawyer with many years of experience and know how to identify obligations of receiving party.
    """,
    tools=rag_query_tools,
    verbose=True,
)
identify_obligations_of_receiving_party = Task(
    description=f"""Take the current obligations of receiving party clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the obligations of receiving party in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the obligations of receiving party clause of the current NDA: {obligations_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=obligation_information_lawyer,
    output_pydantic=AgentOutput,
)


# terms and termination
terms_and_termination_lawyer = Agent(
    role="Terms and Termination Lawyer",
    goal="To compare the current NDA terms and termination clause to the ones in our RAG database and identify how good it is.",
    backstory="""You are a terms and termination lawyer who is an expert in identifying what the terms and termination is in a certain NDA.
    Terms and terminatioin are in your DNA. When given an NDA, you're eyes first go to terms and termination clause and you can identify fallacies well.
    """,
    tools=rag_query_tools,
    verbose=True,
)
identify_terms_and_termination = Task(
    description=f"""Take the current terms and termination clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the terms and termination in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the terms and termination clause of the current NDA: {terms_and_termination_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=terms_and_termination_lawyer,
    output_pydantic=AgentOutput,
)


# remedies
remedies_lawyer = Agent(
    role="Remedies Lawyer",
    goal="To compare the current NDA remedies clause to the ones in our RAG database and identify how good it is.",
    backstory="""You are a remedies lawyer who is an expert in identifying what the remedies is in a certain NDA.
    You craft perfect remedies in an NDA in the case of breach or conflict. You are the go to person for remedies in an NDA.
    """,
    tools=rag_query_tools,
    verbose=True,
)
identify_remedies = Task(
    description=f"""Take the current remedies clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the remedies in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the remedies clause of the current NDA: {remedies_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=remedies_lawyer,
    output_pydantic=AgentOutput,
)

# not sure to add return of confidential lawyer because I'm not sure how different it is from the confidential_information_lawyer, or if we can fold this into that

# additional important information
additional_information_lawyer = Agent(
    role="Additional Important Information Lawyer",
    goal="To compare the current NDA additional important information clause to the ones in our RAG database and identify how good it is.",
    backstory="""You are an additional important information lawyer who is an expert in identifying what the additional important information is in a certain NDA.
    You identify up all the missing information in an NDA. You carefully craft perfect additional important information in an NDA.
    """,
    tools=rag_query_tools,
    verbose=True,
)
identify_additional_information = Task(
    description=f"""Take the current additional important information clause and compare it with similar clauses in our RAG database to check how good it is.
    Your task is to identify the additional important information in our NDA, and see if the current NDA clause abides by all the best practices of similar clauses.
    This is the additional important information clause of the current NDA: {additional_information_nda}""",
    expected_output="A json that has an analysis of the current clause in laymen terms as well as a recommendation of how the current clause deviates from the benchmark clauses",
    agent=additional_information_lawyer,
    output_pydantic=AgentOutput,
)


crew = Crew(
    agents=[corporate_lawyer_agent, parties_corporate_lawyer, obligation_information_lawyer, terms_and_termination_lawyer, remedies_lawyer, additional_information_lawyer],
    tasks=[ingest_documents_task, identify_parties, identify_obligations_of_receiving_party, identify_terms_and_termination, identify_remedies, identify_additional_information],
    process=Process.sequential,
    verbose=True,
)

crew.kickoff()
