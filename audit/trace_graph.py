import networkx as nx

def _is_statutory(citation):
    return bool(citation) and citation.lower().startswith("section")

def build_audit_graph(initial_facts, rule_trace=None, terminal_facts=None,
                       rag_sources=None, answer_label="Final Answer"):
    G = nx.DiGraph()
    G.add_node("root", label=answer_label, citation=None, kind="root", is_statutory=False)

    derived = {step["derived_fact"]: step for step in (rule_trace or [])}

    def ensure_input_node(fact_name):
        node_id = f"input::{fact_name}"
        if node_id not in G:
            value = initial_facts.get(fact_name, "?")
            G.add_node(node_id, label=f"{fact_name} = {value}", citation=None,
                       kind="input", is_statutory=False)
        return node_id

    def ensure_fact_node(fact_name):
        node_id = f"fact::{fact_name}"
        if node_id in G:
            return node_id
        if fact_name in derived:
            step = derived[fact_name]
            G.add_node(node_id, label=f"{fact_name} = {step['value']}",
                       citation=step["citation"], kind="computation",
                       is_statutory=_is_statutory(step["citation"]))
            for dep in step.get("depends_on", []):
                dep_node = ensure_fact_node(dep) if dep in derived else ensure_input_node(dep)
                G.add_edge(node_id, dep_node, relation=step["rule"])
            return node_id
        return ensure_input_node(fact_name)

    if terminal_facts:
        for tf in terminal_facts:
            node_id = ensure_fact_node(tf)
            G.add_edge("root", node_id, relation="concludes")

    if rag_sources:
        for i, src in enumerate(rag_sources):
            node_id = f"rag_{i}_{src['citation'].replace(' ', '_')}"
            G.add_node(node_id, label=f"Retrieved: {src['citation']}",
                       citation=src["citation"], kind="retrieval",
                       is_statutory=_is_statutory(src["citation"]), score=src.get("score"))
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
        cite = f" [{data['citation']}]" if data.get("citation") else ""
        print(f"{indent}\u2514\u2500 {data['label']}{cite}")
    for _, child in G.out_edges(node):
        print_trace(G, child, depth + 1, visited)


def citations_used(G, statutory_only=True):
    cites = set()
    for _, data in G.nodes(data=True):
        if data.get("citation") and (not statutory_only or data.get("is_statutory")):
            cites.add(data["citation"])
    return cites
