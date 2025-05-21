import asyncio
from nicegui import ui
import nest_asyncio



ES_WEB = True

capture_value = None
capture_event = asyncio.Event()
nest_asyncio.apply()

async def obtener_valor_capture(var_name: str) -> str:
    """
    Muestra un diálogo de entrada para CAPTURE usando NiceGUI y espera el valor ingresado.
    """
    global capture_value, capture_event
    capture_value = None
    capture_event.clear()

    with ui.dialog() as dlg, ui.card():
        ui.label(f"Ingrese el valor para {var_name}:")
        input_field = ui.input(placeholder="Ingrese valor").props('outlined')
        ui.button("Enviar", on_click=lambda: submit_capture(input_field.value, dlg))
    dlg.open()

    await capture_event.wait()  # Espera hasta que se envíe el valor
    return capture_value

def submit_capture(val: str, dialog):
    """
    Función llamada al presionar el botón 'Enviar'.
    Guarda el valor ingresado y cierra el diálogo.
    """
    global capture_value, capture_event
    capture_value = val
    capture_event.set()  # Libera la espera
    dialog.close()

def obtener_valor_capture_sync(var_name: str) -> str:
    """
    Función auxiliar que ejecuta la versión asíncrona de CAPTURE de forma sincrónica.
    NOTA: Este método debe usarse con precaución si ya se está ejecutando un bucle de eventos.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(obtener_valor_capture(var_name))