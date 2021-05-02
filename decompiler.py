from binaryninja import *
from pathlib import Path
import hashlib
import os
import subprocess

class Decompiler(BackgroundTaskThread):
    def __init__(self,file_name,current_path):
        self.progress_banner = f"[Ghinja] Running the decompiler job ... Ghinja decompiler output not available until finished."
        BackgroundTaskThread.__init__(self, "", True)
        self.file_name = str(Path(file_name).name)
        self.file_path = file_name
        self.current_path = current_path
        self.decompile_result_path = Path(self.current_path / "decomp_")
        

    def run(self):
        self.progress = f"[Ghinja] Running the decompiler job ... Ghinja decompiler output not available until finished."
        with open(os.path.dirname(os.path.realpath(__file__)) + "/Decompile_TEMPLATE.java",'r') as decomp_file:
            data = decomp_file.read()
            with open(os.path.dirname(os.path.realpath(__file__)) + "/Gnidja/Gnidja.java",'w') as tmp_decomp_file:
                tmp_decomp_file.write(data.replace("PLACEHOLDER_OUTPUT",str(self.decompile_result_path).replace("\\","\\\\")))
        os.system(f"{Settings().get_string('ghinja.ghidra_install_path')} \"{str(self.current_path)}\" \"{self.file_name}\" -import \"{self.file_path}\" -scriptPath \"{os.path.dirname(os.path.realpath(__file__)) + '/Gnidja'}\" -postScript \"Gnidja.java\"")
        #os.system(f"{Settings().get_string('ghinja.ghidra_install_path')} \"{str(self.current_path)}\" \"{self.file_name}\" -import \"{self.file_path}\" -postscript Decompile.java -scriptPath \"{os.path.dirname(os.path.realpath(__file__))}\"")	#new
        #os.system(f"{Settings().get_string('ghinja.ghidra_install_path')} \"{str(self.current_path)}\" \"{self.file_name}\" -import \"{self.file_path}\" -postscript \"{os.path.dirname(os.path.realpath(__file__)) + '/Decompile.java'}\"")		#combi
        #log_info(f"{Settings().get_string('ghinja.ghidra_install_path')} \"{str(self.current_path)}\" \"{self.file_name}\" -import \"{self.file_path}\" -postscript \"/home/c4t/.binaryninja/plugins/ghinja/Decompile.java\"")
        os.remove(os.path.dirname(os.path.realpath(__file__)) + "/Gnidja/Gnidja.java")


