import subprocess
import time
import webview
import sys
import os

PORT = "8501"

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

app_path = os.path.join(base_dir, "streamlit_app.py")

if len(sys.argv) > 1 and sys.argv[1] == "RUN_STREAMLIT":
    import streamlit.web.cli as stcli
    sys.argv = [
        "streamlit", "run", app_path, 
        "--global.developmentMode", "false",
        "--server.headless", "true", 
        "--browser.gatherUsageStats", "false", 
        "--server.port", PORT
    ]
    sys.exit(stcli.main())

class Api:
    def exit_app(self):
        print("Exit command received from UI. Shutting down...")
        window.destroy()

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        cmd = [sys.executable, "RUN_STREAMLIT"]
    else:
        cmd = [sys.executable, __file__, "RUN_STREAMLIT"]

    server_process = subprocess.Popen(cmd)

    time.sleep(2)

    api = Api()
    window = webview.create_window("Random Dot App", f"http://localhost:{PORT}", fullscreen=True, js_api=api)
    webview.start()
    
    if server_process:
        server_process.terminate()
        server_process.wait()
    os._exit(0)