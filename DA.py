import streamlit as st
import pandas as pd
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO

# Load graph data from Excel file
def load_graph_from_excel(file_path):
    df = pd.read_excel(file_path)
    
    graph = {}

    for _, row in df.iterrows():
        src, dest, weight = row['source'], row['destination'], row['weight']
        if src not in graph:
            graph[src] = {}
        graph[src][dest] = weight

        if dest not in graph:
            graph[dest] = {}

    return graph

# Dijkstra's algorithm for shortest path
def compute_shortest_paths(graph, start_node):
    priorq = [(0, start_node)]  # Priority queue for nodes
    distances = {node: float('inf') for node in graph}  # Initialize distances
    distances[start_node] = 0
    previous_nodes = {}

    while priorq:
        current_distance, current_node = heapq.heappop(priorq)

        for neighbor, weight in graph[current_node].items():
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priorq, (new_distance, neighbor))

    return distances, previous_nodes

# Reconstruct the shortest path
def reconstruct_path(previous_nodes, start_node, end_node):
    path = []
    while end_node != start_node:
        path.append(end_node)
        end_node = previous_nodes.get(end_node)
        if end_node is None:
            return None

    path.append(start_node)
    path.reverse()
    return path

# Visualize the graph with optional shortest path
def generate_graph_visualization(graph, path=None):
    G = nx.DiGraph()

    for src, neighbors in graph.items():
        for dest, weight in neighbors.items():
            G.add_edge(src, dest, weight=weight)

    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r', width=2)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

# Main Streamlit app
def main():
    st.title("Shortest Path Finder using Dijkstra's Algorithm")

    st.markdown("<div style='text-align: right; font-size: 12px;'>Delroy Pires | PA-3</div>", unsafe_allow_html=True)

    graph = load_graph_from_excel("graph.xlsx")
    nodes = list(graph.keys())

    start_node = st.selectbox("Select Start Node", nodes)
    end_node = st.selectbox("Select End Node", nodes)

    if st.button("Find Shortest Path"):
        distances, previous_nodes = compute_shortest_paths(graph, start_node)
        shortest_path = reconstruct_path(previous_nodes, start_node, end_node)

        if shortest_path:
            st.success(f"Shortest Distance: {distances[end_node]}")
            st.write("Path:", " → ".join(shortest_path))
            graph_image = generate_graph_visualization(graph, shortest_path)
        else:
            st.error("No path found between the selected nodes.")
            graph_image = generate_graph_visualization(graph)

        st.image(graph_image, caption="Graph Visualization")


if __name__ == "__main__":
    main()