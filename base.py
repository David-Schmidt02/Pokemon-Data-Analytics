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
    page.window_height = 700

    input_busqueda = ft.TextField(label="Buscar Pokémon", width=300, on_change=lambda e: actualizar_sugerencias())
    sugerencias = ft.Column(scroll="auto")
    resultado = ft.Column()
    progreso = ft.ProgressBar(width=300, visible=False)
    estado = ft.Text()
    boton_analisis = ft.ElevatedButton("Análisis de Pokémon")

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

    def analizar_pokemones(e):
        boton_analisis.disabled = True
        progreso.visible = True
        progreso.value = 0
        estado.value = "Descargando datos detallados..."
        page.update()

        base_url = "https://pokeapi.co/api/v2/pokemon/"
        cantidad = 100  # Cambiar según necesidad

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
                time.sleep(0.2)

            except Exception as ex:
                print(f"Error con {p['name']}: {ex}")

        df = pd.DataFrame(resultados)
        df.to_csv("pokemones.csv", index=False)

        estado.value = "¡Análisis completo! Datos guardados en 'pokemones.csv'."
        progreso.visible = False
        boton_analisis.disabled = False
        page.update()

    boton_analisis.on_click = analizar_pokemones

    page.add(
        ft.Column([
            ft.Text("Buscador de Pokémon", size=24, weight="bold"),
            input_busqueda,
            sugerencias,
            resultado,
            boton_analisis,
            progreso,
            estado
        ], spacing=10)
    )

ft.app(target=main)
