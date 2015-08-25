import os
import re

class Directory :
    def __init__ (self):
	pass
	
    def get_files (self, path) :
	fs    = []
	files = os.listdir(path)
	for f in files :
	    fpath = path + os.sep + f;
	    if os.path.isfile(fpath) :
		fs.append(fpath)

	return self.__filter(fs)

    def __filter (self, paths) :
	fs = {}
	for p in paths :
	   idx = self.__get_index (p) 
	   fs[idx] = p

	idxs = fs.keys()
	idxs.sort()
	paths = [] 
	for idx in idxs :
	    paths.append(fs.get(idx))

	return paths

    def __get_index (self, path) :
	basename    = os.path.basename(path)
	book_number = re.compile('^(\d+).*')
	m = re.match(book_number, basename)
	if m :
	    return m.group(1)
	else :
	    return 1
