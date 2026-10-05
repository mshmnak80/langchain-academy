from dotenv import load_dotenv

load_dotenv()


from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-5-nano",temperature=0)

from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage,HumanMessage,RemoveMessage

class State(MessagesState):
    summary:str


def conversation(state:State):

    # Get summary if it exists
    summary = state.get("summary","")

    # If there is summary, then we add it
    if summary:
        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"

        # Append summary to any newer messages
        messages = [SystemMessage(system_message) + state["messages"]]
    else:
        messages = state["messages"]

    response = model.invoke(messages)
    return {"messages":response}


def summarize_conversation(state:State):
    summary = state.get("summary","")

    if summary:
        # A summary already exists
        summary_message = (f"This is summary of the conversation to date: {summary}\n\n"
                           "Extend the summary by taking into account the new messages above:")
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary":response.content,"messages":delete_messages}

from typing import Literal

from langgraph.graph import StateGraph,START,END,MessagesState

def do_continue(state:State) ->Literal["summarize_conversation",END]:

    if len(state["messages"]) > 6:
        return "summarize_conversation"
    
    return END


builder = StateGraph(State)

builder.add_node("conversation",conversation)
builder.add_node("summarize_conversation",summarize_conversation)

builder.add_edge(START,"conversation")
builder.add_conditional_edges("conversation",do_continue)
builder.add_edge("summarize_conversation",END)

from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

config = {"configurable":{"thread_id":"1"}}

input_message = HumanMessage(content="hi! I'm Lance")
output = graph.invoke({"messages":[input_message]},
                      config=config)

for m in output['messages'][-1:]:
    m.pretty_print()

input_message = HumanMessage(content="what's my name?")
output = graph.invoke({"messages": [input_message]}, config) 
for m in output['messages'][-1:]:
    m.pretty_print()

input_message = HumanMessage(content="i like the 49ers!")
output = graph.invoke({"messages": [input_message]}, config) 
for m in output['messages'][-1:]:
    m.pretty_print()

summary = graph.get_state(config).values.get("summary","")
print(summary)

input_message = HumanMessage(content="i like Nick Bosa, isn't he the highest paid defensive player?")
output = graph.invoke({"messages": [input_message]}, config) 
for m in output['messages'][-1:]:
    m.pretty_print()

summary = graph.get_state(config).values.get("summary","")
print(summary)

