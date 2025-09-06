import subprocess
import sys
import os

def main():
    print("🚀 Starting Smart Search Platform...")
    
    # Change to reflex_app directory
    original_dir = os.getcwd()
    os.chdir(os.path.join(original_dir, "reflex_app"))
    
    # Initialize Reflex app if needed
    if not os.path.exists(".web"):
        print("Initializing Reflex app...")
        subprocess.run([sys.executable, "-m", "reflex", "init"], check=True)
    
    # Change back to original directory
    os.chdir(original_dir)
    
    # Start FastAPI in background
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--port", "8000"]
    )
    
    # Start Reflex app
    reflex_process = subprocess.Popen(
        [sys.executable, "-m", "reflex", "run", "--frontend-only"],
        cwd="reflex_app"
    )
    
    print("\n✅ Smart Search is running!")
    print("🌐 API: http://localhost:8000")
    print("🎨 UI: http://localhost:3000")
    print("\nPress Ctrl+C to stop")
    
    try:
        reflex_process.wait()
    except KeyboardInterrupt:
        api_process.terminate()
        reflex_process.terminate()
        print("\n👋 Shutting down...")

if __name__ == "__main__":
    main()