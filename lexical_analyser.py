import re
import copy
from token import *



class Token(object):

	def __init__(self, code, tp, pos, value, line):
		self.code = code
		self.pos = pos
		self.tp = tp
		self.value = value
		self.line = line + 1
		if tp == "INT_VAL":
			if len(value) > 2:
				if value[0] == "0":
					if value[1] == "x" or value[1] == "X":
						self.value = int(value, 16)
					else:
						self.value = int(value, 8)
				else:
					self.value = int(value)
		if tp == "DOUBLE_VAL":
			self.value = float(value)
		if tp == "STRING" or tp == "CHAR":
			self.value = value.encode().decode('unicode_escape')

	def __str__(self):
		return  "%s  %s  %s  -%s-" % (self.code, self.tp, self.value, self.line) 


class TokenError(Exception):
	def __init__(self, pos):
		self.pos = pos

	def __init__(self, token, message):
		self.token = token
		self.message = message

	def __str__(self):
		return "%s %s" % (self.token, self.message)

class TokenGenerator(object):

	def __init__(self, rules, content):
		self.lineNr = 0
		self.lines = iter(content)
		self.pos = 0
		self.content = self.comment_remover(content)
		# print(self.content)
		idx = 1
		regexRules = []
		self.groupType = {}
		for regex, type in rules:
			groupName = "GROUP%s" % idx
			regexRules.append("(?P<%s>%s)" % (groupName, regex))
			self.groupType[groupName] = type
			idx += 1

		self.jointRegex = re.compile("|".join(regexRules))
		self.toSkip = re.compile("\S")
		self.toCount = re.compile(r"\n");


	def comment_remover(self, text):
	    def replacer(match):
	        s = match.group(0)
	        # print(s)
	        # print(s)
	        # if s.startswith('/*'):
	        #     return "\n"
	        # elif s.startswith('/'):
	        # 	return " "
	        if s.startswith('/'):
		        if '\n' in s:
		        	x = s.count('\n')
		        	return '\n'*x
		        else:
		        	return ' '
	        else:
	            return s
	    pattern = re.compile(
	        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
	        re.DOTALL | re.MULTILINE
	    )
	    return re.sub(pattern, replacer, text)


	def reset(self, content):
		self.pos = 0
		self.content = content

	def token(self):
		if self.pos >= len(self.content):
			return None
		else:
			match = self.toSkip.search(self.content, self.pos)
			if match:
				self.pos = match.start()
				# print(content[self.pos])
			else:
				return None
			# match = self.toCount.search(self.content, self.pos)
			# if match:
			# 	# print(match.group(0))
			# 	# self.pos = match.end()
			# 	print("Incrementing")
			# 	self.lineNr = self.lineNr + 1
			#code, tp, pos, value
			match = self.jointRegex.match(self.content, self.pos)
			if match:
				groupName = match.lastgroup
				tokenType = self.groupType[groupName]
				token = Token(TOKENS[tokenType], tokenType, self.pos, match.group(groupName), self.content.count('\n', 0, self.pos))
				self.pos = match.end()
				return token

			raise TokenError(self.pos)

	def tokens(self):
		while 1:
			token = self.token()
			if token is None: break
			yield token
		yield Token(TOKENS["END"], "END", self.pos, "end", self.content.count('\n', 0, self.pos))


# if __name__ == "__main__":
with open("./tests/9.c", "r") as content_file:
	content = content_file.read()
	# print(content)
# with open("./tests/9.c", "r") as f: 
# 	data = f.readlines()
# 	print(data)
	# line_no = data.index("count")
	# print(line_no)
	# print content
all_tokens = []
tg = TokenGenerator(rules, content)
try:
	for tk in tg.tokens():
		# print(tk)
		all_tokens.append(tk)
except TokenError as err:
	print (err)
# tg = TokenGenerator(rules, content)
# for token in all_tokens:
	# print(token)