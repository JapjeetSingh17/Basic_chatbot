import os
from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

import gradio as gr

load_dotenv()

llm = init_chat_model(model="groq:llama-3.1-8b-instant")


class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic math expression, e.g. '12 * (3 + 4)'."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"Error: {e}"


@tool
def human_assistance(query: str) -> str:
    """Ask the human user for help when unsure how to proceed."""
    human_response = interrupt({"query": query})
    return human_response["data"]


tools = [calculator, human_assistance]
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": llm_with_tools.invoke(state["messages"])}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "gradio-session"}}
waiting_for_human = {"flag": False}


def chat_fn(message, history):
    if waiting_for_human["flag"]:
        waiting_for_human["flag"] = False
        events = graph.stream(Command(resume={"data": message}), config, stream_mode="values")
    else:
        events = graph.stream(
            {"messages": [{"role": "user", "content": message}]},
            config,
            stream_mode="values",
        )

    last_message = None
    for event in events:
        if "messages" in event:
            last_message = event["messages"][-1]

    state = graph.get_state(config)
    if state.next:
        waiting_for_human["flag"] = True
        pending = state.tasks[0].interrupts[0].value
        return f"🤖 I need your help: {pending['query']}"

    return last_message.content if last_message else "..."


demo = gr.ChatInterface(
    fn=chat_fn,
    title="My LangGraph Agent",
    description="Chat with your agent — powered by Groq + LangGraph",
)

if __name__ == "__main__":
    demo.launch()