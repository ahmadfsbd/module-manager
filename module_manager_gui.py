import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import yaml

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
    loaded_text.config(state='normal')
    loaded_text.delete(1.0, tk.END)
    loaded_text.insert(tk.END, output)
    loaded_text.config(state='disabled')

def filter_modules(*args):
    query = search_var.get().lower()
    module_listbox.delete(0, tk.END)
    for module in all_modules:
        if query in module.lower():
            module_listbox.insert(tk.END, module)

def show_description(event):
    module = get_selected_module()
    if not module:
        return
    meta_file = os.path.join(MODULES_DIR, module, "meta.yaml")
    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r') as f:
                data = yaml.safe_load(f)
            desc = yaml.dump(data, sort_keys=False, allow_unicode=True)
        except Exception as e:
            desc = f"Failed to load meta.yaml: {e}"
    else:
        desc = "No meta.yaml found."
    desc_text.config(state='normal')
    desc_text.delete(1.0, tk.END)
    desc_text.insert(tk.END, desc)
    desc_text.config(state='disabled')

# --- GUI SETUP ---

root = tk.Tk()
root.title("Module Manager")
root.geometry("1000x700")

# Scrollable Main Canvas
main_canvas = tk.Canvas(root)
main_frame = tk.Frame(main_canvas)
vsb = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
main_canvas.configure(yscrollcommand=vsb.set)

vsb.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)
main_canvas.create_window((0, 0), window=main_frame, anchor="nw")

def on_configure(event):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))

main_frame.bind("<Configure>", on_configure)

# Load all modules
all_modules = get_modules()

# Search
tk.Label(main_frame, text="Search Modules:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
search_var = tk.StringVar()
search_var.trace_add("write", filter_modules)
tk.Entry(main_frame, textvariable=search_var, width=25).grid(row=0, column=1, sticky="w", padx=5, pady=2)

# Module list
tk.Label(main_frame, text="Available Modules:").grid(row=1, column=0, sticky="w", padx=5)
module_frame = tk.Frame(main_frame)
module_frame.grid(row=2, column=0, rowspan=4, sticky="ns", padx=5)

module_scrollbar = tk.Scrollbar(module_frame)
module_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

module_listbox = tk.Listbox(module_frame, height=15, width=35, exportselection=False, yscrollcommand=module_scrollbar.set)
for module in all_modules:
    module_listbox.insert(tk.END, module)
module_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
module_listbox.bind("<<ListboxSelect>>", show_description)

module_scrollbar.config(command=module_listbox.yview)

# Buttons
button_frame = tk.Frame(main_frame)
button_frame.grid(row=2, column=1, sticky="nsew", padx=5)

tk.Button(button_frame, text="Load", command=load).grid(row=0, column=0, sticky="we", padx=5, pady=2)
tk.Button(button_frame, text="Unload", command=unload).grid(row=1, column=0, sticky="we", padx=5, pady=2)
tk.Button(button_frame, text="Restore All", command=restore).grid(row=2, column=0, sticky="we", padx=5, pady=2)
tk.Button(button_frame, text="Status", command=show_status).grid(row=3, column=0, sticky="we", padx=5, pady=2)

# Module Description Box (left)
tk.Label(main_frame, text="Module Description:").grid(row=6, column=0, sticky="w", padx=5)
desc_frame = tk.Frame(main_frame)
desc_frame.grid(row=7, column=0, sticky="nsew", padx=5, pady=5)

desc_scrollbar = tk.Scrollbar(desc_frame)
desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

desc_text = tk.Text(desc_frame, height=15, width=55, wrap=tk.WORD, yscrollcommand=desc_scrollbar.set)
desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
desc_scrollbar.config(command=desc_text.yview)
desc_text.config(state='disabled')

# Loaded Modules Box (right)
tk.Label(main_frame, text="Loaded Modules:").grid(row=6, column=1, sticky="w", padx=5)
loaded_frame = tk.Frame(main_frame)
loaded_frame.grid(row=7, column=1, sticky="nsew", padx=5, pady=5)

loaded_scrollbar = tk.Scrollbar(loaded_frame)
loaded_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

loaded_text = tk.Text(loaded_frame, height=15, width=55, wrap=tk.WORD, yscrollcommand=loaded_scrollbar.set)
loaded_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
loaded_scrollbar.config(command=loaded_text.yview)
loaded_text.config(state='disabled')

# Configure resizing behavior
for i in range(2):
    main_frame.grid_columnconfigure(i, weight=1)
main_frame.grid_rowconfigure(7, weight=1)

update_loaded_list()
root.mainloop()

