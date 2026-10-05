from typing import TypedDict
from typing import Literal
import random
class State(TypedDict):
    graph_state:str


def node_1(state):

    state["graph_state"] = state["graph_state"] + " Hi I'm"
    print("__node1__")
    return {"graph_state":state["graph_state"]}

def node_2(state):
    print("__node2__")
    return {"graph_state":{state["graph_state"]+ " happy"}}

def node_3(state):
    print("__node3__")
    return {"graph_state":{state["graph_state"]+ " sad"}}

def decide_mood(state) -> Literal["node_2", "node_3"]:
    if random.random() < 0.5:
        return "node_2"
    else:
        return "node_3"

from IPython.display import Image, display
from langgraph.graph import StateGraph,START,END
#build graph
builder = StateGraph(State)
#add nodes
builder.add_node("node_1",node_1)
builder.add_node("node_2",node_2)
builder.add_node("node_3",node_3)

#add edges
builder.add_edge(START,"node_1")
builder.add_conditional_edges("node_1",decide_mood)
builder.add_edge("node_2",END)
builder.add_edge("node_3",END)

graph = builder.compile()

#view
display(Image(graph.get_graph().draw_mermaid_png()))

#grap invocation

print(graph.invoke({"graph_state":"Hi this is Lance."}))

