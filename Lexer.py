#!/kill/yourself/Lexer.py

class Lexer:

	NUM, ID, IF, ELSE, WHILE, DO, LBRA, RBRA, LPAR, RPAR, PLUS, MINUS, LESS, \
	EQUAL, SEMICOLON, EOF = range(16)

	SYMBOLS = { '{': LBRA, '}': RBRA, '=': EQUAL, ';': SEMICOLON, '(': LPAR,
		')': RPAR, '+': PLUS, '-': MINUS, '<': LESS }
	WORDS = { 'if': IF, 'else': ELSE, 'do': DO, 'while': WHILE }

	ch = ' ' # assume the first char is a space

	def error(self, msg):
		print 'Lexer error: ', msg
		sys.exit(1)

	def getc(self):
		self.ch = sys.stdin.read(1)
	
	def next_tok(self):
		self.value = None
		self.sym = None
		while self.sym == None:
			if len(self.ch) == 0:
				self.sym = Lexer.EOF
			elif self.ch.isspace():
				self.getc()
			elif self.ch in Lexer.SYMBOLS:
				self.sym = Lexer.SYMBOLS[self.ch]
				self.getc()
			elif self.ch.isdigit():
				intval = 0
				while self.ch.isdigit():
					intval = intval * 10 + int(self.ch)
					self.getc()
				self.value = intval
				self.sym = Lexer.NUM
			elif self.ch.isalpha():
				ident = ''
				while self.ch.isalpha():
					ident = ident + self.ch.lower()
					self.getc()
				if ident in Lexer.WORDS:
					self.sym = Lexer.WORDS[ident]
				elif len(ident) == 1:
					self.sym = Lexer.ID
					self.value = ord(ident) - ord('a')
				else:
					self.error('Unknown identifier: ' + ident)
			else:
				self.error('Unexpected symbol: ' + self.ch)

