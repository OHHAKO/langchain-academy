import random
from typing import Literal, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

# 도구 정의
def random_number(a: int, b: int) -> int:
    """Returns a random integer between a and b.

    Args:
        a: first int
        b: second int
    """
    print('[도구 호출] random_number: ', a, b)
    return random.randint(a, b)

def is_odd_number(a: int) -> bool:
    """Returns True if a is odd, False otherwise.

    Args:
        a: int
    """
    print('[도구 호출] is_odd_number: ', a)
    return a % 2 == 1

def is_prime_number(a: int) -> bool:
    """Returns True if a is prime, False otherwise.

    Args:
        a: first int
    """
    print('[도구 호출] is_prime_number: ', a)
    if a < 2:
        return False
    for i in range(2, int(a**0.5) + 1):
        if a % i == 0:
            return False
    return True

# LLM에게 도구 쥐어주기
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([is_odd_number, random_number, is_prime_number],parallel_tool_calls=True)


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
    last_message = state['messages'][-1]
    tool_call = last_message.additional_kwargs.get('tool_calls')
    print('state: ', tool_call)
    
    if tool_call:
        return "tool"
    return END

# graph 정의
builder = StateGraph(MessageState)
builder.add_node("assistant", assistant_node)
builder.add_node("tool", ToolNode([is_odd_number, random_number, is_prime_number]))

# node 연결
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tool", "assistant")

# graph 생성
graph = builder.compile();
