#!/bin/bash
set -e

# This script sets up the 'uv' package manager.
# It checks if 'uv' is already installed and installs it if not.

# Define installation URLs for uv
UV_LINUX_DARWIN_INSTALL_URL="https://astral.sh/uv/install.sh"
UV_WINDOWS_INSTALL_URL="https://astral.sh/uv/install.ps1"

# Function to check if 'uv' is installed
# Returns 0 if installed, 1 otherwise
check_uv_installed() {
  if command -v uv &> /dev/null
  then
    echo "uv is already installed."
    return 0
  else
    return 1
  fi
}

# Function to install uv based on the operating system
install_uv() {
  echo "Attempting to install uv..."
  os_name=$(uname)
  # Use curl/sh for Unix-like systems and Git Bash/MSYS/Cygwin on Windows
  if [[ "$os_name" == "Darwin" || "$os_name" == "Linux" || "$os_name" == MINGW* || "$os_name" == CYGWIN* || "$os_name" == MSYS* ]]; then
    curl -LsSf "${UV_LINUX_DARWIN_INSTALL_URL}" | sh || { echo "Error: Failed to install uv on Unix-like system or Bash for Windows."; exit 1; }
  # Use PowerShell for native Windows environments
  elif [[ "$(uname -s)" == *NT* ]]; then
    powershell -ExecutionPolicy ByPass -c "irm ${UV_WINDOWS_INSTALL_URL} | iex" || { echo "Error: Failed to install uv on Windows."; exit 1; }
  else
    echo "Unsupported operating system. Please install uv manually." >&2
    exit 1
  fi
  echo "uv installation script finished."
  source "$HOME/.local/bin/env"
}

# Main script logic
if check_uv_installed; then
  echo "Skipping uv setup."
else
  install_uv

  # For non-PowerShell installs, try to source the env script to update the current session's PATH
  os_name=$(uname)
   if [[ "$os_name" != *NT* || "$os_name" == MINGW* || "$os_name" == CYGWIN* || "$os_name" == MSYS* ]]; then
    UV_ENV_SCRIPT="$HOME/.local/bin/env"
    if [ -f "$UV_ENV_SCRIPT" ]; then
      echo "Sourcing environment to update PATH for current session..."
      # shellcheck source=/dev/null
      source "$UV_ENV_SCRIPT"
    else
        echo "Could not find env script to source. You may need to restart your shell."
    fi
  fi

  # Final check to see if uv is now available.
  if check_uv_installed; then
    echo "uv is now configured and ready to use."
  else
    echo "uv was installed, but is not available in the PATH."
    echo "Please restart your terminal or manually add '$HOME/.local/bin' to your PATH."
  fi
fi
