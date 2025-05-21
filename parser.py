import ply.yacc as yacc
from lexer import tokens
from capture_utils import obtener_valor_capture_sync, ES_WEB

variables = {}
salidas = []


precedence = (

    ('left', 'EQUALS', 'NOTEQ', '<', '>', 'LESSEQ', 'GREATEREQ'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'ASSIGN'),

)


def p_program(p):
    'program : statement_list'
    p[0] = p[1]


def p_statement_list(p):
    """statement_list : statement
                      | statement statement_list"""
    if len(p) == 2:
        p[0] = ('statement_list', [p[1]])
    else:
        if isinstance(p[2], tuple) and p[2][0] == 'statement_list':
            p[0] = ('statement_list', [p[1]] + p[2][1])
        else:
            p[0] = ('statement_list', [p[1], p[2]])


def p_statement(p):
    """statement : assignment DPOINTS
                 | write DPOINTS
                 | capture DPOINTS
                 | expression DPOINTS
                 | if_statement
                 | while_statement"""
    p[0] = p[1]


def p_write(p):
    """write : WRITE '(' STRING ')'
             | WRITE '(' expression ')'
             | WRITE '(' STRING ',' expression ')' """

    if len(p) == 5:  # write("mensaje")
        p[0] = ('WRITE', p[3])
    elif len(p) == 7:  # write("mensaje", expresion)
        p[0] = ('WRITE', p[3], p[5])


def p_capture(p):
    "capture : CAPTURE '(' ID ')'"
    p[0] = ('CAPTURE', p[3])


def p_while_statement(p):
    """while_statement : WHILE condition DO statement_list ENDWHILE"""
    p[0] = ('WHILE', p[2], p[4])


def p_if_statement(p):
    "if_statement : IF condition THEN statement_list opt_else ENDIF"
    p[0] = ('IF', p[2], p[4], p[5])


def p_opt_else(p):
    """opt_else : ELSE statement_list
                | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None


def p_condition(p):
    "condition : '(' boolean_expr ')'"
    p[0] = p[2]


def p_boolean_expr(p):
    """boolean_expr : expression relational_operator expression
                    | expression EQUALS expression
                    | expression NOTEQ expression
                    | expression '<' expression
                    | expression '>' expression
                    | expression LESSEQ expression
                    | expression GREATEREQ expression
                    | expression AND expression
                    | expression OR expression
                    | NOT expression"""
    if len(p) == 4:
        if p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = (p[2], p[1], p[3])
    elif len(p) == 3:
        p[0] = ('not', p[2])
    else:
        p[0] = p[1]


def p_relational_operator(p):
    """relational_operator : '<'
                           | '>'
                           | LESSEQ
                           | GREATEREQ
                           | EQUALS
                           | NOTEQ"""
    p[0] = p[1]


def p_assignment(p):
    """assignment : ID ASSIGN expression
                  | ID ASSIGN boolean_expr"""
    if p[3] is None:
        error_message = f"Error: Asignación incompleta para '{p[1]}'"
        print(error_message)
        salidas.append(error_message)
        p[0] = None
    else:
        p[0] = ('ASSIGN', p[1], p[3])


def p_expression(p):
    """expression : term
                  | expression '+' term
                  | expression '-' term
                  | condition"""
    if len(p) == 4:
        if p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]


def p_term(p):
    """term : factor
            | term '*' factor
            | term '/' factor"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = (p[2], p[1], p[3])


def p_factor_num(p):
    "factor : NUMBER"
    p[0] = p[1]


def p_factor_expr(p):
    "factor : '(' expression ')'"
    p[0] = p[2]


def p_factor_id(p):
    "factor : ID"
    try:
        p[0] = ('GETVAR', p[1])
    except KeyError:
        error_message = f"Error: Variable '{p[1]}' not defined."
        print(error_message)
        salidas.append(error_message)
        p[0] = 0


def p_empty(p):
    "empty :"
    p[0] = None


errorFound = False


def p_error(p):
    global errorFound
    errorFound = True
    if p:
        error_message = f"Syntax error at '{p.value}'"
        print(error_message)
        salidas.append(error_message)
    else:
        error_message = "Syntax error at end of input"
        print(error_message)
        salidas.append(error_message)


def obtener_salidas():
    global salidas
    resultado = "\n".join(salidas)
    salidas = []  # Limpia después de obtener
    return resultado


# Build the parser
parser = yacc.yacc(start='program')


def run(p):
    if type(p) == tuple:
        if p[0] == '+':
            return run(p[1]) + run(p[2])
        if p[0] == '-':
            return run(p[1]) - run(p[2])
        if p[0] == '*':
            return run(p[1]) * run(p[2])
        if p[0] == '/':
            return run(p[1]) / run(p[2])
        if p[0] == '<':
            return run(p[1]) < run(p[2])
        if p[0] == '>':
            return run(p[1]) > run(p[2])
        if p[0] == '<=':
            return run(p[1]) <= run(p[2])
        if p[0] == '>=':
            return run(p[1]) >= run(p[2])
        if p[0] == 'EQUALS':
            return run(p[1]) == run(p[2])
        if p[0] == '<>':
            return run(p[1]) != run(p[2])
        if p[0] == 'or':
            return run(p[1]) or run(p[2])
        if p[0] == 'and':
            return run(p[1]) and run(p[2])
        if p[0] == 'not':
            return not run(p[1])


        if p[0] == 'ASSIGN':
            variables[p[1]] = run(p[2])
            return variables[p[1]]

        if p[0] == 'GETVAR':
            try:
                return variables[p[1]]
            except KeyError:
                error_message = f"Error: Variable '{p[1]}' not defined."
                print(error_message)
                salidas.append(error_message)
                p[0] = 0  # Valor por defecto


        if p[0] == 'WRITE':
            string1 = str(run(p[1]))
            if len(p) == 2:
                string = string1
            else:
                string2 = str(run(p[2]))
                string = string1 + string2
            salidas.append(string)
            print(string)

        if p[0] == 'CAPTURE':
            global ES_WEB
            # Ajuste para CAPTURE:
            if ES_WEB:
                # Utilizamos la versión síncrona de la función asíncrona de captura.
                valor = obtener_valor_capture_sync(p[1])
            else:
                valor = input(f"Ingrese valor para {p[1]}: ")
            variables[p[1]] = valor
            return valor


        if p[0] == 'IF':
            do_statement = run(p[1])
            if do_statement:
                return run(p[2])
            elif p[3]:
                return run(p[3])

        if p[0] == 'WHILE':
            while run(p[1]):
                run(p[2])
            return

        if p[0] == 'statement_list':
            for i in p[1]:
                run(i)
    else:
        return p