from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from rhythmix_model.recommender import nodes

# Initialize the graph builder
graph_builder = StateGraph(nodes.State)

graph_builder.add_node("predict_attributes", nodes.predict_attributes)
graph_builder.add_node("extract_attribute_vectors", nodes.extract_attribute_vectors)
graph_builder.add_node("get_similar_songs", nodes.get_similar_songs)
graph_builder.add_node("generate_llm_response", nodes.llm_response)

graph_builder.add_edge(START, "predict_attributes")
graph_builder.add_edge("predict_attributes", "extract_attribute_vectors")
graph_builder.add_edge("extract_attribute_vectors", "get_similar_songs")
graph_builder.add_edge("get_similar_songs", "generate_llm_response")
graph_builder.add_edge("generate_llm_response", END)

# Set up Memory
memory = MemorySaver()

# Compile the graph
compiled_graph = graph_builder.compile(
    checkpointer=memory, interrupt_after=["predict_attributes"]
)
