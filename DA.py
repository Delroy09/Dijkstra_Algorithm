import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load graph data from Excel file with caching
@st.cache_data
def load_graph_from_excel(file_path):
    df = pd.read_excel(file_path)
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['destination'], weight=row['weight'])
    return G

# Visualize the graph with optional shortest path
def generate_graph_visualization(G, path=None):
    pos = nx.spring_layout(G, seed=42, k=2.5)
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#F8F9FA')

    path_nodes = set(path) if path else set()
    path_edges = set(zip(path, path[1:])) if path else set()

    # Node colors
    node_colors = []
    for node in G.nodes():
        if path and node == path[0]:
            node_colors.append('#2ECC71')   # start = green
        elif path and node == path[-1]:
            node_colors.append('#E74C3C')   # end = red
        elif node in path_nodes:
            node_colors.append('#F39C12')   # on path = orange
        else:
            node_colors.append('#AED6F1')   # default = light blue

    # Edge colors and widths
    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        if (u, v) in path_edges:
            edge_colors.append('#E74C3C')
            edge_widths.append(3.0)
        else:
            edge_colors.append('#B0BEC5')
            edge_widths.append(1.0)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_colors,
                           node_size=1800,
                           linewidths=1.5,
                           edgecolors='white')

    # Draw node labels
    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_size=13,
                            font_weight='bold',
                            font_color='#2C3E50')

    # Draw edges with slight curve for directed clarity
    nx.draw_networkx_edges(G, pos, ax=ax,
                           edge_color=edge_colors,
                           width=edge_widths,
                           arrows=True,
                           arrowsize=20,
                           arrowstyle='-|>',
                           connectionstyle='arc3,rad=0.1',
                           min_source_margin=25,
                           min_target_margin=25)

    # Edge weight labels
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax,
                                 font_size=10,
                                 font_color='#555555',
                                 bbox=dict(boxstyle='round,pad=0.2',
                                           facecolor='white',
                                           edgecolor='none',
                                           alpha=0.7))

    # Legend
    legend_handles = [
        mpatches.Patch(color='#2ECC71', label='Start node'),
        mpatches.Patch(color='#E74C3C', label='End node'),
        mpatches.Patch(color='#F39C12', label='Path node'),
        mpatches.Patch(color='#AED6F1', label='Other node'),
    ]
    ax.legend(handles=legend_handles, loc='upper left',
              framealpha=0.9, fontsize=9, edgecolor='#CCCCCC')

    ax.axis('off')
    plt.tight_layout()
    return fig

# Main Streamlit app
def main():
    st.title("Shortest Path Finder using Dijkstra's Algorithm")
    st.markdown("<div style='text-align: right; font-size: 12px;'>Delroy Pires | PA-3</div>",
                unsafe_allow_html=True)

    dataset_options = {
        "Dataset 1 - Varied Weights (Path via B→C→D)":  "graph2.xlsx",
        "Dataset 2 - Varied Weights (Path via B→C)":    "graph3.xlsx",
        "Dataset 3 - Varied Weights (Path via C)":      "graph4.xlsx",
        "Dataset 4 - Equal Weight Paths (Tie: 6 vs 6)": "graph5.xlsx",
    }
    selected_dataset = st.selectbox("Select Dataset", options=dataset_options.keys())

    G = load_graph_from_excel(dataset_options[selected_dataset])
    nodes = list(G.nodes)

    start_node = st.selectbox("Select Start Node", nodes)
    end_node   = st.selectbox("Select End Node",   nodes)

    if st.button("Find Shortest Path"):
        try:
            shortest_path = nx.dijkstra_path(G, start_node, end_node, weight='weight')
            path_length   = nx.dijkstra_path_length(G, start_node, end_node, weight='weight')

            st.success(f"Shortest Distance: {path_length}")
            st.write("Path:", " → ".join(str(n) for n in shortest_path))
            fig = generate_graph_visualization(G, shortest_path)

        except nx.NetworkXNoPath:
            st.error("No path found between the selected nodes.")
            fig = generate_graph_visualization(G)

        st.pyplot(fig)


if __name__ == "__main__":
    main()