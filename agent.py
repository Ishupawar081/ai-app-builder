from planner import generate_react_app, call_llm
import os
import subprocess
import shutil

# 🔥 PATHS
BASE_PROJECT_PATH = os.path.join("..", "projects", "live_app")
SRC_PATH = os.path.join(BASE_PROJECT_PATH, "src")
APP_FILE = os.path.join(SRC_PATH, "App.jsx")


# 🔥 RUN COMMAND
def run_cmd(cmd):
    return subprocess.run(
        cmd,
        cwd=BASE_PROJECT_PATH,
        shell=True,
        capture_output=True,
        text=True
    )


# 🔥 ENSURE BASE SETUP
def ensure_base_setup():
    if not os.path.exists(os.path.join(BASE_PROJECT_PATH, "node_modules")):
        print("📦 Installing base dependencies...")
        run_cmd("npm install")


# 🔥 INSTALL DEPENDENCIES
def install_dependencies(deps):
    for dep in deps:
        print(f"📦 Installing {dep}...")
        run_cmd(f"npm install {dep}")


# 🔥 DETECT DEPENDENCIES (SMART)
def detect_dependencies(code: str):
    deps = []

    mapping = {
        "react-router-dom": "react-router-dom",
        "BrowserRouter": "react-router-dom",
        "uuid": "uuid",
        "axios": "axios",
        "chart": "chart.js"
    }

    for key, pkg in mapping.items():
        if key in code:
            deps.append(pkg)

    return list(set(deps))


# 🔥 CLEAN CODE
def clean_code(code: str):
    if not code:
        return None

    code = code.replace("```jsx", "").replace("```", "")
    code = code.replace("\t", "  ")
    return code.strip()


# 🔥 VALIDATE CODE (STRONGER)
def is_valid(code: str):
    if not code:
        return False

    checks = [
        "function App",
        "return (",
        "export default"
    ]

    return all(c in code for c in checks)


# 🔥 BUILD CHECK
def has_build_error():
    result = run_cmd("npm run build")
    return result.returncode != 0, result.stderr


# 🔥 AUTO FIX
def auto_fix(code, error_logs=""):
    print("🛠️ Attempting auto-fix...")

    prompt = f"""
You are a senior React developer.

Fix the following React code.

STRICT:
- Fix syntax errors
- Fix invalid JSX
- Remove unsupported styles like &:focus
- Fix variable name typos
- Keep functionality same
- Return FULL corrected code

ERRORS:
{error_logs[:1500]}

CODE:
{code}
"""

    fixed = call_llm(prompt)
    return clean_code(fixed)


# 🔥 FALLBACK
def fallback_app():
    return """
import { useState } from 'react'

function App() {
  const [items, setItems] = useState([])
  const [input, setInput] = useState("")

  const addItem = () => {
    if (!input) return
    setItems([...items, input])
    setInput("")
  }

  return (
    <div style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      background: "#f1f5f9"
    }}>
      <div style={{
        background: "white",
        padding: 30,
        borderRadius: 10,
        width: 400,
        boxShadow: "0 4px 10px rgba(0,0,0,0.1)"
      }}>
        <h2>Fallback App</h2>

        <input
          value={input}
          onChange={(e)=>setInput(e.target.value)}
          style={{ width: "100%", padding: 10, marginBottom: 10 }}
        />

        <button
          onClick={addItem}
          style={{
            width: "100%",
            padding: 10,
            background: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: 6
          }}
        >
          Add
        </button>

        <ul>
          {items.map((item,i)=>(
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default App
"""


# 🔥 WRITE FILE
def write_app(code):
    os.makedirs(SRC_PATH, exist_ok=True)
    with open(APP_FILE, "w") as f:
        f.write(code)


# 🔥 MAIN AGENT (SELF-HEALING)
def run_agent(plan):
    print("🤖 Agent started")

    ensure_base_setup()

    # STEP 1: Generate
    code = generate_react_app(plan)
    code = clean_code(code)

    # STEP 2: Validate
    if not is_valid(code):
        print("⚠️ Invalid code → fallback")
        code = fallback_app()

    # STEP 3: Install deps
    deps = detect_dependencies(code)
    if deps:
        install_dependencies(deps)

    # STEP 4: Write initial
    write_app(code)

    # STEP 5: Build check + auto-fix loop
    for _ in range(2):  # retry max 2 times
        error, logs = has_build_error()

        if not error:
            print("✅ Build successful")
            break

        print("⚠️ Build failed → fixing...")
        code = auto_fix(code, logs)

        if not is_valid(code):
            print("❌ Auto-fix failed → fallback")
            code = fallback_app()
            break

        write_app(code)

    print("✅ App.jsx ready")
    return "🚀 App built (self-healing agent)"


# 🔥 EDIT FEATURE (WITH FIX LOOP)
def update_app(user_request):
    print("✏️ Updating app...")

    if not os.path.exists(APP_FILE):
        return "❌ No app found. Build first."

    with open(APP_FILE, "r") as f:
        current_code = f.read()

    prompt = f"""
Modify this React app.

STRICT:
- Keep existing functionality
- Improve or add requested feature
- Ensure valid JSX
- Return FULL code

REQUEST:
{user_request}

CODE:
{current_code}
"""

    updated = call_llm(prompt)
    updated = clean_code(updated)

    if not is_valid(updated):
        return "❌ Update failed"

    deps = detect_dependencies(updated)
    if deps:
        install_dependencies(deps)

    write_app(updated)

    # 🔥 Fix after update
    error, logs = has_build_error()
    if error:
        updated = auto_fix(updated, logs)
        write_app(updated)

    return "✅ App updated successfully 🚀"

def create_downloadable_app():
    print("📦 Creating downloadable app...")

    project_path = BASE_PROJECT_PATH
    zip_path = os.path.join(project_path, "react_app.zip")

    # remove old zip if exists
    if os.path.exists(zip_path):
        os.remove(zip_path)

    shutil.make_archive(
        base_name=zip_path.replace(".zip", ""),
        format="zip",
        root_dir=project_path
    )

    print("✅ ZIP ready:", zip_path)
    return zip_path