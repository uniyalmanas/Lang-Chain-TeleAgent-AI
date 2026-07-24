import os
import sys
import subprocess

def main():
    print("==========================================================")
    print(" Deutsche Telekom Digital Labs - TeleAgent AI Platform ")
    print("==========================================================")

    # Check for .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        print("[WARNING] .env file not found!")
        print("Creating .env from template...")
        with open(env_path, "w") as f:
            f.write("GROQ_API_KEY=your_groq_api_key_here\nGEMINI_API_KEY=your_gemini_api_key_here\n")
        print("[INFO] Please open .env and add your GROQ_API_KEY or GEMINI_API_KEY.")

    print("[INFO] Launching FastAPI Server & Multi-Agent Web UI at http://localhost:8000 ...")
    
    # Launch uvicorn
    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
