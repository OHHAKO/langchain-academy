from typing import Literal, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

# 도구 정의
def is_odd_number(a: int) -> bool:
    print('도구 호출: ', a)
    return a % 2 == 1


# LLM에게 도구 쥐어주기
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([is_odd_number])


# state 정의
class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# node 정의
def node_A(state):
    print('--node A--')
    return {"messages": state['messages']}

def node_B(state):
    print('--node B(SKIP)--')
    return {"messages": state['messages'] + " B!"}

def node_C(state):
    print('--node C. Agent와 대화 시작--')

    return {"messages": [llm.invoke(state['messages'])]}


def decide_next_A(state) -> Literal["skip", "node_C"]:
    user_message = state['messages']
    print('길이: ', len(user_message))
    if len(user_message)%2 == 0:
        return "skip"
    else:
        return "node_C"

# graph 정의
builder = StateGraph(MessageState)
builder.add_node("node_A", node_A)
builder.add_node("skip", node_B)
builder.add_node("node_C", node_C)

# node 연결
builder.add_edge(START, "node_A")
builder.add_conditional_edges("node_A", decide_next_A)
builder.add_edge("skip", END)
builder.add_edge("node_C", END)

# graph 생성
graph = builder.compile();
