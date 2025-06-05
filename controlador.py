import flet as ft
import requests
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
import os

from busqueda import vista_busqueda
from analisis import vista_analisis


def main(page: ft.Page):
    page.title = "Pokémon App"
    page.theme_mode = ft.ThemeMode.LIGHT

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Buscar", content=vista_busqueda()),
            ft.Tab(text="Análisis", content=vista_analisis()),
        ],
        expand=1
    )

    page.add(tabs)


if __name__ == "__main__":
    ft.app(target=main)
