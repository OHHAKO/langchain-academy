from typing import Literal, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

# 도구 정의
def is_odd_number(a: int) -> bool:
    print('도구 호출: ', a)
    return a % 2 == 1

# LLM에게 도구 쥐어주기
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([is_odd_number],parallel_tool_calls=True)


# state 정의
class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]



# node 정의
def assistant_node(state):
    print('--node C. Agent와 대화 시작--')

    return {"messages": [llm_with_tools.invoke(state['messages'])]}

def tool_node(state):
    return {"messages": state['messages']}

def tools_condition(state) -> Literal[END, 'tool']:
    # 도구를 사용했는지 유무 판단
    tool_call = state['messages'][0].additional_kwargs.get('tool_calls')
    print('state: ', tool_call)
    
    if tool_call:
        return "tool"
    return END

# graph 정의
builder = StateGraph(MessageState)
builder.add_node("assistant", assistant_node)
builder.add_node("tool", tool_node)

# node 연결
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tool", "assistant")

# graph 생성
graph = builder.compile();
