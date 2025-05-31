import flet as ft
import requests
import pandas as pd
import time

# Obtener todos los nombres de Pokémon una vez
def obtener_nombres_pokemon():
    url = "https://pokeapi.co/api/v2/pokemon?limit=100000"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return [p["name"] for p in data["results"]]
    return []

lista_nombres = obtener_nombres_pokemon()

def main(page: ft.Page):
    page.title = "Buscador y Análisis de Pokémon"
    page.window_width = 400
    page.window_height = 800

    # --- Página de búsqueda ---
    input_busqueda = ft.TextField(label="Buscar Pokémon", width=300, on_change=lambda e: actualizar_sugerencias())
    sugerencias = ft.Column(scroll="auto")
    resultado = ft.Column()

    def actualizar_sugerencias():
        texto = input_busqueda.value.lower()
        coincidencias = [n for n in lista_nombres if texto in n][:10]  # Máx 10 sugerencias

        sugerencias.controls = []

        for nombre in coincidencias:
            sugerencias.controls.append(
                ft.ListTile(
                    title=ft.Text(nombre.capitalize()),
                    on_click=lambda e, n=nombre: buscar_pokemon(n)
                )
            )
        page.update()

    def buscar_pokemon(nombre):
        url = f"https://pokeapi.co/api/v2/pokemon/{nombre}"
        res = requests.get(url)

        if res.status_code != 200:
            resultado.controls = [ft.Text("Pokémon no encontrado.")]
            page.update()
            return

        data = res.json()
        sprite_url = data["sprites"]["front_default"]
        tipos = [t["type"]["name"] for t in data["types"]]

        resultado.controls = [
            ft.Image(src=sprite_url, width=150, height=150),
            ft.Text(f"Nombre: {data['name'].capitalize()}"),
            ft.Text(f"Tipos: {', '.join(tipos).capitalize()}")
        ]

        sugerencias.controls = []  # Ocultar sugerencias luego de seleccionar
        input_busqueda.value = ""  # Limpiar campo
        page.update()

    buscador_tab = ft.Column([
        ft.Text("Buscador de Pokémon", size=24, weight="bold"),
        input_busqueda,
        sugerencias,
        resultado
    ], spacing=10)

    # --- Página de análisis ---
    progreso = ft.ProgressBar(width=300, visible=False)
    estado = ft.Text()
    input_cantidad = ft.TextField(
        width=140,
        value="100",
        label=None,
        hint_text="Cantidad a analizar",
        tooltip="Ingrese la cantidad de Pokémon a analizar (ej: 50, 100, 150)"
    )
    boton_analisis = ft.ElevatedButton("Analizar Pokémon")

    # Controles para mostrar resultados de pandas
    texto_resultado = ft.Text(size=12, selectable=True, max_lines=20, overflow="hidden")

    # Variable para guardar DataFrame globalmente dentro del scope
    df_global = {"df": None}

    def analizar_pokemones(e):
        try:
            cantidad = int(input_cantidad.value)
            if cantidad <= 0 or cantidad > 1000:
                estado.value = "Por favor, ingresa un número entre 1 y 1000."
                page.update()
                return
        except ValueError:
            estado.value = "Por favor, ingresa un número válido."
            page.update()
            return

        boton_analisis.disabled = True
        progreso.visible = True
        progreso.value = 0
        estado.value = "Descargando datos detallados..."
        texto_resultado.value = ""
        page.update()

        base_url = "https://pokeapi.co/api/v2/pokemon/"

        res = requests.get(f"{base_url}?limit={cantidad}")
        if res.status_code != 200:
            estado.value = "Hubo un problema con el GET."
            progreso.visible = False
            boton_analisis.disabled = False
            page.update()
            return

        data = res.json()
        resultados = []
        total = len(data["results"])

        for i, p in enumerate(data["results"], 1):
            try:
                detalle = requests.get(p["url"]).json()

                resultados.append({
                    "name": detalle["name"],
                    "height": detalle["height"],
                    "weight": detalle["weight"],
                    "types": ", ".join([t["type"]["name"] for t in detalle["types"]]),
                    "hp": next(stat["base_stat"] for stat in detalle["stats"] if stat["stat"]["name"] == "hp")
                })

                progreso.value = i / total
                estado.value = f"{i}/{total} descargados: {detalle['name'].capitalize()}"
                page.update()
                time.sleep(0.1)

            except Exception as ex:
                print(f"Error con {p['name']}: {ex}")

        df = pd.DataFrame(resultados)
        df_global["df"] = df  # Guardar df para usarlo en botones

        df.to_csv("pokemones.csv", index=False)

        estado.value = "¡Análisis completo! Datos guardados en 'pokemones.csv'."
        progreso.visible = False
        boton_analisis.disabled = False
        page.update()

    boton_analisis.on_click = analizar_pokemones

    # Botones para mostrar info del DataFrame
    def mostrar_head(e):
        if df_global["df"] is not None:
            texto_resultado.value = str(df_global["df"].head())
        else:
            texto_resultado.value = "No hay datos para mostrar. Realiza primero el análisis."
        page.update()

    def mostrar_tail(e):
        if df_global["df"] is not None:
            texto_resultado.value = str(df_global["df"].tail())
        else:
            texto_resultado.value = "No hay datos para mostrar. Realiza primero el análisis."
        page.update()

    def mostrar_describe(e):
        if df_global["df"] is not None:
            texto_resultado.value = str(df_global["df"].describe())
        else:
            texto_resultado.value = "No hay datos para mostrar. Realiza primero el análisis."
        page.update()

    btn_head = ft.ElevatedButton("Head()", on_click=mostrar_head)
    btn_tail = ft.ElevatedButton("Tail()", on_click=mostrar_tail)
    btn_describe = ft.ElevatedButton("Describe()", on_click=mostrar_describe)

    analisis_tab = ft.Column([
        ft.Text("Análisis de datos Pokémon", size=24, weight="bold"),
        ft.Text("Esta sección permite descargar y analizar datos básicos de múltiples Pokémon, incluyendo altura, peso, tipos y puntos de vida. El resultado se guarda en un archivo CSV para su posterior análisis.", size=12),
        ft.Row([boton_analisis, input_cantidad], alignment="start"),
        progreso,
        estado,
        ft.Row([btn_head, btn_tail, btn_describe], spacing=10),
        texto_resultado
    ], spacing=10, expand=True)

    # --- Tabs ---
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Buscador", content=buscador_tab),
            ft.Tab(text="Análisis", content=analisis_tab)
        ]
    )

    page.add(tabs)

ft.app(target=main)
