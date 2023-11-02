'''
Tool: Maya Notepad
Version: 1.0.0
Author: Vincent Rossini
Date: October 2023


Github: https://raw.githubusercontent.com/vinman75/maya_notepad/main.py

Description: 
This tool provides a simple notepad functionality within Maya. 
It allows users to open, edit, save, and manage text files directly from the Maya interface. 
Additional features include character count tracking and quick launch options for other applications like CMD and Calculator.

License:
MIT License

Copyright (c) 2023 Vincent Rossini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import maya.cmds as mc
import subprocess
import os
import tempfile

isModified = False

# Automatically set the file path to a temp directory regardless of OS
temp_dir = tempfile.gettempdir()
file_path = os.path.join(temp_dir, "maya_notepad")

# Ensure the directory exists
if not os.path.exists(file_path):
    os.makedirs(file_path)

def create_character_count_job():
    global charCountJob
    charCountJob = mc.scriptJob(event=("idle", update_character_count), parent="_notePadWin")

def update_character_count(*args):
    global isModified
    data = mc.scrollField("_scrollFld", query=True, text=True)
    count = len(data)
    mc.text("_charCount", edit=True, label=f" | Characters: {count}")
    
    # Only set isModified to True if the content has changed
    current_file_data = ""
    file_name_raw = mc.text("_fName", query=True, label=True)
    file_name = file_name_raw[6:]
    if not "File: Not saved" == file_name_raw and os.path.exists(file_name):
        with open(file_name, 'r') as f:
            current_file_data = f.read()
    
    if data != current_file_data:
        isModified = True

def confirm_warning(*args):
    result = mc.confirmDialog( title='Maya Nodepad: Warning!', 
                  message='File has been not saved. Do you wish to continue', 
                  button=['Save', 'Yes','Cancel'], 
                  defaultButton='Save', 
                  cancelButton='Cancel', 
                  dismissString='Cancel')
    
    if result == "Save":
        save_as_file()
        return result
    
    elif result == 'Cancel':
        return result

    elif result == 'Yes':
        return result  
        
def test_save_requirement(*args):
    global isModified
    live_data = mc.scrollField("_scrollFld", query=True, text=True)
    file_name_raw = mc.text("_fName", query=True, label=True)
    file_name = file_name_raw[6:]

    if "File: Not saved" == file_name_raw:
        if live_data:
            return confirm_warning()
    else:
        if not os.path.exists(file_name):  # Check if the file name exists
            return confirm_warning()
        with open(file_name, 'r') as f:
            data = f.read()
            if live_data != data:
                return confirm_warning()
                
    if isModified and live_data:
        return confirm_warning()

def save_as_file(*args):
    global isModified
    result = mc.fileDialog2(startingDirectory = file_path, fileFilter="text (*.txt)", dialogStyle=2, fileMode=0)
    if result:
        selected_save_path = result[0]
        data = mc.scrollField("_scrollFld", query=True, text=True)
        with open(selected_save_path, 'w') as f:
            f.write(data)
            mc.text("_fName", edit=True, label=f"File: {selected_save_path}")
            mc.menuItem("_save_menu", edit=True,  enable=True)
            isModified = False

def save_file(*args):
    global isModified
    file_name_raw = mc.text("_fName", query=True, label=True)
    file_name = file_name_raw[6:]
    
    # If the file has never been saved before (i.e., it's a new file)
    if "File: Not saved" == file_name_raw:
        save_as_file()
    else:
        # Otherwise, save it directly to the current file
        with open(file_name, "w") as f:
            data = mc.scrollField("_scrollFld", query=True, text=True)
            f.write(data)
            
        # After saving, set isModified to False
        isModified = False

def open_file(*args):
    test_save_requirement()
    result = mc.fileDialog2(startingDirectory = file_path, fileFilter="text (*.txt)", dialogStyle=2, fileMode=1)
    if result:
        selected_save_path = result[0]
        with open(selected_save_path, 'r') as f:    
            data = f.read()
            mc.scrollField("_scrollFld", edit=True, text=data)
            mc.text("_fName", edit=True, label=f"File: {selected_save_path}")
            mc.menuItem("_save_menu", edit=True,  enable=True)
            
def new_file(*args):
    global isModified
    save_check = test_save_requirement()
    if save_check == "Cancel":
        return
    mc.scrollField("_scrollFld", edit=True, clear=True)
    mc.text("_fName", edit=True, label="File: Not saved")
    mc.menuItem("_save_menu", edit=True, enable=False)
    isModified = False

def clear_field(*args):
    mc.scrollField("_scrollFld", edit=True, clear=True)

def launch_calc(*args):
    subprocess.run(["calc"])
    
def launch_CMD(*args):
    subprocess.run(["cmd"])

def quit_app(*args):
    global charCountJob
    mc.scriptJob(kill=charCountJob, force=True)
    mc.deleteUI("_notePadWin", window=True)


if mc.window("_notePadWin", exists=True):
    mc.deleteUI("_notePadWin", window=True)
    

mc.window("_notePadWin",
        menuBar=True,
        title="Maya Notepad",
        minimizeButton=True,
        maximizeButton=True,
        sizeable=True)

mc.menu(label="File")
mc.menuItem(label="New", command=new_file)
mc.menuItem(divider=True)
mc.menuItem(label="Open", command=open_file)
mc.menuItem(divider=True)
mc.menuItem("_save_menu", label="Save", enable=False, command=save_file)
mc.menuItem(label="Save as", command=save_as_file)
mc.menuItem(divider=True)
mc.menuItem(label="Quit", command=quit_app)

mc.menu(label="Edit")
mc.menuItem(label="Clear", command=clear_field)

mc.menu(label="Apps")
mc.menuItem(label="Calculator", command=launch_calc, image="calculator2.png")
mc.menuItem(label="CMD", command=launch_CMD, image='CMD.png')

mc.formLayout("_formLay")
mc.scrollField("_scrollFld", changeCommand=update_character_count)

mc.text("_fName",label="File: Not saved")
mc.text("_charCount", label=" | Characters: 0")

mc.formLayout("_formLay", edit=True,
    attachForm=[
    ("_scrollFld", "left", 3),
    ("_scrollFld", "right", 3),
    ("_scrollFld", "top", 3),
    ("_scrollFld", "bottom", 20),
    ("_fName", "left", 4),
    ],
    
    attachControl=[
    ("_fName", "top", 3, "_scrollFld"),
    ("_charCount", "top", 3, "_scrollFld"),
    ("_charCount", "left", 5, "_fName"),        
    ])  

mc.showWindow("_notePadWin")
create_character_count_job()