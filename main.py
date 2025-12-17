import threading
from ws.binance_ws import start_ws
import streamlit.web.cli as stcli
import sys

# ------------------------
# Start WebSocket in background
# ------------------------
ws_thread = threading.Thread(target=start_ws, daemon=True)
ws_thread.start()
print("WebSocket started in background...")

# ------------------------
# Launch Streamlit app
# ------------------------
sys.argv = ["streamlit", "run", "app.py"]
stcli.main()
