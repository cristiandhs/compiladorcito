def preprocess_code(code):
    """Preprocesa el código para unir bloques if/while en una línea"""
    lines = split_and_clean_lines(code)
    processed_lines = process_blocks(lines)
    return join_processed_lines(processed_lines)


def split_and_clean_lines(code):
    """Divide el código en líneas y las limpia"""
    return [line.strip() for line in code.split('\n') if line.strip()]


def process_blocks(lines):
    """Procesa los bloques if/while para unirlos en una línea"""
    processed_lines = []
    inside_block = False
    current_block = []
    block_type = None  # 'if' o 'while'

    for line in lines:
        if inside_block:
            current_block.append(line)
            if is_end_of_block(line, block_type):
                processed_lines.append(" ".join(current_block))
                inside_block = False
                current_block = []
        else:
            if is_start_of_block(line):
                inside_block = True
                block_type = 'if' if line.startswith('if') else 'while'
                current_block.append(line)
            else:
                processed_lines.append(line)

    return processed_lines


def is_start_of_block(line):
    """Determina si una línea inicia un bloque"""
    return line.startswith('if') or line.startswith('while')


def is_end_of_block(line, block_type):
    """Determina si una línea finaliza un bloque"""
    clean_line = line.replace(" ", "")
    if block_type == 'if':
        return clean_line == "endif"
    elif block_type == 'while':
        return clean_line == "endwhile"
    return False


def join_processed_lines(processed_lines):
    """Une las líneas procesadas en un solo string"""
    return '\n'.join(processed_lines)


def parse_code(final_code, parser):
    """Parsea cada línea del código preprocesado"""
    results = []
    for line in final_code.split('\n'):
        line = line.strip()
        if line:
            result = parser.parse(line)
            if result is not None:
                results.append(result)
    return results


# Ejemplo de uso
if __name__ == "__main__":
    code = '''
    write("?AQUIIIIIIIIIII")::
    A = 2 ::
    while 5>3 do
        if ( 5<3) then
            write("SIIIIIIIIII") ::
            A = 5 ::
        else
            write("NOOOOOOOO") ::
            A=2 ::
        endif
        write("hola")::
    endwhile
    write(1+A) ::
    '''

    final_code = preprocess_code(code)
    print("Código preprocesado:")
    print(final_code)

    # Asumiendo que 'parser' está definido en otro lugar
    # results = parse_code(final_code, parser)
    # for result in results:
    #     print(result)