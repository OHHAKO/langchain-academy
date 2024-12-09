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
def find_age_nutrition(age: int) -> list[str]:
    """Returns nutrition information array of age.

    Args:
        age: first int
    """
    print('[도구 호출] find_age_nutrition: ', age)
    return ["비타민A", "비타민B", "비타민C", "비타민D", "비타민E", "비타민F"]

def avoid_unfit_nutrition(age:int) -> list[str]:
    """Returns nutrition array that avoid unfit for age.

    Args:
        age: int
    """
    print('[도구 호출] avoid_unfit_nutrition: ', age)
    return ["비타민A", "비타민B"]

# TODO: 인자로 나중에는 diagnosis가 들어오면 어떨까?
# 혹은 diagnosis를 가져오게 하고 추천을 맡기거나?
# 혹은 diagnosis 기반 추천을 가져오거나?
def required_nutrition_by_diagnosis(age: int) -> list[str]:
    """Returns nutrition array that required for diagnosis.

    Args:
        age: int
    """
    print('[도구 호출] required_nutrition_by_diagnosis: ', age)
    return ["비타민A", "비타민C","비타민D"]

# 도구 배열

# LLM에게 도구 쥐어주기
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([find_age_nutrition, avoid_unfit_nutrition, required_nutrition_by_diagnosis],parallel_tool_calls=True)


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
    last_message = state['messages'][-1]
    tool_call = last_message.additional_kwargs.get('tool_calls')
    print('state: ', tool_call)
    
    if tool_call:
        return "tool"
    return END

# graph 정의
builder = StateGraph(MessageState)
builder.add_node("assistant", assistant_node)
builder.add_node("tool", ToolNode([find_age_nutrition, avoid_unfit_nutrition, required_nutrition_by_diagnosis]))

# node 연결
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tool", "assistant")

# graph 생성
graph = builder.compile();
