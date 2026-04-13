import os
import subprocess

# 🔥 PATH TO YOUR REACT APP
BASE_PROJECT_PATH = os.path.join("..", "projects", "live_app")


# 🔥 RUN COMMAND HELPER
def run_command(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result
    except Exception as e:
        return str(e)


# 🔥 RUN REACT APP (LOCAL ONLY)
def run_app():
    """
    Starts Vite dev server locally
    """
    try:
        subprocess.Popen(
            "npm run dev",
            cwd=BASE_PROJECT_PATH,
            shell=True
        )
    except Exception as e:
        return str(e)

    return "http://localhost:5173"


# 🔥 INSTALL DEPENDENCIES (OPTIONAL HELPER)
def install_base_dependencies():
    """
    Runs npm install if node_modules missing
    """
    node_modules_path = os.path.join(BASE_PROJECT_PATH, "node_modules")

    if not os.path.exists(node_modules_path):
        run_command("npm install", cwd=BASE_PROJECT_PATH)