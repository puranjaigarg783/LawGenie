from composio_crewai import Action, ComposioToolSet
from dotenv import load_dotenv

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
