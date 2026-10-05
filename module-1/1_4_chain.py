from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

messages  = [AIMessage(content=f"So you said you were researching ocean mammals?",name="Model")]
messages.append(HumanMessage(content=f"Yes, that's right.",name="Lance"))
messages.append(AIMessage(content=f"Great, what would you like to learn about.", name="Model"))
messages.append(HumanMessage(content=f"I want to learn about the best place to see Orcas in the US.", name="Lance"))

for m in messages:
    m.pretty_print()

llm = ChatOpenAI(model="gpt-5-nano")

result = llm.invoke(messages)
print(type(result))
print (result)

#Tools
def multiply(a:int,b:int) -> int:
    """Multiply a and b.
    
        Args:
            a: first int
            b: second int
        """
    return a * b


llm_with_tools = llm.bind_tools([multiply])

tool_call = llm_with_tools.invoke([HumanMessage("What is 2 multiplied by 3",name="Lance")])

print(tool_call.tool_calls)

#Using messages as state
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage

class MessagesState(TypedDict):
    messages:list[AnyMessage]

#Reducers
# each node will return a new value for our state key `messages`.
#But, this new value will overwrite the prior `messages` value! 
#As our graph runs, we want to **append** messages to our `messages` state key.

#We can use [reducer functions](https://docs.langchain.com/oss/python/langgraph/graph-api#reducers) to address this.
#Reducers specify how state updates are performed.
#If no reducer function is specified, then it is assumed that updates to the key should *override it* as we saw before.
#But, to append messages, we can use the pre-built `add_messages` reducer.
#This ensures that any messages are appended to the existing list of messages.
#We simply need to annotate our `messages` key with the `add_messages` reducer function as metadata.
from typing import Annotated
from langgraph.graph.message import add_messages

class MessageState(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]

#or use built in MessageState from langraph

from langgraph.graph import MessagesState

class MessagesState(MessagesState):
    # Add any keys needed beyond messages, which is pre-built 
    pass

initial_messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
                    HumanMessage(content="I'm looking for information on marine biology.", name="Lance")
                   ]

# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")

# Test
add_messages(initial_messages , new_message)

#build graph

from langgraph.graph import StateGraph,START,END


#node
def llm_tool_calling(state:MessagesState):
    return {
        "messages":llm_with_tools.invoke(state["messages"])
    }


#Build graph
builder = StateGraph(MessagesState)

#nodes
builder.add_node('llm_tool_calling',llm_tool_calling)

#edges
builder.add_edge(START,"llm_tool_calling")
builder.add_edge('llm_tool_calling',END)

#build graph
graph = builder.compile()

messages = graph.invoke({"messages":[HumanMessage(content="hello")]})

for m in messages['messages']:
    m.pretty_print()


messages = graph.invoke({"messages": HumanMessage(content="Multiply 2 and 3")})
for m in messages['messages']:
    m.pretty_print()