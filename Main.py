"""@Aditya Singh Tejas (c) 2020 PIERA-ZONE"""
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk 
import os 
import random 
import webbrowser 
from threading import Thread
import shutil
import fitz
import time
from tkinter.ttk import Progressbar, OptionMenu, Style
import SendMail as mail
import concurrent.futures
import zipfile
import sys
import SendMail as mail
import Teacher

#________________________________________________Main Exam________________________________________________
def dataCollection(): #Pre-launch data collection 
    global exam_name, exam_folder, parent_folder, pznx, itime
    try:
        parent_folder = os.path.join(os.getcwd(),'My Exams')
        history = '__History__'
        pznx = os.listdir(parent_folder)
        if '.DS_Store' in pznx: #Only for macOS
            pznx.remove('.DS_Store')
        if pznx[0] == history:
            pznx = pznx[1]
        else:
            pznx = pznx[0]
        exam_name = str(pznx[:-5])
        exam_folder = os.path.join(parent_folder, history, exam_name)
        with zipfile.ZipFile(os.path.join(parent_folder, pznx), 'r') as unzip:
            unzip.extractall(exam_folder)
        details_path = os.path.join(exam_folder, f'{exam_name} Details.pzn')
        with open(details_path, 'r') as file:
            data = eval(file.read())
            itime = [data[-3], data[-2]+5, data[-1]]
            file.close()
    except:
        messagebox.showerror('Error', 'No Exam Found')
        return 0
    
def Ques_Disp_GUI(): #Exam GUI
    global res_var, answers, etime, path, opath, otp, retry, sections, section_name, revList, lastQ, currentQ
    global res_email, exam_name
    #Fetch details and assign variables
    path = os.path.join(exam_folder, f'{exam_name} Questions.pdf') 
    opath = os.path.join(cache_dir, "Output_Images") 
    details_path = os.path.join(exam_folder, f'{exam_name} Details.pzn')
    shutil.move(os.path.join(parent_folder, pznx), os.path.join(exam_folder, pznx))

    with open(details_path, 'r') as file:
        data = eval(file.read())
        etime = [data[1], data[2], data[3]]
        res_email = data[4]
        sec = data[5]
        batch = len(sec)//3
        section_name = sec[0:batch]
        marking_scheme = sec[batch:batch*2]
        sections = sec[batch*2+1:batch*3]
        sections.insert(0, 1)
        for s in range(len(sections)):
            sections[s] = int(sections[s])-1
        file.close()
        
    retry = 0
    res_var = []
    answers = []
    revList = []
    lastQ = 1
    currentQ = 1

    def Terminate(): #Terminate the exam immidiately and display the same
        global term
        term = Toplevel(initial)
        term.title("PIERA-ZONE Exam Monitor")
        setup(term)
        term.bell()
        lab = Label(term, text = ("This Exam has been TERMINATED!\n Caused due to a PROHIBITED action."))
        lab.grid(row = 0, column = 1, padx = 20, pady = 20)
        but = ttk.Button(term, text = "Quit", command = term.destroy)
        but.grid(row = 1, column = 1, padx = 20, pady = 20)
        log = Label(term, image = logo)
        log.image = logo
        log.grid(row = 0, column = 0, rowspan = 2, padx = 20, pady = 20)
        dest()

    def Monitor(): #PZ Monitor ensures exam is terminated if exam window's focus changes
        global esc_mb, confs
        while True:
            if not ques_win.focus_get():
                Thread(target = Terminate).start()
                break

    def final_submit(): #Initiates the submission process (COULD HAVE BEEN OMITTED)
        ans_append()
    
    def details(): #Fetches details input by the student
        global apath
        with open(os.path.join(cache_dir, "Student_Input.txt"),'r') as file:
            data = file.read()
            name = data.split(",")[0]
            batch = data.split(",")[1]
            roll = data.split(",")[2]
            email = data.split(",")[3]
            add = data.split(",")[4]
            apath = exam_name + "_" + name + "_" + batch + "_" + roll + "_" + email + "_" + add +'.pzn'
            file.close()
        with open(os.path.join(cache_dir, "Student_Input.txt"),'w+') as file:
            file.truncate()
            file.write(apath)
        
    def Convert(): #Converts PDF pages to images and stores them (MultiThreading used to speed up)
        global prog, pages
        try:
            os.mkdir(opath)
        except:
            shutil.rmtree(opath)
            os.mkdir(opath)
        pdffile = path
        doc = fitz.open(pdffile)
        pages = doc.pageCount
        prog = 0
        
        def part(i):
            zoom = 5    
            mat = fitz.Matrix(zoom, zoom)
            page = doc.loadPage(i)
            pix = page.getPixmap(matrix = mat)
            output = os.path.join(opath, f'Ques_{str(i+1)}.png')
            pix.writePNG(output)
            load.update_idletasks()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(0, pages):
                executor.submit(part, i)
                prog += ((1/pages)*50)
                progress['value'] = prog
            
        launch_main()
        
    def dest(): #destroys exam window
        ques_win.destroy()

    def on_closing(): #Brings back the focus if any native popup comes up to prevent termination
        ques_win.focus_set()

    def close_escape(event=None): #Binded to Escape key, asks for confirmation 
        ccal = Toplevel(ques_win)
        ques_win.focus_set()
        ccal.title("PIERA-ZONE Exam Monitor")
        setup(ccal)
        ccal.bell()

        lab = Label(ccal, text = ("The following acton can terminate the exam!\n"
                                  +"Please click the button below if you wish to proceed.\n"
                                  +"NONE OF YOUR ANSWERS WILL BE CONCIDERED!\n"
                                  +"If this was a mistake you can SAFELY close this pop-up."))
        lab.grid(row = 0, column = 1, padx = 20, pady = 20)
        but = ttk.Button(ccal, text = "Continue", command = dest)
        but.grid(row = 1, column = 1, padx = 20, pady = 20)
        log = Label(ccal, image = logo)
        log.image = logo
        log.grid(row = 0, column = 0, rowspan = 2, padx = 20, pady = 20)

        ccal.protocol("WM_DELETE_WINDOW", Thread(target = on_closing).start)
        
    def buttons(): #Creates CheckButtons and Entry (COULD HAVE BEEN DONE BETTER)
        global op_s, opt_s, ent
        opt_s = ['A','B','C','D']
        op_s = ['op1', 'op2', 'op3', 'op4']
        for i in range (0, 4):
            op_s[i] = Checkbutton(main_frame, text = opt_s[i], font=("Sans",15))
        ent = Entry(main_frame, font=("Sans",15), relief = 'flat', highlightthickness = 1, highlightbackground = 'black')

    def seek(event): #Moves to a question, called from OptionMenu
        global lastQ, currentQ
        lastQ = currentQ
        for i in range (0, ques_count):
            if event == "Question " + str(i+1):
                loc = float(i/ques_count)
                text.yview_moveto(loc)
        Thread(target = refreshMenu, args = [lastQ]).start()
        currentQ = int(event.split(' ')[1])
        lastQ = int(event.split(' ')[1])

    def refreshCurrent(opt, colour): #Refreshes OptionMenu to show the current question
        global red_vars
        for i in red_vars:
            pos = 0
            for op in opList:
                if "Question "+str(opt) in quesList[pos][1:]:
                    red_vars[pos].set("Question "+str(opt))
                else:
                    red_vars[pos].set("Select Question")
                pos += 1

    def refreshMenu(opt): #Refreshes the menu of OptionMenu with updated status
        global res_var, opList, quesList, revList, currentQ
        flag = 0

        for ref in res_var[(opt-1)*5: opt*5]:
            if ref.get():
                flag = 1

        if flag == 1 and opt not in revList:
            pos = 0
            for op in opList:
                if "Question "+str(opt) in quesList[pos][1:]:
                    menu = op.nametowidget(op.cget('menu'))
                    index = menu.index("Question "+str(opt))
                    colour = 'lawn green'
                    menu.entryconfigure(index, background = colour)
                    refreshCurrent(currentQ, colour)
                pos += 1
        elif flag == 0  and opt not in revList:
            pos = 0
            for op in opList:
                if "Question "+str(opt) in quesList[pos][1:]:
                    menu = op.nametowidget(op.cget('menu'))
                    index = menu.index("Question "+str(opt))
                    colour = 'red'
                    menu.entryconfigure(index, background = 'red')
                    refreshCurrent(currentQ, colour)
                pos += 1
        elif flag == 1 and opt in revList:
            pos = 0
            for op in opList:
                if "Question "+str(opt) in quesList[pos][1:]:
                    menu = op.nametowidget(op.cget('menu'))
                    index = menu.index("Question "+str(opt))
                    colour = 'SlateBlue2'
                    menu.entryconfigure(index, background = 'SlateBlue2')
                    refreshCurrent(currentQ, colour)
                pos += 1
        elif flag == 0 and opt in revList:
            pos = 0
            for op in opList:
                if "Question "+str(opt) in quesList[pos][1:]:
                    menu = op.nametowidget(op.cget('menu'))
                    index = menu.index("Question "+str(opt))
                    colour = 'orange'
                    menu.entryconfigure(index, background = colour)
                    refreshCurrent(currentQ, colour)
                pos += 1
        return flag
                
    def seek_prev(qes): #Seeks previous question, called form Previous Button
        global lastQ, currentQ
        qes_to = "Question " + str(qes-1)
        if qes > 1:
            for i in range (0, ques_count):
                if qes_to == "Question " + str(i+1):
                    loc = float(i/ques_count)
                    text.yview_moveto(loc)
        lastQ = qes
        currentQ = qes-1
        Thread(target = refreshMenu, args = [lastQ]).start()

    def seek_next(qes): #Seeks previous question, called form Next Button
        global lastQ, currentQ
        qes_to = "Question " + str(qes+1)
        if qes < ques_count:
            for i in range (0, ques_count):
                if qes_to == "Question " + str(i+1):
                    loc = float(i/ques_count)
                    text.yview_moveto(loc)
        lastQ = qes
        currentQ = qes+1
        Thread(target = refreshMenu, args = [lastQ]).start()

    def refreshMforMenu(qno): #Refreshes Mark for Review Menu, calls for updating Question Menu
        global revList
        for choice in revList:
            rev['menu'].add_command(label="Question "+str(choice), command = lambda q = "Question "+str(choice): seek(q))                
            flag = refreshMenu(choice)
            if flag == 0:
                menu = rev.nametowidget(rev.cget('menu'))
                index = menu.index("Question "+str(choice))
                menu.entryconfigure(index, background = 'orange')
            elif flag == 1:
                menu = rev.nametowidget(rev.cget('menu'))
                index = menu.index("Question "+str(choice))
                menu.entryconfigure(index, background = 'SlateBlue2')
                    
    def mfor(qno): #Marks the question for review, adds it to the Mark for Review menu, config. Button
        global revList, rev_butList, quesList, opList, mafore, rev
        if qno in revList:
            revList.remove(qno)
            mafore.set('Select Question')
            rev['menu'].delete(0, 'end')
            rev_butList[qno-1].configure(fg = 'black', text = '  Mark for Review  ')
            Thread(target = refreshMforMenu, args = [qno]).start()
            
        else:
            revList.append(qno)
            mafore.set('Select Question')
            rev['menu'].delete(0, 'end')
            rev_butList[qno-1].configure(fg = 'orange', text = '  Unmark for Review  ')
            Thread(target = refreshMforMenu, args = [qno]).start()
    
    def cont_display(): #Sets up the content to be displayed during exam
        global op_s, opt_s, ent, answers, res_var, prog, pages, text, ques_count, test
        global vsb, mafore, rev, red_vars, rev_butList, quesList, opList

        def scrollwheel(event): #Prevents MouseWheel binding to Text
            return 'break'
        text = Text(main_frame, wrap="none", bd = 0)
        text.pack(fill="both", expand=True, padx = (10,0))
        text.bind('<MouseWheel>', scrollwheel)
        temp = 1
        ques_count = 0
        height = int(screen_height/1.2)
        width = int((2480/1748)*height)
        rev_butList = []
        prev_butList = []
        next_butList = []
        quesList = []
        opList = []
        
        for images in sorted(os.listdir(opath)):
            #Canvas, Scrollbar, Frame
            canvas = Canvas(main_frame, height = height, width = width+15, bd = 0)
            img_frame = Frame(canvas)
            img_text = Text(img_frame, bd = 0)
            vsb = Scrollbar(canvas, orient = 'vertical')
            vsb.pack(side = 'right', fill = 'y')
            vsb.configure(command = img_text.yview)
            img_text.config(yscrollcommand = vsb.set)
            img_frame.configure(height = height, width = width)

            #Insert Image into the Text
            im = Image.open(os.path.join(opath, f'Ques_{str(temp)}.png'))
            w, h = im.size
            im = im.resize((width, int((h/w)*width)), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(im)
            img_frame.pack(side = 'left', fill = 'both', expand = True)
            img_frame.pack_propagate(False)
            img_text.pack(side = 'left', fill = 'both', expand = True)
            img_text.configure(state = 'disabled')
            img_text.image_create('end', image = img)
            img_text.image = img
            text.window_create("end", window = canvas)
            text.insert("end", "\n")

            #CheckButtons
            buttons()
            options = Label(main_frame, text = "OPTIONS", font=("Open Sans",15), bg = 'white')
            text.window_create("end", window=options)
            text.insert("end", " "*16)
            
            for i in range(0, 4):
                text.window_create("end", window=op_s[i])
                k = BooleanVar()
                op_s[i].configure(variable = k, bg = 'white')
                text.insert("end", " "*8)
                res_var.append(k)
            text.insert("end", "\n\n")

            #Entry
            entry = Label(main_frame, text = "ENTRY", font=("Open Sans",15), bg = 'white')
            text.window_create("end", window=entry)
            text.insert("end", " "*19)
            text.window_create("end", window=ent)

            #Navigation/Marking Buttons
            prev = Button(main_frame, text = "  Previous  ", font=("Havelika",12), command = lambda temp = temp: seek_prev(temp), relief = 'flat')
            prev_butList.append(prev)
            mfr = Button(main_frame, text = "  Mark for Review  ", font=("Sans",12), command = lambda temp = temp: mfor(temp), relief = 'flat')
            rev_butList.append(mfr)
            nex = Button(main_frame, text = "  Next  ", font=("Havelika",12), command = lambda temp = temp: seek_next(temp), relief = 'flat')
            next_butList.append(nex)
            text.insert("end", " "*13)
            text.window_create("end", window=prev)
            text.insert("end", " "*11)
            text.window_create("end", window=mfr)
            text.insert("end", " "*11)
            text.window_create("end", window=nex)
            text.insert("end", "\n")
            m = StringVar()
            ent.configure(textvariable = m)
            res_var.append(m)
            if temp != len(os.listdir(opath)):
                text.insert("end", "\n")

            #Updation
            temp += 1
            ques_count += 1
            prog += ((1/pages)*50)
            progress['value'] = prog
            load.update_idletasks()

        #Configuration
        text.configure(state="disabled")
        prev_butList[0].configure(state = "disabled")
        next_butList[-1].configure(state = "disabled")

        #SideFrames Initialization
        info_lab = Label(toggle_frame, text = "Quick Question Navigation", bg = 'white', font=("Sans",12))
        info_lab.pack(side = 'top', anchor = 'nw', pady = 10)
        lab_frame = Frame(toggle_frame, bg = 'white')
        lab_frame.pack(side = 'left')#, fill = 'y')
        opmenu_frame = Frame(toggle_frame, bg = 'white')
        opmenu_frame.pack(side = 'left')#, fill = 'y')
        style = Style()
        style.configure('my.TMenubutton', font=('sans', 12))

        #OptionMenu
        red_vars = []
        for i in range (0, len(sections)):
            qnoList = []
            if sections[i] == 0:
                try:
                    for qno in range(0, sections[i+1]+1):
                        qnoList.append("Question "+str(qno))
                except:
                    for qno in range(sections[-1], ques_count+1):
                        qnoList.append("Question "+str(qno))
            else:
                try:
                    for qno in range(sections[i], sections[i+1]+1):
                        qnoList.append("Question "+str(qno))
                except:
                    for qno in range(sections[-1], ques_count+1):
                        qnoList.append("Question "+str(qno))

            ques_redir = "var"+str(i)
            ques_redir = StringVar()
            red_vars.append(ques_redir)
            v = "tog"+str(i)
            v = OptionMenu(opmenu_frame, ques_redir, *qnoList, command = seek, style = 'my.TMenubutton')
            opList.append(v)
            v["menu"].config(font = ('Sans', 12))
            label = Label(lab_frame, text = section_name[i], bg = 'white', font=("Sans",12))
            label.pack(side = 'top', anchor = 'nw', padx = (0,10), pady = (2,0))
            ques_redir.set("Select Question")
            v.pack(side = 'top', anchor = 'ne', padx = (0,10))
            quesList.append(qnoList)
            
        mafore = StringVar()
        mafore.set("Select Question")
        labelm = Label(lab_frame, text = "Marked for Review", bg = 'white', font=("Sans",12))
        labelm.pack(side = 'top', anchor = 'nw', padx = (0,10), pady = (2,0))
        rev = OptionMenu(opmenu_frame, mafore, *[None], command = seek, style = 'my.TMenubutton')
        rev["menu"].config(font = ('Sans', 12))
        rev.pack(side = 'top', anchor = 'ne', padx = (0,10))
        red_vars[0].set("Question 1")

        #Indicatiors
        ligand_frame = Frame(base_frame, bg = 'white')
        ligand_frame.pack(anchor = 'se', side = 'bottom')
        color_frame = Frame(ligand_frame, bg = 'white')
        color_frame.pack(side = 'left', pady = (0,10))
        des_frame = Frame(ligand_frame, bg = 'white')
        des_frame.pack(side = 'right', pady = (0,10))
        colors = ['lawn green', 'red', 'SlateBlue2', 'orange']
        des = ['Answered', 'Unanswered but Seen', 'Answered and Marked for Review', 'Unanswered and Marked for Review']
        for color, description in zip(colors, des):
            col = Label(color_frame, text = "    ", bg = color, bd = 0, font = 10)
            col.pack(side = 'top', anchor = 'nw', padx = (0,10))
            des = Label(des_frame, text = description, bg = 'white', font=("Sans",10), justify = 'left')
            des.pack(side = 'top', anchor = 'nw', padx = (0,10), pady = (2,0))
        #Complete Loading
        load.destroy()
        #Threads
        time_th = Thread(target = timer).start()
        #mon_th = Thread(target = Monitor).start()

    def ans_append(): #Appends the responses to the answers list
        global res_var, answers
        a = 0
        while a <= len(res_var)-4:
            for i in range(a,a+4):
                answers.append(res_var[i].get())
            answers.append(res_var[a+4].get())
            a += 5
        generate_ans()

    def generate_ans(): #Writes the respones in a file, initiates mailing Thread and destroys exam window
        global apath, answers
        details()
        with open(os.path.join('Student Responses', apath), 'w+') as file:
            file.write(str(answers))
        Thread(target = mail_res).start()
        dest()

    def mail_res(): #Starts the mailing, displays an error if it fails to        
        send = Toplevel(initial)
        setup(send)
        send.title("Sucessful Submission")
        send.attributes('-topmost', True)
        sts = StringVar()
        lab = Label(send, textvariable = sts)
        sts.set("Sucessfully Submitted!\n"
                +"Sending an Email of your responses...")
        lab.grid(row = 0, column = 1, padx = 20, pady = 20)
        but = ttk.Button(send, text = "Exit", command = send.destroy, state = 'disabled')
        but.grid(row = 1, column = 1, padx = 20, pady = 20)
        log = Label(send, image = logo)
        log.image = logo
        log.grid(row = 0, column = 0, rowspan = 2, padx = 20, pady = 20)
        try:
            term.destroy()
        except:
            pass
        try:
            mail.Send_response(res_email)
            sts.set("Email has been sent successfully!")
            but.config(state = 'normal')
        except Exception as e:
            print(e)
            sts.set(("Failed to send Email!\n"
                     +"This may happend due to various reasons, see USER GUIDE.\n"
                     +"A local copy of your response has been saved.\n"
                     +"You may find it in PIERA-ZONE\Student Responses.\n"
                     +"You can share it as per the instructions."))
            but.config(state = 'normal')

    def conf(): #Asks for confirmation to submit before completion time
        global confs
        confs = Toplevel(ques_win)
        ques_win.focus_set()
        confs.title("Notice!")
        setup(confs)
        confs.bell()
        lab = Label(confs, text = ("Are you sure you want to SUBMIT the test?\n"
                                   +"This action CANNOT be undone.\n"
                                   +"If this was a mistake you can SAFELY close this pop-up."))
        lab.grid(row = 0, column = 1, padx = 20, pady = 20)
        but = ttk.Button(confs, text = "Continue", command = final_submit)
        but.grid(row = 1, column = 1, padx = 20, pady = 20)
        log = Label(confs, image = logo)
        log.image = logo
        log.grid(row = 0, column = 0, rowspan = 2, padx = 20, pady = 20)

        confs.protocol("WM_DELETE_WINDOW", Thread(target = on_closing).start)

    def timer(): #Runs the countdown timer in a different Thread, submits upon completion
        global etime, stop_threads       
        lo_lab.destroy()
        temp = etime[0]*3600 + etime[1]*60 + etime[2]
        hours = etime[0]
        mins = etime[1]
        secs = etime[2]
        hour = StringVar() 
        minute = StringVar() 
        second = StringVar()

        sub_frame = Frame(timer_frame, width = 100, bg = 'black')
        sub_frame.pack(fill = 'both', side = 'left', ipady = 0, expand = True)
        sub_frame.pack_propagate(True)
        img = Image.open (os.path.join(data_dir, "logo.png"))
        img = img.resize((25, 25), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(img)
        log = Label(sub_frame, image = image, bg = 'black', bd = 0)
        log.image = image
        final_sub = Button(sub_frame, text = "SUBMIT", bg = 'green', fg = 'white', width = 15, font=("Comic Sans MS",11), command = conf)
        final_sub.pack(padx = 30, fill = 'y', anchor = 'e', side = 'right')
        log.pack(side = 'left', anchor = 'w', expand = True, padx = (5,0))
        l = Label(timer_frame, text = "Time remaing ", bg = 'black', fg = 'white', font=("Comic Sans MS",18))
        l.pack(side = 'left')  
        hourEntry= Label(timer_frame, width=3, font=("Comic Sans MS",18,""), textvariable=hour, bg = 'black', fg = 'white') 
        hourEntry.pack(side = 'left')    
        minuteEntry= Label(timer_frame, width=3, font=("Comic Sans MS",18,""), textvariable=minute, bg = 'black', fg = 'white') 
        minuteEntry.pack(side = 'left')        
        secondEntry= Label(timer_frame, width=3, font=("Comic Sans MS",18,""), textvariable=second, bg = 'black', fg = 'white') 
        secondEntry.pack(side = 'left')
        while temp > -1:
            mins,secs = divmod(temp, 60)  
            hours=0
            if mins >60: 
                hours, mins = divmod(mins, 60)        
            hour.set("{0:2d}".format(hours)) 
            minute.set("{0:2d}".format(mins)) 
            second.set("{0:2d}".format(secs))
            timer_frame.update()
            time.sleep(1)
            if temp == 0 and Toplevel.winfo_exists(ques_win) == 1: 
                final_submit()
            temp -= 1

    def loading(): #Displays loading progress while setting up the exam
        global load, progress      
        load = Toplevel()
        load.title("Loading")
        load.attributes('-topmost', True)
        load.overrideredirect(True)
        lab = Label(load, text = ("Preparing Your Exam, Please Wait!\nPlease DO NOT open any other window.\n"
                                  +"Doing so may lead to immidiate Termination."))
        lab.grid(row = 0, column = 1, padx = 20, pady = 20)
        progress=Progressbar(load,orient=HORIZONTAL,length=200,mode='determinate')
        progress.grid(row = 1, column = 1, padx = 20, pady = 20)
        log = Label(load, image = logo)
        log.image = logo
        log.grid(row = 0, column = 0, rowspan = 2, padx = 20, pady = 20)
        load.update_idletasks()
        w_req, h_req = load.winfo_width(), load.winfo_height()
        w_form = load.winfo_rootx() - load.winfo_x()
        w = w_req + w_form*2
        h = h_req + (load.winfo_rooty() - load.winfo_y()) + w_form
        x = (load.winfo_screenwidth() // 2) - (w // 2)
        y = (load.winfo_screenheight() // 2) - (h // 2)
        load.geometry(f'{w_req}x{h_req}+{x}+{y}')

    def launch_main(): #Creates the exam window
        global ques_win, timer_frame, main_frame, lo_lab, toggle_frame, base_frame
        ques_win = Toplevel(initial)
        ques_win.bind("<Escape>", close_escape)

        ques_win.attributes("-fullscreen", True)
        ques_win.configure(bg = 'black')
        ques_win.focus_force()

        timer_frame = Frame(ques_win, width = 100, height = 100, bg = 'black')
        timer_frame.pack(anchor = 'e', fill = 'x')
        base_frame = Frame(ques_win, bg = 'white')
        base_frame.pack(fill = 'both', expand = 'yes')
        main_frame = Frame(base_frame, bg = 'white')
        main_frame.pack(fill = 'both', expand = 'yes', side = 'left')
        toggle_frame = Frame(base_frame, bg = 'white')
        toggle_frame.pack(side = 'top', anchor = 'ne')

        lo_lab = Label(timer_frame, text = "Loading Questions...", bg = 'black', fg = 'white',  font=("Comic Sans MS",18))
        lo_lab.pack(anchor = 'e')
        
        disp_th = Thread(target = cont_display).start()
    
    loading()
    conv_th = Thread(target = Convert).start()
    
#________________________________________________Main Window________________________________________________

#________________________________________________Teacher________________________________________________
    
def teacher(): #Redirects to teacher's window
    with open(f"{cache_dir}\\UsageType.txt", 'r') as file:
        typ = file.read()
        file.close()
    if typ == '0': #Organisation mode
        Teacher.orgSet()
    else: #Individual mode
        Teacher.indSet()
    initial.iconify()
#________________________________________________About________________________________________________        

def about(): #Displays basic information   
    def web(link): #Main website
        webbrowser.open(link)
            
    about = Toplevel()
    about.title("About")
    about.resizable(False, False)
    setup(about)
    with open(os.path.join(data_dir, "About.txt"),'r', encoding = 'utf8') as file:
        abt = file.read()
        abt_disp = abt.split('-*-')[0]
        link = abt.split('-*-')[1].replace("-*-", '')
        file.close()
    l1 = Label(about, text = abt_disp, font=("Helvetica", 11), justify = 'left')
    l1.pack(padx = 20, pady = (10,0))

    w = Button(about, text = "Visit our Website", command = lambda: web(link), font=("Helvetica", 11,'underline'),borderwidth=0, fg = 'blue')
    w.pack(side = 'bottom', pady = (0,10))    

#________________________________________________Student________________________________________________
    
def student(): #Pre-exam GUI
    global students
    proceed = dataCollection()
    if proceed != 0:
        initial.iconify()
        students = Toplevel(initial)
        students.title("Student")
        students.configure(bg = 'white')
        students.attributes('-topmost', True)
        setup(students)
        top_frame = Frame(students, bg = 'white')
        top_frame.grid(row = 0, column = 0, pady = 10)
        head_img = Image.open(os.path.join(data_dir, 'details.png'))
        head_img = head_img.resize((193, 45), Image.ANTIALIAS)
        head_img = ImageTk.PhotoImage(head_img)
        head_lab = Label(top_frame, image = head_img, bg = 'white')
        head_lab.image = head_img
        head_lab.pack(side = 'left', padx = 10, fill = 'both')

        def verify(): #Veryfy entries
            flag = 1
            global name_entry,class_entry,email_entry,add_entry,roll_entry
            chk = [name_entry,class_entry,roll_entry,email_entry]
            val = ['Name', 'Batch', 'Roll', 'Email']
            for c in range(len(chk)):
                if chk[c].get() == '':
                    messagebox.showerror('Error', f'{val[c]} cannot be empty!', parent = students)
                    flag = 0
                    break
            if flag == 1:
                instruct()

        def instruct(): #Launch instructions window
            with open(os.path.join(cache_dir, "Student_Input.txt"), 'w+') as file:
                file.truncate(0)
                file.write(name_entry.get()+","+class_entry.get()+","+roll_entry.get()+","+email_entry.get()+","+add_entry.get())
                file.close()
            def Launch():
                instructions.destroy()
                Thread(target = Ques_Disp_GUI).start()
            def ver():
                cont.config(state = DISABLED if var1.get() == 0 else NORMAL)
            def itimer():
                global itop_frame, itime
                itemp = itime[0]*3600 + itime[1]*60 + itime[2]
                hours = itime[0]
                mins = itime[1]
                secs = itime[2]
                hour = StringVar() 
                minute = StringVar() 
                second = StringVar()
                secondEntry= Label(itop_frame, width=3, textvariable=second, bg = 'white', fg = 'red', font = 15) 
                secondEntry.pack(side = 'right', padx = (0, 10))
                minuteEntry= Label(itop_frame, width=3, textvariable=minute, bg = 'white', fg = 'red', font = 15) 
                minuteEntry.pack(side = 'right', padx = (0, 10)) 
                hourEntry= Label(itop_frame, width=3, textvariable=hour, bg = 'white', fg = 'red', font = 15) 
                hourEntry.pack(side = 'right', padx = (0, 10))
                time_lab = Label(itop_frame, text = 'Time to read:', bg = 'white', fg = 'red', font = 15)
                time_lab.pack(side = 'right', padx = (0, 10))            
                while itemp > -1:
                    mins,secs = divmod(itemp, 60)  
                    hours=0
                    if mins >60: 
                        hours, mins = divmod(mins, 60)        
                    hour.set("{0:2d}".format(hours)) 
                    minute.set("{0:2d}".format(mins)) 
                    second.set("{0:2d}".format(secs))
                    itop_frame.update_idletasks()
                    time.sleep(1)
                    if itemp == 0 and Toplevel.winfo_exists(instructions) == 1: 
                        instructions.destroy()
                        Ques_Disp_GUI()
                    elif Toplevel.winfo_exists(instructions) == 0:
                        break
                    itemp -= 1

            global students, instruct_path
            students.destroy()
            with open (os.path.join(data_dir, 'Mandatory Instructions.txt'), 'r') as file:
                data1 = file.read()
                file.close()
            with open (os.path.join(exam_folder, f'{exam_name} Instructions.pzn'), 'r') as file:
                data2 = file.read()
                file.close()
            instructions = Toplevel(initial)
            instructions.title("Instructions")
            instructions.attributes('-topmost', True)
            setup(instructions)
            instructions.configure(bg = 'white') #______________________________________Instructions Tittle Frame
            global itop_frame
            itop_frame = Frame(instructions, bg = 'white') 
            itop_frame.pack(side = 'top', pady = 10, anchor = 'w', fill = 'x')
            head_img = Image.open(os.path.join(data_dir, 'instructions.png'))
            head_img = head_img.resize((193, 45), Image.ANTIALIAS)
            head_img = ImageTk.PhotoImage(head_img)
            head_lab = Label(itop_frame, image = head_img, bg = 'white')
            head_lab.image = head_img
            head_lab.pack(side = 'left', padx = 10, fill = 'both')
            disp_inst_frame = Frame(instructions, bg = 'white') #______________________Instructions Display Frame
            disp_inst_frame.pack(side = 'top', fill = 'both', padx = 10, pady = 10)
            inst_text_frame = Frame(disp_inst_frame, width = 995, height = 400, bg = 'white')
            inst_text_frame.pack(side = 'left', expand = False, fill = 'x')
            inst_text_frame.pack_propagate(False)
            inst_text = Text(inst_text_frame, font = ('Roboto', 15), wrap = 'word', bd = 0)
            inst_vsb = Scrollbar(disp_inst_frame, command = inst_text.yview)
            inst_text.configure(yscrollcommand = inst_vsb.set)
            inst_text.pack(padx = 10, pady = (0, 10), fill = 'x')
            inst_text.insert('end', data1)
            inst_text.insert('end', data2)
            inst_text.configure(state = 'disabled')
            inst_vsb.pack(side = 'right', fill = 'y', padx = (0, 10), pady = (0, 10))
            start_img = Image.open(os.path.join(data_dir, 'start.png'))
            start_img = start_img.resize((119, 45), Image.ANTIALIAS)
            start_img = ImageTk.PhotoImage(start_img)
            cont = Button(instructions, image = start_img, command = Launch, bg = 'white', relief = 'flat')
            cont.img = start_img
            cont.pack(side = 'bottom', pady = (0, 20))
            var1 = IntVar()
            ag = Checkbutton(instructions, text = "I have read the the insructions carefully and agree to the T&C",
                             font=("Comic Sans MS", 12), variable = var1, command = ver, bg = 'white')
            ag.var = var1
            ag.pack(side = 'bottom', pady = 10, padx = 10)
            ag.var = var1
            Thread(target = itimer).start()
            ver()

        global name_entry,class_entry,email_entry,add_entry,roll_entry
        name = Label(students, text = "Name: ", font=("Comic Sans MS", 15), bg = 'white')
        name.grid(row = 1, column = 0, padx = 20, sticky = 'e')
        name_entry = Entry(students, font=("Open Sans", 15), width = 32, relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
        name_entry.grid(row = 1, column = 1, padx = 20)
        clas = Label(students, text = "Class/Batch: ", font=("Comic Sans MS", 15), bg = 'white')
        clas.grid(row = 2, column = 0, padx = 20, sticky = 'e')
        class_entry = Entry(students, font=("Open Sans", 15), width = 32, relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
        class_entry.grid(row = 2, column = 1, padx = 20)
        roll = Label(students, text = "Roll Number: ", font=("Comic Sans MS", 15), bg = 'white')
        roll.grid(row = 3, column = 0, padx = 20, sticky = 'e')
        roll_entry = Entry(students, font=("Open Sans", 15), width = 32, relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
        roll_entry.grid(row = 3, column = 1, padx = 20)
        email = Label(students, text = "Email Address: ", font=("Comic Sans MS", 15), bg = 'white')
        email.grid(row = 4, column = 0, padx = 20, sticky = 'e')
        email_entry = Entry(students, font=("Open Sans", 15), width = 32, relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
        email_entry.grid(row = 4, column = 1, padx = 20)
        add = Label(students, text = "Other Info.: ", font=("Comic Sans MS", 15), bg = 'white')
        add.grid(row = 5, column = 0, padx = 20, sticky = 'e')
        add_entry = Entry(students, font=("Open Sans", 15), width = 32, relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
        add_entry.grid(row = 5, column = 1, padx = 20)
        con_img = Image.open(os.path.join(data_dir, 'continue.png'))
        con_img = con_img.resize((156, 45), Image.ANTIALIAS)
        con_img = ImageTk.PhotoImage(con_img)
        begin = Button(students, image = con_img, command = verify, relief = 'flat', bg = 'white')
        begin.img = con_img
        begin.grid(row = 6, column = 0, columnspan = 2, pady = 20)

#________________________________________________Window Setup________________________________________________

def uType(): #User type
    utype = Toplevel(initial)
    utype.title('Configuration')
    utype.configure(bg = 'white')
    setup(utype)
    prog_dir = 'Program Files'
    data_dir = os.path.join(prog_dir, 'Data Files')
    cache_dir = os.path.join(prog_dir, 'Cache')

    def set_org():
        with open(os.path.join(cache_dir, "UsageType.txt"), 'w') as file:
            file.truncate()
            file.write('0')
            file.close()
        messagebox.showinfo('Success', 'Successfully configured to organisation!')
        utype.destroy()
        disp_type()

    def set_ind():
        with open(os.path.join(cache_dir, "UsageType.txt"), 'w') as file:
            file.truncate()
            file.write('1')
            file.close()
        messagebox.showinfo('Success', 'Successfully configured to individual!')
        utype.destroy()
        disp_type()

    head_lab = Label(utype, text = 'Chooese what best describes your purpose', font = ('Roboto', 12), fg = 'red', bg = 'white')
    head_lab.pack(side = 'top', pady = 20, padx = 20)
    org_frame = Frame(utype, bg = 'white', highlightthickness = 1, highlightbackground = 'black')
    org_frame.pack(side = 'top', fill = 'x', padx = 20, pady = (0,20))
    org_but = Button(org_frame, text = 'ORGANISATION', font = ('Roboto', 15), relief = 'flat', command = set_org)
    org_but.pack(fill = 'both')
    ind_frame = Frame(utype, bg = 'white', highlightthickness = 1, highlightbackground = 'black')
    ind_frame.pack(side = 'top', fill = 'x', padx = 20, pady = (0,20))
    ind_but = Button(ind_frame, text = 'INDIVIDUAL', font = ('Roboto', 15), relief = 'flat', command = set_ind)
    ind_but.pack(fill = 'both')

def disp_type(): #Diaplay user type
    try:
        with open(os.path.join(cache_dir, "UsageType.txt"), 'r') as file:
            typ = file.read()
            file.close()
        if typ == '0':
            config_lab.configure(text = 'ORGANISATION')
        else:
            config_lab.configure(text = 'INDIVIDUAL')
    except:
        with open(os.path.join(cache_dir, "UsageType.txt"), 'w+') as file:
            file.write('0')
            file.close()
        disp_type()
    
#File paths
global data_dir, cache_dir, prog_dir
prog_dir = os.path.join(os.getcwd(),'Program Files') #Optimized
data_dir = os.path.join(prog_dir, 'Data Files')
cache_dir = os.path.join(prog_dir, 'Cache')

def setup(temp_win): #Standard setup for all windows
    temp_win.resizable(False, False)
    temp_win.iconbitmap(os.path.join(data_dir, 'logo.icns'))
def cpyrc(): #Copyright badge
    webbrowser.open("https://github.com/AST07/PIERA-ZONE")
#__Main GUI__
initial = Tk()
initial.title("Welcome to PIERA-ZONE")
setup(initial)

canvas = Canvas(initial, width = 960, height = 540)
canvas.pack()
img = Image.open (os.path.join(data_dir, "PIERA-ZONE.png"))
img = img.resize((960, 540), Image.ANTIALIAS)
spimg = ImageTk.PhotoImage(img)
canvas.create_image(482, 272, image = spimg)

teach_img = Image.open(os.path.join(data_dir, 'teacher.png'))
teach_img = teach_img.resize((141, 45), Image.ANTIALIAS)
teach_img = ImageTk.PhotoImage(teach_img)
teach = Button(initial, image = teach_img, command = teacher, relief = 'flat', bg = 'ivory2')
teach.img = teach_img
canvas.create_window(482, 292, window=teach)
stud_img = Image.open(os.path.join(data_dir, 'student.png'))
stud_img = stud_img.resize((141, 45), Image.ANTIALIAS)
stud_img = ImageTk.PhotoImage(stud_img)
stud = Button(initial, image = stud_img, command = student, relief = 'flat', bg = 'ivory2')
stud.img = stud_img
canvas.create_window(482, 392, window=stud)
about = ttk.Button(initial, text = "About", command = about)
canvas.create_window(950, 535, anchor = 'se', window=about)
config_but = ttk.Button(initial, text = "Configure", command = uType)
canvas.create_window(870, 535, anchor = 'se', window=config_but)
crimg = Image.open (os.path.join(data_dir, "GitHub-Mark-120px-plus.png"))
crimg = crimg.resize((32, 32), Image.ANTIALIAS)
copyright_badge = ImageTk.PhotoImage(crimg)
cyp = Button(initial, image = copyright_badge, command = cpyrc, borderwidth = 0, cursor = 'hand2')
canvas.create_window(12, 535, anchor = 'sw', window=cyp)
config_lab = Label(initial, fg = 'red')
canvas.create_window(90, 20, anchor = 'se', window=config_lab)
disp_type()
global logo #Logo image
logo_img = Image.open (os.path.join(os.getcwd(),data_dir, 'logo.png'))
logo_img = logo_img.resize((200, 200), Image.ANTIALIAS)
logo = ImageTk.PhotoImage(logo_img)
global screen_width, screen_height
screen_width = initial.winfo_screenwidth()
screen_height = initial.winfo_screenheight()
initial.mainloop()
