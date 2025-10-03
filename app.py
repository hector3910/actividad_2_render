import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import janitor as jan
import plotly.express as px
import folium
from folium.features import GeoJsonTooltip
import branca.colormap as cm


#Preprocesamiento de los datos a utilizar
#Dataset para graficar Colombia
mapa_col= gpd.read_file("data/COLOMBIA/COLOMBIA.shp",encoding="latin1")
mapa_col['DPTO_CNMBR'] = mapa_col['DPTO_CNMBR'].replace({'NARI?O':'NARIÑO'})

#Dataset del IPM
data=pd.read_csv("data/Hogares (Departamental) 2024.csv")
data=jan.clean_names(data)
data_ipm=data.loc[:,["departamento","ipm"]]

#Groupby por departamento del IPM
resum = (
    data_ipm.groupby("departamento", as_index=False)
         .agg(ipm_promedio=("ipm", "mean"))
         .round(2)
)

#Reordenamiento de mapa_col para no tener problemas en el merge
aux=mapa_col.iloc[27]
mapa_col.iloc[27]=mapa_col.iloc[32]
for i in range(31,26,-1):
    mapa_col.iloc[i+1]=mapa_col.iloc[i]
mapa_col.iloc[28]=aux

#Corrección de códigos de departamentos para hacer el merge
mal_car = [5,8,11,13,15,17,18,19,20,23,25,27,41,44,47,50,52,54,63,66,68,70,73,76,81,85,86,88,91,94,95,97,99]  # Caracteres que queremos cambiar
bien_car = ['05', '08', '11', '13', '15', '17', '18', '19', '20', '23', '25',
       '27', '41', '44', '47', '50', '52', '54', '63', '66', '68', '70',
       '73', '76', '81', '85', '86','88', '91', '94', '95', '97', '99'] # Caracteres por los que queremos cambiar

munic_1=resum['departamento']
for j in range(len(mal_car)):  # Este for recorre cada elemento de cada municipio reemplazando los caracteres malos
    munic_1 = munic_1.replace(mal_car[j], bien_car[j]) # Reemplazamos los caracteres
        
        
#Merge de ambos datasets
resum['codigo']= munic_1
mapa_col['codigo']=mapa_col['DPTO_CCDGO']

data_final = pd.merge(mapa_col, resum , on ='codigo', how = 'outer')

#Guardamos el IPM en el dataset del mapa
mapa_col['ipm'] = data_final["ipm_promedio"]     

# Inicializamos la app con un tema de Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server
# ---- Sidebar ----
sidebar = html.Div(
    [
        html.H2("Actividad #2", className="display-6"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Contexto", href="/contexto", active="exact"),
                dbc.NavLink("EDA", href="/eda", active="exact"),
                dbc.NavLink("Georreferenciación", href="/georreferenciacion", active="exact"),
                dbc.NavLink("Conclusiones", href="/conclusiones", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "18rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa"
    },
)

# ---- Layouts de cada página ----
# Contextualización con acordeones
contexto_layout = html.Div(
    [
        html.H2("Contextualización"),
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        html.P(
                            """El índice de pobreza multidimensional o 
                            IPM surge como una medida de pobreza que no solo abarca los 
                            ingresos del individuo, sino también información sobre 
                            diferentes dimensiones y variables del bienestar de los hogares
                            como lo pueden ser: condiciones educativas del hogar,
                            las condiciones de la niñez y juventud, trabajo, salud y 
                            acceso a servicios públicos domiciliarios y condiciones de 
                            la vivienda, etc. Por tanto, este índice no mide únicamente 
                            la pobreza a nivel monetario, sino que sirve también para 
                            reflejar las privaciones a las que se debe enfrentar un hogar
                            en Colombia. El IPM se calculó tanto para individuos como 
                            para hogares de diversas regiones de Colombia. Para este 
                            análisis se hará uso del índice para hogares. Así mismo, 
                            debemos de tener en cuenta que se evaluaron 23 variables,
                            y que un hogar se cataloga como 'pobre' si el índice es 
                            superior o igual a 1/3."""
                        ),
                        html.P("Fuente: DANE - https://microdatos.dane.gov.co/index.php/catalog/860"),
                    ],
                    title="Sobre el IPM",
                ),
                dbc.AccordionItem(
                    [
                        html.P(
                            """Para este estudio se obtuvieron registros de las 
                            siguientes regiones, y departamentos, del país:"""
                        ),
                        html.P("""1. Región Caribe (Atlántico, Bolívar, Cesar, Córdoba,
                               Sucre, Magdalena, La Guajira)."""),
                        html.P("""2. Región Oriental (Norte de Santander, Santander, Boyacá,
                               Cundinamarca, Meta y Centros Poblados y Rural disperso 
                               de Bogotá)."""),
                        html.P("""3. Región Central (Caldas, Risaralda, Quindío, Tolima, 
                               Huila, Caquetá, Antioquia)."""),
                        html.P("""4. Región Pacífica (Chocó, Cauca, Nariño, Valle de Cauca)."""),
                        html.P("""5. Región Bogotá (Cabecera)."""),
                        html.P("""6. San Andrés"""),
                        html.P("""7. Región Amazonía-Orinoquía (Arauca, Casanare, 
                               Putumayo, Amazonas, Guainía, Guaviare, Vaupés, Vichada)."""),
                    ],
                    title="Lugares encuestados",
                ),
                dbc.AccordionItem(
                    [
                        html.Ul([
                        html.Li("Privación por bajo logro educativo"),
                        html.Li("Privación por analfabetismo"),
                        html.Li("Privación por inasistencia escolar"),
                        html.Li("Privación por rezago escolar"),
                        html.Li("Privación por barreras de acceso a servicios para el cuidado de la primera infancia"),
                        html.Li("Privación por trabajo infantil"),
                        html.Li("Privación por desempleo de larga duración"),
                        html.Li("Privación por trabajo informal"),
                        html.Li("Privación por sin aseguramiento a salud"),
                        html.Li("Privación por barreras de acceso a salud dada una necesidad"),
                        html.Li("Privación por sin acceso a fuente de agua mejorada"),
                        html.Li("Privación por inadecuada eliminación de excretas"),
                        html.Li("Privación por material inadecuado de pisos"),
                        html.Li("Privación por material inadecuado de paredes exteriores"),
                        html.Li("Privación por hacinamiento crítico")]),
                        html.P("""Además se realizaron preguntas del tipo:
                               ¿El hogar tiene conexión a internet? 
                               ¿Cuántas personas componen este hogar? 
                               ¿Con qué tipo de servicio sanitario cuenta el hogar? 
                               para así completar las 23 variables usadas en el dataset
                               seleccionado.""")
                    ],
                    title="Variables utilizadas",
                ),
                dbc.AccordionItem("""El objetivo de este taller es analizar
                                  mediante un mapa la información recogida por
                                  el DANE y hacer una comparación departamental 
                                  de la pobreza en el país según el índice de pobreza 
                                  multidimensional de los encuestados.""", title="Objetivo"),
            ],
            start_collapsed=True,
        ),
    ],
    style={"margin-left": "20rem", "padding": "2rem 1rem"}
)

eda_layout = html.Div(
    [html.H2("Análisis Exploratorio de Datos (EDA)"),
    dcc.Tabs(id="eda-tabs", value="tab-1", children=[
            dcc.Tab(label="Resúmen del dataset", value="tab-1"),
            dcc.Tab(label="Resúmen gráfico del IPM", value="tab-2"),
            dcc.Tab(label="Top departamentos por IPM promedio", value="tab-3"),
    ]),    
    html.Div(id="eda-content")],
    style={"margin-left": "20rem", "padding": "2rem 1rem"}
)

geo_layout = html.Div(
    [html.H2("Georreferenciación del IPM en Colombia"),
    dcc.Tabs(id="geo-tabs", value="tab-1", children=[
            dcc.Tab(label="Mapa del IPM promedio por departamento", value="tab-1"),
            dcc.Tab(label="Mapa del IPM promedio por departamento (rangos)", value="tab-2")
    ]),    
    html.Div(id="geo-content")],
    style={"margin-left": "20rem", "padding": "2rem 1rem"}
)

conclusiones_layout = html.Div(
    [html.H2("Conclusiones"),
    html.Hr(),
    html.P("""1. Desigualdad territorial en el índice: Se puede apreciar una desigualdad
           a lo largo del territorio colombiano, cuyos departamentos con mayor índice de
           pobreza multidimensional son Guainía, Vichada, Chocó y la Guajira."""),
    html.P("""2. Departamentos 'pobres': En promedio, un hogar en Vichada es 'pobre' 
           según el IPM y el umbral proporcionado por el DANE para esta clasificación.
           Recordemos que este índice mide las privaciones a las que se debe enfrentar 
           un hogar en Colombia, así que, si bien este departamento es el único que cruza
           el umbral, en promedio los hogares en otros departamentos como el Guainía, el 
           Chocó o la Guajira también deben lidiar con bastantes privaciones cada día."""),
    html.P("""3. Otras regiones con un IPM menos elevado son tanto la región Caribe como el sur del país."""),
    html.P("""4. Estas desigualdades que podemos notar pueden deberse a factores como 
           la ubicación en si del departamento, ya que por las condiciones medioambientales 
           del territorio o por cómo se encuentre distribuido este demográficamente puede 
           haber más o menos dificultades al acceso de servicios públicos, la educación, 
           la salud, etc."""),
    html.P("""5. Estos mapas los podemos utilizar como un indicador de cuales territorios 
           necesitan recibir una ayuda prioritaria por parte del gobierno para contrarrestar
           las privaciones que fueron tomadas como parte del cálculo del IPM."""),
    html.P("""En conclusión, la georreferenciación en este tipo de estudios es clave ya
           que permite un análisis de resultados mucho más preciso cuando es posible
           graficar los valores de una variable por medio de su ubicación en el planeta,
           y resulta más amigable visualmente representarlos directamente en un mapa, que,
           por ejemplo, colocar los 32 departamentos en un gráfico de barras.""")],
    style={"margin-left": "20rem", "padding": "2rem 1rem"}
)


content = html.Div(id="page-content")

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(
    dash.Output("page-content", "children"),
    [dash.Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/contexto":
        return contexto_layout
    elif pathname == "/eda":
        return eda_layout
    elif pathname == "/georreferenciacion":
        return geo_layout
    elif pathname == "/conclusiones":
        return conclusiones_layout
    else:
        return contexto_layout  # default



# ---- Callback para cambiar el contenido dentro de las subpestañas del EDA ----
@app.callback(
    dash.Output("eda-content", "children"),
    [dash.Input("eda-tabs", "value")]
)
def render_eda_tab(tab):
    if tab == "tab-1":
        return html.Div([
            html.H4("Características básicas del dataset del IPM"),
            html.P(f"Tamaño: {data.shape[0]} filas, {data.shape[1]} columnas"),
            html.Hr(),
            html.H5("Head del dataset"),
            dbc.Table.from_dataframe(data.head(), striped=True, bordered=True, hover=True),
            html.Hr(),
            html.H5("Resúmen numérico del IPM en el país según la encuesta del DANE"),
            dbc.Table.from_dataframe(data_ipm["ipm"].describe().reset_index(), striped=True, bordered=True, hover=True)
        ])
    elif tab == "tab-2":
        # Histograma interactivo
        hist_fig = px.histogram(data_ipm, x="ipm", nbins=30, title="Histograma del IPM")
        hist_fig.update_traces(marker_line_color="black", marker_line_width=1) 
        # Boxplot interactivo
        box_fig = px.box(data_ipm, y="ipm", title="Boxplot del IPM")
        return html.Div([
            html.H4("Visualizaciones exploratorias"),
            dcc.Graph(figure=hist_fig),
            dcc.Graph(figure=box_fig)
        ])
    elif tab == "tab-3":
        return html.Div([
        html.H4("Departamentos con mayor IPM promedio"),
        html.Label("Número de departamentos a mostrar:"),
        dcc.Slider(
            id="top-n-slider",
            min=1, max=len(resum),
            step=1, value=10,
            marks={i: str(i) for i in range(1, len(resum)+1, 4)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        dcc.Graph(id="top-n-bar")
    ])

#Callback para actualizar la gráfica de barras según el slider
@app.callback(
    dash.Output("top-n-bar", "figure"),
    [dash.Input("top-n-slider", "value")]
)
def update_top_departamentos(n):
    #Ordenamos los departamentos por IPM promedio
    top = mapa_col.sort_values("ipm", ascending=False).head(n)
    fig = px.bar(
        top,
        x="ipm",
        y="DPTO_CNMBR",
        orientation="h",
        title=f"Top {n} Departamentos con mayor IPM promedio",
        labels={"ipm": "IPM Promedio", "DPTO_CNMBR": "Departamento"}
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))  # Para que el top quede arriba
    return fig


@app.callback(
    dash.Output("geo-content", "children"),
    [dash.Input("geo-tabs", "value")]
)
def render_eda_tab(tab):
    if tab == "tab-1":
    # Crear mapa centrado en Colombia
        m = folium.Map(location=[4.5709, -74.2973], zoom_start=5)

        # Definir escala de colores continua
        colormap = cm.linear.YlOrRd_09.scale(
            mapa_col["ipm"].min(),
            mapa_col["ipm"].max()
        )
        colormap.caption = "IPM promedio"

        # Agregar polígonos con escala continua
        folium.GeoJson(
            mapa_col,
            style_function=lambda feature: {
                "fillColor": colormap(feature["properties"]["ipm"]) 
                             if feature["properties"]["ipm"] is not None else "transparent",
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.7,
            },
            tooltip=GeoJsonTooltip(
                fields=["DPTO_CNMBR", "ipm"],
                aliases=["Departamento:", "IPM promedio:"],
                localize=True
            )
        ).add_to(m)

        # Añadir la escala de colores al mapa
        colormap.add_to(m)

        # Guardar mapa como HTML temporal
        m.save("mapa_colombia.html")

        # Incrustar en Dash con un iframe
        return html.Iframe(
            srcDoc=open("mapa_colombia.html", "r", encoding="utf-8").read(),
            width="100%",
            height="600"
        )

    elif tab == "tab-2":
        # Crear mapa centrado en Colombia
        m = folium.Map(location=[4.5709, -74.2973], zoom_start=5)

        # Añadir coroplético
        folium.Choropleth(
            geo_data=mapa_col,
            data=mapa_col,
            columns=["DPTO_CCDGO", "ipm"],
            key_on="feature.properties.DPTO_CCDGO",
            fill_color="Blues",
            fill_opacity=0.7,
            line_opacity=0.5,
            legend_name="IPM promedio (rangos)",
            bins=[0, 0.15, 0.2, 0.25, 0.3, 0.4]
        ).add_to(m)

        # Añadir tooltip con nombre de departamento
        folium.GeoJson(
            mapa_col,
            style_function=lambda x: {"fillOpacity": 0, "color": "black", "weight": 0.5},
            tooltip=GeoJsonTooltip(
                fields=["DPTO_CNMBR", "ipm"],
                aliases=["Departamento:", "IPM promedio:"],
                localize=True
            )
        ).add_to(m)

        # Guardar mapa como HTML temporal
        m.save("mapa_colombia_rangos.html")

        # Incrustar en Dash con un iframe
        return html.Iframe(
            srcDoc=open("mapa_colombia_rangos.html", "r", encoding="utf-8").read(),
            width="100%",
            height="600"
        )

if __name__ == "__main__":
    app.run(debug=True)

