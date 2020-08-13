#Setup & Agreement
from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog
import sys, os, traceback, types
import requests
import zipfile
from pathlib import Path
from threading import Thread
import win32com.client
import pythoncom
import winshell
from tkinter.ttk import Progressbar
import time

def welcomeScreen():
    lab = Label(welcome, text = "Welcome to PIERA-ZONE\nLet's complete the installation.")
    lab.grid(row = 0, column = 1, padx = 20, pady = 20)
    but = Button(welcome, text = "Continue", command = agreement)
    but.grid(row = 1, column = 1, padx = 20, pady = 20)
    img = Image.open ("Prog. Files\\logo.png")
    img = img.resize((200, 200), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(img)
    log = Label(welcome, image = image)
    log.image = image
    log.grid(row = 0, column = 0, rowspan = 2, padx = 20, pady = 20)

def agreement():
    welcome.destroy()
    global agree
    agree = Frame(root)
    agree.pack(fill = 'both')
    ag_left = Frame(agree, width = 100, bg = 'white')
    ag_left.pack(side = 'left', fill = 'y')
    img = Image.open ("Prog. Files\\logo.png")
    img = img.resize((100, 100), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(img)
    log = Label(ag_left, image = image, bg = 'white')
    log.image = image
    log.pack(padx = 20, pady = 20, anchor = 'n')
    intro = Label(agree, text = "LICENSE AND TERMS OF USE", bg = 'white')
    intro.pack(pady = (10,0), padx = 20)

    with open("Prog. Files\\COPYING_Intro.txt", 'r') as file:
        cyp_int = file.read()
        file.close()
    with open ("Prog. Files\\COPYING.txt", 'r') as file:
        cyp_lic = file.read()
        file.close()

    but_frame = Frame(agree)
    but_frame.pack(side = 'bottom', fill = 'x')
    '''lab = Label(agree, text = data, justify=LEFT)
    lab.pack(padx = 20)'''
    accbut = Button(but_frame, text = "Accept and Continue", bg = 'green', fg = 'white', command = loc_select)
    accbut.pack(side = 'right', padx = (0, 10), pady = (0,10))
    denbut = Button(but_frame, text = "Decline and Quit", command = root.destroy)
    denbut.pack(side = 'right', padx = 10, pady = (0,10))

    data = cyp_int +"\n\n"+ cyp_lic

    txt = Text(agree, height=20, width=75, wrap = 'word')
    scr = Scrollbar(agree)
    scr.config(command=txt.yview)
    txt.config(yscrollcommand=scr.set)
    txt.insert(INSERT, data)
    txt.insert(END,"\n")
    txt.configure(state="disabled")
    txt.bind("<1>", lambda event: txt.focus_set())
    txt.pack(side = 'left', fill="both", expand=True, pady = 10, padx = (10,0))
    scr.pack(side = 'right', fill="y", expand=False, pady = 10, padx = (0,10))

def loc_select():
    def select():
        folder_selected = filedialog.askdirectory()
        loc.set(folder_selected)
    global inst
    agree.destroy()
    inst = Frame(root)
    inst.pack(fill = 'both')
    lab = Label(inst, text = "Choose your destination folder for Installing")
    lab.grid(row = 0, column = 1, padx = 20, pady = 20)
    global loc, ent
    loc = StringVar()
    ent = Entry(inst, textvariable = loc, width = 50)
    ent.grid(row = 1, column = 1, padx = 20, pady = 20)
    loc.set(os.environ["ProgramFiles"])
    but1 = Button(inst, text = "Change Folder", command = select)
    but1.grid(row = 2, column = 1, padx = 20, pady = 20)
    but2 = Button(inst, text = "Continue", command = download)
    but2.grid(row = 3, column = 1, padx = 20, pady = 20)
    img = Image.open ("Prog. Files\\logo.png")
    img = img.resize((200, 200), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(img)
    log = Label(inst, image = image)
    log.image = image
    log.grid(row = 0, column = 0, rowspan = 4, padx = 20, pady = 20)

def download():    
    def dld():
        def createShortcut():
            pythoncom.CoInitialize()
            desktop = winshell.desktop() # path to where you want to put the .lnk
            path = os.path.join(desktop, 'PIERA-ZONE.lnk')

            with open("Prog. Files\\Shcut_Target.txt", 'r') as file:
                data = file.read().split(", ")
                mainExe = data[0]
                wd = data[1]
                file.close()
            
            target = os.path.join(loc.get(), mainExe)
            wDir = os.path.join(loc.get(), wd)
            #icon = r'C:\path\to\icon\resource.ico' # not needed, but nice

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            #shortcut.IconLocation = icon
            shortcut.WindowStyle = 7 # 7 - Minimized, 3 - Maximized, 1 - Normal
            shortcut.save()

            stat.set("Successfully Installed")
            progress.destroy()
            but.config(state = 'normal')
        
        def unzip():
            with zipfile.ZipFile(str(Path.home() / "Downloads")+"\\PIERA-ZONE.zip", 'r') as zip_ref:
                zip_ref.extractall(loc.get())
            os.remove(str(Path.home() / "Downloads")+"\\PIERA-ZONE.zip")
            createShortcut()
        
        url = MainDownload
        r = requests.get(url, allow_redirects=True)
        file = str(Path.home() / "Downloads")+"\\PIERA-ZONE.zip"
        open(file, 'wb').write(r.content)
        stat.set("Installing...")
        unzip()
            
    def dest():
        root.destroy()
    
    inst.destroy()
    dwd = Frame(root)
    dwd.pack(fill = 'both')
    global stat, but
    stat = StringVar()
    lab = Label(dwd, textvariable = stat)
    lab.grid(row = 0, column = 1, padx = 20, pady = 20)
    stat.set("Downloading...")
    progress=Progressbar(dwd, orient=HORIZONTAL, length=200, mode='indeterminate')
    progress.grid(row = 1, column = 1, padx = 20, pady = 20)

    def bar():
        while True:
            for i in range(0, 101, 2):
                progress['value'] = i
                root.update_idletasks() 
                time.sleep(0.1) 
            
    but = Button(dwd, text = "Finish", command = dest, fg = 'white', bg = 'green', state = 'disabled')
    but.grid(row = 2, column = 1, padx = 20, pady = 20)
    img = Image.open ("Prog. Files\\logo.png")
    img = img.resize((200, 200), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(img)
    log = Label(dwd, image = image)
    log.image = image
    log.grid(row = 0, column = 0, rowspan = 3, padx = 20, pady = 20)

    Thread(target = dld).start()
    Thread(target = bar).start()

root = Tk()
root.title("PIERA-ZONE Installer")
icon = PhotoImage(file = "Prog. Files\\logo.png")
root.iconphoto(False, icon)
root.resizable(False, False)
welcome = Frame(root)
welcome.pack(fill = 'both')

with open("Prog. Files\\Dld_source.txt", 'r') as file:
    global MainDownload
    MainDownload = file.read()
    file.close()

welcomeScreen()

root.mainloop()
