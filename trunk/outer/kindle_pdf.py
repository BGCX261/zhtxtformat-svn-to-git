import sys
import os
import copy

import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import Paragraph, BaseDocTemplate, Spacer, PageBreak,Image, Frame, PageTemplate, Flowable
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics,ttfonts
from reportlab.pdfgen import canvas 
import PIL;

def _doNothing (canvas, doc) :
    pass

class Bookmark (Flowable) :

    def __init__ (self, title, key) :
	self._title = title
	self._key   = key
	Flowable.__init__(self)

    def wrap (self, availWidth, availHeight) :
	return (0, 0)

    def draw (self) :
	#self.canv.showOutline()
	self.canv.bookmarkPage(self._key)
	#self.canv.addOutlineEntry(self._title, self._key, 0, 0)
	#self.canv.linkAbsolute(self._title, self._key)


class KindleDocTemplate(BaseDocTemplate):
    _invalidInitArgs = ('pageTemplates',)

    def set_hidden_style (self, style) :
	self.hiddenStyle      = style
	self._breaks          = 0
	self._bookmark_index  = 0 
	self._bookmarks       = {}

    def afterFlowable (self, flowable) :
	className = flowable.__class__.__name__
	if className == 'Paragraph' :
	    style = flowable.style.name
	    if style == 'TOCEntry_h2' :
		level = 1 
		text  = flowable.getPlainText()
		E     = [level, text, self.page]
		key   = getattr(flowable, '_bookmark_key', None)
		if key is not None : 
		    E.append(key)
		self.notify('TOCEntry', tuple(E))

    '''
    def handle_flowable (self, flowables) :
	print "FLOWABLE: ", type(flowables), len(flowables) 
	BaseDocTemplate.handle_flowable(self, flowables)
    '''

    def handle_pageBreak(self, slow=None):
	self._breaks += 1
	if self._breaks > 1 and self.page > 1 :
	    frame = self.frame
	    while (frame._y > 60) :
		para = Paragraph (u'\u3000.'.encode('utf8'), self.hiddenStyle) 
		frame.add(para, self.canv, trySplit=0)
	BaseDocTemplate.handle_pageBreak(self, slow)

    def handle_pageBegin(self):
        '''override base method to add a change of page template after the firstpage.
        '''
        self._handle_pageBegin()
        self._handle_nextPageTemplate('Later')

    def build(self,flowables,onFirstPage=_doNothing, onLaterPages=_doNothing, canvasmaker=canvas.Canvas):
        self._calc()    #in case we changed margins sizes etc
        frameT = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='normal')
        self.addPageTemplates([PageTemplate(id='First',frames=frameT, onPage=onFirstPage,pagesize=self.pagesize),
                        PageTemplate(id='Later',frames=frameT, onPage=onLaterPages,pagesize=self.pagesize)])
        if onFirstPage is _doNothing and hasattr(self,'onFirstPage'):
            self.pageTemplates[0].beforeDrawPage = self.onFirstPage
        if onLaterPages is _doNothing and hasattr(self,'onLaterPages'):
            self.pageTemplates[1].beforeDrawPage = self.onLaterPages
        BaseDocTemplate.build(self,flowables, canvasmaker=canvasmaker)


class KindlePDF :

    def __init__ (self) :

	self._toc = None 

	pdfmetrics.registerFont(ttfonts.TTFont('huangcao', '/home/ali0t4/.fonts/TTF/FZHuangCao-S09.ttf')) 
	pdfmetrics.registerFont(ttfonts.TTFont('weibei', '/home/ali0t4/.fonts/TTF/FZWeiBei-S03.ttf')) 
	pdfmetrics.registerFont(ttfonts.TTFont('yahei', '/home/ali0t4/.fonts/TTF/FZLanTingHei-R-GBK.ttf')) 
	pdfmetrics.registerFont(ttfonts.TTFont('shoujinshu', '/home/ali0t4/.fonts/TTF/STKaiti.ttf')) 
	reportlab.lib.fonts.ps2tt = lambda psfn: ('yahei', 0, 0)
	reportlab.lib.fonts.tt2ps = lambda fn,b,i: 'yahei'

	ParagraphStyle.defaults['wordWrap'] = 'CJK'
	ParagraphStyle.defaults['spaceBefore'] = 0 
	ParagraphStyle.defaults['spaceAfter'] = 0 

	style = getSampleStyleSheet()
	self.normalStyle = copy.deepcopy(style['Normal']) 
	self.normalStyle.fontName = 'yahei'
	self.normalStyle.fontSize = 22 
	self.normalStyle.leading  = 32 
	self.normalStyle.firstLineIndent = 44 
	self.normalStyle.spaceBefore = 8 
	self.normalStyle.spaceAfter  = 8 

	self.hiddenStyle = copy.deepcopy(style['Normal']) 
	self.hiddenStyle.fontName = 'yahei'
	self.hiddenStyle.fontSize = 22 
	self.hiddenStyle.leading  = 32 
	self.hiddenStyle.textColor= (0.99, 0.99, 0.99) 
	self.hiddenStyle.firstLineIndent = 44 
	self.hiddenStyle.spaceBefore = 8 
	self.hiddenStyle.spaceAfter  = 8 
	
	self.titleStyle = copy.deepcopy(style['Title']) 
	self.titleStyle.fontName = 'huangcao'
	self.titleStyle.fontSize = 48 
	self.titleStyle.leading  = 64 
	self.titleStyle.name     = 'TOCEntry_h2'
	
	self.authorStyle = copy.deepcopy(style['Normal']) 
	self.authorStyle.fontName = 'weibei'
	self.authorStyle.textColor= (0.3, 0.3, 0.3) 
	self.authorStyle.fontSize = 32 
	self.authorStyle.leading  = 48 
	self.authorStyle.alignment = 2  # TA_RIGHT
	self.authorStyle.rightIndent = 20 

	self.descStyle = copy.deepcopy(style['Normal']) 
	self.descStyle.fontName = 'shoujinshu'
	self.descStyle.textColor= (0.3, 0.3, 0.3) 
	self.descStyle.fontSize = 20 
	self.descStyle.leading  = 36 
	self.descStyle.firstLineIndent = 40
	
	self.sectionStyle = copy.deepcopy(style['Heading4']) 
	self.sectionStyle.fontName = 'shoujinshu'
	self.sectionStyle.fontSize = 30 
	self.sectionStyle.leading  = 40

	self._bookmark_index = None
	self.story = []

    def is_empty (self) :
	return len(self.story) == 0

    def append_author (self, author) :
	self.story.append(Paragraph(author, self.authorStyle))

    def append_author_description (self, description) :
	self.story.append(Paragraph(description, self.descStyle))

    def append_title  (self, title) :
	bookmarkName = None
	if self._bookmark_index is not None :
	    self._bookmark_index += 1
	    bookmarkName = 's' + str(self._bookmark_index)
	    p = Paragraph(title + '<a name="%s"/>' % bookmarkName,  self.titleStyle)
	else :
	    p = Paragraph(title,  self.titleStyle)
	p._bookmark_key = bookmarkName
	self.story.append(p)

    def create_table_of_contents (self) :
	self._bookmark_index = 0;
	h1 = ParagraphStyle(name = 'heading1', fontSize=22, leading=32, fontName='shoujinshu')
	self._toc = TableOfContents()
	self._toc.levelStyles = [h1]
	if len(self.story) == 1 :
	    item = self.story[0]
	    if item.__class__.__name__ == 'Image' :
		self.append_pagebreak()
	self.story.append(self._toc)

    def add_bookmark (self, title, key) :
	pass
	'''
	if self._toc :
	    pageNum = int(key[1:]) 
	    self._toc.addEntry(0, title, pageNum, key)
	    #self.story.append(Bookmark(title, key))
	    print title, "\t", key, "\t", pageNum
	'''

    def append_section_header (self, header) :
        self.story.append(Paragraph(header, self.sectionStyle))

    def append_paragraph (self, text) :
	self.story.append(Paragraph(text, self.normalStyle))

    def append_pagebreak (self) :
	self.story.append(PageBreak()) 

    def set_cover (self, cover_path) :
	self.append_image (cover_path, 0)

    def append_image (self, picpath, story_index = None) :

	im = PIL.Image.open(picpath)
	img = im.copy()
	(rw, rh) = img.size
	if (rw > rh) :
	    img.rotate(90)
	img.thumbnail((560, 760), PIL.Image.ANTIALIAS)
	(rw, rh) = img.size

	(thumbnail, ext) = os.path.splitext(picpath)
	thumbnail_path = thumbnail + '.thumb.jpg'
	img2 = img.convert('L')
	img2.save(thumbnail_path)

	image = Image(thumbnail_path, rw, rh)
	if None is story_index :
	    self.story.append(image)
	else :
	    self.story.insert(story_index, image)

    def build (self, pdf_path) :

	author = ''
	title  = ''

	#pdf = SimpleDocTemplate(pdf_path, pagesize = (600, 800), leftMargin = 15, topMargin=15, rightMargin=10, bottomMargin=10, author=author, title=title.encode('gb2312'))
	pdf = KindleDocTemplate(pdf_path, pagesize = (600, 800), leftMargin = 15, topMargin=15, rightMargin=10, bottomMargin=10, author=author, title=title.encode('gb2312'))
	pdf.set_hidden_style (self.hiddenStyle)

	if self._toc :
	    pdf.multiBuild(self.story)
	else :
	    pdf.build(self.story)
