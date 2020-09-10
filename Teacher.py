"""@Aditya Singh Tejas, Rikhil Gupta, Aditya Sharma (C) 2020 PIERA-ZONE"""
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import re
from datetime import datetime
import SQLiteSetup as sql 
import random 
import webbrowser 
from threading import Thread
import SendMail as mail
import shutil
from threading import Thread
from prettytable import PrettyTable
from fpdf import FPDF
import requests
import csv

def Evaluate(): #Evaluation GUI
	evalt = Toplevel()
	setup(evalt)
	evalt.title('Evaluate')
	evalt.configure(bg = 'white')

	def loading(): #Display progress while the evaluation happens
		global load, exam, progress
		keycon.destroy()
		load = Toplevel()
		setup(load)
		load.title('Processing')
		lab = Label(load, text = 'Processing results. Please wait!')
		lab.pack(padx = 10, pady = 10)
		progress = ttk.Progressbar(load, orient ='horizontal' , length=200, mode='determinate')
		progress.pack(padx = 30, pady = 10)
		load.update()
		start()

	def askResDir(): #Ask the directory containing responses
		global folder_name
		fol_entry.configure(state = 'normal')
		folder = filedialog.askdirectory()
		folder_name.set(folder)

	def askKey(): #Ask thr exam directory (Auto created by PZ Exam Editor)
		global key_filename
		key_file = filedialog.askdirectory()
		if key_file:
			key_filename.set(key_file)

	def start(): #Begin evaluation 
		global prog, load, progress

		def gen_key(exam_dir): #Generate the key
			global marking, pattern
			for file in os.listdir(exam_dir):
				if file[-7:-4] == 'Key':
					key_filename = os.path.join(exam_dir, file)

			for file in os.listdir(os.path.join(exam_dir, 'Raw Data')):
				if file[-11:-4] == 'Details':
					det_filename = os.path.join(exam_dir, 'Raw Data', file)

			with open(det_filename, 'r') as file:
				cont = eval(file.read())
				batch = len(cont[5])//3
				marking_raw = cont[5][batch:batch*2]
				pattern = cont[5][batch*2:batch*3]
				marking = []
				for i in range(len(pattern)):
					pattern[i] = int(pattern[i])-1
					for j in range(0, 3):
						marking.append(int(marking_raw[i].split(',')[j]))	
				pattern.pop(0) 		
				file.close() 		
			with open(key_filename,'r') as file:
				key = []
				data = file.read()
				data = data[1:-1]
				data = data.split(", ")
				beg = 0
				end = 5
				for i in range (0, len(data)//5):
					ktemp = []
					for k in data[beg:end]:
						ktemp.append(eval(k))
					key.append(ktemp)
					beg += 5
					end += 5
				file.close()
			return key

		def calculate(key, ans_filename): #Calcualte and produce the output

			def decrypt(val):
				final_str = ''
				if val[0] == 'True':
					final_str += 'A,'
				if val[1] == 'True':
					final_str += 'B,'
				if val[2] == 'True':
					final_str += 'C,'
				if val[3] == 'True':
					final_str += 'D,'
				if val[4] != '':
					final_str += val[4]
				try:
					if final_str[-1] == ',':
						final_str = final_str[:-1]
				except:
					pass
				return final_str

			global pattern, marking, rpos	
			with open(ans_filename,'r') as file:
				ans = []
				data = file.read()
				data = data[1:-1]
				data = data.split(", ")
				beg = 0
				end = 5
				for i in range (0, len(data)//5):
					ans.append(data[beg:end-1] + [eval(data[end-1])])
					beg += 5
					end += 5
				student_det = os.path.basename(file.name)
				student_det = student_det[0:-4]

			tmarking = list(marking)
			tpattern = list(pattern)
			cor = tmarking[0]
			wro = tmarking[1]
			unat= tmarking[2]  
			score = 0
			status = []
			obtainedmarks = []
			wrongqs = []
			correctqs = []
			unatqs = []
			ques = 1
			
			for i,j in zip(key, ans):
				if i == j:
					status.append("Correct")
					obtainedmarks.append(cor)
					score=score+cor
					correctqs.append(ques)
				else:
					if j[0] == j[1] == j[2] == j[3] == 'False' and j[4] == '': 
						status.append("Unattempted")
						obtainedmarks.append(unat)
						score=score+unat
						unatqs.append(ques)
					else:
						status.append("Incorrect")
						obtainedmarks.append(wro)
						score=score+wro
						wrongqs.append(ques)	
				if ques == tpattern[0]:
					del tmarking[0:3]
					if len(tpattern) != 1:
						del tpattern[0]
					cor = tmarking[0]
					wro = tmarking[1]
					unat= tmarking[2]
				ques += 1

			#Create Table
			table = PrettyTable(['Question Number', 'Your answer', 'Correct answer', 'Status', 'Marks Obtained'])
			for i in range(0, len(ans)):
				table.add_row([str(i+1), decrypt(ans[i]), decrypt(key[i]), str(status[i]), str(obtainedmarks[i])])
			#Other Details
			prestring = f"""Exam: {student_det.split("_")[0]}
							\nStudent Name: {student_det.split("_")[1]}
							\nRoll: {student_det.split("_")[3]}
							\nBatch: {student_det.split("_")[2]}\n\n"""
			poststring = f"""\n\nFinal Result:
							\nCorrectly Answered Questions: {correctqs}
							\nIncorrectly Answered Questions: {wrongqs}
							\nUnattempted Questions: {unatqs}
							\nFinal Score: {score}"""
			final_str = prestring + str(table) + poststring

			#Create PDF
			pdf = FPDF() 
			pdf.add_page() 
			pdf.set_font("Courier", size = 10) 
			pdf.multi_cell(200, 5, txt = final_str, align = 'L')
			pdf.output(os.path.join('Exam Results', parent_folder, f'{rpos}{student_det.split("_")[0]} Results {student_det.split("_")[2]} {student_det.split("_")[1]}.pdf'))
			rpos += 1
			return score, student_det

		folder_path = folder_name.get()
		key_path = key_filename.get()
		key = gen_key(key_path)
		global parent_folder, total, exam, rpos
		exam = os.path.basename(key_path)[:-6]
		parent_folder = f'{exam} Results'
		total = len(os.listdir(folder_path))
		rpos = 0
		prog = 0
		try:
			os.mkdir(os.path.join('Exam Results', parent_folder))
		except:
			shutil.rmtree(os.path.join('Exam Results', parent_folder))
			os.mkdir(os.path.join('Exam Results', parent_folder))
		emails = []
		try: 
			db.deleteTable(f'{exam}')
		except:
			pass
		db.addTable(f'{exam}', 'results')
		for file in os.listdir(folder_path):
			try:
				score,student_det = calculate(key, os.path.join(folder_path, file))
				name = student_det.split("_")[1]
				batch = student_det.split("_")[2]
				roll = student_det.split("_")[3]
				email = student_det.split("_")[4]
				others = student_det.split("_")[5]
				values = (roll,name,batch,email,others,score)
				db.addRecord(f'{exam}', values)
				emails.append(email)
			except:
				pass
			prog += ((1/total)*100)
			progress['value'] = prog
			load.update_idletasks()
		with open(os.path.join('Exam Results', parent_folder, f"""_{exam} Emails_.txt"""), 'w+') as ifile:
			ifile.write(str(emails))
			ifile.close()
		messagebox.showinfo('Success', 'Evaluation sucessfully completed!')
		load.destroy()

	def editKey():

		def addParentheses(event = None):
			key_text.focus_set()
			key_text.insert('insert', '(),')
			pos = key_text.index('insert')
			line = int(pos.split('.')[0])
			char = int(pos.split('.')[1])
			key_text.mark_set('insert', "%d.%d" % (line,char-2))

		def adecrypt(val):
			final_str = ''
			if val[0] == 'True':
				final_str += 'a,'
			if val[1] == 'True':
				final_str += 'b,'
			if val[2] == 'True':
				final_str += 'c,'
			if val[3] == 'True':
				final_str += 'd,'
			if val[4] != '':
				final_str += val[4]
			try:
				if final_str[-1] == ',':
					final_str = final_str[:-1]
			except:
				pass
			final_str = f"({final_str}),"
			return final_str

		def saveKey():
			final_key = []
			key_list = re.findall(r"\(([a-d,0-9]+)\)", key_text.get('1.0', 'end-1c'))
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
			with open(kkey_filename, 'w+') as kfile:
				kfile.truncate()
				kfile.write(str(final_key))
				kfile.close()
			messagebox.showinfo('Sucess', 'Answer key updated sucessfully!')
			key_edit.destroy()

		def retrieveKey():
			global kkey_filename
			key_path = key_filename.get()
			for file in os.listdir(key_path):
				if file[-7:-4] == 'Key':
					kkey_filename = os.path.join(key_path, file)
			with open(kkey_filename, 'r') as kfile:
				key_data = eval(kfile.read())
				kfile.close()

			insert_key = ''
			beg = 0
			end = 5
			for k in range(0, len(key_data)//5):
				insert_key += adecrypt(key_data[beg:end])
				beg += 5
				end += 5
			return insert_key

		global key_edit
		key_edit = Toplevel()
		key_edit.title('Edit Answer Key')
		setup(key_edit)
		key_frame = Frame(key_edit, highlightthickness = 1, highlightbackground = 'black', bg = 'white')
		key_frame.pack(padx = 10, pady = 10, side = 'top', anchor = 'w')
		sub_button = ttk.Button(key_edit, text = 'Submit', command = saveKey)
		sub_button.pack(side = 'bottom', anchor = 'e', padx = 10, pady = (0,10))
		top_key_frame = Frame(key_frame, bg = 'RoyalBlue4')
		top_key_frame.pack(side = 'top', fill = 'x', pady = (0, 10))
		opt = StringVar()
		add_but = ttk.Button(top_key_frame, text = 'Insert', command = addParentheses)
		add_but.pack(side = 'right', anchor = 's', padx = 10)
		lab = Label(top_key_frame, text = 'Answer Key', bg = 'RoyalBlue4', font = ('Roboto', 12), fg = 'white')
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
		key_edit.bind('<Control-q>', addParentheses)
		key_text.insert(END, retrieveKey())

	def conKey():
		global keycon
		keycon = Toplevel()
		keycon.title('Confirmation')
		keycon.configure(bg = 'white')
		setup(keycon)
		keycon.bell()
		con_lab = Label(keycon, text = 'Continue with the given key?', bg = 'white')
		con_lab.pack(side = 'top', padx = 60, pady = 10)
		bot_frame = Frame(keycon)
		bot_frame.pack(side = 'bottom', fill = 'x')
		edit = ttk.Button(bot_frame, text = 'Edit key', command = editKey)
		edit.pack(side = 'right', pady = 10, padx = 10)
		con = ttk.Button(bot_frame, text = 'Continue', default = 'active', command = loading)
		con.pack(side = 'right', padx = (10,0), pady = 10)

	top_frame = Frame(evalt, bg = 'white')
	top_frame.pack(side = 'top', fill = 'x', pady = (10,0))
	head_img = Image.open(os.path.join(file_dir, 'evaluation.png'))
	head_img = head_img.resize((193, 45), Image.ANTIALIAS)
	head_img = ImageTk.PhotoImage(head_img)
	head_lab = Label(top_frame, image = head_img, bg = 'white')
	head_lab.image = head_img
	head_lab.pack(side = 'left', padx = 10, fill = 'both')

	base_frame = Frame(evalt, bg = 'white')
	base_frame.pack(side = 'top', padx = 20, pady = (20,10))
	left_base_frame = Frame(base_frame, bg = 'white')
	left_base_frame.pack(side = 'left', padx = (0, 20))
	right_base_frame = Frame(base_frame, bg = 'white')
	right_base_frame.pack(side = 'right', padx = (20, 0))

	fol_lab = Label(left_base_frame, text = 'Response Folder', bg = 'white', font = ('Roboto', 12))
	fol_lab.pack(side = 'top', pady = (15,2), anchor = 'e')
	global folder_name, key_filename
	folder_name = StringVar()
	fol_entry = ttk.Entry(base_frame, textvariable = folder_name, width = 32)
	fol_entry.pack(side = 'top', pady = (20,10))
	res_browse = ttk.Button(right_base_frame, text = 'Browse', command = askResDir)
	res_browse.pack(side = 'top', pady = (10,7))

	key_lab = Label(left_base_frame, text = 'Exam Folder', bg = 'white', font = ('Roboto', 12))
	key_lab.pack(side = 'top', pady = (15,0), anchor = 'e')
	key_filename = StringVar()
	key_entry = ttk.Entry(base_frame, textvariable = key_filename, width = 32)
	key_entry.pack(side = 'top', pady = 10)
	key_browse = ttk.Button(right_base_frame, text = 'Browse', command = askKey)
	key_browse.pack(side = 'top', pady = (10,0))

	start_img = Image.open(os.path.join(file_dir, 'start.png'))
	start_img = start_img.resize((119, 45), Image.ANTIALIAS)
	start_img = ImageTk.PhotoImage(start_img)
	start_but = Button(evalt, image = start_img, bg = 'white', relief = 'flat', command = conKey)
	start_but.image = start_img
	start_but.pack(side = 'bottom', padx = 10, pady = 20)

def Results(): #Results GUI

	def MassMail(): #Mass mail resuts to all the students
		def send(email, file): #Send email
			chk = mail.Send_results(email, file, tab)

		sprog = 0
		sload = Toplevel()
		sload.title('Processing')
		setup(sload)
		lab = Label(sload, text = 'Sending email(s). Please wait!')
		lab.pack(padx = 10, pady = 10)
		sprogress = ttk.Progressbar(sload, orient ='horizontal' , length=200, mode='determinate')
		sprogress.pack(padx = 30, pady = 10)
		sload.update()
		tab = cbox.get()
		main_folder = os.path.join('Exam Results', f'{tab} Results')
		file_list = []
		list_dir = sorted(os.listdir(main_folder))
		for f in list_dir[:-1]:
			file_list.append(os.path.join('Exam Results', f'{tab} Results', f))
		with open(os.path.join('Exam Results', f'{tab} Results', list_dir[-1]), 'r', encoding="utf8") as infile:
			remails = eval(infile.read())
			infile.close()

		for email, file in zip(remails, file_list):
			send(email, file)
			sprog = sprog+((1/(len(list_dir)-1)*100))
			sprogress['value'] = sprog
			sload.update()

		messagebox.showinfo('Success', 'Sucessfully sent email(s)!')
		sload.destroy()

	def Open(): #View result as a table

		def save(data):
			out_path = os.path.join('Exam Results', f'{tab} Results', f'{tab} Results.csv')
			try:
				with open(out_path, 'w+', newline="") as sfile:
					writer = csv.writer(sfile, dialect = 'excel')
					writer.writerow(cols)
					for record in data:
						writer.writerow(record)
				sfile.close()
				messagebox.showinfo('Success', 'File saved sucessfully!')
				try:
					os.system(f""" "{os.path.realpath(out_path)}" """)
				except:
					pass
			except:
				messagebox.showerror('Failed', 'Failed to save file! Please try again.')

		global tab
		tab = cbox.get()
		try:
			open_res = Toplevel()
			open_res.title(f'{tab} Results')
			open_res.minsize(900, 300)
			open_res.iconbitmap(os.path.join(file_dir, 'logo.ico'))	
			data = db.viewTable(f'{tab}')
			b_frame = Frame(open_res)
			b_frame.pack(side = 'bottom', fill = 'x')
			save_button = ttk.Button(b_frame, text = 'Export as Excel', command = lambda: save(data))
			save_button.pack(side = 'right', padx = (0,16), pady = 10)
			disp_text = Text(open_res, bd = 0, relief = 'flat')
			disp_vsb = Scrollbar(open_res, command = disp_text.yview)
			disp_text.configure(yscrollcommand = disp_vsb.set)
			disp_text.pack(fill = 'both', side = 'left', expand = True, padx = (5,0))
			disp_vsb.pack(side = 'right', fill = 'y')
			disp_frame = Frame(disp_text, bg = 'white')
			global cols
			cols = ['Roll', 'Name', 'Batch', 'Email', 'Others', 'Score']
			for c in range(len(cols)):
				tentry = Entry(disp_frame, font = ('Roboto', 10), relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
				tentry.insert(END, f'{cols[c]}')
				tentry.grid(row = 0, column = c, sticky = 'nsew')
				tentry.configure(state = 'readonly')
			for row in range(0, len(data)):
				col = 0
				for ent in data[row]:
					ientry = Entry(disp_frame, font = ('Roboto', 10), relief = 'flat', highlightthickness = 1, highlightbackground = 'black')
					ientry.insert(END, f'{ent}')
					ientry.grid(row = row+1, column = col, sticky = 'nsew')
					ientry.configure(state = 'readonly')
					col += 1
			disp_text.window_create(END, window = disp_frame)
		except:
			messagebox.showerror('Error', 'No such exam found!')
	res = Toplevel()
	setup(res)
	res.title('Results')
	tables = db.viewTables()
	tables = [t[0] for t in tables]
	try:
		tables.remove('log')
		tables.remove('credentials')
	except:
		pass
	top_frame = Frame(res, bg = 'white')
	top_frame.pack(side = 'top', fill = 'x')
	lab = Label(top_frame, text = 'Choose an exam', font = ('Roboto', 10), bg = 'white')
	lab.pack(side = 'left', padx = 10, pady = 10)
	cbox = ttk.Combobox(top_frame, values = tables)
	cbox.pack(side = 'right', padx = 10, pady = 10)
	bottom_frame = Frame(res)
	bottom_frame.pack(side = 'bottom', fill = 'x')
	but = ttk.Button(bottom_frame, text = 'View', command = Open)
	but.pack(side = 'right', pady = 10, padx = 10)
	sbut = ttk.Button(bottom_frame, text = 'Email', command = MassMail)
	sbut.pack(side = 'right', pady = 10, padx = (10,0))

def AskOpen(): #Ask for New Exam/Evaluate
	ask = Toplevel()
	ask.title('Teacher')
	setup(ask)
	ask.configure(bg = 'white')

	def openNew(): #Open PZ Exam Editor
		import ExamSetup

	def openEval(): #Open PZ Evaluation
		Evaluate()

	def delete(): #Delete Accunt (Only in organistion mode)
		global teacher_ver
		if db.viewTable('log'):
			con = messagebox.askokcancel('Warning', ('Are you sure you want to delete your account?\n'
											+'This action CANNOT be undone!'))
			if con:
				db.deleteRecord('credentials', user[0])
				now = datetime.now()
				values = (str(now), user[1], user[0], 'Deleted')
				db.addRecord('log', values)
				messagebox.showinfo('Success', 'Account sucessfully deleted!', parent = ask)
				ask.destroy()
		else:
			messagebox.showerror('Error', 'This option is only available in organisation mode')

	new_img = Image.open(os.path.join(file_dir, 'NewExam.png'))
	new_img = new_img.resize((320, 180), Image.ANTIALIAS)
	new_img = ImageTk.PhotoImage(new_img)
	new_button = Button(ask, image = new_img, bg = 'white', bd = 0, relief = 'flat', command = openNew)
	new_button.image = new_img
	new_button.pack(side = 'top', pady = 20, padx = 100)
	eval_img = Image.open(os.path.join(file_dir, 'EvalExam.png'))
	eval_img = eval_img.resize((320, 180), Image.ANTIALIAS)
	eval_img = ImageTk.PhotoImage(eval_img)
	eval_button = Button(ask, image = eval_img, bg = 'white', bd = 0, relief = 'flat', command = openEval)
	eval_button.imgae = eval_img
	eval_button.pack(side = 'top', pady = 20, padx = 100)
	bottom_frame = Frame(ask)
	bottom_frame.pack(side = 'bottom', fill = 'x')
	del_button = ttk.Button(bottom_frame, text = 'Delete Account', command = delete)
	del_button.pack(side = 'right', anchor = 'e', padx = 10, pady = 10)
	res_button = ttk.Button(bottom_frame, text = 'Results', command = Results)
	res_button.pack(side = 'right', anchor = 'w', padx = (10,0), pady = 10)

tries = 0
def otpValidation(): #Validate OTP
	global tires
	stop = 0
	def otpRun(action, message = None): #Open the current channe in webbrowser
		global stop
		with open(os.path.join('Program Files', 'Cache', "OTP Channel.txt"), 'r') as file:
			chlink = file.read()
			file.close()
		if chlink != '':
			try:
				if action == 'open':
					webbrowser.open(chlink)
				elif action == 'otp':
					global OTP
					OTP = random.randint(1000, 9999)
					requests.post(chlink.replace('c/',''), data=f"Your OTP is: {OTP}, requested by {user[1]}", verify = True)
				elif action == 'push':
					requests.post(chlink.replace('c/',''), data = message, verify = True)
				stop = 0
			except:
				messagebox.showerror('Error', 'Invalid channel!')
				stop = 1
		else:
			messagebox.showerror('Error', 'No Channel Found!')
			stop = 1

	def ver(): #Verify
		global tries, otp_entry, l1, stop
		if stop == 0:
			if otp_entry.get() == "":
				messagebox.showerror('Error', 'Please enter an OTP')
			else:
				if int(otp_entry.get()) == OTP and tries < 3:
					teacher_ver.destroy()
					AskOpen()
					otpRun('push', message = f"Verification Update: {user[1]} verification successful!")
				elif int(otp_entry.get()) != OTP and tries >= 2:
					otpRun('push', message = f"Verification Update: {user[1]} verification failed!")
					messagebox.showinfo('Verificaition Failed', 'Failed to verify!')
					teacher_ver.destroy()
				else:
					tries += 1
					l1.configure(text = "Please enter the OTP sent to the channel"
										+f"\n{3-tries} attempt(s) remaining")
					messagebox.showerror('Error', "Please enter a valid OTP!")

	def send_notif(): #Push notification to the channel
		global stop_otp
		try:
			global otp_entry, ent_frame, l1
			otpRun('otp')
			req.destroy()
			l3.pack(pady = 10, padx = 100)
			l1 = Label(ent_frame, text = "Please enter the OTP sent to the channel"
				   +"\n3 attempt(s) remaining", bg = 'white', fg = 'red')
			l1.pack(padx = 10, pady = 10)
			sub_frame = Frame(ent_frame, bg = 'white')
			sub_frame.pack(side = 'top')
			b1 = ttk.Button(sub_frame, text = "Verify", command = ver, default = 'active')
			b1.pack(padx = 10, pady = 10, side = 'right', anchor = 'w')
			otp_entry = ttk.Entry(sub_frame, width = 4)
			otp_entry.pack(padx = 10, pady = 10, side = 'left', anchor = 'e')			
		except:
			messagebox.showerror('Error', 'No Channel Found!')

	def reg_chan(): #Register a new channel
		def output():
			with open(os.path.join('Program Files', 'Cache', "OTP Channel.txt"), 'w+') as file:
				file.truncate()
				file.write(str(chan_ent.get()))
				file.close()
			messagebox.showinfo('Success', 'Channel registerd sucessfully!')
			
		sc = Toplevel()
		sc.title("Channel Registry")
		setup(sc)
		sc.configure(bg = 'white')
		lab = Label(sc, text = "Enter the channel link", bg = 'white')
		lab.pack(padx = 10, pady = 10)
		sub_frame = Frame(sc)
		sub_frame.pack(side = 'bottom', fill = 'x')
		global chan_ent
		chan_ent = ttk.Entry(sc, width = 32)
		chan_ent.pack(pady = (0,10), padx = 50)
		but = ttk.Button(sub_frame, text = "Continue", command = output, default = 'active')
		but.pack(pady = 10, padx = 10, side = 'right')
		cancel_but = ttk.Button(sub_frame, text = "Cancel", command = sc.destroy)
		cancel_but.pack(pady = 10, padx = (10,0), side = 'right')

	def otp_chan():
		webbrowser.open('https://notify.run/')

	global teacher_ver
	teacher_ver = Toplevel()
	teacher_ver.title("Teacher Verification")
	teacher_ver.configure(bg = 'white')
	setup(teacher_ver)
	top_frame = Frame(teacher_ver, bg = 'white')
	top_frame.pack(side = 'top', pady = 10, anchor = 'w')
	head_img = Image.open(os.path.join(file_dir, 'verification.png'))
	head_img = head_img.resize((193, 45), Image.ANTIALIAS)
	head_img = ImageTk.PhotoImage(head_img)
	head_lab = Label(top_frame, image = head_img, bg = 'white')
	head_lab.image = head_img
	head_lab.pack(side = 'left', padx = 10, fill = 'both')
	global ent_frame, chlink
	req_frame = Frame(teacher_ver, bg = 'white')
	req_frame.pack(side = 'top', fill = 'x')
	ent_frame = Frame(teacher_ver, bg = 'white')
	ent_frame.pack(side = 'top', fill = 'x')
	bottom_frame = Frame(teacher_ver, bg = 'white')
	bottom_frame.pack(side = 'bottom', fill = 'x')
	l3 = Label(req_frame, text = "Verify with OTP", bg = 'white')
	l3.pack(padx = (50, 0), pady = 10, side = 'left')
	req = ttk.Button(req_frame, text = "Request OTP", command = send_notif)
	req.pack(padx = (10, 50), pady = 10, side = 'right')
	chan = Button(bottom_frame, text = "Show my channel", command = lambda: otpRun('open'), 
					bg = 'white', font=("Comic Sans MS", 10, 'underline'),borderwidth = 0, fg = 'blue', cursor = 'hand2')
	chan.pack(padx = 10, pady = 10, anchor = 'se')
	aotp = Button(bottom_frame, text = "Create new channel", command = otp_chan, bg = 'white', font=("Comic Sans MS", 10, 'underline'), borderwidth = 0, cursor = 'hand2', fg = 'blue')
	aotp.pack(padx = 10, pady = 0, anchor = 'sw')
	aotp = Button(bottom_frame, text = "Register new channel", command = reg_chan, bg = 'white', font=("Comic Sans MS", 10, 'underline'), borderwidth = 0, cursor = 'hand2')
	aotp.pack(padx = 10, pady = (0,10), anchor = 'sw')

def UpdateDatabase(): #Update database (Only in organisation mode)
	global entries, sign
	if len(entries) == 6:
		entries.pop(-2)
	entries = [entries[-1]] + entries[:-1] #Optimising entries
	inps = []
	for entry in entries:
		inps.append(entry.get())
	db.addRecord('credentials', tuple(inps))
	now = datetime.now()
	values = (str(now), entries[1].get(), entries[0].get(), 'Created')
	db.addRecord('log', values)
	messagebox.showinfo('Success', 'Sucessfully created user!')
	sign.destroy()

def Validate(): #Validate registeration (Only in organisation mode)
	flag = 0
	regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

	for i in range(len(entries)): #Check for empty fields
		if entries[i].get() == '':
			flag = 0
			messagebox.showerror('Error',f'{display[i]} cannot be empty!')
			break
		else:
			flag = 1

	if flag == 1:
		if entries[-2].get() != entries[-3].get():
			flag = 0
			messagebox.showerror('Error', 'Passwords do not match!')

	if flag == 1: 
		if not re.search(regex, entries[-1].get()): #Check email
			flag = 0  
			messagebox.showerror('Error', 'Please enter valid emial address!')

	if flag == 1: #Check for duplicate 
		users = db.viewTable('credentials')
		for user in users:
			if user[0] == entries[-1].get():
				flag = 0
				messagebox.showerror('Error', 'Email associated with another user!')

	if flag == 1: #Update database
		UpdateDatabase()

def ValLogin(id, pwd): #Validate login (Only in organisation mode)
	users = db.viewTable('credentials')
	mm = 0
	global user
	for user in users:
		if user[0] == id.get():
			mm = 1
		if user[0] == id.get() and user[-1] == pwd.get():
			root.destroy()
			now = datetime.now()
			values = (str(now), user[1], user[0], 'Logged In')
			db.addRecord('log', values)
			#import AskOpen
			otpValidation()
			break
	else:
		if mm == 1:
			messagebox.showerror('Error', 'Incorrect Password!')
		else:
			mm = 0
			messagebox.showerror('Error', 'No user found!')
	return True

#__Login GUI__
def Login(): #(Only in organisation mode)
	login = Toplevel(root, bg = 'white')
	login.title('Login')
	setup(login)
	top_frame = Frame(login, bg = 'white')
	top_frame.pack(side = 'top', fill = 'x', pady = (10,0))
	head_lab = Label(top_frame, image = head_img, bg = 'white')
	head_lab.image = head_img
	head_lab.pack(side = 'left', padx = 10, fill = 'both')
	base_frame = Frame(login)
	base_frame.pack(side = 'bottom', fill = 'x')
	left_frame = Frame(login, bg = 'white')
	left_frame.pack(side = 'left', fill = 'y')
	right_frame = Frame(login, bg = 'white')
	right_frame.pack(side = 'right', fill = 'y')
	id_lab = Label(left_frame, text = 'Email', bg = 'white')
	id_lab.pack(side = 'top', padx = 10, pady = 10)
	id_entry = ttk.Entry(right_frame, width = 32)
	id_entry.pack(side = 'top', padx = 10, pady = 10)
	pass_lab = Label(left_frame, text = 'Password', bg = 'white')
	pass_lab.pack(side = 'top', padx = 10, pady = 10)
	pass_entry = ttk.Entry(right_frame, width = 32)
	pass_entry.pack(side = 'top', padx = 10, pady = 10) 
	cancel_log = ttk.Button(base_frame, text = 'Cancel', command = login.destroy)
	cancel_log.pack(side = 'right', padx = 10, pady = 10, anchor = 'e')
	sub = ttk.Button(base_frame, text = 'Login', default = 'active', 
						command = lambda id = id_entry, pwd = pass_entry: ValLogin(id, pwd))
	sub.pack(side = 'right', padx = (10,0), pady = 10, anchor = 'e')
	

#__Sign Up GUI__
def SignUp(): #(Only in organisation mode)
	global entries, sign, display

	def populate(label):
		lab = Label(left_frame, text = label, bg = 'white')
		lab.pack(side = 'top', padx = 10, pady = 10)
		entry = ttk.Entry(right_frame, width = 32)
		entry.pack(side = 'top', padx = 10, pady = 10)
		return entry

	sign = Toplevel(root, bg = 'white')
	setup(sign)
	sign.title('Sign Up')
	top_frame = Frame(sign, bg = 'white')
	top_frame.pack(side = 'top', fill = 'x', pady = (10,0))
	head_lab = Label(top_frame, image = head_img, bg = 'white')
	head_lab.image = head_img
	head_lab.pack(side = 'left', padx = 10, fill = 'both')
	base_frame = Frame(sign)
	base_frame.pack(side = 'bottom', fill = 'x')
	left_frame = Frame(sign, bg = 'white')
	left_frame.pack(side = 'left', fill = 'y')
	right_frame = Frame(sign, bg = 'white')
	right_frame.pack(side = 'right', fill = 'y')
	display = ['Username', 'First Name', 'Last Name', 'Password', 'Repeat Password', 'Email']
	entries = []
	for disp in display:
		entries.append(populate(disp))
	cancel_log = ttk.Button(base_frame, text = 'Cancel', command = sign.destroy)
	cancel_log.pack(side = 'right', padx = 10, pady = 10, anchor = 'e')
	sub = ttk.Button(base_frame, text = 'Sign Up', default = 'active', command = Validate)
	sub.pack(side = 'right', padx = (10,0), pady = 10, anchor = 'e')
	

#__Main GUI__
def setup(window):
	window.iconbitmap(os.path.join(file_dir, 'logo.ico'))
	window.resizable(False, False)

def start(): #Launch the login/sign up GUI (Only in organisation mode)
	global head_img
	root = Toplevel()
	root.configure(bg = 'white')
	root.title('Login')
	setup(root)
	top_frame = Frame(root, bg = 'white')
	top_frame.pack(side = 'top', fill = 'x', pady = (10,0))
	head_img = Image.open(os.path.join(file_dir, 'verification.png'))
	head_img = head_img.resize((193, 45), Image.ANTIALIAS)
	head_img = ImageTk.PhotoImage(head_img)
	head_lab = Label(top_frame, image = head_img, bg = 'white')
	head_lab.pack(side = 'left', padx = 10, fill = 'both')
	log_but = ttk.Button(root, text = 'Login', command = Login)
	log_but.pack(side = 'top', pady = 20, padx = 30)
	sign_but = ttk.Button(root, text = 'Sign Up', command = SignUp)
	sign_but.pack(side = 'top', pady = 20, padx = 30)

	root.mainloop()

def orgSet(): #Called form Main if mode is set to organisation 
	global head_img, root, db, file_dir
	root = Toplevel()
	root.configure(bg = 'white')
	root.title('Login')
	file_dir = os.path.join('Program Files', 'Data Files')
	setup(root)
	top_frame = Frame(root, bg = 'white')
	top_frame.pack(side = 'top', fill = 'x', pady = (10,0))
	head_img = Image.open(os.path.join(file_dir, 'verification.png'))
	head_img = head_img.resize((193, 45), Image.ANTIALIAS)
	head_img = ImageTk.PhotoImage(head_img)
	head_lab = Label(top_frame, image = head_img, bg = 'white')
	head_lab.pack(side = 'left', padx = 10, fill = 'both')
	log_but = ttk.Button(root, text = 'Login', command = Login)
	log_but.pack(side = 'top', pady = 20, padx = 30)
	sign_but = ttk.Button(root, text = 'Sign Up', command = SignUp)
	sign_but.pack(side = 'top', pady = 20, padx = 30)
	db = sql.Database('Default_org')
	try: #Temporary
		db.addTable('credentials', 'cred')
		db.addTable('log', 'log')
	except:
		pass	

def indSet(): #Called form Main if mode is set to individual
	global db, file_dir
	file_dir = os.path.join('Program Files', 'Data Files')
	db = sql.Database('Default_ind')
	AskOpen()