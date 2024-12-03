from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# state 정의
class State(TypedDict):
    graph_state: str

# node 정의
def node_A(state):
    print('--node A--')
    return {"graph_state": state['graph_state'] + " First!"}

def node_B(state):
    print('--node B--')
    return {"graph_state": state['graph_state'] + " Second!"}

def node_C(state):
    print('--node C--')
    return {"graph_state": state['graph_state'] + " Third!"}

# graph 정의
builder = StateGraph(State)
builder.add_node("node_A", node_A)
builder.add_node("node_B", node_B)
builder.add_node("node_C", node_C)

# node 연결
builder.add_edge(START, "node_A")
builder.add_edge("node_A", "node_B")
builder.add_edge("node_A", "node_C")
builder.add_edge("node_B", "node_C")
builder.add_edge("node_C", END)

# graph 생성
graph = builder.compile();