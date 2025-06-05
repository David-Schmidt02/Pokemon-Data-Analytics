import flet as ft
import requests
import pandas as pd
import os

CSV_PATH = "pokemons.csv"

def obtener_datos_pokemon(nombre):
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return {
            "name": data["name"],
            "height": data["height"],
            "weight": data["weight"],
            "base_experience": data["base_experience"],
            "hp": data["stats"][0]["base_stat"],
            "attack": data["stats"][1]["base_stat"],
            "defense": data["stats"][2]["base_stat"],
            "speed": data["stats"][5]["base_stat"],
        }
    return None

def vista_analisis():
    cantidad_input = ft.TextField(
        hint_text="Cantidad de Pokémon", width=150, height=40,
        tooltip="Cantidad de Pokémon a analizar (ej. 20)"
    )
    barra_progreso = ft.ProgressBar(width=400, visible=False)
    resultado = ft.Column()

    def analizar_pokemones(e):
        cantidad = int(cantidad_input.value or "0")
        if cantidad <= 0:
            resultado.controls = [ft.Text("Ingrese un número válido.")]
            resultado.update()
            return

        barra_progreso.visible = True
        barra_progreso.value = 0
        barra_progreso.update()

        url = f"https://pokeapi.co/api/v2/pokemon?limit={cantidad}"
        res = requests.get(url)

        if res.status_code != 200:
            resultado.controls = [ft.Text("Error al obtener los datos.")]
            barra_progreso.visible = False
            resultado.update()
            barra_progreso.update()
            return

        data = res.json()
        resultados = []
        for i, p in enumerate(data["results"]):
            pokemon_data = obtener_datos_pokemon(p["name"])
            if pokemon_data:
                resultados.append(pokemon_data)
            barra_progreso.value = (i + 1) / cantidad
            barra_progreso.update()

        df = pd.DataFrame(resultados)
        df.to_csv(CSV_PATH, index=False)

        resultado.controls = [
            ft.Text(f"Datos de {len(df)} Pokémon guardados en {CSV_PATH}.")
        ]
        barra_progreso.visible = False
        resultado.update()
        barra_progreso.update()

    return ft.Column([
        ft.Text("Análisis de Pokémon", size=24, weight="bold"),
        ft.Row([
            ft.ElevatedButton("Analizar", on_click=analizar_pokemones),
            cantidad_input
        ]),
        barra_progreso,
        resultado
    ], spacing=15)
