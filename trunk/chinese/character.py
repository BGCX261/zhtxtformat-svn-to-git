# coding: utf-8

'''
Unicode For CJK 
注：
    中文范围 4E00-9FBF：CJK 统一表意符号 (CJK Unified Ideographs)

2E80-2EFF：CJK 部首补充 (CJK Radicals Supplement)
3000-303F：CJK 符号和标点 (CJKSymbols and Punctuation)
31C0-31EF：CJK 笔画 (CJK Strokes)
3200-32FF：封闭式 CJK 文字和月份 (Enclosed CJK Letters andMonths)
3300-33FF：CJK 兼容 (CJK Compatibility)
3400-4DBF：CJK 统一表意符号扩展 A (CJK Unified Ideographs Extension A)
4E00-9FBF：CJK 统一表意符号 (CJK Unified Ideographs)
F900-FAFF：CJK 兼容象形文字 (CJK Compatibility Ideographs)
FE30-FE4F：CJK 兼容形式 (CJKCompatibility Forms)
20000..2A6D6; CJK Unified Ideographs Extension B   
2F800..2FA1F; CJK Compatibility Ideographs Supplement  

'''

class Character :

    def __init__ (self) :
	self._white_code = [0xff00, 0x3000]  # 0xFACF~0xFAD7
	pass

    def is_zh_char (self, char) :
	if 0x4E00 <= ord(char) <= 0x9FBF :
	    return True
	else :
	    return False

    def is_zh_symbol (self, char) :
	code = ord(char)
	if 0x3000 <= code <= 0x303F :
	    return True
	elif 0xFF00 <= code <= 0xFFEF:
	    return True
	elif 0xFE30 <= code <= 0xFE4F:
	    return True
	elif 0xFE10 <= code <= 0xFE1F:
	    return True
	else :
	    return False

    def is_white (self, char) :
	code = ord(char)
	return code in self._white_code

    def is_special (self, char) :
	code = ord(char)
	if 0xFFF0 <= code <= 0xFFFF :
	    return True
	else :
	    return False


    def debug (self, first_code, second_code) :
	i = 0
	for c in range(first_code, second_code + 1) :
	    print "%s -- %s\t" % (hex(c), unichr(c).encode('utf8')),
	    i += 1
	    if i % 5 == 0 :
		print ''
	print ''

