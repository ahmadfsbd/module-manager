import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

MODULES_DIR = os.path.expanduser("~/module-manager/modules")

def get_modules():
    try:
        return sorted([d for d in os.listdir(MODULES_DIR)
                       if os.path.isdir(os.path.join(MODULES_DIR, d))])
    except FileNotFoundError:
        return []

def run_command(action, module=None):
    cmd = [os.path.expanduser("/usr/local/bin/module-manager"), action]
    if module:
        cmd.append(module)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout + "\n" + result.stderr

def load():
    module = selected_module.get()
    output = run_command("load", module)
    messagebox.showinfo("Load Module", output)
    update_loaded_list()

def unload():
    module = selected_module.get()
    output = run_command("unload", module)
    messagebox.showinfo("Unload Module", output)
    update_loaded_list()

def restore():
    output = run_command("restore")
    messagebox.showinfo("Restore Modules", output)
    update_loaded_list()

def show_status():
    module = selected_module.get()
    output = run_command("status", module)
    messagebox.showinfo("Module Status", output)

def update_loaded_list():
    output = run_command("list")
    loaded_text.delete(1.0, tk.END)
    loaded_text.insert(tk.END, output)

# GUI setup
root = tk.Tk()
root.title("Module Manager")

# Dropdown for modules
tk.Label(root, text="Select Module:").grid(row=0, column=0, sticky="w")
selected_module = tk.StringVar()
modules_dropdown = ttk.Combobox(root, textvariable=selected_module, width=30)
modules_dropdown['values'] = get_modules()
modules_dropdown.grid(row=0, column=1, columnspan=2, sticky="we")

# Buttons
tk.Button(root, text="Load", command=load).grid(row=1, column=0, sticky="we")
tk.Button(root, text="Unload", command=unload).grid(row=1, column=1, sticky="we")
tk.Button(root, text="Restore", command=restore).grid(row=1, column=2, sticky="we")
tk.Button(root, text="Status", command=show_status).grid(row=2, column=0, columnspan=3, sticky="we")

# Loaded modules display
tk.Label(root, text="Available and Loaded Modules:").grid(row=3, column=0, columnspan=3, sticky="w")
loaded_text = tk.Text(root, height=20, width=80)
loaded_text.grid(row=4, column=0, columnspan=3)

update_loaded_list()
root.mainloop()

