import subprocess
import sys

def main():
    print("🚀 Starting Smart Search Platform...")
    
    # Start FastAPI in background
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--port", "8000"]
    )
    
    # Start Streamlit
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "api/app.py"]
    )
    
    print("\n✅ Smart Search is running!")
    print("🌐 API: http://localhost:8000")
    print("🎨 UI: http://localhost:8501")
    print("\nPress Ctrl+C to stop")
    
    try:
        streamlit_process.wait()
    except KeyboardInterrupt:
        api_process.terminate()
        streamlit_process.terminate()
        print("\n👋 Shutting down...")

if __name__ == "__main__":
    main()