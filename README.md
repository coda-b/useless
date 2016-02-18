# Compiler(Python).

---

Simple compiller based on Tiny-C. 

## Menu
  * [Abilities](##Abilities)
    * [Syntax](##Syntax)
  * Uses
    * [Lexer](###Lexical-analysis)
    * [Parser](##Parser)
    * [Machine code](##Machine-code)
    * [Compiler](##Compiler)
    * [What's next?](##What's-next?)
  
---

## Abilities
- One type of variables - int.
- All variables is global and there are can be only 26 variables(a-z).
- It supports only "+" and "-".
- One conditional operator "<".
- Only: if, if/else, while, do/while.

There are no any arrays or functions.

## Syntax
It is written in the [ENBF](https://en.wikipedia.org/wiki/Extended_Backus-Naur_Form) form.

```EBNF
<program> ::= <statement>
<statement> ::= "if" <paren-expr> <statement> |
                 "if" <paren-expr> <statement> "else" <statement> |
                 "while" <paren-expr> <statement> |
                 "do" <statement> "while" <paren-expr> |
                 "{" { <statement> } "}" |
                 <expr> ";" |
                 ";"
<paren-expr> ::= "(" <expr> ")"
<expr> ::= <test> | <id> "=" <expr>
<test> ::= <sum> | <sum> "<" <sum>
<sum>  ::= <term> | <sum> "+" <term> | <sum> "-" <term>
<term> ::= <id> | <int> | <paren-expr>
<id>   ::= "a" | "b" | ... | "z"
<int>  ::= <digit>, { <digit> }
<digit> ::= "0" | "1" | ... | "9" 
```
I explain this approximately:
- Program is always one statement.
- Operators can be conditional(if/else), loop(do/while), simple(a=5+6).
- Also you can use "{}".
- Expressions is always sum or variable assignment.
- Sum is always the sequence of addition and substraction terms.
- Term means number, variable or expressins in brackets.
- Variables - letters from "a" to "z". Numbers is 0-9.

### Lexical analysis
These [lexical analyzer](https://en.wikipedia.org/wiki/Lexical_analysis) must to know:

- Numbers.
- Variables.
- If, if/else, while, do/while.
- Symbols: +, -, <, =, {}, ().
- End of file.
```Python
class Lexer:

	NUM, ID, IF, ELSE, WHILE, DO, LBRA, RBRA, LPAR, RPAR, PLUS, MINUS, LESS, \
	EQUAL, SEMICOLON, EOF = range(16)

	# специальные символы языка
	SYMBOLS = { '{': LBRA, '}': RBRA, '=': EQUAL, ';': SEMICOLON, '(': LPAR,
		')': RPAR, '+': PLUS, '-': MINUS, '<': LESS }

	# ключевые слова
	WORDS = { 'if': IF, 'else': ELSE, 'do': DO, 'while': WHILE }

	# текущий символ, считанный из исходника
	ch = ' ' # допустим, первый символ - это пробел

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
```
And it also ignore spaces. It cheks current symbol whether it's specific symbol of these language, if not - whether if it's a number.

## Parser
It needs to built his own [hierarchy](https://en.wikipedia.org/wiki/Abstract_syntax_tree) from current tokens like: 
```
"if (a < 0) a = 5;"

IF
+-LESS
|  +-VAR(a)
|  +-NUM(0)
+-SET
  +-VAR(a)
  +-NUM(5)
```
Here these code:
```Python
class Node:
	def __init__(self, kind, value = None, op1 = None, op2 = None, op3 = None):
		self.kind = kind
		self.value = value
		self.op1 = op1
		self.op2 = op2
		self.op3 = op3

class Parser:

	VAR, CONST, ADD, SUB, LT, SET, IF1, IF2, WHILE, DO, EMPTY, SEQ, EXPR, PROG = range(14)

	def __init__(self, lexer):
		self.lexer = lexer

	def error(self, msg):
		print 'Parser error:', msg
		sys.exit(1)

	def term(self):
		if self.lexer.sym == Lexer.ID:
			n = Node(Parser.VAR, self.lexer.value)
			self.lexer.next_tok()
			return n
		elif self.lexer.sym == Lexer.NUM:
			n = Node(Parser.CONST, self.lexer.value)
			self.lexer.next_tok()
			return n
		else:
			return self.paren_expr()

	def summa(self):
		n = self.term()
		while self.lexer.sym == Lexer.PLUS or self.lexer.sym == Lexer.MINUS:
			if self.lexer.sym == Lexer.PLUS:
				kind = Parser.ADD
			else:
				kind = Parser.SUB
			self.lexer.next_tok()
			n = Node(kind, op1 = n, op2 = self.term())
		return n

	def test(self):
		n = self.summa()
		if self.lexer.sym == Lexer.LESS:
			self.lexer.next_tok()
			n = Node(Parser.LT, op1 = n, op2 = self.summa())
		return n

	def expr(self):
		if self.lexer.sym != Lexer.ID:
			return self.test()
		n = self.test()
		if n.kind == Parser.VAR and self.lexer.sym == Lexer.EQUAL:
			self.lexer.next_tok()
			n = Node(Parser.SET, op1 = n, op2 = self.expr())
		return n

	def paren_expr(self):
		if self.lexer.sym != Lexer.LPAR:
			self.error('"(" expected')
		self.lexer.next_tok()
		n = self.expr()
		if self.lexer.sym != Lexer.RPAR:
			self.error('")" expected')
		self.lexer.next_tok()
		return n

	def statement(self):
		if self.lexer.sym == Lexer.IF:
			n = Node(Parser.IF1)
			self.lexer.next_tok()
			n.op1 = self.paren_expr()
			n.op2 = self.statement()
			if self.lexer.sym == Lexer.ELSE:
				n.kind = Parser.IF2
				self.lexer.next_tok()
				n.op3 = self.statement()
		elif self.lexer.sym == Lexer.WHILE:
			n = Node(Parser.WHILE)
			self.lexer.next_tok()
			n.op1 = self.paren_expr()
			n.op2 = self.statement();
		elif self.lexer.sym == Lexer.DO:
			n = Node(Parser.DO)
			self.lexer.next_tok()
			n.op1 = self.statement()
			if self.lexer.sym != Lexer.WHILE:
				self.error('"while" expected')
			self.lexer.next_tok()
			n.op2 = self.paren_expr()
			if self.lexer.sym != Lexer.SEMICOLON:
				self.error('";" expected')
		elif self.lexer.sym == Lexer.SEMICOLON:
			n = Node(Parser.EMPTY)
			self.lexer.next_tok()
		elif self.lexer.sym == Lexer.LBRA:
			n = Node(Parser.EMPTY)
			self.lexer.next_tok()
			while self.lexer.sym != Lexer.RBRA:
				n = Node(Parser.SEQ, op1 = n, op2 = self.statement())
			self.lexer.next_tok()
		else:
			n = Node(Parser.EXPR, op1 = self.expr())
			if self.lexer.sym != Lexer.SEMICOLON:
				self.error('";" expected')
			self.lexer.next_tok()
		return n

	def parse(self):
		self.lexer.next_tok()
		node = Node(Parser.PROG, op1 = self.statement())
		if (self.lexer.sym != Lexer.EOF):
			self.error("Invalid statement syntax")
		return node
```
## Machine code
Here you can see bite-code of these virtual machine. It also uses [stack](https://en.wikipedia.org/wiki/Stack_(abstract_data_type)), because it's easier than register.

- FETCH x - write x.
- STORE x - save on variable x value from top.
- PUSH  n - write n to the top.
- POP     - delete number from the top.
- ADD     - add two numbers from the top.
- SUB     - substract two numbers from the top.
- LT      - compare two numbers from the top (a < b). Result - 0 or 1 (true or false).
- JZ    a - if it is 0 on the top - go to a.
- JNZ   a - if it isn't 0 on the top - go to a.
- JMP   a - go to a.
- HALT    - stop.

Example: a = 69; b = 9; means PUSH 69 STORE 0 PUSH 9 STORE 1

Here the code:
```Python
IFETCH, ISTORE, IPUSH, IPOP, IADD, ISUB, ILT, JZ, JNZ, JMP, HALT = range(11)

class VirtualMachine:

	def run(self, program):
		var = [0 for i in xrange(26)]
		stack = []
		pc = 0
		while True:
			op = program[pc]
			if pc < len(program) - 1:
				arg = program[pc+1]

			if op == IFETCH: stack.append(var[arg]); pc += 2
			elif op == ISTORE: var[arg] = stack.pop(); pc += 2
			elif op == IPUSH: stack.append(arg); pc += 2
			elif op == IPOP: stack.append(arg); stack.pop(); pc += 1
			elif op == IADD: stack[-2] += stack[-1]; stack.pop(); pc += 1
			elif op == ISUB: stack[-2] -= stack[-1]; stack.pop(); pc += 1
			elif op == ILT: 
				if stack[-2] < stack[-1]:
					stack[-2] = 1
				else:
					stack[-2] = 0
				stack.pop(); pc += 1
			elif op == JZ: 
				if stack.pop() == 0:
					pc = arg
				else:
					pc += 2
			elif op == JNZ: 
				if stack.pop() != 0:
					pc = arg
				else:
					pc += 2
			elif op == JMP: pc = arg;
			elif op == HALT: break

		print 'Execution finished.'
		for i in xrange(26):
			if var[i] != 0:
				print '%c = %d' % (chr(i+ord('a')), var[i])
```

## Compiler
Properly here the code:
```Python
class Compiler:
	
	program = []
	pc = 0

	def gen(self, command):
		self.program.append(command)
		self.pc = self.pc + 1
	
	def compile(self, node):
		if node.kind == Parser.VAR:
			self.gen(IFETCH)
			self.gen(node.value)
		elif node.kind == Parser.CONST:
			self.gen(IPUSH)
			self.gen(node.value)
		elif node.kind == Parser.ADD:
			self.compile(node.op1)
			self.compile(node.op2)
			self.gen(IADD)
		elif node.kind == Parser.SUB:
			self.compile(node.op1)
			self.compile(node.op2)
			self.gen(ISUB)
		elif node.kind == Parser.LT:
			self.compile(node.op1)
			self.compile(node.op2)
			self.gen(ILT)
		elif node.kind == Parser.SET:
			self.compile(node.op2)
			self.gen(ISTORE)
			self.gen(node.op1.value)
		elif node.kind == Parser.IF1:
			self.compile(node.op1)
			self.gen(JZ); addr = self.pc; self.gen(0);
			self.compile(node.op2)
			self.program[addr] = self.pc
		elif node.kind == Parser.IF2:
			self.compile(node.op1)
			self.gen(JZ); addr1 = self.pc; self.gen(0)
			self.compile(node.op2)
			self.gen(JMP); addr2 = self.pc; self.gen(0)
			self.program[addr1] = self.pc
			self.compile(node.op3)
			self.program[addr2] = self.pc
		elif node.kind == Parser.WHILE:
			addr1 = self.pc
			self.compile(node.op1)
			self.gen(JZ); addr2 = self.pc; self.gen(0)
			self.compile(node.op2)
			self.gen(JMP); self.gen(addr1);
			self.program[addr2] = self.pc
		elif node.kind == Parser.DO:
			addr = self.pc
			self.compile(node.op1)
			self.compile(node.op2)
			self.gen(JNZ); 
			self.gen(addr);
		elif node.kind == Parser.SEQ:
			self.compile(node.op1)
			self.compile(node.op2)
		elif node.kind == Parser.EXPR:
			self.compile(node.op1);
			self.gen(IPOP)
		elif node.kind == Parser.PROG:
			self.compile(node.op1);
			self.gen(HALT)
		return self.program
```
## What's next?
I going to complete these in a future, maybe.
