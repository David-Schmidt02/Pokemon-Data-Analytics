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

def vista_busqueda():
    lista_nombres = obtener_nombres_pokemon()

    input_busqueda = ft.TextField(
        hint_text="Buscar Pokémon", width=300,
        on_change=lambda e: actualizar_sugerencias(), color="white",
        bgcolor="#393E46", border_radius=10,
        hint_style=ft.TextStyle(color="#B0B0B0")
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
                    title=ft.Text(nombre.capitalize(), color="#FFD369"),
                    on_click=lambda e, n=nombre: buscar_pokemon(n)
                )
            )
        sugerencias.update()

    def buscar_pokemon(nombre):
        url = f"https://pokeapi.co/api/v2/pokemon/{nombre}"
        res = requests.get(url)

        if res.status_code != 200:
            resultado.controls = [ft.Text("Pokémon no encontrado.", color="red")]
            resultado.update()
            return

        data = res.json()
        sprite_url = data["sprites"]["other"]["official-artwork"]["front_default"]

        sprites = [
            data["sprites"]["front_default"],
            data["sprites"]["back_default"],
            data["sprites"]["front_shiny"],
            data["sprites"]["back_shiny"]
        ]
        sprites = [s for s in sprites if s]
        carrusel_index = {"valor": 0}

        def mostrar_sprite_actual():
            if sprites:
                imagen_sprite.src = sprites[carrusel_index["valor"]]
                imagen_sprite.update()

        def siguiente_sprite(e):
            carrusel_index["valor"] = (carrusel_index["valor"] + 1) % len(sprites)
            mostrar_sprite_actual()

        def anterior_sprite(e):
            carrusel_index["valor"] = (carrusel_index["valor"] - 1) % len(sprites)
            mostrar_sprite_actual()

        if sprites:
            imagen_sprite = ft.Image(src=sprites[0], width=120, height=120)
            carrusel = ft.Row([
                ft.IconButton(icon="arrow_back_ios", on_click=anterior_sprite),
                imagen_sprite,
                ft.IconButton(icon="arrow_forward_ios", on_click=siguiente_sprite)
            ], alignment="center")
        else:
            carrusel = ft.Text("No hay sprites adicionales.")

        tipos = [t["type"]["name"] for t in data["types"]]

        colores_tipo = {
            "fire": "#F08030", "water": "#6890F0", "grass": "#78C850", "electric": "#F8D030",
            "psychic": "#F85888", "ice": "#98D8D8", "dragon": "#7038F8", "dark": "#705848",
            "fairy": "#EE99AC", "normal": "#A8A878", "fighting": "#C03028", "flying": "#A890F0",
            "poison": "#A040A0", "ground": "#E0C068", "rock": "#B8A038", "bug": "#A8B820",
            "ghost": "#705898", "steel": "#B8B8D0",
        }
        tipos_claros = ["electric", "fairy", "ice", "normal", "ground", "rock", "bug", "steel"]
        color_text = "#222831" if tipos[0] in tipos_claros else "white"
        color_fondo = colores_tipo.get(tipos[0], "#CCCCCC")

        habilidades = [h["ability"]["name"] for h in data["abilities"]]
        habilidades_cards = [
            ft.Container(
                content=ft.Text(hab.capitalize(), color=color_text),
                bgcolor=color_fondo, border_radius=10, padding=8, margin=4
            ) for hab in habilidades
        ]

        stats_cards = [
            ft.Container(
                content=ft.Text(f"{stat['stat']['name'].capitalize()}: {stat['base_stat']}", color=color_text),
                bgcolor=color_fondo, border_radius=10, padding=8, margin=4
            )
            for stat in data["stats"]
        ]

        img_principal = ft.Image(src=sprite_url, width=200, height=200)
        nombre_texto = ft.Text(f"Nombre: {data['name'].capitalize()}", size=22, weight="bold", color="#FFD369")
        tipos_texto = ft.Text(f"Tipos: {', '.join(tipos).capitalize()}", color="white")

        seccion_izquierda = ft.Column([carrusel, img_principal], alignment="center", horizontal_alignment="center")
        seccion_derecha = ft.Column([
            nombre_texto,
            tipos_texto,
            ft.Text("Habilidades:", size=16, weight="bold", color="#FFD369"),
            ft.Row(habilidades_cards, wrap=True, spacing=5),
            ft.Text("Estadísticas:", size=16, weight="bold", color="#FFD369"),
            ft.Row(stats_cards, wrap=True, spacing=5),
        ], spacing=10)

        ficha_pokemon = ft.Container(
            content=ft.Row([seccion_izquierda, seccion_derecha], spacing=30),
            padding=20,
            bgcolor="#393E46",
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=15, color="grey", offset=ft.Offset(4, 4))
        )

        resultado.controls = [ficha_pokemon]
        sugerencias.controls = []
        input_busqueda.value = ""
        resultado.update()
        sugerencias.update()
        input_busqueda.update()

    return ft.Container(
        content=ft.Column([
            ft.Text("Buscador de Pokémon", size=24, weight="bold", color="white"),
            input_busqueda,
            sugerencias,
            resultado
        ], spacing=10),
        bgcolor="#222831",
        padding=30,
        expand=True
    )