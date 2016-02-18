#!/kill/yourself/virtual.py


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


