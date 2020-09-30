"""@Aditya Singh Tejas (c) 2020 PIERA-ZONE"""
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename
from threading import Thread
from PIL import Image, ImageTk
import os
import re
import zipfile

#GUI Initialization 
root = Toplevel()
file_dir = os.path.join('Program Files', 'Data Files')
root.title('PIERA-ZONE Exam Setup')
root.iconbitmap(os.path.join(file_dir, 'logo.ico'))
root.resizable(False, False)
mainbg = 'White'
barbg = 'RoyalBlue4'
root.configure(bg = mainbg)
class MyTk:
    """Costumized Lable and Entry"""
    def Label(self, location, text, font, padx, pady, side, anchor):
        self.text = text
        self.font = font
        self.location = location
        self.padx = padx
        self.pady = pady
        self.anchor = anchor
        self.side = side
        self.label = Label(location, text = text, bg = 'white', font = ('Roboto', font))
        self.label.pack(padx = padx, pady = pady, anchor = anchor, side = side)

    def Entry(self, location, font, padx, pady, side, anchor):
        self.font = font
        self.location = location
        self.padx = padx
        self.pady = pady
        self.anchor = anchor
        self.side = side
        self.var = StringVar()
        self.label = Entry(location, textvariable = self.var, font = ('Roboto', font), relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
        self.label.pack(padx = padx, pady = pady, anchor = anchor, side = side)

def select(): #Select the Questions File
    global content
    ques_path = askopenfilename(filetypes =(('PDF Files', '*.pdf'),))
    if ques_path != 'None':
        ques.var.set(ques_path)
        with open (f'{ques_path}', 'rb') as file:
            content = file.read()
            file.close()

def addSec(event = None): #Add Section
    global sec_text, markings, names, ranges
    insert_frame = Frame(sec_text, bg = 'white')
    left_frame = Frame(insert_frame, bg = 'white')
    left_frame.pack(side = 'left', fill = 'y')
    right_frame = Frame(insert_frame, bg = 'white')
    right_frame.pack(side = 'right', fill = 'y')
    sec_text.configure(state = 'normal')
    name_lab = Label(left_frame, text = 'Section Name', font = ('Roboto', 12), bg = 'white')
    name_entry = Entry(right_frame, font = ('Roboto', 12), relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
    names.append(name_entry)
    mark_lab = Label(left_frame, text = 'Marking Scheme', font = ('Roboto', 12), bg = 'white')
    mark_entry = Entry(right_frame, font = ('Roboto', 12), relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
    markings.append(mark_entry)
    range_lab = Label(left_frame, text = 'Starting Question', font = ('Roboto', 12), bg = 'white')
    range_entry = Entry(right_frame, font = ('Roboto', 12), relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
    ranges.append(range_entry)
    name_lab.pack(side = 'top', padx = 10, pady = (0,10))
    mark_lab.pack(side = 'top', padx = 10, pady = (0,10))
    range_lab.pack(side = 'top', padx = 10, pady = (0,10))
    name_entry.pack(side = 'top', padx = 10, pady = (0,10))
    mark_entry.pack(side = 'top', padx = 10, pady = (0,10))
    range_entry.pack(side = 'top', padx = 10, pady = (0,10))
    sec_text.window_create('end', window = insert_frame)
    sec_text.insert('end', '\n\n')
    sec_text.configure(state = 'disabled')

def addParentheses(event = None):
    key_text.focus_set()
    key_text.insert('insert', '(),')
    pos = key_text.index('insert')
    line = int(pos.split('.')[0])
    char = int(pos.split('.')[1])
    key_text.mark_set('insert', "%d.%d" % (line,char-2))

#__Processing__
markings = []
names = []
ranges = []

def finish():
    def process():
        global name, email, dur, ques, markings, ranges, names
        #Get Data
        exam_name = name.var.get()
        exam_duration = dur.var.get()
        inst_duration = idur.var.get()
        to_email = email.var.get()
        ques_pdf = ques.var.get()
        sections = []
        for nam in names:
            sections.append(nam.get())
        for mark in markings:
            sections.append(mark.get())
        for ran in ranges:
            sections.append(ran.get())
        ans_key = key_text.get('1.0', 'end-1c')
        instructions = inst_text.get('1.0', 'end-1c')
        #Convert the Key to usable format
        final_key = []
        key_list = re.findall(r"\(([a-d,0-9]+)\)", ans_key)
        for key in key_list:
            key = key.split(',')
            temp = ['False', 'False', 'False', 'False', '']
            for i in range(0,4):
                try:
                    if key[i] == 'a':
                        temp[0] = 'True'
                    if key[i] == 'b':
                        temp[1] = 'True'
                    if key[i] == 'c':
                        temp[2] = 'True'
                    if key[i] == 'd':
                        temp[3] = 'True'
                    if type(int(key[i])) == int:
                        temp[4] = str(key[i])
                except:
                    continue
            for k in temp:
                final_key.append(k)

        #Write in Files
        with open(os.path.join(main_dir, f'{exam_name} Key.pzn'), 'w+') as file:
            file.write(str(final_key))
            file.close()
        with open(os.path.join(raw_dir, f'{exam_name} Details.pzn'), 'w+') as file:
            #file.write("'"+exam_name+"'"+','+exam_duration+','+"'"+to_email+"'"+','+str(sections))+','+inst_duration
            file.write(f"'{exam_name}',{exam_duration},'{to_email}',{sections},{inst_duration}")
            file.close()
        with open(os.path.join(raw_dir, f'{exam_name} Instructions.pzn'), 'w+') as file:
            file.write(instructions)
            file.close()
        with open(f'{ques_pdf}', 'rb') as file:
            content = file.read()
            with open(os.path.join(raw_dir, f'{exam_name} Questions.pdf'), 'wb') as ofile:
                ofile.write(content)
                ofile.close()
            file.close()
        with zipfile.ZipFile(os.path.join(main_dir, f'{exam_name}.pznx'), 'a') as pznx:
            for file in os.listdir(raw_dir):
                pznx.write(os.path.join(raw_dir, file), file)
        messagebox.showinfo('Success', 'Exam has been Successfully Created!')
        root.destroy()

    #Verify and create directories
    try:
        flag = 1
        if not name.var.get():
            messagebox.showerror('Error', "Please give a name to the Exam!")
            flag = 0
        if not dur.var.get() and flag == 1:
            messagebox.showerror('Error', "Please enter the Exam Duration!")
            flag = 0
        if not ques.var.get() and flag == 1:
            messagebox.showerror('Error', "Please select the Question Paper!")
            flag = 0
        if names == [] and markings == [] and ranges == [] and flag == 1:
            messagebox.showerror('Error', "There should be at least 1 section!")
            flag = 0
        if not key_text.get('1.0', 'end-1c') and flag == 1:
            messagebox.showerror('Error', "Please enter the Key!")
            flag = 0
        if not inst_text.get('1.0', 'end-1c') and flag == 1:
            ins = messagebox.askokcancel('Warning', "There are no Instrucions for this Exam\n"
                                         +"Select Ok if you wish to continue")
            if ins:
                flag = 1
        if not email.var.get() and flag == 1:
            mail = messagebox.askokcancel('Warning', "Auto emailing will be disabled!\nPlease enter and email\n"
                                   +"if you wish to have that feature.")
            if mail:
                flag = 1
        if flag == 1:
            try:
                main_dir = 'Exam Setup Files\\'+name.var.get()+' Files'
                raw_dir = os.path.join(main_dir, 'Raw Data')
                os.mkdir(main_dir)
                os.mkdir(raw_dir)
            except:
                messagebox.showerror('Error', "Failed to create Exam!\n An exam with same name exists\n"
                            +"Please Delete/Rename the existing/currrent.")
            process()
    except:
        messagebox.showinfo('Warning', "An error occured!\nPlease try again.")

#__GUI__   
#Tittle/Foot Bar
top_frame = Frame(root, bg = 'white')
top_frame.pack(side = 'top', fill = 'x', pady = (10,0))
head_img = Image.open(os.path.join(file_dir, 'ExamSetup.png'))
head_img = head_img.resize((193, 45), Image.ANTIALIAS)
head_img = ImageTk.PhotoImage(head_img)
head_lab = Label(top_frame, image = head_img, bg = 'white')
head_lab.pack(side = 'left', padx = 10, fill = 'both')
bottom_frame = Frame(root, bg = 'white')
bottom_frame.pack(side = 'bottom', fill = 'x', pady = (0,10))
sub_but = ttk.Button(bottom_frame, text = 'Submit', command = finish)
sub_but.pack(side = 'right', anchor = 'e', padx = 10)
#Instructions
inst_frame = Frame(root, highlightthickness = 1, highlightbackground = 'black', bg = 'white')
inst_frame.pack(padx = 10, pady = (0,10), side = 'bottom', anchor = 'w')
lab = Label(inst_frame, text = 'Pre-Exam Instructions', bg = barbg, font = ('Roboto', 12), fg = 'white') 
lab.pack(side = 'top', anchor = 'nw', fill = 'x', pady = (0,10))
disp_inst_frame = Frame(inst_frame, bg = 'white')
disp_inst_frame.pack(side = 'bottom', fill = 'both')
inst_text_frame = Frame(disp_inst_frame, width = 820, height = 200, bg = 'white')
inst_text_frame.pack(side = 'left', expand = False, fill = 'x')
inst_text_frame.pack_propagate(False)
inst_text = Text(inst_text_frame, font = ('Roboto', 12), wrap = 'word', bd = 0)
inst_vsb = Scrollbar(disp_inst_frame, command = inst_text.yview)
inst_text.configure(yscrollcommand = inst_vsb.set)
inst_text.pack(padx = 10, pady = (0, 10), fill = 'x')
inst_vsb.pack(side = 'right', fill = 'y', padx = (0, 10), pady = (0, 10))
#Base Frames
left_base_frame = Frame(root, bg = mainbg)
left_base_frame.pack(side = 'left', fill = 'both')
right_base_frame = Frame(root, bg = mainbg)
right_base_frame.pack(side = 'right', fill = 'both')
#Intro
intro_frame = Frame(left_base_frame, highlightthickness = 1, highlightbackground = 'black', bg = 'white')
intro_frame.pack(padx = 10, pady = 10, side = 'top', anchor = 'n')
lab = Label(intro_frame, text = 'Basic Details', bg = barbg, font = ('Roboto', 12), fg = 'white') 
lab.pack(side = 'top', anchor = 'nw', fill = 'x', pady = (0,10))
ques_but = ttk.Button(intro_frame, text = 'Browse', command = select)
ques_but.pack(side = 'right', padx = 10, pady = 9, anchor = 'se')
left_intro_frame = Frame(intro_frame, bg = 'white')
left_intro_frame.pack(side = 'left', anchor = 'w')
right_intro_frame = Frame(intro_frame, bg = 'white')
right_intro_frame.pack(side = 'right', anchor = 'e')
name = MyTk()
name.Label(left_intro_frame, 'Exam Name', 12, 10, (0,10), 'top', 'e')
name.Entry(right_intro_frame, 12, 10, (0,10), 'top', 'e')
dur = MyTk()
dur.Label(left_intro_frame, 'Exam Duration', 12, 10, (0,10), 'top', 'e')
dur.Entry(right_intro_frame, 12, 10, (0,10), 'top', 'e')
idur= MyTk()
idur.Label(left_intro_frame, 'Inst. Duration', 12, 10, (0,10), 'top', 'e')
idur.Entry(right_intro_frame, 12, 10, (0,10), 'top', 'e')
email = MyTk()
email.Label(left_intro_frame, 'Your Email', 12, 10, (0,10), 'top', 'e')
email.Entry(right_intro_frame, 12, 10, (0,10), 'top', 'e')
ques = MyTk()
ques.Label(left_intro_frame, 'Question Paper', 12, 10, (0,10), 'top', 'e')
ques.Entry(right_intro_frame, 12, 10, (0,10), 'top', 'e')
#Sections
sec_frame = Frame(right_base_frame, highlightthickness = 1, highlightbackground = 'black', bg = 'white')
sec_frame.pack(padx = (0,10), pady = 10, side = 'top')
top_sec_frame = Frame(sec_frame, bg = barbg)
top_sec_frame.pack(side = 'top', fill = 'x', pady = (0, 10))
opt = StringVar()
add_but = ttk.Button(top_sec_frame, text = 'Add New Section', command = addSec)
add_but.pack(side = 'right', anchor = 's', padx = 10)
lab = Label(top_sec_frame, text = 'Add/Edit Sections', bg = barbg, font = ('Roboto', 12), fg = 'white')
lab.pack(side = 'left', anchor = 'w', fill = 'x', padx = 10)
disp_sec_frame = Frame(sec_frame, bg = 'white')
disp_sec_frame.pack(side = 'bottom', fill = 'both')
sec_text_frame = Frame(disp_sec_frame, width = 370, height = 308, bg = 'white')
sec_text_frame.pack(side = 'left', expand = False)
sec_text_frame.pack_propagate(False)
sec_text = Text(sec_text_frame, font = ('Roboto', 12), bd = 0)
sec_vsb = Scrollbar(disp_sec_frame, command = sec_text.yview)
sec_text.configure(yscrollcommand = sec_vsb.set, state = 'disabled', wrap = 'none')
sec_text.pack(expand = False, padx = 10, pady = (0, 10))
sec_vsb.pack(side = 'right', fill = 'y', padx = (0, 10), pady = (0, 10))
#Key
key_frame = Frame(left_base_frame, highlightthickness = 1, highlightbackground = 'black', bg = 'white')
key_frame.pack(padx = 10, pady = (0,10), side = 'top', anchor = 'w')
top_key_frame = Frame(key_frame, bg = barbg)
top_key_frame.pack(side = 'top', fill = 'x', pady = (0, 10))
opt = StringVar()
add_but = ttk.Button(top_key_frame, text = 'Insert', command = addParentheses)
add_but.pack(side = 'right', anchor = 's', padx = 10)
lab = Label(top_key_frame, text = 'Answer Key', bg = barbg, font = ('Roboto', 12), fg = 'white')
lab.pack(side = 'left', anchor = 'w', fill = 'x', padx = 10)
disp_key_frame = Frame(key_frame, bg = 'white')
disp_key_frame.pack(side = 'bottom', fill = 'both')
key_text_frame = Frame(disp_key_frame, width = 410, height = 92, bg = 'white')
key_text_frame.pack(side = 'left', expand = False, fill = 'x')
key_text_frame.pack_propagate(False)
key_text = Text(key_text_frame, font = ('Roboto', 12), wrap = 'word', bd = 0)
key_vsb = Scrollbar(disp_key_frame, command = key_text.yview)
key_text.configure(yscrollcommand = key_vsb.set)
key_text.pack(padx = 10, pady = (0, 10), fill = 'x')
key_vsb.pack(side = 'right', fill = 'y', padx = (0, 10), pady = (0, 10))
root.bind('<Control-q>', addParentheses)
root.bind('<Control-w>', addSec)
root.mainloop()