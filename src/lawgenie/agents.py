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


crew = Crew(
    agents=[corporate_lawyer_agent, parties_corporate_lawyer],
    tasks=[ingest_documents_task, identify_parties],
    process=Process.sequential,
    verbose=True,
)

crew.kickoff()
