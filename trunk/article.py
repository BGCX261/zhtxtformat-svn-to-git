
import re
class Article :

    def __init__ (self) :
	pass

    def parse (self, lines, outer) :
	mode = self.__guess_article_mode(lines)
	if mode == 'standard' :
	    self.parse_standard  (lines, outer)
	else :
	    self.parse_truncated (lines, outer) 

    def parse_standard (self, lines, outer) :
	if len(lines) < 3 :
	    return False

	title = lines.pop(0)
	author= lines.pop(0)
	desc  = lines.pop(0)

	if not outer.is_empty() :
	    outer.append_pagebreak()

	outer.append_title (title)
	outer.append_author (author)
	outer.append_author_description (desc)

	for line in lines :
	    outer.append_paragraph (line)

    def parse_truncated (self, lines, outer) :
	if len(lines) < 3 :
	    return False

	title = lines.pop(0)
	author= lines.pop(0)

	newline1 = re.compile(u'^[\u3000 ]{4,}')
	newline2 = re.compile(u'^\s*\d+\s*$')
	content = []
	single_line = ''
	
	for line in lines :
	    line = line.decode('utf8')

	    if re.match(newline2, line) :
		line = line.strip(u'\u3000\n\r\t ')
		if not line :
		    continue
		content.append(single_line.encode('utf8'))
		content.append(line.encode('utf8'))
		single_line = '' 

	    elif re.match(newline1, line) :
		line = line.strip(u'\u3000\n\r\t ')
		if not line :
		    continue
		content.append(single_line.encode('utf8'))
		single_line = line

	    else :
		line = line.strip(u'\u3000\n\r\t ')
		if not line :
		    continue
		single_line += line
	
	if len(single_line) > 0 :
	    content.append(single_line.encode('utf8'))

	outer.append_title (title)
	outer.append_author (author)
	for line in content :
	    outer.append_paragraph (line)
	
    def __guess_article_mode (self, lines) :
	return 'standard'
