import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random

# Dummy session list
DUMMY_SESSIONS = ["MATLAB_1234", "MATLAB_5678", "MATLAB_XYZ"]

# Fake shared state
app_state = {
    "connected": False,
    "session": None
}

def search_sessions():
    """Mock function that pretends to find shared MATLAB sessions."""
    time.sleep(1)  # Simulate delay
    return DUMMY_SESSIONS.copy()

def connect_to_session(session_name):
    """Mock connect logic."""
    print(f"[DEBUG] Connecting to session: {session_name}")
    time.sleep(1)
    app_state["connected"] = True
    app_state["session"] = session_name

def monitor_connection(label):
    """Mock monitor that randomly disconnects after a few seconds."""
    time.sleep(random.randint(5, 10))  # Random disconnect time
    if app_state["connected"]:
        app_state["connected"] = False
        label.config(text="Status: 🔴 Disconnected")
        messagebox.showwarning("Connection Lost", "MATLAB engine disconnected. Please reconnect.")

def start_monitor_thread(label):
    thread = threading.Thread(target=monitor_connection, args=(label,), daemon=True)
    thread.start()

def build_gui():
    root = tk.Tk()
    root.title("MATLAB MCP Launcher")
    root.geometry("400x300")

    status_label = tk.Label(root, text="Status: ⚪ Waiting", font=("Arial", 12))
    status_label.pack(pady=10)

    instruction = tk.Label(root, text="Please share your MATLAB session first.\nThen click 'Check for Sessions'", wraplength=300)
    instruction.pack()

    combo_label = tk.Label(root, text="Available Sessions:")
    combo_label.pack(pady=(20, 0))
    session_combo = ttk.Combobox(root, state="readonly", width=30)
    session_combo.pack()

    def on_check():
        sessions = search_sessions()
        if sessions:
            session_combo['values'] = sessions
            session_combo.current(0)
        else:
            messagebox.showinfo("No Sessions", "No shared MATLAB sessions found.")

    def on_proceed():
        selected = session_combo.get()
        if not selected:
            messagebox.showerror("No Selection", "Please select a session.")
            return
        connect_to_session(selected)
        status_label.config(text="Status: 🟢 Connected")
        start_monitor_thread(status_label)

    def on_quit():
        if app_state["connected"]:
            confirm = messagebox.askyesno("Confirm Quit", "The server is running. Quit anyway?")
            if not confirm:
                return
        root.quit()

    tk.Button(root, text="🔄 Check for Sessions", command=on_check).pack(pady=10)
    tk.Button(root, text="▶️ Proceed", command=on_proceed).pack(pady=5)
    tk.Button(root, text="❌ Quit", command=on_quit).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    build_gui()
