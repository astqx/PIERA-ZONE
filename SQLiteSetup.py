"""@Aditya Sharma, Aditya Singh Tejas (c) 2020 PIERA-ZONE"""
#__SQLite Setup__
import sqlite3
import os

class Database:
	"""Use variorus commands of SQLite and create/modify database."""
	def __init__(self, database):
		parent_dir = os.path.join(os.getcwd(),'Program Files', 'Database Files')
		self.connect = sqlite3.connect(os.path.join(parent_dir, f"{database}.db"))
		self.cursor = self.connect.cursor()

	def addTable(self, table, type):
		if type == 'cred':
			try:
				self.cursor.execute(f"""CREATE TABLE "{table}" (
										email text PRIMARY KEY,
										username text,
										first_name text,
										last_name text,
										password text)""")
				self.connect.commit()
				return True
			except Exception as e: 
				return e
		elif type == 'log':
			try:
				self.cursor.execute(f"""CREATE TABLE "{table}" (
										dtime text,
										username text,
										email text,
										status text)""")
				self.connect.commit()
				return True
			except Exception as e:
				return e
		elif type == 'results':
			try:
				self.cursor.execute(f"""CREATE TABLE "{table}" (
										roll_num text,
										name text,
										batch text,
										email text,
										others text,
										score text)""")
				self.connect.commit()
				return True
			except Exception as e:
				return e

	def viewTable(self, table):
		try:
			self.cursor.execute(f"""SELECT * FROM "{table}" """)
			data = self.cursor.fetchall()
			self.connect.commit()
			return data
		except:
			return  False

	def addRecord(self, table, values):
		try:
			self.cursor.execute(f"""INSERT INTO "{table}" VALUES {values}""")
			self.connect.commit()
			return True
		except Exception as e:
			return e

	def viewTables(self):
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
		data = self.cursor.fetchall()
		self.connect.commit()
		return data

	def deleteRecord(self, table, key):
		try:
			self.cursor.execute(f"""DELETE FROM "{table}" WHERE email = "{key}" """)
			self.connect.commit()
			return True
		except Exception as e:
			return e

	def deleteTable(self, table):
		try:
			self.cursor.execute(f"""DROP TABLE "{table}" """)
			self.connect.commit()
			return True
		except Exception as e:
			return e