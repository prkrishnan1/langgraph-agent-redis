from langgraph.types import StateSnapshot
from agent import LanggraphAgent
from typing import Dict, Iterable, List, Tuple, Any

from agent import LanggraphAgent

class Thread:
    def __init__(self, user_id: str, thread_id: str, agent: LanggraphAgent):
        self.config: Dict[str, str] = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        print(self.config)
        self.agent: LanggraphAgent = agent

    def stream_agent_response(self, input_text: str, config: Dict[str, str]) -> Iterable[Any]:
        inputs = {"messages": [("user", input_text)]}
        return self.agent.get_compiled_graph().stream(inputs, config=config, stream_mode="messages")
    
    def populate_chat_history(self) -> List[Tuple[str, str]]:
        state_history: Iterable[StateSnapshot] = self.agent.get_state_history(config=self.config)
        type_mapping: Dict[str, str] = {
            "human": "user",
            "ai": "assistant",
            "tool": "tool",
            "system": "system"
        }
        messages_tuples: List[Tuple[str, str]] = []

        state_history = list(state_history)
        if len(state_history) > 0:
            last_snapshot: StateSnapshot = state_history[-1]
            messages: List[Dict[str, Any]] = last_snapshot.values.get("messages", [])

            for message in messages:
                if message:
                    messages_tuples.append((type_mapping[message['kwargs']['type']], message['kwargs']['content']))

            print(messages_tuples)
            return messages_tuples
        
        return []