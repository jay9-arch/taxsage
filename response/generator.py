from classifier.query_classifier import classify
from extraction.extractor import extract_profile
from engine.tax_rules import compute_tax
from rag.generator import answer_question
from audit.trace_graph import build_audit_graph, print_trace, citations_used

def handle_query(user_message, preferred_regime="old"):
    label = classify(user_message)
    result = {"query": user_message, "classification": label}

    rag_result = None
    tax_result = None
    audit_graph = None

    if label in ("rag", "both"):
        rag_result = answer_question(user_message)
        result["explanation"] = rag_result["answer"]

    if label in ("compute", "both"):
        profile = extract_profile(user_message)
        if "error" in profile:
            result["computation_error"] = profile["error"]
        else:
            old_facts, old_trace, new_facts, new_trace = compute_tax(profile)
            chosen_trace = old_trace if preferred_regime == "old" else new_trace
            chosen_facts = old_facts if preferred_regime == "old" else new_facts
            final_key = "final_tax_old" if preferred_regime == "old" else "final_tax_new"

            result["extracted_profile"] = profile
            result["old_regime_tax"] = old_facts["final_tax_old"]
            result["new_regime_tax"] = new_facts["final_tax_new"]

            audit_graph = build_audit_graph(
                initial_facts=profile,
                rule_trace=chosen_trace,
                terminal_facts=[final_key],
                rag_sources=rag_result["sources"] if rag_result else None,
                answer_label=f"Answer to: {user_message[:50]}",
            )

    if audit_graph is None and rag_result is not None:
        audit_graph = build_audit_graph(
            initial_facts={},
            rule_trace=None,
            terminal_facts=None,
            rag_sources=rag_result["sources"],
            answer_label=f"Answer to: {user_message[:50]}",
        )

    result["audit_graph"] = audit_graph
    return result


def print_full_answer(result):
    print(f"Query: {result['query']}")
    print(f"Routed as: {result['classification']}\n")
    if "explanation" in result:
        print("Explanation:", result["explanation"], "\n")
    if "old_regime_tax" in result:
        print(f"Old Regime tax: Rs. {result['old_regime_tax']:,}")
        print(f"New Regime tax: Rs. {result['new_regime_tax']:,}\n")
    if result.get("audit_graph") is not None:
        print("Reasoning trace:")
        print_trace(result["audit_graph"])
        print("\nStatutory citations used:", citations_used(result["audit_graph"]))
