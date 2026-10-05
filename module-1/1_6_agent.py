from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

# This will be a tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b

tools = [multiply,add,divide]

llm = ChatOpenAI(model="gpt-5-nano")

llm_with_tools = llm.bind_tools(tools,parallel_tool_calls=False)


from langgraph.graph import StateGraph,MessagesState,START,END
from langchain.messages import SystemMessage,HumanMessage
from langgraph.prebuilt import ToolNode,tools_condition

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

#Node
def assistant(state:MessagesState):
    return {"messages":[llm_with_tools.invoke([sys_msg] + state["messages"])]}



builder = StateGraph(MessagesState)

#nodes
builder.add_node('assistant',assistant)
builder.add_node("tools",ToolNode(tools))

#edges

builder.add_edge(START,'assistant')
builder.add_conditional_edges("assistant",tools_condition)

builder.add_edge("tools","assistant")

graph = builder.compile()
messages = [HumanMessage(content="Add 3 and 4. Multiply the output by 2. Divide the output by 5")]

messages = graph.invoke({"messages":messages})

for m in messages["messages"]:
    m.pretty_print()