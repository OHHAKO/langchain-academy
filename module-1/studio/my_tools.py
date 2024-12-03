from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# state 정의
class State(TypedDict):
    graph_state: str

# node 정의
def node_A(state):
    print('--node A--')
    return {"graph_state": state['graph_state']}

def node_B(state):
    print('--node B--')
    return {"graph_state": state['graph_state'] + " B!"}

def node_C(state):
    print('--node C--')
    return {"graph_state": state['graph_state'] + " C!"}


def decide_next_A(state) -> Literal["node_B", "node_C"]:
    user_message = state['graph_state']
    print('길이: ', len(user_message))
    if len(user_message)%2 == 0:
        return "node_B"
    else:
        return "node_C"


# graph 정의
builder = StateGraph(State)
builder.add_node("node_A", node_A)
builder.add_node("node_B", node_B)
builder.add_node("node_C", node_C)

# node 연결
builder.add_edge(START, "node_A")
builder.add_conditional_edges("node_A", decide_next_A)
builder.add_edge("node_B", END)
builder.add_edge("node_C", END)

# graph 생성
graph = builder.compile();
graph.invoke({"graph_state":"IamHako"})
