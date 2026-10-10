import streamlit as st
from response.generator import handle_query
from audit.trace_graph import print_trace, citations_used
import io
import contextlib

st.set_page_config(page_title="TaxSage", page_icon="\U0001F4B0")
st.title("\U0001F4B0 TaxSage")
st.caption("Ask about Indian personal income tax eligibility or get your tax computed, with every figure traced to its statutory clause.")

if "history" not in st.session_state:
    st.session_state.history = []


def render_assistant_turn(result, key_prefix):
    if "explanation" in result:
        st.write(result["explanation"])

    if "old_regime_tax" in result:
        col1, col2 = st.columns(2)
        col1.metric("Old Regime Tax", f"\u20b9{result['old_regime_tax']:,}")
        col2.metric("New Regime Tax", f"\u20b9{result['new_regime_tax']:,}")

    if "computation_error" in result:
        st.warning(f"Couldn't extract a complete profile: {result['computation_error']}")

    if result.get("audit_graph") is not None:
        with st.expander("\U0001F50E Show reasoning trace (proof tree)", key=f"{key_prefix}_expander"):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                print_trace(result["audit_graph"])
            st.code(buf.getvalue(), language=None)

            cites = citations_used(result["audit_graph"])
            if cites:
                st.caption("Statutory citations used: " + ", ".join(sorted(cites)))

    st.caption(f"Routed as: **{result['classification']}**")


# Replay full history, each with its own working expander
for i, entry in enumerate(st.session_state.history):
    with st.chat_message("user"):
        st.write(entry["query"])
    with st.chat_message("assistant"):
        render_assistant_turn(entry["result"], key_prefix=f"history_{i}")

user_input = st.chat_input("Ask about your taxes, e.g. 'Can I claim HRA if I live with my parents?'")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = handle_query(user_input)
        render_assistant_turn(result, key_prefix=f"live_{len(st.session_state.history)}")

    st.session_state.history.append({"query": user_input, "result": result})
