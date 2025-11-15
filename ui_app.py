import importlib.metadata as _im

if not hasattr(_im, "packages_distributions"):
    def _dummy_packages_distributions():
        return {}
    _im.packages_distributions = _dummy_packages_distributions

import asyncio
import random
from typing import List, Dict, Any

import streamlit as st
import pandas as pd

from main_demo import AgentRuntime
from memory.memory_service import get_memory_service


# ---------- Async event loop helper (persistent) ----------

def get_event_loop() -> asyncio.AbstractEventLoop:
    if "loop" not in st.session_state:
        st.session_state.loop = asyncio.new_event_loop()
    return st.session_state.loop


# ---------- Session + runtime helpers ----------

def init_runtime() -> AgentRuntime:
    if "runtime" not in st.session_state:
        st.session_state.runtime = AgentRuntime()
    return st.session_state.runtime


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = []
    if "last_emissions" not in st.session_state:
        st.session_state.last_emissions: Dict[str, Any] = {}
    if "session_id" not in st.session_state:
        st.session_state.session_id = "ui_session_1"

    # Random vibrant eco / galaxy style background per session
    if "bg_style" not in st.session_state:
        backgrounds = [
            # Galaxy
            "linear-gradient(135deg, rgba(0,0,0,0.75), rgba(25,0,51,0.85)), "
            "url('https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=1600&q=80')",
            # Forest
            "linear-gradient(135deg, rgba(0,40,0,0.75), rgba(0,90,60,0.85)), "
            "url('https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=80')",
            # Waterfall
            "linear-gradient(135deg, rgba(0,40,70,0.75), rgba(0,100,120,0.85)), "
            "url('https://images.unsplash.com/photo-1500534314211-0a24cd01c60e?auto=format&fit=crop&w=1600&q=80')",
            # Sunrise mountains
            "linear-gradient(135deg, rgba(20,0,40,0.8), rgba(0,80,60,0.8)), "
            "url('https://images.unsplash.com/photo-1444090542259-0af8fa96557e?auto=format&fit=crop&w=1600&q=80')",
            # Ocean
            "linear-gradient(135deg, rgba(0,30,60,0.8), rgba(0,120,120,0.85)), "
            "url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80')",
        ]
        st.session_state.bg_style = random.choice(backgrounds)


async def handle_user_message_async(runtime: AgentRuntime, text: str) -> str:
    """
    Async handler that calls the orchestrator and updates memory-based emissions.
    """
    session_id = st.session_state.session_id
    reply = await runtime.handle_user(session_id, text)

    mem = get_memory_service()
    history = await mem.get_history(session_id)
    if history:
        st.session_state.last_emissions = history[-1]

    return reply


def handle_user_message(runtime: AgentRuntime, text: str) -> str:
    loop = get_event_loop()
    return loop.run_until_complete(handle_user_message_async(runtime, text))


def fetch_history() -> List[Dict[str, Any]]:
    mem = get_memory_service()
    session_id = st.session_state.session_id
    loop = get_event_loop()
    history = loop.run_until_complete(mem.get_history(session_id))
    return history or []


# ---------- UI rendering helpers ----------

def render_emissions_summary(emissions: Dict[str, Any]):
    st.markdown("### 🌱 Latest Snapshot")

    if not emissions:
        st.info(
            "No emissions calculated yet.\n\n"
            "Try something like:\n\n"
            "“Last month I took 3 domestic flights, drove 200 km and used 150 kWh of electricity. "
            "I eat meat 3 times a week. Estimate my footprint and tell me where I should focus on reducing it.”"
        )
        return

    total = emissions.get("total", 0.0)
    by_cat = emissions.get("by_category", {})

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total emissions", f"{total:.2f} kg CO₂e")
    with col2:
        if by_cat:
            top_cat = max(by_cat, key=by_cat.get)
            st.metric(
                "Top contributor",
                f"{top_cat.capitalize()}",
                f"{by_cat[top_cat]:.1f} kg",
            )
        else:
            st.metric("Top contributor", "—", "0.0 kg")
    with col3:
        runs = len(fetch_history())
        st.metric("Recorded runs", str(runs))

    if by_cat:
        st.markdown("#### Category breakdown")
        df = pd.DataFrame(
            [{"Category": k.capitalize(), "Emissions (kg CO₂e)": v}
             for k, v in by_cat.items()]
        )
        st.bar_chart(df.set_index("Category"))


def render_history_and_trends():
    st.markdown("### 📈 Trends & Insights")

    history = fetch_history()
    if not history:
        st.info("No history yet. Ask about your footprint at least once to build trends.")
        return

    rows = []
    for i, rec in enumerate(history, start=1):
        total = rec.get("total", 0.0)
        by_cat = rec.get("by_category", {})
        rows.append(
            {
                "Run": i,
                "Total": total,
                "Travel": by_cat.get("travel", 0.0),
                "Electricity": by_cat.get("electricity", 0.0),
                "Food": by_cat.get("food", 0.0),
            }
        )

    df = pd.DataFrame(rows).set_index("Run")

    # High-level total trend
    st.markdown("#### 🔍 Total emissions over time")
    st.line_chart(df[["Total"]])

    # Category trends
    st.markdown("#### 📊 Category trends")
    st.line_chart(df[["Travel", "Electricity", "Food"]])

    # Interactive run inspector
    st.markdown("#### 🔎 Inspect a specific run")
    selected_run = st.slider("Select run", min_value=1, max_value=len(df), value=len(df))
    selected_row = df.loc[selected_run]

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Run #{selected_run} – details**")
        st.write(f"- Total: `{selected_row['Total']:.2f}` kg CO₂e")
        st.write(f"- Travel: `{selected_row['Travel']:.2f}` kg")
        st.write(f"- Electricity: `{selected_row['Electricity']:.2f}` kg")
        st.write(f"- Food: `{selected_row['Food']:.2f}` kg")

    with col2:
        bar_df = pd.DataFrame(
            {
                "Category": ["Travel", "Electricity", "Food"],
                "Emissions (kg CO₂e)": [
                    selected_row["Travel"],
                    selected_row["Electricity"],
                    selected_row["Food"],
                ],
            }
        ).set_index("Category")
        st.bar_chart(bar_df)

    st.markdown("#### Raw data")
    st.dataframe(df.style.format("{:.2f}"), width="stretch")


def render_about_tab():
    st.markdown("### ℹ️ About EcoGuardian")
    st.markdown(
        """
**EcoGuardian** is a multi-agent sustainability assistant

It uses:

- 🧠 Gemini-powered agents
- 🧩 Specialized agents for data extraction, carbon calculation, and progress tracking
- ⚙️ Custom tools for emissions factors and product alternatives
- 🧵 Memory to track your runs over time
- 📈 Evaluation + observability hooks 

Use this UI to:
- Chat about your lifestyle and get a carbon estimate
- See your emission history as charts and tables
- Understand which category contributes the most
"""
    )


def render_scenarios(runtime: AgentRuntime):
    st.markdown("### ⚡ Quick Scenarios")

    scenarios = {
        "Frequent flyer ✈️": (
            "In the last month I took 5 international flights, 2 domestic flights, "
            "drove 100 km, and used 200 kWh of electricity. I eat meat almost every day. "
            "Estimate my footprint and tell me the top 3 things I should change."
        ),
        "Remote worker 🧑‍💻": (
            "I work fully remote, no flights this year, but I use AC heavily and my "
            "electricity usage is around 400 kWh per month. I eat mostly vegetarian food "
            "with meat once a week. Estimate my footprint and suggest improvements."
        ),
        "Student on a budget 🎓": (
            "I rarely travel, maybe one train trip a month and no flights. I share a flat "
            "with roommates, electricity is moderate, and I eat meat 2–3 times a week. "
            "Estimate my footprint and tell me low-cost changes I can make."
        ),
    }

    cols = st.columns(len(scenarios))
    for (label, prompt), col in zip(scenarios.items(), cols):
        if col.button(label):
            # simulate a user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking about this scenario 🌱..."):
                    reply = handle_user_message(runtime, prompt)
                    st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})


# ---------- Streamlit App ----------

def main():
    st.set_page_config(
        page_title="EcoGuardian – Sustainability Assistant",
        page_icon="🌍",
        layout="wide",
    )

    init_session_state()
    runtime = init_runtime()

    # Custom styling – random image background per session
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: {st.session_state.bg_style};
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            background-color: rgba(255, 255, 255, 0.88);
            border-radius: 18px;
            margin-top: 1rem;
            margin-bottom: 2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar: brand + quick info
    with st.sidebar:
        st.markdown("## 🌍 EcoGuardian")
        st.caption("Your multi-agent sustainability copilot.")
        st.markdown("### 💡 How to use")
        st.markdown(
            "- Describe your month in natural language\n"
            "- Mention flights, driving, electricity, and food\n"
            "- Ask where to focus to reduce emissions\n"
            "- Reuse it monthly to see trends 📈"
        )
        st.markdown("---")
        st.markdown("### 📌 Session")
        st.text(f"Session ID: {st.session_state.session_id}")
        if st.button("Clear conversation"):
            st.session_state.messages = []
            st.session_state.last_emissions = {}
            st.success("Conversation and snapshot cleared. Start fresh ✨")

    st.markdown("# EcoGuardian")
    st.caption("Estimate your carbon footprint, see trends, and get practical reduction advice.")

    # Tabs: Chat / Trends / About
    tab_chat, tab_trends, tab_about = st.tabs(["💬 Chat", "📈 Trends & Insights", "ℹ️ About"])

    # ----- CHAT TAB -----
    with tab_chat:
        col_chat, col_side = st.columns([2, 1])

        with col_chat:
            if not st.session_state.messages:
                st.chat_message("assistant").markdown(
                    "Hi, I’m **EcoGuardian** 🌍.\n\n"
                    "Tell me about your recent activities (flights, driving, electricity, food), "
                    "and I’ll estimate your carbon footprint and suggest where to cut emissions. "
                    "You can also say things like:\n\n"
                    "- *“Compare this month vs last month.”*\n"
                    "- *“What small changes give the biggest impact?”*"
                )

            # Existing chat history
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Chat input
            user_input = st.chat_input(
                "Describe your activities or ask a question about your footprint..."
            )

            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant"):
                    with st.spinner("Calculating and analysing your footprint 🌱..."):
                        reply = handle_user_message(runtime, user_input)
                        st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            st.markdown(
                """
                <script>
                window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"});
                </script>
                """,
                unsafe_allow_html=True,
            )

        with col_side:
            render_emissions_summary(st.session_state.last_emissions)
            st.markdown("---")
            render_scenarios(runtime)

    # ----- TRENDS TAB -----
    with tab_trends:
        render_history_and_trends()

    # ----- ABOUT TAB -----
    with tab_about:
        render_about_tab()


if __name__ == "__main__":
    main()
