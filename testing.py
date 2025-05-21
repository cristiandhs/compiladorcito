from lexer import lexer
from parser import parser, variables, run
from clear_code import preprocess_code


code = '''
i = 0 ::
while (i < 2) do
    write(i) ::
    i = i + 1::
endwhile
'''
final_code = preprocess_code(code)

ast = parser.parse(final_code)

print(run(ast))



print("\nVariables definidas:")
for var, val in variables.items():
    print(f"{var} = {val}")