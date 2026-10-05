from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from dotenv import load_dotenv
load_dotenv()
#default overwriting state

class State(TypedDict):
    foo:int


def node_1(state):
    print("---Node 1---")
    return {"foo":state["foo"] + 1}

builder = StateGraph(State)
builder.add_node("node_1",node_1)

builder.add_edge(START,"node_1")
builder.add_edge("node_1",END)

graph = builder.compile()

result = graph.invoke({"foo":1})
print(result)

#branching 
#node 1 branches to node 2 and 3 
#they both attemp to overwrite the foo in same step (node 2 and 3 are on same level this called step)
#use reducers use annotedt o append the valure returned from each node rather than overwwritng it 
from operator import add 
from typing import Annotated

class State(TypedDict):
    foo:Annotated[list[int],add]

def node_1(state):
    print("---node1---")
    return {"foo":[state["foo"][0] + 1]}

builder = StateGraph(State)

builder.add_node("node_1",node_1)

builder.add_edge(START,"node_1")
builder.add_edge("node_1",END)

graph = builder.compile()

result = graph.invoke({"foo":[1]})

# now, our state key `foo` is a list.
# This `operator.add` reducer function will append updates from each node to this list. 

def node_1(state):
    print("---Node 1---")
    return {"foo": [state['foo'][-1] + 1]}

def node_2(state):
    print("---Node 2---")
    return {"foo": [state['foo'][-1] + 1]}

def node_3(state):
    print("---Node 3---")
    return {"foo": [state['foo'][-1] + 1]}

#Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

graph = builder.compile()
result = graph.invoke({"foo" : [1]})
print(result)

#custom reducers when passing None for example 

def reduce_list(left:list | None ,right: list | None):

    if not left:
        left=[]
    if not right:
        right = []

    return left + right

class DefaultState(TypedDict):
    foo: Annotated[list[int], add]

class CustomReducerState(TypedDict):
    foo:Annotated[list[int],reduce_list]

#try wit None it will raise error 
def node_1(state):
    print("---Node 1---")
    return {"foo": [2]}

# Build graph
builder = StateGraph(DefaultState)
builder.add_node("node_1", node_1)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

# Add
graph = builder.compile()

try:
    print(graph.invoke({"foo" : None}))
except TypeError as e:
    print(f"TypeError occurred: {e}")


#use custome reducer 
# Build graph
builder = StateGraph(CustomReducerState)
builder.add_node("node_1", node_1)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

# Add
graph = builder.compile()

try:
    print(graph.invoke({"foo" : None}))
except TypeError as e:
    print(f"TypeError occurred: {e}")

#messages
from langgraph.graph import MessagesState
from langchain_core.messages import AnyMessage,AIMessage,HumanMessage
from langgraph.graph import add_messages
from typing import Annotated

# Define a custom TypedDict that includes a list of messages with add_messages reducer
#both CustomMessageState abnd ExtenedMessageState are equivlant
class CustomMessageState(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]
    added_key_1 :str
    added_jey_2 :str
    #etc

class ExtenedMessageState(MessagesState):
    added_key_1 :str
    added_jey_2 :str
    #etc

initial_messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
                    HumanMessage("I'm looking for information on marine biology.", name="Lance")]

new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")

# test

print(add_messages(initial_messages,new_message))

#Rewriting messages 
# messages id 2 overwrite
# Initial state
initial_messages = [AIMessage(content="Hello! How can I assist you?", name="Model", id="1"),
                    HumanMessage(content="I'm looking for information on marine biology.", name="Lance", id="2")
                   ]

# New message to add
new_message = HumanMessage(content="I'm looking for information on whales, specifically", name="Lance", id="2")

# Test
print(add_messages(initial_messages , new_message))

#Message Removal
# Message list
messages = [AIMessage("Hi.", name="Bot", id="1")]
messages.append(HumanMessage("Hi.", name="Lance", id="2"))
messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3"))
messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about?", name="Lance", id="4"))

from langchain_core.messages import RemoveMessage

delete_messages = [RemoveMessage(id=m.id)for m in messages[:-2]]
print("---------------------------------")
print(delete_messages)

messages_after_delete = add_messages(messages,delete_messages)
print(messages_after_delete)
