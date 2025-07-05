import subprocess
import subprocess
import sys
import os

def run_dev_server():
    # First, ensure dependencies are installed and venv is created
    print("Ensuring dependencies are installed and virtual environment is set up...")
    try:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'install_dependencies.py')], check=True)
    except subprocess.CalledProcessError:
        print("Dependency installation or virtual environment setup failed. Please fix the issues and try again.")
        sys.exit(1)

    # Determine the virtual environment's Python executable
    venv_dir = ".venv"
    if sys.platform == "win32":
        python_executable = os.path.join(os.getcwd(), venv_dir, "Scripts", "python.exe")
    else:
        python_executable = os.path.join(os.getcwd(), venv_dir, "bin", "python")

    if not os.path.exists(python_executable):
        print(f"Error: Virtual environment Python executable not found at {python_executable}")
        print("Please ensure install_dependencies.py ran successfully.")
        sys.exit(1)

    # Command to run the FastAPI application using the venv's python
    command = [python_executable, "main.py"]

    print(f"Starting development server with command: {' '.join(command)}")
    try:
        # Use the venv's python to run main.py
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting development server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_dev_server()