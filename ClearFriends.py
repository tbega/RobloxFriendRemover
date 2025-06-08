import sys
import subprocess

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    import tkinter as tk
    from tkinter import messagebox, scrolledtext
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
    import tkinter as tk
    from tkinter import messagebox, scrolledtext

import time

HEADERS = {}
CSRF_TOKEN = None

def get_csrf_token():
    global CSRF_TOKEN
    # Make a dummy POST to get the token
    resp = requests.post("https://friends.roblox.com/v1/users/1/unfriend", headers=HEADERS)
    token = resp.headers.get("x-csrf-token")
    if token:
        CSRF_TOKEN = token
        HEADERS["X-CSRF-TOKEN"] = CSRF_TOKEN

def start_unfriend(cookie):
    global HEADERS
    HEADERS = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.roblox.com/"
    }
    get_csrf_token()
    try:
        my_id = get_user_id()
        friends = get_friends(my_id)
        result_text.insert(tk.END, f"Found {len(friends)} friends.\n")
        for friend in friends:
            unfriend(friend["id"])
            result_text.insert(tk.END, f"Unfriended user {friend['id']}\n")
            result_text.see(tk.END)
            root.update()
            time.sleep(1)
        result_text.insert(tk.END, "Done!\n")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def get_user_id():
    resp = requests.get("https://users.roblox.com/v1/users/authenticated", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]

def get_friends(user_id):
    friends = []
    cursor = ""
    while True:
        url = f"https://friends.roblox.com/v1/users/{user_id}/friends"
        if cursor:
            url += f"?cursor={cursor}"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        friends.extend(data["data"])
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return friends

def unfriend(user_id):
    url = f"https://friends.roblox.com/v1/users/{user_id}/unfriend"
    resp = requests.post(url, headers=HEADERS)
    if resp.status_code == 403 and "x-csrf-token" in resp.headers:
        # Token expired, refresh and retry
        HEADERS["X-CSRF-TOKEN"] = resp.headers["x-csrf-token"]
        resp = requests.post(url, headers=HEADERS)
    if resp.status_code == 200:
        pass
    else:
        result_text.insert(tk.END, f"Failed to unfriend {user_id}: {resp.status_code} {resp.text}\n")
        result_text.see(tk.END)

def on_start():
    cookie = cookie_entry.get().strip()
    if not cookie:
        messagebox.showwarning("Input required", "Please enter your .ROBLOSECURITY cookie.")
        return
    start_unfriend(cookie)

# window setup
root = tk.Tk()
root.title("Roblox Friends Remover")
root.geometry("520x500")
root.resizable(False, False)

FONT_MAIN = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_MONO = ("Consolas", 10)

info = (
    "How to get your .ROBLOSECURITY cookie:\n"
    "1. Open roblox.com in your browser and log in.\n"
    "2. Open Developer Tools (F12), go to the Application tab.\n"
    "3. Find the '.ROBLOSECURITY' cookie under Cookies for roblox.com.\n"
    "4. Copy its value and paste it below.\n"
)

frame = tk.Frame(root, padx=16, pady=16, bg="#f5f6fa")
frame.pack(fill="both", expand=True)

tk.Label(frame, text="Roblox Friends Remover", font=FONT_TITLE, bg="#f5f6fa", fg="#222").pack(pady=(0, 10))
tk.Label(frame, text=info, wraplength=480, justify="left", font=FONT_MAIN, bg="#f5f6fa").pack(padx=4, pady=(0, 12))

tk.Label(frame, text=".ROBLOSECURITY cookie:", font=FONT_MAIN, bg="#f5f6fa").pack(anchor="w", padx=2)
cookie_entry = tk.Entry(frame, width=60, show="*", font=FONT_MAIN, relief="solid", borderwidth=1)
cookie_entry.pack(pady=(2, 10), padx=2, ipady=4)

tk.Button(
    frame, text="Start Removing Friends", command=on_start,
    font=FONT_MAIN, bg="#4f8cff", fg="white", activebackground="#357ae8", relief="raised", bd=2
).pack(pady=(0, 12), ipadx=8, ipady=4)

result_text = scrolledtext.ScrolledText(
    frame, width=62, height=15, font=FONT_MONO, bg="#f8f9fb", relief="solid", borderwidth=1
)
result_text.pack(padx=2, pady=2, fill="both", expand=True)

root.mainloop()