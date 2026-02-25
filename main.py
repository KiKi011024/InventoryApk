import flet as ft
import pandas as pd
import os
import sys

def main(page: ft.Page):
    page.title = "Buscador de Motores Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 800
    page.padding = 20

    # 1. LOCALIZACIÓN DEL ARCHIVO
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    file_name = "Lista de Motores Planta de Procesos.csv"
    file_path = os.path.join(base_path, file_name)

    # 2. CARGA DE DATOS SEGURA
    try:
        # Cargamos con latin-1 y detectamos separador automáticamente
        df = pd.read_csv(file_path, encoding='latin-1', sep=None, engine='python')
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
        df = df.fillna("-")
        
        # Identificamos columnas principales
        tag_col = next((c for c in df.columns if 'TAG' in c.upper()), df.columns[0])
        desc_col = next((c for c in df.columns if 'DESCRIPTION' in c.upper()), df.columns[1])
    except Exception as e:
        return page.add(ft.Text(f"Error cargando archivo: {e}", color="red"))

    # --- FUNCIÓN PARA LA FICHA TÉCNICA ---
    def mostrar_detalle(fila):
        # Creamos el contenido de la ficha de forma segura
        lista_info = ft.Column(scroll=ft.ScrollMode.AUTO, height=400, tight=True)
        
        for clave, valor in fila.items():
            lista_info.controls.append(
                ft.Text(f"{clave}: {valor}", size=13)
            )

        def cerrar(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Ficha Técnica Completa"),
            content=lista_info,
            actions=[ft.TextButton("Cerrar", on_click=cerrar)],
        )

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # --- LÓGICA DE BÚSQUEDA ---
    def buscar(e):
        texto = e.control.value.lower()
        lista_resultados.controls.clear()
        
        if len(texto) > 1:
            # Buscador universal en todas las celdas
            mask = df.apply(lambda r: texto in str(r).lower(), axis=1)
            filtrado = df[mask].head(20)
            
            for _, row in filtrado.iterrows():
                lista_resultados.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"TAG: {row[tag_col]}", weight="bold", color="blue200"),
                            ft.Text(f"{row[desc_col]}", size=12),
                            ft.Text("Ver más detalles...", size=10, italic=True, color="green"),
                        ]),
                        padding=15,
                        bgcolor="white10",
                        border_radius=10,
                        on_click=lambda _, r=row: mostrar_detalle(r)
                    )
                )
        page.update()

    # 4. INTERFAZ
    cuadro_busqueda = ft.TextField(
        label="Escribe para buscar (ej. 'Chancado')",
        prefix_icon="search", # Usamos strings para evitar errores de versión
        on_change=buscar,
        border_radius=15
    )
    
    lista_resultados = ft.ListView(expand=True, spacing=10)

    page.add(
        ft.Text("Inventario Planta", size=25, weight="bold"),
        cuadro_busqueda,
        ft.Text("Resultados:", size=12, color="white54"),
        lista_resultados
    )

if __name__ == "__main__":
    ft.app(target=main)