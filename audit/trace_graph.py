import networkx as nx

def build_audit_graph(answer_label="Final Answer", rule_trace=None, rag_sources=None):
    G = nx.DiGraph()
    G.add_node("root", label=answer_label, citation=None, kind="root")

    if rule_trace:
        prev_node = "root"
        for i, step in enumerate(rule_trace):
            node_id = f"rule_{i}_{step['derived_fact']}"
            G.add_node(node_id, label=f"{step['derived_fact']} = {step['value']}",
                        citation=step['citation'], kind="computation")
            G.add_edge(prev_node, node_id, relation=step['rule'])
            prev_node = node_id  # chain reflects derivation order

    if rag_sources:
        for i, src in enumerate(rag_sources):
            node_id = f"rag_{i}_{src['citation'].replace(' ', '_')}"
            G.add_node(node_id, label=f"Retrieved: {src['citation']}",
                        citation=src['citation'], kind="retrieval",
                        score=src.get('score'))
            G.add_edge("root", node_id, relation="supported_by")

    return G


def print_trace(G, node="root", depth=0, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return
    visited.add(node)
    data = G.nodes[node]
    indent = "  " * depth
    if node == "root":
        print(f"{indent}{data['label']}")
    else:
        cite = f" [{data['citation']}]" if data.get('citation') else ""
        print(f"{indent}\u2514\u2500 {data['label']}{cite}")
    for _, child in G.out_edges(node):
        print_trace(G, child, depth + 1, visited)


def citations_used(G):
    """Return the set of unique statutory citations referenced in this proof tree."""
    cites = set()
    for node, data in G.nodes(data=True):
        if data.get("citation"):
            cites.add(data["citation"])
    return cites
