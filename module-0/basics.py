from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch  # updated at 1.0

load_dotenv()

from langchain_openai import ChatOpenAI
gpt4o_chat = ChatOpenAI(model="gpt-4o", temperature=0)
gpt35_chat = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)


# Create a message
msg = HumanMessage(content="Hello world", name="Lance")

# Message list
messages = [msg]

# Invoke the model with a list of messages 
print(gpt4o_chat.invoke(messages))

print(gpt4o_chat.invoke("hello world"))


tavily_search = TavilySearch(max_results=3)

data = tavily_search.invoke({"query": "What is LangGraph?"})
search_docs = data.get("results", data)
print(search_docs)