# coding: utf-8

import re
import chardet
from article import Article

class Plain :

    def __init__ (self, path) :
	self.path = path
	self.default_coding = 'utf-8'
	self.outer = None

    def parse (self, outer) :
	self.outer = outer
	self.single_article ()
	#self.multiple_articles()
	#self.menuable_articles()

    def single_article (self) :
	lines = self.__load_content_lines ()
	page_number = re.compile(u'\u00b7\d+\u00b7');
	#pattern = re.compile('[\ufb00-\ufffd]\d+[\ufb00-\ufffd]');

	texts = []
	for line_orig in lines :
	    line = line_orig.decode('utf8')
	    line = line.strip(u'\u3000 \t\r\n')
	    
	    if not line :
		continue

	    if re.search (page_number, line) :
		continue
	    else :
		line = line.encode('utf8')
		texts.append(line)

	if len(texts) > 0 :
	    article = Article()
	    article.parse(texts, self.outer)

    def menuable_articles (self) :
	lines = self.__load_content_lines ()
	menu  = self.__load_book_menu (lines)
	articles = self.__parse_articles (lines, menu)
	for art in articles :
	    start_line = art['start_line']
	    end_line   = art['end_line']
	    author     = art['author']
	    title      = art['title']

	    print "%06d, %06d, %s, %s" % (start_line, end_line, author, title)

	    contents   = lines[start_line : end_line]
	    contents.insert(0, title.encode('utf8'))
	    contents.insert(1, author.encode('utf8'))

	    article = Article()
	    article.parse(contents, self.outer)

    def multiple_articles (self) :
	lines = self.__load_content_lines ()
	page_number = re.compile(u'\u00b7\d+\u00b7');
	#pattern = re.compile('[\ufb00-\ufffd]\d+[\ufb00-\ufffd]');

	texts = []
	for line_orig in lines :
	    line = line_orig.decode('utf8')
	    line = line.strip(u'\u3000 \t\r\n')
	    
	    if not line :
		continue

	    if re.search (page_number, line) :
		line = line.encode('utf8')
		if len(texts) > 0 :
		    article = Article()
		    article.parse(texts, self.outer)
		texts = []
	    else :
		line = line.encode('utf8')
		texts.append(line)

    def __auto_convert (self, s, coding) :
	codes = chardet.detect(s[:600])
	code1 = codes.get('encoding')
	if 'gb2312' == code1.lower() :
	    code1 = 'gbk'

	if code1 == coding :
	    return s
	else :
	    return s.decode(code1, 'ignore').encode(coding)

    def __load_content_lines (self) :
	f = open(self.path, 'r') 
	content = f.read()
	content = self.__auto_convert(content, self.default_coding)
	f.close()

	return content.split("\n")

    def __load_book_menu (self, lines) :
	r1 = re.compile(u'^\s*目\s*录\s*$')
	r2 = re.compile(u'^\s*([^·…]+)\s*[·．…]{2,}\s*([l\d]+)\s*$')
	menus = {}
	start = False
	not_match = 0
	for line in lines :
	    words = line.decode(self.default_coding)
	    words.strip('\n')
	    if re.match(r1, words) :
		start = True
		continue
	    elif start :
		m = re.match(r2, words)
		if m :
		    title = m.group(1)
		    page  = m.group(2)
		    page  = page.replace('l', '1')
		    page  = int(page.encode(self.default_coding))
		    menus[page] = self.__get_simple_string(title)
		    not_match = 0
		else :
		    not_match += 1
		    if not_match > 10 :
			break
	
	return menus

    def __parse_articles (self, lines, menus) :
	titles = menus.values()
	i = 0
	article_idxs = {}
	for line in lines :
	    words = line.decode(self.default_coding)
	    words.strip('\n')
	    words = self.__get_simple_string(words)

	    if len(titles) == 0 :
		break;

	    try :
		t = titles.index(words)
		titles.pop(t)
		author_line = lines[i - 1]
		author_line = author_line.decode(self.default_coding)
		author = self.__get_simple_string(author_line)

		article = {
		    'start_line' : i + 1,
		    'end_line' : 0,
		    'author' : author,
		    'title' : words,
		}

		article_idxs[i + 1] = article
	    except :
		pass
	    i += 1

	# sort 
	idxs = article_idxs.keys()
	idxs.append(len(lines) + 1)
	idxs.sort()
	articles = []
	for i in range(0, len(idxs) - 1) :
	    start_line = idxs[i]
	    end_line   = idxs[i + 1] - 2;
	    article_idxs[start_line]['end_line'] = end_line
	    articles.append(article_idxs[start_line])

	for t in titles :
	    pass

	return articles

    def __get_simple_string (self, s) :
	s1 = s.strip(u'\u3000 \t\r\n')
	s1 = s1.replace(u'\u3000', '')
	s1 = s1.replace(' ', '')
	return s1
