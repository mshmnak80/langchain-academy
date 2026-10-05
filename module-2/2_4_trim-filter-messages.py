# Filtering and trimming messages
from dotenv import load_dotenv
load_dotenv()

#define messages
from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage
messages = [AIMessage(f"So you said you were researching ocean mammals?", name="Bot")]
messages.append(HumanMessage(f"Yes, I know about whales. But what others should I learn about?", name="Lance"))

for m in messages:
    m.pretty_print()

#pass to chat model
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-5-nano")
print(llm.invoke(messages))


#chat model with MessageState this will append or delete messages
from langgraph.graph import MessagesState,START,END,StateGraph

def chat_model(state:MessagesState):
    return {"messages":llm.invoke(state['messages'])} #will return last message and append it to messages since qe are using MessageState

builder = StateGraph(MessagesState)
builder.add_node("chat_model",chat_model)
builder.add_edge(START,"chat_model")
builder.add_edge("chat_model",END)

grap = builder.compile()

output = grap.invoke({"messages":messages})

for m in output['messages']:
    m.pretty_print()


#manage long conversations
#REDUCER RemoveMessage
#removemessage addmessage to state
from langchain_core.messages import RemoveMessage
def filter_messages(state:MessagesState):
    deleted_messages = [RemoveMessage(m.id) for m in state['messages'][:-2]]

    return {"messages":deleted_messages}


builder = StateGraph(MessagesState)

builder.add_node("filter_messages",filter_messages)
builder.add_node("chat_model",chat_model)

builder.add_edge(START,"filter_messages")
builder.add_edge("filter_messages","chat_model")
builder.add_edge("chat_model",END)

graph = builder.compile()

output = graph.invoke({"messages":messages})

for m in output['messages']:
    m.pretty_print()


#FILTER MESSAGES
#in case you dont want to update the state to remove messages , just pass the filtered messages into llm

def chat_model_node(state:MessagesState):
    return {"messages":[llm.invoke(state['messages'][-1:])]}

#build graph

builder = StateGraph(MessagesState)
builder.add_node("chat_model",chat_model_node)
builder.add_edge(START,"chat_model")
builder.add_edge("chat_model",END)

graph = builder.compile()

#Let's take our existing list of messages, append the above LLM response, and append a follow-up question.
messages.append(output['messages'][-1])
messages.append(HumanMessage(f"Tell me more about Narwhals!", name="Lance"))

for m in messages:
    m.pretty_print()

# Invoke, using message filtering
output = graph.invoke({'messages': messages})
for m in output['messages']:
    m.pretty_print()


#TRIM MESSAGES
#This restricts the message history to a specified number of TOKENS.

from langchain_core.messages import trim_messages

def chat_model_node(state:MessagesState):
    messages = trim_messages(state["messages"],
                             max_tokens=100,
                             strategy="last",
                             token_counter=ChatOpenAI(model="gpt-5-nano"),
                             allow_partial=False)

    return {"messages":llm.invoke(messages)}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

messages.append(output['messages'][-1])
messages.append(HumanMessage(f"Tell me where Orcas live!", name="Lance"))

messages_out_trim = graph.invoke({'messages': messages})
for m in messages_out_trim["messages"]:
    m.pretty_print()
#print(messages_out_trim)