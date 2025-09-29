# import the required methods
import requests
import os
from typing import List, Literal, Dict, Any, Callable, Iterable
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
from langchain_openai import AzureChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.redis import RedisSaver
from langgraph.types import StateSnapshot
from settings import Settings

settings = Settings()

os.environ["REQUESTS_CA_BUNDLE"] = settings.roche_certs

@tool
def _get_weather(query: str) -> List[Dict[str, Any]]:
    """Search weatherapi to get the current weather."""
    endpoint: str = f"http://api.weatherapi.com/v1/current.json?key={settings.weather_api_key}&q={query}"
    response: requests.Response = requests.get(endpoint)
    data: Dict[str, Any] = response.json()

    if data.get("location"):
        return data
    else:
        return [{"error" :"Weather Data Not Found"}]   

class LanggraphAgent:
    def __init__(self):
        self.graph = None
        self.agent = None
        self.checkpointer: RedisSaver = None

        with RedisSaver.from_conn_string(settings.redis_url) as redis_saver:
            redis_saver.setup()
            self.checkpointer = redis_saver
        
        self.llm: AzureChatOpenAI = AzureChatOpenAI(
            api_key=settings.openai_api_key,
            azure_endpoint=settings.azure_endpoint,
            azure_deployment=settings.azure_deployment,  
            api_version=settings.api_version,
        )

        _browse_web = TavilySearchResults(max_results=2, tavily_api_key=settings.tavily_api_key)
        tools: List[Callable] = [_get_weather, _browse_web]
        self.llm_with_tools: AzureChatOpenAI = self.llm.bind_tools(tools)
        self.tool_node: ToolNode = ToolNode(tools)

        self._create_graph()
        self.compiled_graph: CompiledStateGraph = self.graph.compile(checkpointer=self.checkpointer)

    def _create_graph(self) -> None:
        # initialize the workflow from StateGraph
        self.graph = StateGraph(MessagesState)
        
        self.graph.add_node("LLM", self._call_model)
        self.graph.add_edge(START, "LLM")
        self.graph.add_node("tools", self.tool_node)
        self.graph.add_conditional_edges("LLM", self._call_tools)
        self.graph.add_edge("tools", "LLM")

    def get_compiled_graph(self) -> CompiledStateGraph:
        return self.compiled_graph
    
    def _call_model(self, state: MessagesState) -> Dict[str, Any]:
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def _call_tools(self, state: MessagesState) -> Literal["tools", END]:
        messages: List[BaseMessage] = state["messages"]
        last_message: BaseMessage = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def get_state_history(self, config) -> Iterable[StateSnapshot]:
        return self.compiled_graph.get_state_history(config=config)
    

