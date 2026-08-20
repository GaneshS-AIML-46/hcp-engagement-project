"""
Stop Backend Server Script
Terminates any process currently listening on port 8080 (or running AgentKF backend).
"""

import os
import sys
import subprocess


def stop_backend_server(port=8080):
    print(f"Stopping backend server on port {port}...")
    try:
        # Check process on port using netstat / PowerShell
        if sys.platform == "win32":
            cmd = f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"
            subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            print(f"[SUCCESS] Backend server on port {port} has been completely stopped.")
        else:
            cmd = f"fuser -k {port}/tcp"
            subprocess.run(cmd, shell=True, capture_output=True)
            print(f"[SUCCESS] Backend server on port {port} stopped.")
    except Exception as e:
        print(f"Error stopping server: {e}")


if __name__ == "__main__":
    stop_backend_server()
