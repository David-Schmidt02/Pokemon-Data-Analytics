# busqueda.py

import flet as ft
import requests
import matplotlib.pyplot as plt
import numpy as np
import os

def obtener_nombres_pokemon():
    url = "https://pokeapi.co/api/v2/pokemon?limit=100000"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return [p["name"] for p in data["results"]]
    return []

def crear_radar(valores, etiquetas, nombre_pokemon):
    # Cerrar el círculo
    valores += valores[:1]
    etiquetas += etiquetas[:1]

    angulos = np.linspace(0, 2 * np.pi, len(etiquetas))

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, 'b-', linewidth=2)
    ax.fill(angulos, valores, 'skyblue', alpha=0.4)
    ax.set_xticks(angulos)
    ax.set_xticklabels(etiquetas)
    ax.set_title(nombre_pokemon.capitalize())
    ax.grid(True)

    img_path = f"radar_{nombre_pokemon}.png"
    plt.savefig(img_path, bbox_inches="tight")
    plt.close()
    return img_path

def vista_busqueda():
    lista_nombres = obtener_nombres_pokemon()

    input_busqueda = ft.TextField(
        hint_text="Buscar Pokémon", width=300,
        on_change=lambda e: actualizar_sugerencias()
    )
    sugerencias = ft.Column(scroll="auto")
    resultado = ft.Column()

    def actualizar_sugerencias():
        texto = input_busqueda.value.lower()
        coincidencias = [n for n in lista_nombres if texto in n][:10]

        sugerencias.controls = []
        for nombre in coincidencias:
            sugerencias.controls.append(
                ft.ListTile(
                    title=ft.Text(nombre.capitalize()),
                    on_click=lambda e, n=nombre: buscar_pokemon(n)
                )
            )
        input_busqueda.update()
        sugerencias.update()

    def buscar_pokemon(nombre):
        url = f"https://pokeapi.co/api/v2/pokemon/{nombre}"
        res = requests.get(url)

        if res.status_code != 200:
            resultado.controls = [ft.Text("Pokémon no encontrado.")]
            resultado.update()
            return

        data = res.json()
        sprite_url = data["sprites"]["other"]["official-artwork"]["front_default"]
        tipos = [t["type"]["name"] for t in data["types"]]

        # Colores por tipo (puedes agregar más)
        colores_tipo = {
            "fire": "#F08030", "water": "#6890F0", "grass": "#78C850", "electric": "#F8D030",
            "psychic": "#F85888", "ice": "#98D8D8", "dragon": "#7038F8", "dark": "#705848",
            "fairy": "#EE99AC", "normal": "#A8A878", "fighting": "#C03028", "flying": "#A890F0",
            "poison": "#A040A0", "ground": "#E0C068", "rock": "#B8A038", "bug": "#A8B820",
            "ghost": "#705898", "steel": "#B8B8D0"
        }
        color_fondo = colores_tipo.get(tipos[0], "#CCCCCC")

        # Habilidades
        habilidades = [h["ability"]["name"] for h in data["abilities"]]
        habilidades_cards = [
            ft.Container(
                content=ft.Text(hab.capitalize(), color="white"),
                bgcolor=color_fondo, border_radius=10, padding=8, margin=4
            ) for hab in habilidades
        ]

        # Estadísticas
        etiquetas = []
        valores = []
        stats_cards = []
        for stat in data["stats"]:
            etiquetas.append(stat["stat"]["name"])
            valores.append(stat["base_stat"])
            stats_cards.append(
                ft.Container(
                    content=ft.Text(f"{stat['stat']['name'].capitalize()}: {stat['base_stat']}", color="white"),
                    bgcolor=color_fondo, border_radius=10, padding=8, margin=4
                )
            )

        #grafico = crear_radar(valores, etiquetas, nombre)

        resultado.controls = [
            ft.Image(src=sprite_url, width=200, height=200),
            ft.Text(f"Nombre: {data['name'].capitalize()}", size=20, weight="bold"),
            ft.Text(f"Tipos: {', '.join(tipos).capitalize()}"),
            ft.Text("Habilidades:", size=16, weight="bold"),
            ft.Row(habilidades_cards, wrap=True),
            ft.Text("Estadísticas:", size=16, weight="bold"),
            ft.Row(stats_cards, wrap=True),
            # ft.Image(src=grafico, width=300, height=300),
        ]
        sugerencias.controls = []
        input_busqueda.value = ""
        resultado.update()
        sugerencias.update()
        input_busqueda.update()

    return ft.Column([
        ft.Text("Buscador de Pokémon", size=24, weight="bold"),
        input_busqueda,
        sugerencias,
        resultado
    ], spacing=10)
