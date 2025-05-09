#!/usr/bin/env python3
import networkx as nx
import matplotlib.pyplot as plt

def annotate_graph(G, title):
    degrees = dict(G.degree())  # Degree of each node
    diameter = nx.diameter(G) if nx.is_connected(G) else "Infinite"
    fault_tolerance = nx.node_connectivity(G) if nx.is_connected(G) else 0
    
    print(f"Topology: {title}")
    print(f"Node Degrees: {degrees}")
    print(f"Diameter: {diameter}")
    print(f"Fault Tolerance: {fault_tolerance}")
    
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10)
    plt.title(f"{title}\nDiameter: {diameter}, Fault Tolerance: {fault_tolerance}")
    plt.savefig(f"outputs/{title.lower().replace(' ', '_')}.png")
    plt.close()

# Linear Topology (4 hosts, 4 switches)
G_linear = nx.Graph()
G_linear.add_nodes_from(['h1', 'h2', 'h3', 'h4', 's1', 's2', 's3', 's4'])
G_linear.add_edges_from([('h1', 's1'), ('s1', 's2'), ('s2', 'h2'), ('s2', 's3'), ('s3', 'h3'), ('s3', 's4'), ('s4', 'h4')])
annotate_graph(G_linear, "Linear Topology")

# Minimal Topology (2 hosts, 1 switch)
G_minimal = nx.Graph()
G_minimal.add_nodes_from(['h1', 'h2', 's1'])
G_minimal.add_edges_from([('h1', 's1'), ('h2', 's1')])
annotate_graph(G_minimal, "Minimal Topology")

# Tree Topology (4 hosts, 4 switches, binary tree)
G_tree = nx.Graph()
G_tree.add_nodes_from(['h1', 'h2', 'h3', 'h4', 's1', 's2', 's3', 's4'])
G_tree.add_edges_from([('s1', 's2'), ('s1', 's3'), ('s2', 's4'), ('s2', 'h1'), ('s3', 'h2'), ('s4', 'h3'), ('s4', 'h4')])
annotate_graph(G_tree, "Tree Topology")

# Torus Topology (2x2 grid, 4 switches, 4 hosts)
G_torus = nx.Graph()
G_torus.add_nodes_from(['h1', 'h2', 'h3', 'h4', 's1', 's2', 's3', 's4'])
G_torus.add_edges_from([
    ('s1', 's2'), ('s2', 's3'), ('s3', 's4'), ('s4', 's1'),  # Horizontal/vertical connections
    ('s1', 'h1'), ('s2', 'h2'), ('s3', 'h3'), ('s4', 'h4')    # Host connections
])
annotate_graph(G_torus, "Torus Topology")

# Full Topology (4 switches, 4 hosts)
G_full = nx.Graph()
G_full.add_nodes_from(['h1', 'h2', 'h3', 'h4', 's1', 's2', 's3', 's4'])
G_full.add_edges_from([
    ('s1', 's2'), ('s1', 's3'), ('s1', 's4'), ('s2', 's3'), ('s2', 's4'), ('s3', 's4'),  # Full switch connections
    ('s1', 'h1'), ('s2', 'h2'), ('s3', 'h3'), ('s4', 'h4')                             # Host connections
])
annotate_graph(G_full, "Full Topology")
