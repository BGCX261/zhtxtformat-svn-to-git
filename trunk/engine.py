
import os
import sys
from directory import Directory
from plain import Plain
from outer.kindle_pdf import KindlePDF
from outer.text       import TextOutput

class Engine :
    
    def __init__ (self, pdf_path, debug = False) :
	self.pdf_path = pdf_path
	if False is debug :
	    self.pdf = KindlePDF()
	else :
	    self.pdf = TextOutput()

    def parse (self, path) :

	files = self.get_files (path)
	for fpath in files :
	    plain = Plain(fpath)
	    plain.parse(self.pdf)
	
	self.create_pdf ()

    def set_cover (self, cover_path) :
	self.pdf.set_cover (cover_path)

    def enable_bookmark (self) :
	self.pdf.create_table_of_contents()

    def get_files (self, path) :
		if os.path.isdir(path) :
			files = self.parse_dir_files (path)
		elif os.path.isfile(path) :
			files = [path]
		return files

    def parse_dir_files (self, path) :
	fdir = Directory()
	return fdir.get_files(path)

    def create_pdf (self) :
	self.pdf.build(self.pdf_path)
