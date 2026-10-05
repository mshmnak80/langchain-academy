from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-5-nano")

def multiply(x:int,y:int):
    """
    multiply  numbers
    """
    return x*y


llm_with_tools = llm.bind_tools([multiply])

from IPython.display import Image, display
from langgraph.graph import StateGraph,START,END,MessagesState
from langgraph.prebuilt import ToolNode,tools_condition


#Node 
def tool_calling_llm(state:MessagesState):
    
    return {"messages":[llm_with_tools.invoke(state["messages"])]}


#builder
builder = StateGraph(MessagesState)

#nodes
builder.add_node("tool_calling_llm",tool_calling_llm)
builder.add_node("tools",ToolNode([multiply]))

#edges
builder.add_edge(START,"tool_calling_llm")
# If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
# If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
builder.add_conditional_edges("tool_calling_llm",tools_condition)
builder.add_edge("tools",END)

#graph
graph = builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))
from langchain_core.messages import HumanMessage
messages = [HumanMessage(content="Hello, what is 2 multiplied by 2?")]
messages = graph.invoke({"messages": messages})
for m in messages['messages']:
    m.pretty_print()


