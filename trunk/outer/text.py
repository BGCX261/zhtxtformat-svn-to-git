import sys
import os

class TextOutput :

    def __init__ (self) :
	self.story = []

    def is_empty (self) :
	return len(self.story) == 0

    def append_author (self, author) :
	self.story.append("<AUTHOR>: " + author)

    def append_author_description (self, description) :
	self.story.append("<DESCRIPTION>: " + description)

    def append_title  (self, title) :
	self.story.append("<TITLE>: " + title)

    def append_section_header (self, header) :
	self.story.append("<HEADER>: " + header)

    def append_paragraph (self, text) :
	self.story.append(text)

    def append_pagebreak (self) :
	self.story.append("============ NEW PAGE =============")

    def set_cover (self, cover_path) :
	self.append_image (cover_path, 0)

    def append_image (self, picpath, story_index = None) :
	self.story.append("<IMG>: " + picpath)

    def build (self, file_path) :

	fh = open(file_path, 'w')
	for line in self.story :
	    fh.write(line + "\n")
	fh.close()
