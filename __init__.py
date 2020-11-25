from binaryninja import *
from binaryninjaui import DockHandler, DockContextHandler, UIActionHandler
from PySide2 import QtCore
from .highlighter import Highlighter
from .decompiler import Decompiler
from PySide2.QtCore import Qt
from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QTextEdit
import json
import os
import hashlib
from pathlib import Path
import shutil
import re

instance_id = 0
class GhinjaDockWidget(QWidget, DockContextHandler):
	def __init__(self, parent, name, data):
		# Read the configuration
		settings = Settings()
		settings.register_group("ghinja", "Ghinja")
		settings.register_setting("ghinja.ghidra_install_path", """
				{
					"title" : "Ghidra Installation Path",
					"type" : "string",
					"default" : "",
					"description" : "Path to analyzeHeadless file in Ghidra installation dir."
				}
				""")
		if not os.path.exists(settings.get_string("ghinja.ghidra_install_path")):
			show_message_box("Path to Ghidra headless was not found!", "To allow the Ghinja plugin to work, you will be prompted to specify the path to the \"analyzeHeadless(.bat)\" file.", buttons=0, icon=2)
			settings.set_string("ghinja.ghidra_install_path",get_open_filename_input("Provide Path to Ghidra \"analyzeHeadless(.bat)\" file (Usually: <GHIDRA_INSTALL>/support/analyzeHeadless)").decode("utf-8"))
		
		self.rename_settings = Settings()
		self.rename_settings.register_group("ghinja_rename","Rename")
		self.rename_settings.register_setting("ghinja_rename.ghinja_rename_struct", """
				{
					"title" : "Ghidra Rename Struct",
					"type" : "string",
					"default" : "{}",
					"description" : "Settings to hold renames for variables."
				}
				""")

		global instance_id
		self.binja_renames = {} # {"function_name":[{"original":"new"})]}
		self.current_function = None
		self.current_offset = None
		self.decomp = None
		self.current_view = None
		self.function_output = None
		self.decompile_result_path = None
		self.decompile_offset_path = None
		self.decompiler_done = False
		self.function_args = []
		QWidget.__init__(self, parent)
		DockContextHandler.__init__(self, self, name)
		self.actionHandler = UIActionHandler()
		self.actionHandler.setupActionHandler(self)
		layout = QVBoxLayout()
		self.editor = QTextEdit(self)
		self.editor.setReadOnly(True)
		self.editor.installEventFilter(self)
		self.editor.setStyleSheet("QTextEdit { font-family: Consolas }")
		self.editor.setPlainText(" Click anywhere in the dock to start decompiler")
		self.editor.selectionChanged.connect(self.onSelect)
		highlighter = Highlighter(self.editor.document(),"",self.function_args)
		layout.addWidget(self.editor)
		layout.setAlignment(QtCore.Qt.AlignLeft)
		self.setLayout(layout)
		instance_id += 1
		self.data = data

	def onSelect(self):
		cursor = self.editor.textCursor()
		if cursor.selectedText():
			ch = Highlighter(self.editor.document(),"\\b" + cursor.selectedText() + "\\b",self.function_args)
		else:
			ch = Highlighter(self.editor.document(),"",self.function_args)

	def notifyOffsetChanged(self, offset):
		if self.decompiler_done:
			if not self.current_function or not (self.current_function.lowest_address < offset and self.current_function.highest_address > offset):
				self.current_offset = offset
				try:
					self.editor.setPlainText(self.find_function(offset))
					ch = Highlighter(self.editor.document(),"",self.function_args)
				except:
					pass

	def shouldBeVisible(self, view_frame):
		if view_frame is None:
			return False
		else:
			return True

	def eventFilter(self, obj, event):
		if event.type() == QtCore.QEvent.FocusIn and self.editor.hasFocus() and not self.decompiler_done:
			self.decomp = Decompiler(self.filename,self.current_path)
			self.editor.setPlainText(" Decompiler running ... ")
			self.decomp.start()
			self.decompiler_done = True
		if event.type() == QtCore.QEvent.KeyPress and obj is self.editor:
			cursor = self.editor.textCursor()
			if event.key() == QtCore.Qt.Key_F and self.editor.hasFocus():
				# Find TODO
				search_string = get_text_line_input("Find: ","Find")
				if search_string:
					ch = Highlighter(self.editor.document(),search_string.decode("UTF-8"),self.function_args)
			if event.key() == QtCore.Qt.Key_N and self.editor.hasFocus():
				if self.current_view.file.has_database == False:
					show_message_box("Project not saved", "To enable renaming, make sure that the current project is saved to a BNDB file.", buttons=0, icon=2)
					return False
				# Handle rename action
				selected = cursor.selectedText()
				if selected != "":
					#self.binja_renames = json.loads(self.rename_settings.get_string("ghinja_rename.ghinja_rename_struct",self.current_view))
					# Get selected text
					new_name = get_text_line_input(f"Rename {selected}: ","Rename")
					if new_name and not re.match(b"^\\w+$", new_name):
						show_message_box("Name not valid", "Please use only 'word' characters (A-Z, a-z, 0-9 and _)", buttons=0, icon=2)
						return False
					if re.search(f"\\b{new_name.decode('UTF-8')}\\b",self.function_output):
						show_message_box("Name not unique", "Please use only unique name to avoid conflicts.", buttons=0, icon=2)
						return False
					found = False
					for key in self.binja_renames[hex(self.current_function.start)]:
						if key["original"] == selected:
							# Was already renamed so just reassign to avoid accumulating tons of data
							key["new"] = new_name.decode("UTF-8")
							found = True
						if key["new"] == selected:
							key["new"] = new_name.decode("UTF-8")
							found = True
					if not found:
						self.binja_renames[hex(self.current_function.start)].append({"original":selected,"new":new_name.decode("UTF-8")})
					self.rename_settings.set_string("ghinja_rename.ghinja_rename_struct",json.dumps(self.binja_renames),self.current_view,SettingsScope.SettingsResourceScope)
					self.notifyOffsetChanged(self.current_offset)
		return False
	

	def notifyViewChanged(self, view_frame):
		if view_frame is None:
			pass
		else:
			self.current_view = view_frame.actionContext().binaryView
			self.binja_renames = json.loads(self.rename_settings.get_string("ghinja_rename.ghinja_rename_struct",self.current_view))
			md5 = hashlib.md5()
			try:
				with open(view_frame.actionContext().binaryView.file.original_filename,'rb') as binary:
					file_content = binary.read()
					md5.update(file_content)
					self.current_path = Path(Path(user_plugin_path()) / ".." / f"ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name) + '_' + md5.hexdigest()}")
				self.filename = view_frame.actionContext().binaryView.file.original_filename
				self.current_path.mkdir(parents=True, exist_ok=True)
			except:
				# File does not exist
				tmp_path = Path(user_plugin_path()) / ".." / f"ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name)}"
				self.current_view.save(str(tmp_path))
				while not os.path.exists(str(tmp_path)):
					pass
				with open(str(tmp_path),'rb') as binary:
					file_content = binary.read()
					md5.update(file_content)
				self.current_path = Path(Path(user_plugin_path()) / ".." / f"ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name) + '_' + md5.hexdigest()}")
				self.current_path.mkdir(parents=True, exist_ok=True)
				shutil.move(tmp_path, self.current_path / tmp_path.name)
				self.filename = str(self.current_path / tmp_path.name)
			# Create relevant_folder
			#current_path = Path(Path.home() / f".ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name) + '_' + md5.hexdigest()}")
			self.decompile_result_path = Path(self.current_path / "decomp_")
			self.decompile_offset_path = Path(self.current_path / "decomp_offset")
			
			if os.path.exists(str(self.decompile_offset_path)):
				# Already decompiled we dont have to do anything
				self.decompiler_done = True
				


	def contextMenuEvent(self, event):
		self.m_contextMenuManager.show(self.m_menu, self.actionHandler)

	@staticmethod
	def create_widget(name, parent, data = None):
		return GhinjaDockWidget(parent, name, data)

	def find_function(self, offset):
		function_output = "DECOMPILER OUTPUT FOR THIS FUNCTION WAS NOT FOUND"
		try:
			self.current_function = self.current_view.get_functions_containing(offset)[0]
			try:
				self.binja_renames[hex(self.current_function.start)]
			except:
				self.binja_renames[hex(self.current_function.start)] = []
		except:
			return "DECOMPILER OUTPUT FOR THIS FUNCTION WAS NOT FOUND"
		# Get different offset functions os.listdir()
		offset = 0
		with open(str(self.decompile_offset_path),"r") as offset_file:
			ghidra_offset = int(offset_file.read())
			offset_diff = ghidra_offset - self.current_view.functions[0].start
			if offset_diff == 0:
				offset = self.current_function.start
			else:
				offset = self.current_function.start + offset_diff

		if os.path.exists(str(self.decompile_result_path) + str(offset)):
			with open(str(self.decompile_result_path) + str(offset),"r") as function_file:
				function_output = function_file.read()
			# Replace function name
			function_output = re.sub("\\b\\w*\\(", self.current_function.name + "(", function_output, 1)
			# Rename functions
			for callee in self.current_function.callees:
				look_for = f'FUN_{callee.start:08x}'
				function_output = function_output.replace(look_for,callee.name)
			
			#for ghinja_rename in self.binja_renames[hex(self.current_function.start)]:
			js = json.loads(self.rename_settings.get_string("ghinja_rename.ghinja_rename_struct",self.current_view))
			if js:
				try:
					for ghinja_rename in js[hex(self.current_function.start)]:
						function_output = re.sub('\\b'+ghinja_rename["original"]+'\\b',ghinja_rename["new"],function_output)
				except:
					pass
			# Searching in frist 300 chars is enough
			self.function_args = []
			for arg in re.findall("\\w+ [*&]?(\\w+),|\\w+ [*&]?(\\w+)\\)", function_output[:300]):
				if arg[0]:
					self.function_args.append(arg[0])
				elif arg[1]:
					self.function_args.append(arg[1])
			# Rename locals - quite buggy actually
			for local in self.current_function.stack_layout:
				if local.storage < 0:
					look_for = f"local_{hex(local.storage)[3:]}"
					function_output = re.sub(look_for,local.name,function_output)
		self.function_output = function_output
		return function_output
		

def addStaticDockWidget():
	dock_handler = DockHandler.getActiveDockHandler()
	parent = dock_handler.parent()
	dock_widget = GhinjaDockWidget.create_widget("Ghinja Decompiler", parent)
	dock_handler.addDockWidget(dock_widget, Qt.TopDockWidgetArea, Qt.Horizontal, True, False)

addStaticDockWidget()
