import re

def _compile(pattern):
	return re.compile(pattern)


def wrap(pattern):
	return "(" + pattern + ")"
def group(*patterns):
	return "(" + "|".join(patterns) + ")"
def any(*patterns):
	return group(*patterns) + "*"
def maybe(*patterns):
	return group(*patterns) + "?"

TOKENS = { "END" : 0,
"ID" : 1,
"KEYWORD" : 2,
"INT_VAL" : 3,
"DOUBLE_VAL" : 4,
"CHAR" : 5,
"STRING" : 6,
"COMMA" : 7,
"SEMICOLON" : 8,
"LPAR" : 9,
"RPAR" : 10,
"LBRACKET" : 11,
"RBRACKET" : 12,
"LACC" : 13,
"RACC" : 14,
"ADD" : 15,
"SUB" : 16,
"MUL" : 17,
"DIV" : 18,
"DOT" : 19,
"AND" : 20,
"OR" : 21,
"NOT" : 22,
"ASSIGN" : 23,
"EQUAL" : 24,
"NOTEQ" : 25,
"LESS" : 26,
"LESSEQ" : 27,
"GREATER" : 28,
"GREATEREQ" : 29,
"BREAK" : 30,
"CHAR" : 31,
"DOUBLE" :32,
"ELSE" : 33,
"FOR" : 34,
"IF" : 35,
"INT" : 36,
"RETURN" : 37,
"STRUCT" : 38,
"VOID" : 39,
"WHILE" : 40 }

keywords = ["break", "char", "double", "else", "for", "if", "int", "return", "struct", "void", "while"]

WhiteSpace = "\S"
LineComment = "\/\/([^\n\r\0])*"
Comment = "(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)"
Ignore = group(WhiteSpace, Comment, LineComment)


HexNumber = r"0x[0-9a-fA-F]+"
OctalNumber = r"0[0-7]*"
DecNumber = r"[1-9][0-9]*"
IntNumber = group(HexNumber, OctalNumber, DecNumber)
Exponent = "((e|E)(\-|\+)?[0-9]+)"
FloatNumber = r"[0-9]+(\.[0-9]+%s?|(\.[0-9]+)?%s)" % (Exponent, Exponent)
Name = r"[a-zA-Z_][a-zA-Z0-9_]*"
Number = group(IntNumber, FloatNumber)
# EscapeSeq = "(\\[abfnrtv\'\"\\0])"
# String = r'"(%s|[^\"\\])*"' % EscapeSeq
String = r'\"(\\[abfnrtv\'\"\\0]|[^\"\\])*\"'
Char = r"\'(\\[abfnrtv\'\"\\0]|[^\'\\])\'"
# SingularTokens = r"%s" % group(*map(re.escape, SINGULAR_TOKENS.keys()))
Keywords = r"%s" % group(*keywords)


rules = [
	(String, "STRING"),
	(Char, "CHAR"),
	(FloatNumber, "DOUBLE_VAL"),
	(IntNumber, "INT_VAL"),
	("break", "BREAK"),
	("char", "CHAR"),
	("double", "DOUBLE"),
	("else", "ELSE"),
	("for", "FOR"),
	("if", "IF"),
	("int", "INT"),
	("return", "RETURN"),
	("struct", "STRUCT"),
	("void", "VOID"),
	("while", "WHILE"),
	(Name, "ID"),
	("\,", "COMMA"),
	("\.", "DOT"),
	("\;", "SEMICOLON"),
	("\(", "LPAR"),
	("\)", "RPAR"),
	("\[", "LBRACKET"),
	("\]", "RBRACKET"),
	("\{", "LACC"),
	("\}", "RACC"),
	("\+", "ADD"),
	("\-", "SUB"),
	("\*", "MUL"),
	("\/", "DIV"),
	("\&\&", "AND"),
	("\|\|", "OR"),
	("\!\=", "NOTEQ"),
	("\!", "NOT"),
	("\=\=", "EQUAL"),
	("\<\=", "LESSEQ"),
	("\>\=", "GREATEREQ"),
	("\=", "ASSIGN"),
	("\<", "LESS"),
	("\>", "GREATER")

]