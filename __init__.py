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
		# TODO handle cancel
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
			settings.set_string("ghinja.ghidra_install_path",get_open_filename_input("Provide Path to Ghidra \"analyzeHeadless(.bat)\" file (Usually: <GHIDRA_INSTALL>/support/analyzeHeadless)").decode("utf-8"))
		global instance_id
		self.binja_renames = {} # {"function_name":[{"original":"new"})]}
		self.current_function = None
		self.current_offset = None
		self.decomp = None
		self.decomp_results = None
		self.current_view = None
		self.decompile_result_path = None
		self.decompile_offset_path = None
		QWidget.__init__(self, parent)
		DockContextHandler.__init__(self, self, name)
		self.actionHandler = UIActionHandler()
		self.actionHandler.setupActionHandler(self)
		layout = QVBoxLayout()
		self.editor = QTextEdit(self)
		self.editor.setReadOnly(True)
		self.editor.installEventFilter(self)
		self.editor.setStyleSheet("QTextEdit { background-color: #2a2a2a; font-family: Consolas }")
		self.editor.setPlainText("N/A")
		self.editor.selectionChanged.connect(self.onSelect)
		highlighter = Highlighter(self.editor.document(),"")
		layout.addWidget(self.editor)
		layout.setAlignment(QtCore.Qt.AlignLeft)
		self.setLayout(layout)
		instance_id += 1
		self.data = data

	def onSelect(self):
		cursor = self.editor.textCursor()
		ch = Highlighter(self.editor.document(),cursor.selectedText())
		#log_info("selected: " + str(cursor.selectedText()))

	def notifyOffsetChanged(self, offset):
		if self.decomp.finished:
			self.current_offset = offset
			self.editor.setPlainText(self.find_function(offset))

	def shouldBeVisible(self, view_frame):
		if view_frame is None:
			return False
		else:
			return True

	def eventFilter(self, obj, event):
		if event.type() == QtCore.QEvent.KeyPress and obj is self.editor:
			cursor = self.editor.textCursor()
			if event.key() == QtCore.Qt.Key_N and self.editor.hasFocus():
				if self.current_view.file.has_database == False:
					show_message_box("Project not saved", "To enable renaming, make sure that the current project is saved to a BNDB file.", buttons=0, icon=2)
					return False
				# Handle rename action
				selected = cursor.selectedText()
				if selected != "":
					# Get selected text
					new_name = get_text_line_input(f"Rename {selected}: ","Rename")
					if not re.match(b"^\\w+$", new_name):
						show_message_box("Name not valid", "Please use only 'word' characters (A-Z, a-z, 0-9 and _)", buttons=0, icon=2)
						return False
					found = False
					for key in self.binja_renames[hex(self.current_function.start)]:
						if key["original"] == selected:
							# Was already renamed so just reassign to avoid accumulating tosn of data
							key["new"] = new_name.decode("UTF-8")
							found = True
					if not found:
						self.binja_renames[hex(self.current_function.start)].append({"original":selected,"new":new_name.decode("UTF-8")})
					self.notifyOffsetChanged(self.current_offset)
			if event.key() == QtCore.Qt.Key_G:
				# TODO check if highlighted thing is a function
				# current_view.offset = 4206085
				show_message_box("GOTO", "Hello", buttons=0, icon=2)
		return False
	

	def notifyViewChanged(self, view_frame):
		if view_frame is None:
			pass
		else:
			self.current_view = view_frame.actionContext().binaryView
			md5 = hashlib.md5()
			try:
				with open(view_frame.actionContext().binaryView.file.original_filename,'rb') as binary:
					file_content = binary.read()
					md5.update(file_content)
					current_path = Path(Path(user_plugin_path()) / ".." / f"ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name) + '_' + md5.hexdigest()}")
				filename = view_frame.actionContext().binaryView.file.original_filename
				current_path.mkdir(parents=True, exist_ok=True)
			except:
				# File does not exist
				tmp_path = Path(user_plugin_path()) / ".." / f"ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name)}"
				self.current_view.save(str(tmp_path))
				while not os.path.exists(str(tmp_path)):
					pass
				with open(str(tmp_path),'rb') as binary:
					file_content = binary.read()
					md5.update(file_content)
				current_path = Path(Path(user_plugin_path()) / ".." / f"ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name) + '_' + md5.hexdigest()}")
				current_path.mkdir(parents=True, exist_ok=True)
				shutil.move(tmp_path, current_path / tmp_path.name)
				filename = str(current_path / tmp_path.name)
			# Create relevant_folder
			#current_path = Path(Path.home() / f".ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name) + '_' + md5.hexdigest()}")
			self.decompile_result_path = Path(current_path / "decomp_")
			self.decompile_offset_path = Path(current_path / "decomp_offset")
			if not os.path.exists(filename + ".rep"):
				self.decomp = Decompiler(filename,current_path)
				self.decomp.start()
			else:
				self.decomp = Decompiler(filename,current_path)
				self.decomp.finished = True


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
			for ghinja_rename in self.binja_renames[hex(self.current_function.start)]:
				function_output = re.sub(ghinja_rename["original"],ghinja_rename["new"],function_output)
			
			# Rename locals
			for local in self.current_function.stack_layout:
				if local.storage < 0:
					look_for = f"local_{hex(local.storage)[3:]}"
					function_output = re.sub(look_for,local.name,function_output)
		return function_output
		

def addStaticDockWidget():
	dock_handler = DockHandler.getActiveDockHandler()
	parent = dock_handler.parent()
	dock_widget = GhinjaDockWidget.create_widget("Ghinja Decompiler", parent)
	dock_handler.addDockWidget(dock_widget, Qt.TopDockWidgetArea, Qt.Vertical, True, False)

addStaticDockWidget()