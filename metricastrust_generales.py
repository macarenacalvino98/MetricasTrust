# -*- coding: utf-8 -*-
"""MetricasTrust_Generales.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1T7lhhRV7hNdP1_9Lmoo7wrZPJrjh51EY
"""

# Función para definir el sentimiento preponderante
def definir_sentimiento_preponderante(row):
    if row['sentimiento_global_positivo'] >= row['sentimiento_global_neutro'] and row['sentimiento_global_positivo'] >= row['sentimiento_global_negativo']:
        return 'Sentimiento Positivo'
    elif row['sentimiento_global_neutro'] >= row['sentimiento_global_positivo'] and row['sentimiento_global_neutro'] >= row['sentimiento_global_negativo']:
        return 'Sentimiento Neutro'
    else:
        return 'Sentimiento Negativo'

# Función para obtener detalles de las noticias
def obtener_detalles_noticias(data, sentimiento):
    noticias = data[data['sentimiento_preponderante'] == sentimiento]['seccion_principal'].unique()
    noticias = [str(noticia) for noticia in noticias]  # Convertir todos los valores a cadenas de texto
    return '<br>'.join(noticias)

# Función principal para generar las métricas y gráficos
def metricas_generales(data):
    # Asegurarse de que las fechas estén en el formato correcto
    data['fecha'] = pd.to_datetime(data['fecha'])

    # Cantidad de noticias analizadas
    cantidad_noticias = len(data)

    # Cantidad de secciones principales
    cantidad_secciones_principales = data['seccion_principal'].nunique()

    # Añadir la columna de sentimiento preponderante
    data['sentimiento_preponderante'] = data.apply(definir_sentimiento_preponderante, axis=1)

    # Calcular la media global de sentimiento positivo, negativo y neutro
    media_sentimientos = data[['sentimiento_global_positivo', 'sentimiento_global_neutro', 'sentimiento_global_negativo']].mean()

    # Sentimiento global a lo largo del tiempo
    sentimiento_tiempo = data.groupby('fecha')[['sentimiento_global_positivo', 'sentimiento_global_neutro', 'sentimiento_global_negativo']].mean().reset_index()

    # Crear line chart de sentimiento a lo largo del tiempo
    fig_line = px.line(sentimiento_tiempo, x='fecha', y=['sentimiento_global_positivo', 'sentimiento_global_neutro', 'sentimiento_global_negativo'],
                       title='Sentimiento Global a lo Largo del Tiempo',
                       labels={'value': 'Valor del Sentimiento', 'variable': 'Tipo de Sentimiento'},
                       color_discrete_map={'sentimiento_global_positivo': 'green', 'sentimiento_global_neutro': 'blue', 'sentimiento_global_negativo': 'red'})

    # Calcular la proporción de cada sentimiento preponderante
    proporciones_sentimiento = data['sentimiento_preponderante'].value_counts(normalize=True) * 100

    # Crear un DataFrame para las proporciones de sentimiento
    proporciones_sentimiento_df = proporciones_sentimiento.reset_index()
    proporciones_sentimiento_df.columns = ['Sentimiento', 'Proporción']
    proporciones_sentimiento_df['Detalles'] = proporciones_sentimiento_df['Sentimiento'].apply(lambda x: obtener_detalles_noticias(data, x))

    # Crear el gráfico de pastel (Pie Chart) para las proporciones de sentimiento
    color_map = {'Sentimiento Positivo': 'green', 'Sentimiento Neutro': 'blue', 'Sentimiento Negativo': 'red'}
    fig_pie = px.pie(proporciones_sentimiento_df, values='Proporción', names='Sentimiento',
                     title='Proporción de Noticias con Sentimiento Preponderante',
                     color='Sentimiento', color_discrete_map=color_map)

    # Añadir detalles en el hover para cada porción
    fig_pie.update_traces(
        hoverinfo='label+percent+value+text',
        textinfo='percent',
        insidetextorientation='radial',
        textfont=dict(size=14),
        hovertemplate='<b>%{label}</b><br>Proporción: %{percent}<br>Noticias: %{value}<br>Detalles: %{text}<extra></extra>'
    )

    # Crear un Violin Plot para la distribución de sentimientos del dataset
    sentimientos = data[['sentimiento_global_positivo', 'sentimiento_global_neutro', 'sentimiento_global_negativo']]

    # Renombrar las columnas para mejor legibilidad
    sentimientos = sentimientos.rename(columns={
        'sentimiento_global_positivo': 'Sentimiento Positivo',
        'sentimiento_global_neutro': 'Sentimiento Neutro',
        'sentimiento_global_negativo': 'Sentimiento Negativo'
    })

    # Crear un DataFrame largo para usar con Plotly Express
    sentimientos_long = sentimientos.melt(var_name='Sentimiento', value_name='Valor')

    # Crear el Violin Plot
    fig_violin = px.violin(sentimientos_long, x='Sentimiento', y='Valor', color='Sentimiento', box=True, points='all',
                           title='Distribución de Sentimientos en el Dataset (Violin Plot)',
                           labels={'Valor': 'Valor del Sentimiento', 'Sentimiento': 'Tipo de Sentimiento'},
                           color_discrete_map={'Sentimiento Positivo': 'green', 'Sentimiento Neutro': 'blue', 'Sentimiento Negativo': 'red'})

    # Determinar el sentimiento global preponderante
    sentimiento_global_preponderante = definir_sentimiento_preponderante(media_sentimientos)

    # Resultados
    resultados_m_grales = {
        'cantidad_noticias': cantidad_noticias,
        'cantidad_secciones_principales': cantidad_secciones_principales,
        'media_sentimiento_positivo': media_sentimientos['sentimiento_global_positivo'],
        'media_sentimiento_neutro': media_sentimientos['sentimiento_global_neutro'],
        'media_sentimiento_negativo': media_sentimientos['sentimiento_global_negativo'],
        'sentimiento_preponderante': sentimiento_global_preponderante
    }

    plots_m_grales = {
        'fig_line': fig_line,
        'fig_pie': fig_pie,
        'fig_violin': fig_violin
    }

    return resultados_m_grales, plots_m_grales

# Cargar el archivo preprocesado
file_path_preprocessed = 'dataset_corpus_003_preprocessed.xlsx'
data_preprocessed = pd.read_excel(file_path_preprocessed)

# Calcular métricas generales
resultados_m_grales, plots_m_grales = metricas_generales(data_preprocessed)

# Crear la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# Definir el layout de la aplicación
app.layout = dbc.Container([
    # Fila 1
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H2('Resultados', className='card-title', style={'textAlign': 'center'}),
                html.H1(f'{resultados_m_grales["cantidad_noticias"]}', className='card-text', style={'textAlign': 'center'}),
                html.P('Noticias Analizadas', className='card-text', style={'textAlign': 'center'}),
                html.H1(f'{resultados_m_grales["cantidad_secciones_principales"]}', className='card-text', style={'textAlign': 'center'}),
                html.P('Secciones Principales', className='card-text', style={'textAlign': 'center'}),
                html.H2(f'{resultados_m_grales["sentimiento_preponderante"]}', className='card-title', style={'textAlign': 'center', 'color': 'blue'}),
                html.P('Sentimiento Preponderante', className='card-text', style={'textAlign': 'center'})
            ])
        ], style={'margin-bottom': '20px'}), width=3),
        dbc.Col(dcc.Graph(figure=plots_m_grales['fig_line']), width=9)
    ], className='mb-4'),
    # Fila 2
    dbc.Row([
        dbc.Col(dcc.Graph(figure=plots_m_grales['fig_violin']), width=10),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H3(f'{resultados_m_grales["media_sentimiento_positivo"]:.3f}', className='card-title', style={'color': 'green', 'textAlign': 'center'}),
                html.P('Media Sentimiento Positivo', className='card-text', style={'textAlign': 'center'}),
                html.H3(f'{resultados_m_grales["media_sentimiento_neutro"]:.3f}', className='card-title', style={'color': 'blue', 'textAlign': 'center'}),
                html.P('Media Sentimiento Neutro', className='card-text', style={'textAlign': 'center'}),
                html.H3(f'{resultados_m_grales["media_sentimiento_negativo"]:.3f}', className='card-title', style={'color': 'red', 'textAlign': 'center'}),
                html.P('Media Sentimiento Negativo', className='card-text', style={'textAlign': 'center'})
            ])
        ], style={'margin-bottom': '20px'}), width=2)
    ], className='mb-4'),

], fluid=True)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
