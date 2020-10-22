from binaryninja import *
from binaryninjaui import DockHandler, DockContextHandler, UIActionHandler
from PySide2 import QtCore
from .highlighter import Highlighter
from .decompiler import Decompiler
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QTextEdit
import json
import os
import hashlib
from pathlib import Path

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
		self.decomp = None
		self.decomp_results = None
		self.current_view = None
		self.decompile_result_path = None
		QWidget.__init__(self, parent)
		DockContextHandler.__init__(self, self, name)
		self.actionHandler = UIActionHandler()
		self.actionHandler.setupActionHandler(self)
		layout = QVBoxLayout()
		self.editor = QTextEdit(self)
		self.editor.setReadOnly(True)
		self.editor.setStyleSheet("QTextEdit { background-color: #2a2a2a; font-family: Consolas }")
		self.editor.setPlainText("N/A")
		highlighter = Highlighter(self.editor.document())
		layout.addWidget(self.editor)
		layout.setAlignment(QtCore.Qt.AlignLeft)
		self.setLayout(layout)
		instance_id += 1
		self.data = data

	def notifyOffsetChanged(self, offset):
		if self.decomp.finished:
			self.editor.setPlainText(self.find_function(offset))

	def shouldBeVisible(self, view_frame):
		if view_frame is None:
			return False
		else:
			return True

	def notifyViewChanged(self, view_frame):
		if view_frame is None:
			pass
		else:
			self.current_view = view_frame.actionContext().binaryView
			md5 = hashlib.md5()
			with open(view_frame.actionContext().binaryView.file.original_filename,'rb') as binary:
				file_content = binary.read()
				md5.update(file_content)
			# Create relevant_folder
			current_path = Path(Path(user_plugin_path()) / ".." / f"ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name) + '_' + md5.hexdigest()}")
			#current_path = Path(Path.home() / f".ghinja_projects/{str(Path(view_frame.actionContext().binaryView.file.original_filename).name) + '_' + md5.hexdigest()}")
			self.decompile_result_path = Path(current_path / "decompiled.c")

			self.decomp = Decompiler(view_frame.actionContext().binaryView.file.original_filename)
			self.decomp.start()


	def contextMenuEvent(self, event):
		self.m_contextMenuManager.show(self.m_menu, self.actionHandler)

	@staticmethod
	def create_widget(name, parent, data = None):
		return GhinjaDockWidget(parent, name, data)

	def find_function(self, offset):
		function_output = "DECOMPILER OUTPUT FOR THIS FUNCTION WAS NOT FOUND"
		try:
			current_function = self.current_view.get_functions_containing(offset)[0]
		except:
			return "DECOMPILER OUTPUT FOR THIS FUNCTION WAS NOT FOUND"
		function_name = current_function.name
		function_anon_name = f'FUN_{current_function.start:08x}'
		# TODO figure out better way in distinguisihin between these
		if function_name == "main" or function_name == "_main" or function_name == "start" or function_name == "_start":
			function_name = "entry"

		function_name += "("
		output = False
		open_found = False
		stack = []
		if os.path.exists(str(self.decompile_result_path)):
			with open(str(self.decompile_result_path)) as search:
				for line in search:
					l = line.rstrip()
					if l:
						if output:
							for i, c in enumerate(line):
								if c == "{":
									open_found = True
									stack.append(i)
								elif c == "}":
									stack.pop()
							if len(stack) == 0 and open_found:
								function_output += line
								break
							else:
								function_output += line
						elif (function_name in line or function_anon_name in line) and not ";" in line:
							function_output = ""
							output = True
							if function_name == "entry(":
								function_output += line.replace("entry",current_function.name)
							elif function_anon_name in line:
								function_output += line.replace(function_anon_name,current_function.name)
							else:
								function_output += line
			# Rename functions
			for callee in current_function.callees:
				look_for = f'FUN_{callee.start:08x}'
				function_output = function_output.replace(look_for,callee.name)
			# Rename locals
			for local in current_function.stack_layout:
				if local.storage < 0:
					look_for = f"local_{hex(local.storage)[3:]}"
				function_output = re.sub(look_for,local.name,function_output)
		return function_output
		

def addStaticDockWidget():
	dock_handler = DockHandler.getActiveDockHandler()
	parent = dock_handler.parent()
	dock_widget = GhinjaDockWidget.create_widget("Ghinja Decompiler", parent)
	dock_handler.addDockWidget(dock_widget, Qt.TopDockWidgetArea, Qt.Horizontal, True, False)

addStaticDockWidget()