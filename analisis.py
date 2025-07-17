import flet as ft
import requests
import pandas as pd
import os
import time
from colores_tipo import colores_tipo
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import threading

CSV_PATH = "pokemons.csv"

def obtener_lista_nombres():
    url = "https://pokeapi.co/api/v2/pokemon?limit=100000"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return [p["name"] for p in data["results"]]
    return []

def obtener_datos_pokemon(nombre):
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        tipos = [t["type"]["name"] for t in data["types"]]
        return {
            "name": data["name"],
            "type": ",".join(tipos),
            "height": data["height"],
            "weight": data["weight"],
            "base_experience": data["base_experience"],
            "hp": data["stats"][0]["base_stat"],
            "attack": data["stats"][1]["base_stat"],
            "defense": data["stats"][2]["base_stat"],
            "speed": data["stats"][5]["base_stat"],
        }
    return None

def filtrar_por_tipo(df, tipos):
    if tipos and len(tipos) > 0 and "Todos" not in tipos:
        mask = df["type"].apply(lambda x: any(t in x for t in tipos))
        return df[mask]
    return df

def filtrar_por_rango(df, columna, minimo, maximo, tipo=float):
    if minimo:
        df = df[df[columna] >= tipo(minimo)]
    if maximo:
        df = df[df[columna] <= tipo(maximo)]
    return df

def vista_analisis():
    analisis_dropdown = ft.Dropdown(
        label="Analysis type",
        options=[
            ft.dropdown.Option("Comparisons"),
            ft.dropdown.Option("Distributions"),
            ft.dropdown.Option("Outliers"),
        ],
        value="Comparisons",
        width=200,
        label_style=ft.TextStyle(color="#FFD369"),
        color="#bfa85c",
        border_color="#FFD369",
        focused_border_color="#FFD369",
        bgcolor="#EEE7BE"
    )

    stat_dropdown = ft.Dropdown(
        label="Stat",
        options=[
            ft.dropdown.Option("hp"),
            ft.dropdown.Option("attack"),
            ft.dropdown.Option("defense"),
            ft.dropdown.Option("speed"),
            ft.dropdown.Option("weight"),
            ft.dropdown.Option("height"),
        ],
        value="attack",
        width=140,
        label_style=ft.TextStyle(color="#FFD369"),
        color="#bfa85c",
        border_color="#FFD369",
        focused_border_color="#FFD369",
        bgcolor="#EEE7BE"
    )

    cantidad_pokemons = ft.TextField(
        label="Amount",
        label_style=ft.TextStyle(color="#bfa85c"),
        color="#bfa85c",
        border_color="#FFD369",
        focused_border_color="#FFD369",
        bgcolor="#393E46",
        border_radius=10,
        width=140,
        value="100"
    )

    resultado = ft.Column()
    datos_cargados = ft.Text("", color="#FFD369")
    loading = ft.ProgressRing(visible=False, color="#FFD369")
    stop_loading = [False]

    def styled_button(text, on_click):
        return ft.ElevatedButton(
            text,
            on_click=on_click,
            style=ft.ButtonStyle(
                color="#222831",
                bgcolor="#FFD369",
                overlay_color="#ffe9a7",
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

    def cargar_datos(e):
        def worker():
            stop_loading[0] = False
            loading.visible = True
            loading.update()
            limite = int(cantidad_pokemons.value) if cantidad_pokemons.value.isdigit() else 100
            datos_cargados.value = "Descargando datos de la PokeAPI, por favor espera..."
            datos_cargados.update()
            nombres = obtener_lista_nombres()[:limite]
            pokemones = []
            for i, nombre in enumerate(nombres):
                if stop_loading[0]:
                    datos_cargados.value = "Descarga detenida por el usuario."
                    datos_cargados.update()
                    break
                poke = obtener_datos_pokemon(nombre)
                if poke:
                    pokemones.append(poke)
                if (i+1) % 25 == 0:
                    datos_cargados.value = f"Descargados {i+1} pokemones..."
                    datos_cargados.update()
                time.sleep(0.1)
            if not stop_loading[0] and pokemones:
                df = pd.DataFrame(pokemones)
                df.to_csv(CSV_PATH, index=False)
                datos_cargados.value = f"Datos cargados: {len(df)} pokemones."
                datos_cargados.update()
            loading.visible = False
            loading.update()
        threading.Thread(target=worker).start()

    def delete_csv(e):
        if os.path.exists(CSV_PATH):
            os.remove(CSV_PATH)
            datos_cargados.value = "Archivo CSV eliminado."
        else:
            datos_cargados.value = "No hay archivo CSV para eliminar."
        datos_cargados.update()

    def stop_carga(e):
        stop_loading[0] = True

    def mostrar_analisis(e=None):
        if not os.path.exists(CSV_PATH):
            resultado.controls = [ft.Text("No hay datos cargados. Por favor, carga los datos primero.", color="red")]
            resultado.update()
            return

        df = pd.read_csv(CSV_PATH)
        analisis = analisis_dropdown.value
        stat = stat_dropdown.value

        def resultado_container(content):
            return ft.Container(
                content=content,
                bgcolor="#2d2d2d",
                border_radius=12,
                padding=16,
                margin=ft.Margin(0, 0, 0, 10)
            )

        if analisis == "Comparisons":
            df["main_type"] = df["type"].apply(lambda x: x.split(",")[0])
            mean_by_type = df.groupby("main_type")[stat].mean().sort_values(ascending=False)
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Tipo", color="#FFD369")),
                    ft.DataColumn(ft.Text(f"Promedio {stat.title()}", color="#FFD369"))
                ],
                rows=[
                    ft.DataRow([
                        ft.DataCell(ft.Text(str(idx), color="#FFD369")),
                        ft.DataCell(ft.Text(f"{val:.2f}", color="#FFD369"))
                    ])
                    for idx, val in mean_by_type.items()
                ]
            )
            resultado.controls = [
                resultado_container(
                    ft.Column([
                        ft.Text(f"Mean {stat.title()} by Type", color="#FFD369", size=18, weight="bold"),
                        ft.Column(
                            [tabla],
                            scroll="auto",
                            height=300
                        )
                    ], spacing=10)
                )
            ]
        elif analisis == "Distributions":
            import matplotlib.pyplot as plt
            import io, base64
            plt.figure(figsize=(5,3))
            df[stat].hist(bins=20, color="#5BC0F8", edgecolor="black")
            plt.title(f"Distribucion de {stat.title()}")
            plt.xlabel(stat.title())
            plt.ylabel("Count")
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)
            img_data = base64.b64encode(buf.read()).decode("utf-8")
            resultado.controls = [
                resultado_container(
                    ft.Column([
                        ft.Text(f"Distribucion de {stat.title()}", color="#FFD369", size=18, weight="bold"),
                        ft.Image(src_base64=img_data, width=400)
                    ], spacing=10)
                )
            ]
        elif analisis == "Outliers":
            top5 = df.nlargest(5, stat)[["name", "type", stat]]
            bottom5 = df.nsmallest(5, stat)[["name", "type", stat]]
            def tabla_outliers(df_out, title):
                tabla = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Nombre", color="#FFD369")),
                        ft.DataColumn(ft.Text("Tipo", color="#FFD369")),
                        ft.DataColumn(ft.Text(stat.title(), color="#FFD369")),
                    ],
                    rows=[
                        ft.DataRow([
                            ft.DataCell(ft.Text(str(row["name"]), color="#FFD369")),
                            ft.DataCell(ft.Text(str(row["type"]), color="#FFD369")),
                            ft.DataCell(ft.Text(str(row[stat]), color="#FFD369"))
                        ]) for _, row in df_out.iterrows()
                    ]
                )
                return resultado_container(
                    ft.Column([
                        ft.Text(title, color="#FFD369", weight="bold"),
                        ft.Column([tabla], scroll="auto", height=220)
                    ], spacing=10)
                )
            resultado.controls = [
                ft.Row([
                    tabla_outliers(top5, f"Top 5 Pokémon por {stat.title()}"),
                    tabla_outliers(bottom5, f"Bottom 5 Pokémon por {stat.title()}")
                ], spacing=20)
            ]
        resultado.update()

    analisis_dropdown.on_change = mostrar_analisis
    stat_dropdown.on_change = mostrar_analisis

    analisis_section = ft.Container(
        content=ft.Column([
            ft.Text("Análisis de Pokémon", size=20, weight="bold", color="#FFD369"),
            ft.Row([analisis_dropdown, stat_dropdown], spacing=20),
            styled_button("Show analysis", mostrar_analisis),
            resultado
        ], spacing=16),
        bgcolor="#393E46",
        padding=24,
        border_radius=18,
        margin=ft.Margin(0, 0, 0, 20),
        expand=True
    )

    controles_carga = ft.Container(
        content=ft.Column([
            cantidad_pokemons,
            styled_button("Load data", cargar_datos),
            styled_button("Stop", stop_carga),
            styled_button("Delete CSV", delete_csv),
            loading,
            datos_cargados
        ], spacing=18, alignment="start", horizontal_alignment="center"),
        bgcolor="#393E46",
        padding=24,
        border_radius=18,
        margin=ft.Margin(0, 0, 0, 20),
        expand=False
    )

    return ft.Container(
        content=ft.Row([
            controles_carga,
            analisis_section
        ], spacing=30),
        bgcolor="#222831",
        padding=30,
        margin=ft.Margin(0, 15, 0, 0),
        border_radius=20,
        expand=False
    )