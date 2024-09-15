from composio_crewai import Action, App, ComposioToolSet
from dotenv import load_dotenv

load_dotenv()

tool_set = ComposioToolSet()
rag_tools = tool_set.get_tools(
    apps=[App.RAGTOOL],
    actions=[
        Action.FILETOOL_LIST_FILES,
    ],
)

rag_query_tools = tool_set.get_tools(
    apps=[App.RAGTOOL],
)
