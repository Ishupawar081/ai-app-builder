import streamlit as st
import os
from agent import create_downloadable_app

# 🔹 Configure Streamlit page
st.set_page_config(page_title="AI App Builder", layout="centered")

# 🔹 App title
st.title("🚀 AI App Builder (Agent Mode)")

# --- INIT STATE ---
# Stores generated plan
if "plan" not in st.session_state:
    st.session_state.plan = None

# Tracks whether app is built
if "app_built" not in st.session_state:
    st.session_state.app_built = False


# --- IMPORTS ---
# Import core modules of system
try:
    from planner import generate_plan          # Generates structured plan using LLM
    from agent import run_agent, update_app    # Builds + updates React app
    from builder import run_app                # Runs Vite dev server

    st.success("✅ Agent System Ready")

except Exception as e:
    st.error(f"❌ Import Failed: {e}")
    st.stop()


# --- EXAMPLE PROMPTS ---
# Helps user quickly test system
st.markdown("### 💡 Try these ideas:")
st.code("""
- build a todo app with add and delete
- create a calculator with clear button
- make a notes app with title and content
- build a dashboard with tasks and notes
""")


# --- USER INPUT ---
# Text area where user describes app idea
user_input = st.text_area("Describe your app idea:")


# --- GENERATE PLAN ---
# Converts user input into structured JSON plan
if st.button("Generate Plan"):
    if not user_input.strip():
        st.warning("Please enter an app idea")
    else:
        with st.spinner("🧠 Generating plan..."):
            plan = generate_plan(user_input)

        # Save plan in session state
        st.session_state.plan = plan
        st.session_state.app_built = False


# --- DISPLAY PLAN ---
if st.session_state.plan:
    st.subheader("📋 Generated Plan")

    # Show plan JSON
    st.json(st.session_state.plan)

    # Create two columns (Build + Run buttons)
    col1, col2 = st.columns(2)


    # --- BUILD APP ---
    with col1:
        if st.button("🚀 Build App"):
            try:
                with st.spinner("🤖 Agent building..."):

                    # 🔥 Main agent pipeline
                    result = run_agent(st.session_state.plan)

                st.success(result)

                # Mark app as built
                st.session_state.app_built = True

            except Exception as e:
                st.error(f"❌ Build Failed: {e}")


    # --- RUN APP (MODIFIED FOR DEPLOYMENT) ---
    with col2:
        if st.button("▶️ Run App"):
            st.info("⚠️ Live app preview runs locally. Please download and run using npm install && npm run dev.")


    # --- MODIFY APP ---
    # Only visible after app is built
    if st.session_state.app_built:
        st.divider()
        st.subheader("✏️ Modify Your App")

        # Input for user modifications
        edit_prompt = st.text_input(
            "Describe changes (e.g., add delete button, improve UI)"
        )

        if st.button("Apply Changes"):
            if not edit_prompt.strip():
                st.warning("Please describe the change")
            else:
                try:
                    with st.spinner("🤖 Updating app..."):

                        # 🔥 Agent updates existing app
                        result = update_app(edit_prompt)

                    st.success(result)

                except Exception as e:
                    st.error(f"❌ Update Failed: {e}")


    # --- SHOW GENERATED CODE ---
    st.divider()
    st.subheader("📄 Generated Code")

    # Path to React App.jsx
    app_file = os.path.join("..", "projects", "live_app", "src", "App.jsx")

    if os.path.exists(app_file):
        try:
            # Read generated code
            with open(app_file, "r") as f:
                code = f.read()

            # Display code in UI
            st.code(code, language="jsx")

        except Exception as e:
            st.error(f"❌ Could not read code: {e}")
    else:
        st.info("No app generated yet")


# --- RESET SYSTEM ---
# Clears state and restarts app
st.divider()
if st.button("🔄 Reset"):
    st.session_state.plan = None
    st.session_state.app_built = False
    st.rerun()


if st.button("📦 Download App"):
    zip_file = create_downloadable_app()

    with open(zip_file, "rb") as f:
        st.download_button(
            label="⬇️ Download ZIP",
            data=f,
            file_name="react_app.zip",
            mime="application/zip"
        )