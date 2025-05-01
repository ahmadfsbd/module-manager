import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

MODULES_DIR = os.path.expanduser("/genesandhealth/library-red/modules")

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

def get_selected_module():
    selected_indices = module_listbox.curselection()
    if not selected_indices:
        return None
    return module_listbox.get(selected_indices[0])

def load():
    module = get_selected_module()
    if not module:
        messagebox.showwarning("No Module Selected", "Please select a module first.")
        return
    output = run_command("load", module)
    messagebox.showinfo("Load Module", output)
    update_loaded_list()

def unload():
    module = get_selected_module()
    if not module:
        messagebox.showwarning("No Module Selected", "Please select a module first.")
        return
    output = run_command("unload", module)
    messagebox.showinfo("Unload Module", output)
    update_loaded_list()

def restore():
    output = run_command("restore")
    messagebox.showinfo("Restore Modules", output)
    update_loaded_list()

def show_status():
    module = get_selected_module()
    if not module:
        messagebox.showwarning("No Module Selected", "Please select a module first.")
        return
    output = run_command("status", module)
    messagebox.showinfo("Module Status", output)

def update_loaded_list():
    output = run_command("list")
    loaded_text.delete(1.0, tk.END)
    loaded_text.insert(tk.END, output)

# GUI setup
root = tk.Tk()
root.title("Module Manager")

# Scrollable listbox for modules
tk.Label(root, text="Available Modules:").grid(row=0, column=0, sticky="w")
module_frame = tk.Frame(root)
module_frame.grid(row=1, column=0, rowspan=3, sticky="ns")

module_scrollbar = tk.Scrollbar(module_frame)
module_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

module_listbox = tk.Listbox(module_frame, height=15, width=30, exportselection=False, yscrollcommand=module_scrollbar.set)
for module in get_modules():
    module_listbox.insert(tk.END, module)
module_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

module_scrollbar.config(command=module_listbox.yview)

# Buttons
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=1, columnspan=2, sticky="nsew")

tk.Button(button_frame, text="Load", command=load).grid(row=0, column=0, sticky="we", padx=5, pady=2)
tk.Button(button_frame, text="Unload", command=unload).grid(row=1, column=0, sticky="we", padx=5, pady=2)
tk.Button(button_frame, text="Restore All", command=restore).grid(row=2, column=0, sticky="we", padx=5, pady=2)
tk.Button(button_frame, text="Status", command=show_status).grid(row=3, column=0, sticky="we", padx=5, pady=2)

# Loaded modules display
tk.Label(root, text="Available and Loaded Modules:").grid(row=4, column=0, columnspan=3, sticky="w")
loaded_text = tk.Text(root, height=20, width=80)
loaded_text.grid(row=5, column=0, columnspan=3)

update_loaded_list()
root.mainloop()

