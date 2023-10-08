import os
import sys
import tempfile
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from tkinter import filedialog
import subprocess
import shutil

temp_dir = tempfile.mkdtemp()

game_path = ""
output_path = ""
mods_paths = ""

filename = "godotmod.exe"

appsize = (400,300)

def select_file():
    global game_path, filename
    file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")],title="Select Godot App")
    if file_path:
        game_path = file_path
        filename = game_path.split("/")[-1]
        filename = filename[:-4] + " [MODDED]"

def select_output_file():
    global output_path
    file_options = {
        'defaultextension': '.exe',
        'initialfile': filename+'.exe',
        'filetypes': [("Executable Files", "*.exe")]
    }
    file_path = filedialog.asksaveasfilename(title="Select Output File", **file_options)
    if file_path:
        output_path = file_path

def select_mods_files():
    global mods_paths
    file_paths = filedialog.askopenfilenames(title="Select Mod Files", filetypes=(("Mod Files", "*.pck"), ("Mod Files", "*.zip")))
    if file_paths:
        mods_paths = file_paths
        if len(mods_paths) > 0:
            list_loaded(mods_paths)  # Assuming you have a function to list the selected files
            third_button.config(bootstyle="success")
        else:
            third_button.config(bootstyle="danger")

def select_mods_folder():
    global mods_path
    folder_path = filedialog.askdirectory(title="Select Mods Folder")
    if folder_path:
        mods_path = folder_path
        if(len(os.listdir(folder_path)) > 0):
            list_files(mods_path)
            third_button.config(bootstyle="success")
        else:
            third_button.config(bootstyle="danger")

def list_loaded(files):
    file_text.delete(1.0, ttk.END)  # Clear the scrolled text

    for file in files:
        file_text.insert(ttk.END, file.split("/")[-1] + "\n")

def list_files(folder_path):
    file_text.delete(1.0, ttk.END)  # Clear the scrolled text

    try:
        files = os.listdir(folder_path)
        for file in files:
            file_text.insert(ttk.END, file + "\n")
    except Exception as e:
        file_text.insert(ttk.END, f"Error: {str(e)}")

def runPCKE(params):
    if getattr(sys, 'frozen', False):  # Check if running as an executable
        # If running as an executable, use sys._MEIPASS to locate the resources folder
        resources_dir = os.path.join(sys._MEIPASS, 'resources')
    else:
        # If running as a script, use a relative path to the resources folder
        resources_dir = os.path.join(os.getcwd(), 'resources')

    pcke_exe = os.path.join(resources_dir, 'pcke.exe')
    command = f'"{pcke_exe}" {params}'    
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    for line in process.stdout:
        status_label.config(text=line.decode().strip())
        app.update_idletasks()
    
    app.update_idletasks()
    process.wait()

def patch_files():
    if(len(mods_paths) <= 0):
        return
    select_file()
    if(game_path == ""):
        return
    select_output_file()
    if(output_path == ""):
        return
    
    status_label.config(text="SPLITTING APP")
    app.update_idletasks()
    runPCKE(f" -s \"{game_path}\" \"{temp_dir}\split.exe\"")

    status_label.config(text="EXTRACTING APP")
    app.update_idletasks()
    runPCKE(f" -e \"{temp_dir}\split.pck\" \"{temp_dir}\extracted\"")

    for file in mods_paths:
        status_label.config(text="LOADING MOD "+ file)
        app.update_idletasks()
        runPCKE(f" -e \"{file}\" \"{temp_dir}\extracted\"")

    status_label.config(text="PACKING APP")
    app.update_idletasks()
    runPCKE(f" -pe \"{temp_dir}/extracted\" \"{temp_dir}/split.exe\" 1.3.5.0")

    error = None
    try:
        status_label.config(text="COPYING FILES TO OUTPUT DIRECTORY")
        app.update_idletasks()
        shutil.copy(f'{temp_dir}\\split.exe', output_path)
    except Exception as e:
        error = e
    shutil.rmtree(temp_dir)

    if error is None:
        status_label.config(text="DONE PATCHING MODS\nYOU CAN NOW CLOSE THIS WINDOW", bootstyle="success")
    else:
        status_label.config(text="AN ERROR OCCURED\n"+error, bootstyle="danger")
    app.update_idletasks()

def clear_list():
    file_text.delete(1.0, ttk.END)

app = ttk.Window()
ttk.Style(theme='darkly')

app.title("Godot Mod Loader")

app.geometry(f"{appsize[0]}x{appsize[1]}")
app.resizable(width=False, height=False)

title_label = ttk.Label(app, text="Godot Mod Loader",  font=("Helvetica", 16))
title_label.pack(pady=5)

frame = ttk.Frame(app)
frame.pack()

frame2 = ttk.Frame(app)
frame2.pack()

frame3 = ttk.Frame(app)
frame3.pack()

frame4 = ttk.Frame(app)
frame4.pack()

select_button = ttk.Button(frame, text="Select Mods", command=select_mods_files)
select_button.pack(side=ttk.LEFT, padx=5)

file_text = ScrolledText(frame2, width=50, height=10)
file_text.pack()

third_button = ttk.Button(frame, text="Patch", command=patch_files, bootstyle="danger")
third_button.pack(padx=10, pady=5)

status_label = ttk.Label(frame3, text="",wraplength=200,  font=("Helvetica", 8),bootstyle="info")
status_label.pack(pady=5)

app.mainloop()
