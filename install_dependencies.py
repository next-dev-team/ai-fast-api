import subprocess
import subprocess
import sys
import os

def ensure_global_uv_installed():
    try:
        # Check if uv is already installed globally
        subprocess.run([sys.executable, '-m', 'uv', '--version'], check=True, capture_output=True)
        print("uv is already installed globally.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("uv not found globally. Attempting to install uv globally...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'uv'], check=True)
            print("uv installed successfully globally.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing uv globally: {e}")
            print("Please ensure pip is installed and in your PATH, or install uv manually.")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: 'pip' command not found. Please ensure Python and pip are installed and in your PATH.")
            sys.exit(1)

# Determine the virtual environment directory name based on OS
if sys.platform == "win32":
    VENV_DIR = ".venv"
else:
    VENV_DIR = ".venv" # For Linux/macOS, it's typically .venv as well

def create_and_activate_venv():
    venv_path = os.path.join(os.getcwd(), VENV_DIR)
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment in {VENV_DIR}...")
        try:
            subprocess.run([sys.executable, '-m', 'uv', 'venv', VENV_DIR], check=True)
            print("Virtual environment created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: 'uv' command not found. Please ensure uv is installed and in your PATH.")
            print("You can install uv using: pip install uv")
            sys.exit(1)
    else:
        print(f"Virtual environment already exists in {VENV_DIR}.")

    # Activate the virtual environment
    if sys.platform == "win32":
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
        # For Windows, activation is typically done in the shell, not directly via subprocess for persistent activation.
        # We'll rely on the dev_start.py to activate it, but for install, we need to ensure uv uses the venv's python.
        # The 'uv pip install' command automatically uses the venv's python if run from within the venv or if the venv is active.
        # For this script, we'll ensure uv is called with the venv's python.
        python_executable = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        activate_script = os.path.join(venv_path, "bin", "activate")
        python_executable = os.path.join(venv_path, "bin", "python")



    return python_executable

def install_dependencies():
    venv_python = create_and_activate_venv()
    try:
        print("Installing dependencies using uv...")
        # Use the venv's python to run uv pip install
        subprocess.run(['uv', 'pip', 'install', '-r', 'requirements.txt', '--python', venv_python], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Please ensure uv is installed and in your PATH.")
        print("You can install uv using: pip install uv")
        sys.exit(1)

if __name__ == "__main__":
    ensure_global_uv_installed()
    install_dependencies()