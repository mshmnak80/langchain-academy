from dotenv import load_dotenv
from typing import TypedDict,Literal
import random
from langgraph.graph import StateGraph,START,END
from dataclasses import dataclass
load_dotenv()

# class TypeddictState(TypedDict):
#     name:str
#     mood:Literal["happy","sad"]

# @dataclass
# class DataClassState():
#     name:str
#     mood:Literal["happy","sad"]

from pydantic import BaseModel ,field_validator,ValidationError

class PydanticState(BaseModel):
      
    name:str 
    mood:str # happy sad

    @field_validator("mood")
    @classmethod
    def validate_mood(cls,value):
        if value not in ["happy","sad"]:
            raise ValueError("Each mood must be either 'happy' or 'sad'")
        return value
                         

def node_1(state):
    print("---Node 1---")
    #return {"name":state['name'] + " is ..."} #Typeddict
    return {"name":state.name + " is ..."} #dataclass

def node_2(state):
    print("---Node 2---")
    return {"mood":"happy"}

def node_3(state):
    print("---Node 3---")
    return {"mood":"sad"}

def decide_mood(state) -> Literal["node_2","node_3"]:

# Here, let's just do a 50 / 50 split between nodes 2, 3
    if random.random() < 0.5:
        return "node_2"
    
    return "node_3"

try:
    state = PydanticState(name="John Doe", mood="mad")
except ValidationError as e:
    print("Validation Error:", e)

#builder = StateGraph(TypeddictState) #Typeddict
#builder = StateGraph(DataClassState)#dataclass
builder = StateGraph(PydanticState)
builder.add_node("node_1",node_1)
builder.add_node("node_2",node_2)
builder.add_node("node_3",node_3)

builder.add_edge(START,"node_1")
builder.add_conditional_edges("node_1",decide_mood)
builder.add_edge("node_2",END)
builder.add_edge("node_3",END)

graph = builder.compile()

#result = graph.invoke({"name":"Lance"})
#result = graph.invoke(DataClassState(name="Lance",mood="sad"))#dataclass
result = graph.invoke(PydanticState(name="Alice",mood="sad"))


print(result)