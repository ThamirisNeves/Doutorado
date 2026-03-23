import os
import sys
import socket
import threading
import time
import webbrowser
from pathlib import Path

from streamlit import config as _config
from streamlit.web.bootstrap import run

os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"

def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def open_browser_once(url: str):
    time.sleep(2)
    webbrowser.open_new(url)


def main():
    
    app_path = resource_path("new_app_output.py")
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    _config.set_option("global.developmentMode", False)
    _config.set_option("server.headless", True)
    _config.set_option("server.port", port)
    _config.set_option("server.address", "127.0.0.1")
    _config.set_option("browser.gatherUsageStats", False)
    _config.set_option("server.enableCORS", False)
    _config.set_option("server.enableXsrfProtection", False)

    threading.Thread(target=open_browser_once, args=(url,), daemon=True).start()

    run(
        str(app_path),
        is_hello=False,
        args=[],
        flag_options={},
    )


if __name__ == "__main__":
    main()