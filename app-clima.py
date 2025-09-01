import flet as ft
import requests
import folium
import io
import base64
from flet_webview import WebView

# --- CONFIGURAÇÃO ---
API_KEY = "a5676ce9dbe81f9ddad2125c4dedb9b6"
BACKGROUND_URL = "https://images.pexels.com/photos/1118873/pexels-photo-1118873.jpeg"

# --- FUNÇÕES ---
def obter_previsao_tempo(cidade):
    endpoint = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": cidade,
        "appid": API_KEY,
        "units": "metric",
        "lang": "pt_br"
    }
    resp = requests.get(endpoint, params=params)
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

def criar_mapa_html(latitude, longitude, dados_clima):
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    pop_up_content = f"""
    <b>Cidade:</b> {dados_clima['name']}<br>
    <b>País:</b> {dados_clima['sys']['country']}<br>
    <b>Temperatura Atual:</b> {dados_clima['main']['temp']}°C<br>
    <b>Tempo:</b> {dados_clima['weather'][0]['description'].capitalize()}
    """
    folium.Marker(
        location=[latitude, longitude],
        popup=folium.Popup(folium.Html(pop_up_content, script=True)),
        icon=folium.Icon(color='blue')
    ).add_to(m)

    map_data = io.BytesIO()
    m.save(map_data, close_file=False)
    map_html = map_data.getvalue().decode()
    map_data_uri = "data:text/html;base64," + base64.b64encode(map_html.encode()).decode()
    return map_data_uri

# --- APP FLET ---
def main(page: ft.Page):
    page.title = "App de Previsão do Tempo e Mapa"
    page.padding = 0
    page.window_maximized = True   # abre em tela cheia
    page.bgcolor = ft.Colors.BLACK

    # Controles
    cidade_input = ft.TextField(label="Digite o nome da cidade", width=340, text_size=16)
    resultado_column = ft.Column(spacing=8, tight=True)

    def obter_clima(e):
        resultado_column.controls.clear()
        cidade = (cidade_input.value or "").strip()
        if not cidade:
            resultado_column.controls.append(ft.Text("Insira o nome da cidade.", color=ft.Colors.YELLOW))
            page.update()
            return

        dados = obter_previsao_tempo(cidade)
        if dados:
            resultado_column.controls.append(ft.Text(f"Cidade: {dados['name']}", color=ft.Colors.WHITE, size=16))
            resultado_column.controls.append(ft.Text(f"País: {dados['sys']['country']}", color=ft.Colors.WHITE, size=14))
            resultado_column.controls.append(ft.Text(f"Temperatura: {dados['main']['temp']}°C", color=ft.Colors.WHITE, size=14))
            resultado_column.controls.append(ft.Text(f"Tempo: {dados['weather'][0]['description'].capitalize()}", color=ft.Colors.WHITE, size=14))

            map_uri = criar_mapa_html(dados['coord']['lat'], dados['coord']['lon'], dados)
            resultado_column.controls.append(
                ft.Container(
                    WebView(url=map_uri, expand=True),
                    padding=ft.padding.only(top=10),
                    height=400
                )
            )
        else:
            resultado_column.controls.append(ft.Text("Cidade inválida ou erro na API.", color=ft.Colors.RED))

        page.update()

    buscar_button = ft.ElevatedButton("Obter Previsão do Tempo", on_click=obter_clima)

    # Caixa com conteúdo sobre a imagem (semi-transparente para leitura)
    content_card = ft.Container(
        ft.Column([
            ft.Row([cidade_input, buscar_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=12, color="transparent"),
            resultado_column
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
        width=880,
        padding=20,
        bgcolor="rgba(0,0,0,0.45)",
        border_radius=10
    )

    # Stack: imagem de fundo + conteúdo em cima
    page.add(
        ft.Stack(
            [
                ft.Image(src=BACKGROUND_URL, fit=ft.ImageFit.COVER, expand=True),
                ft.Container(content=content_card, alignment=ft.alignment.center, expand=True)
            ],
            expand=True
        )
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
