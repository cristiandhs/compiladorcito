import ply.lex as lex
from ply.lex import LexToken

# reserved words
reserved = {
    # logical operators
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',

    # control structures
    'if' : 'IF',
    'then' : 'THEN',
    'else' : 'ELSE',
    'endif' : 'ENDIF',
    'while' : 'WHILE',
    'endwhile' : 'ENDWHILE',
    'do' : 'DO',

    # others
    'write' : 'WRITE',
    'capture' : 'CAPTURE',
}

# List of token names.
tokens = (
    'ID',       # variable
    'ASSIGN',   # =
    'NUMBER',
    'STRING',

    'DPOINTS',  # ::

    'LESSEQ',   # <=
    'GREATEREQ',# >=
    'EQUALS',   # ==
    'NOTEQ',    # <>
) + tuple(reserved.values())

literals = ('+', '-', '*', '/', '(', ')', '<', '>', ',')

t_EQUALS = r'=='
t_LESSEQ = r'<='
t_GREATEREQ = r'>='
t_NOTEQ = r'<>'
t_DPOINTS = r'::'
t_ASSIGN = r'='

def t_ID(t: LexToken):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t


# A regular expression rule with some action code
def t_NUMBER(t: LexToken):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t: LexToken):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_STRING(t: LexToken):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]  # Remove quotes
    return t


# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t: LexToken):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()