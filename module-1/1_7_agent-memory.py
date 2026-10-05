from dotenv import load_dotenv

load_dotenv()


def multiply(a:int, b:int) -> int:
    """
    Multiply a and b

    Args:
        a:first int
        b:second int
    """
    return a*b


def add (a:int , b:int) -> int:
    """"
    Adds a and b

    Args:
        a: first int
        b:second int
    """
    return a+b 

def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b

tools = [add,multiply,divide]

#llm 
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-5-nano")
llm_with_tools = llm.bind_tools(tools=tools)
#builder
from langgraph.graph import StateGraph,START,END
from langgraph.graph import MessagesState
from langchain.messages import SystemMessage,HumanMessage,AIMessage
from langgraph.prebuilt import tools_condition,ToolNode
builder = StateGraph(MessagesState)

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")
#node
def assistant(state:MessagesState):
    return {"messages":[llm_with_tools.invoke([sys_msg]+ state["messages"])]}

builder.add_node("assistant",assistant)
builder.add_node("tools",ToolNode(tools))

#edges
builder.add_edge(START,"assistant")
builder.add_conditional_edges("assistant",tools_condition)
builder.add_edge("tools","assistant")

react_graph = builder.compile()

messages = [HumanMessage(content="Add 3 and 4.")]
messages = react_graph.invoke({"messages":messages})

for m in messages["messages"]:
    m.pretty_print()

messages = [HumanMessage(content="Multiply that by 2.")]
messages = react_graph.invoke({"messages": messages})
for m in messages['messages']:
    m.pretty_print()

#with memory 
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
react_graph_memory = builder.compile(checkpointer=memory)

config = {"configurable":{"thread_id":"1"}}

messages = [HumanMessage(content="Add 3 and 4")]

messages = react_graph_memory.invoke({"messages":messages},config)
for m in messages['messages']:
    m.pretty_print()
messages = [HumanMessage(content="Multiply that by 2.")]

messages = react_graph_memory.invoke({"messages": messages}, config)
for m in messages['messages']:
    m.pretty_print()