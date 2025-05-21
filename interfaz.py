from nicegui import ui
from nicegui import app
from lexer import lexer
from parser import parser, obtener_salidas, run
from clear_code import preprocess_code
import os
import asyncio

#---------Prueba
#ejecucion_actual = []
#indice_actual = 0
#modo_paso_a_paso = False

lineas_codigo = None  # iterador global
modo_linea_a_linea = False
ejecucion_actual = []
indice_actual = 0
modo_paso_a_paso = False
salidas = []
variables = {}
capture_value = None
capture_event = asyncio.Event()

#---------Prueba

# Crear carpeta 'archivos' si no existe (útil para Render)
os.makedirs("archivos", exist_ok=True)

# Ruta absoluta a la carpeta docs
docs_path = os.path.join(os.path.dirname(__file__), 'docs')

# Sirve la carpeta docs como ruta "/docs"
app.add_static_files('/docs', docs_path)

#  Estilo global de la página
#ui.query('body').style('background-color: #1e1e1e; color: white; font-family: sans-serif;')


#  Variables globales
editor = None           # Área donde se escribe el código fuente
resultado_label = None  # Etiqueta para mostrar resultados o mensajes


#Funcion para guardar archivos
def guardar_archivo():
    consola.clear()

    nombre = archivo_input.value.strip()
    if not nombre:
        resultado_label.set_text(" Ingresa un nombre para el archivo.")
        return
    ruta = os.path.join("archivos", f"{nombre}.code")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(editor.value)
    #resultado_label.set_text(f"Archivo '{nombre}.code' guardado.")
    consola.push(f"Archivo '{nombre}.code' guardado.")

#Funcion para abrir archivos
def abrir_archivo():
    consola.clear()

    nombre = archivo_input.value.strip()
    if not nombre:
        resultado_label.set_text(" Ingresa el nombre del archivo a abrir.")
        return
    ruta = os.path.join("archivos", f"{nombre}.code")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            editor.value = f.read()
        resultado_label.set_text(f"Archivo '{nombre}.code' cargado.")
    except FileNotFoundError:
        #resultado_label.set_text(f" Archivo '{nombre}.code' no encontrado.")
        consola.push(f" Archivo '{nombre}.code' no encontrado.")


#Funcion para ver los archivos existenntes
def listar_archivos():
    consola.clear()

    archivos = os.listdir("archivos")
    archivos_code = [f for f in archivos if f.endswith(".code")]
    if archivos_code:
        #resultado_label.set_text("Archivos disponibles:\n" + "\n".join(archivos_code))
        consola.push("Archivos disponibles:\n" + "\n".join(archivos_code))
    else:
        #resultado_label.set_text("No hay archivos guardados.")
        consola.push("No hay archivos guardados.")

#Funcion para crear un archivo
def nuevo_archivo():
    consola.clear()

    archivo_input.value = ""
    editor.value = ""
    #resultado_label.set_text("Nuevo archivo creado.")
    consola.push("Nuevo archivo creado.")


#  Elimina el archivo de código y limpia el editor
def eliminar_archivo():
    consola.clear()

    nombre = archivo_input.value.strip()
    if not nombre:
        resultado_label.set_text(" Ingresa el nombre del archivo a eliminar.")
        return
    ruta = os.path.join("archivos", f"{nombre}.code")
    try:
        os.remove(ruta)
        editor.value = ""
        #resultado_label.set_text(f"Archivo '{nombre}.code' eliminado.")
        consola.push(f"Archivo '{nombre}.code' eliminado.")
    except FileNotFoundError:
        #resultado_label.set_text(f" Archivo '{nombre}.code' no encontrado.")
        consola.push(f" Archivo '{nombre}.code' no encontrado.")

# Analiza el código y muestra los tokens encontrados
def ver_tokens():
    consola.clear()

    lexer.input(editor.value)
    tokens_encontrados = []

    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_encontrados.append((tok.type, tok.value))

    # Mostrar resumen
    if tokens_encontrados:
        #resultado_label.set_text(f" Total de tokens: {len(tokens_encontrados)}")
        consola.push(f" Total de tokens: {len(tokens_encontrados)}")

        
        # Limpiar tablas anteriores (si las hay)
        if hasattr(ver_tokens, "tabla"):
            ver_tokens.tabla.delete()

        # Crear nueva tabla
        ver_tokens.tabla = ui.table(
            columns=[
                {'name': 'tipo', 'label': 'Tipo de Token', 'field': 'tipo'},
                {'name': 'valor', 'label': 'Valor', 'field': 'valor'}
            ],
            rows=[{'tipo': t[0], 'valor': t[1]} for t in tokens_encontrados],
            row_key='tipo'
        ).classes("mt-4 w-full max-w-2xl mx-auto bg-white text-black")
    
    else:
        #resultado_label.set_text(" No se encontraron tokens válidos.")
        consola.push(" No se encontraron tokens válidos.")
        if hasattr(ver_tokens, "tabla"):
            ver_tokens.tabla.delete()


def mostrar_documentacion():
    consola.clear()
    with ui.dialog() as dialog, ui.card():
        ui.label("📘 Documentación Disponible").classes("text-lg font-bold mb-2")
        
        ui.link("📄 Manual del Usuario", "/docs/manual_usuario.pdf", new_tab=True).classes("text-blue-500 underline")
        ui.link("📄 Manual del Programador", "/docs/manual_programador.pdf", new_tab=True).classes("text-blue-500 underline")

        ui.button("Cerrar", on_click=dialog.close).classes("mt-4")
    
    dialog.open()


#  Función para compilar el código fuente
def compilar():
    consola.clear()
    consola.push("")

    codigo = editor.value.strip()
    if not codigo:
        consola.push(" No hay código para compilar.")
        return

    final_code = preprocess_code(codigo)

    try:
        # Parsear el bloque completo de código de una sola vez
        ultimo_arbol = parser.parse(final_code)

        if ultimo_arbol is None:
            consola.push("No se pudo obtener el árbol sintáctico.")
            return

        # Ejecuta todo el código usando run, que se encarga de iterar sobre
        # las instrucciones internamente (por ejemplo, si el AST es ('statement_list', [...]))
        resultado_evaluado = run(ultimo_arbol)
        salida_final = obtener_salidas()

        if salida_final:
            consola.push(f"Salida:\n{salida_final}")
        elif resultado_evaluado is not None:
            consola.push(f"Resultado: {resultado_evaluado}")
        else:
            consola.push("Compilación exitosa.")

    except SyntaxError as se:
        consola.push(f"Error de sintaxis: {se}")
    except Exception as e:
        consola.push(f"Error inesperado: {e}")




#--------------- EJECUTAR -------------------------


def ejecutar_codigo():
    consola.clear()
    salidas.clear()
    variables.clear()
    global lineas_codigo, modo_linea_a_linea
    global ejecucion_actual, indice_actual, modo_paso_a_paso

    consola.clear()
    consola.push("🟢 Iniciando ejecución línea por línea...")

    try:
        codigo = editor.value.strip()
        if not codigo:
            consola.push("⚠️ No hay código para ejecutar.")
            return

        final_code = preprocess_code(codigo)

        # Parsear todo el código y obtener el AST
        ast_result = parser.parse(final_code)
        if ast_result is None:
            consola.push("⚠️ No se pudo obtener el árbol sintáctico.")
            return

        # Si el AST viene envuelto en ('statement_list', instrucciones), extraemos la lista.
        if isinstance(ast_result, tuple) and ast_result[0] == 'statement_list':
            ejecucion_actual = ast_result[1]
        # Si el resultado no es una lista, lo encapsulamos para trabajar uniformemente.
        elif not isinstance(ast_result, list):
            ejecucion_actual = [ast_result]
        else:
            ejecucion_actual = ast_result

        indice_actual = 0
        modo_paso_a_paso = True
        modo_linea_a_linea = True

        consola.push("⏭️ Paso a paso listo. Pulsa 'Ejecutar' otra vez para avanzar una línea.")

    except Exception as e:
        consola.push(f"❌ Error al iniciar: {e}")


def ejecutar_siguiente_paso():
    global indice_actual, modo_paso_a_paso, ejecucion_actual

    if not modo_paso_a_paso:
        consola.push("⚠️ No hay ejecución paso a paso activa.")
        return

    if indice_actual < len(ejecucion_actual):
        try:
            instruccion = ejecucion_actual[indice_actual]
            consola.push(f"➡️ Ejecutando instrucción {indice_actual + 1}:")

            # Ejecuta la instrucción actual mediante la función run del parser
            run(instruccion)

            # Mostrar cualquier salida generada (por ejemplo, de write)
            salida = obtener_salidas()
            if salida:
                consola.push(f"🖨️ {salida}")

            consola.push("✅ Ejecutado.")
            indice_actual += 1
        except Exception as e:
            consola.push(f"❌ Error en paso {indice_actual + 1}: {e}")
            modo_paso_a_paso = False
    else:
        consola.push("✅ Ejecución finalizada.")
        modo_paso_a_paso = False
        ejecucion_actual = []  # Limpia las instrucciones anteriores


def on_boton_ejecutar_click():
    global modo_paso_a_paso
    if modo_paso_a_paso:
        ejecutar_siguiente_paso()
    else:
        ejecutar_codigo()

#--------------- CASO CAPTURE ------------------------









# -------------- INTERFAZ GRÁFICA ----------------

#  Título principal centrado
ui.label("Micro Compilador - Versión Web").classes("text-3xl text-black font-bold mb-4 text-center")

#Nobre del archivo
archivo_input = ui.input(label="Nombre del archivo").classes("w-full max-w-xs")


#  Área de texto para ingresar el código fuente
editor = ui.textarea(
    label="Código fuente",
    placeholder="Escribe tu código aquí..."
).classes('w-full h-60 bg-white text-black rounded p-2')

#  Botones de acción organizados en fila
with ui.row().classes("justify-center gap-4 mt-4"):
    ui.button("🆕 Nuevo", on_click=nuevo_archivo).classes("bg-blue-700 text-white")
    ui.button("💾 Guardar", on_click=guardar_archivo).classes("bg-green-600 text-white")
    ui.button("📂 Abrir", on_click=abrir_archivo).classes("bg-indigo-600 text-white")
    ui.button("📃 Ver Archivos", on_click=listar_archivos).classes("bg-gray-600 text-white")
    ui.button("❌ Eliminar", on_click=eliminar_archivo).classes("bg-red-600 text-white")
    ui.button("🔍 Ver Tokens", on_click=ver_tokens).classes("bg-yellow-600 text-black")
    ui.button("⚙️ Compilar", on_click=compilar).classes("bg-purple-700 text-white")
    ui.button("🟢 Ejecutar", on_click=on_boton_ejecutar_click).classes("bg-teal-600 text-white")
    ui.button("📄 Ver/Descargar Documentación", on_click=mostrar_documentacion).classes("bg-gray-700 text-white")
    





#  Área para mostrar resultados o mensajes
#resultado_label = ui.label("").classes('text-lg mt-6 whitespace-pre-wrap text-center text-black')
consola = ui.log().classes("w-full h-48 mt-6 bg-black text-green-400 font-mono rounded p-2")


# --------------- Iniciar servidor web local -------------------
ui.run()

# ---------------- Iniciar servidor web en render -----------------
#ui.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
