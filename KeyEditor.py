"""@Aditya Singh Tejas Copyright (c) PIERA-ZONE 2020"""
import tkinter as tk
from tkinter import messagebox
import os

class TextLineNumbers(tk.Canvas):
	def __init__(self, *args, **kwargs):
		tk.Canvas.__init__(self, *args, **kwargs)
		self.textwidget = None

	def attach(self, text_widget):
		self.textwidget = text_widget

	def redraw(self, *args):
		'''redraw line numbers'''
		self.delete("all")

		i = self.textwidget.index("@0,0")
		while True :
			dline= self.textwidget.dlineinfo(i)
			if dline is None: break
			y = dline[1]
			linenum = str(i).split(".")[0]
			self.create_text(5,y,anchor="nw", text=linenum, font=('Consolas',12), fill='white')
			i = self.textwidget.index("%s+1line" % i)

class CustomText(tk.Text):
	def __init__(self, *args, **kwargs):
		tk.Text.__init__(self, *args, **kwargs)

		# create a proxy for the underlying widget
		self._orig = self._w + "_orig"
		self.tk.call("rename", self._w, self._orig)
		self.tk.createcommand(self._w, self._proxy)

	def _proxy(self, *args):
		# let the actual widget perform the requested action
		cmd = (self._orig,) + args
		result = self.tk.call(cmd)

		# generate an event if something was added or deleted,
		# or the cursor position changed
		if (args[0] in ("insert", "replace", "delete") or 
			args[0:3] == ("mark", "set", "insert") or
			args[0:2] == ("xview", "moveto") or
			args[0:2] == ("xview", "scroll") or
			args[0:2] == ("yview", "moveto") or
			args[0:2] == ("yview", "scroll")
		):
			self.event_generate("<<Change>>", when="tail")

		# return what the actual widget returned
		return result 

class Editor(tk.Frame):
	def __init__(self, key, *args, **kwargs):

		def on_close(self):
			cache_dir=os.path.join('Program Files','Cache')
			with open(os.path.join(cache_dir,'TempKey.txt'),'w+') as file:
				file.write(self.text.get('1.0','end-1c'))
				file.close()
			messagebox.showinfo('Success','Answer key saved successfully!')
			self.master.destroy()

		tk.Frame.__init__(self, *args, **kwargs)
		self.text = CustomText(self, font=('Consolas',12),wrap='word')
		self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
		self.text.configure(yscrollcommand=self.vsb.set)
		self.text.tag_configure("bigfont", font=("Helvetica", "24", "bold"))
		self.linenumbers = TextLineNumbers(self, width=35, bg='RoyalBlue4')
		self.linenumbers.attach(self.text)

		self.vsb.pack(side="right", fill="y")
		self.linenumbers.pack(side="left", fill="y")
		self.text.pack(side="right", fill="both", expand=True)

		self.text.bind("<<Change>>", self._on_change)
		self.text.bind("<Configure>", self._on_change)
		self.text.master.master.protocol("WM_DELETE_WINDOW", lambda: on_close(self))

		key=key.split('\n')
		for k in range(len(key)):
			if k!=len(key)-1:
				self.text.insert("end", f"{key[k]}\n")
			else:
				self.text.insert("end", f"{key[k]}")

	def _on_change(self, event):
		self.linenumbers.redraw()