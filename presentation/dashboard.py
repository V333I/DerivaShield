import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objs as plotly_go
import pandas as pd
from collections import deque
import threading
import time

from application.event_bus import bus
from application.services import AppService
from infrastructure.database import get_recent_metrics, get_recent_alerts, clear_alerts, get_historical_flow
from config import settings

app = dash.Dash(__name__, title="DerivaShield SOC", suppress_callback_exceptions=True)
server = app.server

metrics_history = deque(maxlen=settings.DEFAULT_WINDOW_SIZE)
alerts_history = deque(maxlen=50)

def on_metric_calculated(metric):
    metrics_history.append(metric)

def on_alert_saved(alert):
    alerts_history.appendleft(alert)

bus.subscribe('metrica_calculada', on_metric_calculated)
bus.subscribe('alerta_guardada', on_alert_saved)

app_service = None

# Componente principal con Pestañas
app.layout = html.Div(className='dashboard-container', children=[
    html.H1("DerivaShield SOC", className='title'),
    
    dcc.Tabs(id="tabs", value='tab-realtime', className='custom-tabs-container', children=[
        dcc.Tab(label='Monitoreo en Tiempo Real', value='tab-realtime', className='custom-tab', selected_className='custom-tab--selected'),
        dcc.Tab(label='Auditoría Histórica', value='tab-history', className='custom-tab', selected_className='custom-tab--selected'),
    ]),
    
    html.Div(id='tabs-content')
])

def render_realtime_tab():
    return html.Div([
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(className='card', style={'flex': '1'}, children=[
                html.H3("Ajustes de Detección (Filtro Matemático)", className='card-title'),
                html.Label("Sensibilidad k (Menor = Más estricto):", className='control-label'),
                dcc.Slider(
                    id='k-slider', min=1.0, max=5.0, step=0.1, value=settings.DEFAULT_K_THRESHOLD,
                    marks={i: {'label': str(i), 'style': {'color': '#94a3b8'}} for i in range(1, 6)},
                    className='custom-slider'
                ),
                html.Label("Ventana de tiempo (segundos):", className='control-label', style={'marginTop': '20px'}),
                dcc.Input(id='window-input', type='number', value=settings.DEFAULT_WINDOW_SIZE, min=10, max=300, className='control-input'),
                html.Div(style={'marginTop': '20px'}, children=[
                    html.Button('Aplicar Cambios', id='btn-update', n_clicks=0, className='btn btn-primary'),
                    html.Span(id='system-status', style={'marginLeft': '15px', 'color': '#00f2fe', 'fontSize': '0.9rem'})
                ])
            ]),
            
            html.Div(className='card', style={'flex': '1'}, children=[
                html.H3("Estado Global del Sistema", className='card-title'),
                html.Div(id='alert-counters', className='counters'),
                html.Div(style={'marginTop': '20px', 'textAlign': 'right'}, children=[
                    html.Button('Purgar Alertas', id='btn-clear', n_clicks=0, className='btn btn-danger')
                ])
            ])
        ]),
        
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(className='card', style={'flex': '1'}, children=[
                dcc.Graph(id='graph-packets', config={'displayModeBar': False})
            ]),
            html.Div(className='card', style={'flex': '1'}, children=[
                dcc.Graph(id='graph-ports', config={'displayModeBar': False})
            ])
        ]),
        
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(className='card', style={'flex': '1'}, children=[
                dcc.Graph(id='graph-deriv-packets', config={'displayModeBar': False})
            ]),
            html.Div(className='card', style={'flex': '1'}, children=[
                dcc.Graph(id='graph-deriv-ports', config={'displayModeBar': False})
            ])
        ]),
        
        html.Div(className='card', children=[
            html.H3("Registro de Eventos Anómalos", className='card-title'),
            html.Div(id='alerts-table')
        ]),
        
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
    ])

def render_history_tab():
    return html.Div([
        html.Div(className='card', style={'marginBottom': '20px'}, children=[
            html.H3("Auditoría a Largo Plazo de Consumo de Red", className='card-title'),
            html.P("Agrupación automatizada desde la base de datos local SQLite.", style={'color': '#94a3b8', 'marginBottom': '20px'}),
            html.Div(style={'marginBottom': '30px'}, children=[
                dcc.RadioItems(
                    id='history-period',
                    options=[
                        {'label': ' Últimas 24 Horas (Por Hora)', 'value': 'daily'},
                        {'label': ' Últimos 7 Días (Por Día)', 'value': 'weekly'},
                        {'label': ' Últimos 30 Días (Por Día)', 'value': 'monthly'}
                    ],
                    value='daily',
                    labelStyle={'display': 'inline-block', 'marginRight': '25px', 'color': '#e2e8f0', 'cursor': 'pointer', 'fontSize': '1.1rem'}
                )
            ]),
            dcc.Graph(id='graph-history-mb', config={'displayModeBar': False}),
            html.Br(),
            dcc.Graph(id='graph-history-pkts', config={'displayModeBar': False})
        ])
    ])

@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def update_layout(tab):
    if tab == 'tab-history':
        return render_history_tab()
    return render_realtime_tab()

def get_empty_figure(title):
    fig = plotly_go.Figure()
    fig.update_layout(
        title=title, template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=30, t=50, b=50), font=dict(color='#94a3b8')
    )
    return fig

# --- Callbacks Pestaña Historia ---
@app.callback(
    Output('graph-history-mb', 'figure'),
    Output('graph-history-pkts', 'figure'),
    Input('history-period', 'value')
)
def update_historical_graphs(period):
    rows = get_historical_flow(period)
    
    if not rows or len(rows) == 0:
        return get_empty_figure("Volumen de Datos Transferidos (MB) - Sin datos suficientes"), get_empty_figure("Volumen Total de Paquetes - Sin datos suficientes")
        
    df = pd.DataFrame(rows, columns=['period_time', 'total_packets', 'total_mb'])
    
    layout_config = dict(
        template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=30, t=50, b=80), font=dict(color='#94a3b8'),
        xaxis=dict(showgrid=True, gridcolor='#1e293b', tickangle=45),
        yaxis=dict(showgrid=True, gridcolor='#1e293b')
    )
    
    fig_mb = plotly_go.Figure()
    fig_mb.add_trace(plotly_go.Bar(x=df['period_time'], y=df['total_mb'], marker_color='#00c6ff', name='MB', opacity=0.8))
    fig_mb.update_layout(title="Volumen de Datos Transferidos por Periodo (Megabytes)", **layout_config)
    
    fig_pkts = plotly_go.Figure()
    fig_pkts.add_trace(plotly_go.Bar(x=df['period_time'], y=df['total_packets'], marker_color='#b100ff', name='Paquetes', opacity=0.8))
    fig_pkts.update_layout(title="Cantidad Total de Paquetes Procesados por Periodo", **layout_config)
    
    return fig_mb, fig_pkts

# --- Callbacks Pestaña Tiempo Real ---
@app.callback(
    Output('system-status', 'children'),
    Input('btn-update', 'n_clicks'),
    State('k-slider', 'value'), State('window-input', 'value'), prevent_initial_call=True
)
def update_settings(n_clicks, k_val, window_val):
    if n_clicks and app_service:
        app_service.update_settings(k_val, window_val)
        return f"✔ Actualizado: k={k_val}, Ventana={window_val}s"
    return ""

@app.callback(
    Output('alert-counters', 'children'),
    Output('alerts-table', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('btn-clear', 'n_clicks')
)
def update_alerts(n_intervals, clear_clicks):
    ctx = dash.callback_context
    if ctx.triggered and 'btn-clear' in ctx.triggered[0]['prop_id']:
        clear_alerts()
        alerts_history.clear()
        
    alerts_data = get_recent_alerts(50)
    total = len(alerts_data)
    ddos = sum(1 for a in alerts_data if a[2] == "Posible DDoS")
    portscan = sum(1 for a in alerts_data if a[2] == "Posible Port Scanning")
    
    counters_html = [
        html.Div(className='counter-box', children=[html.Div("Alertas Totales", className='counter-label'), html.Div(f"{total}", className='counter-value val-total')]),
        html.Div(className='counter-box' + (' pulse-alert' if ddos > 0 else ''), children=[html.Div("Impactos DDoS", className='counter-label'), html.Div(f"{ddos}", className='counter-value val-ddos')]),
        html.Div(className='counter-box', children=[html.Div("Escaneos de Puerto", className='counter-label'), html.Div(f"{portscan}", className='counter-value val-port')])
    ]
    
    if len(alerts_data) == 0:
        table = html.P("No se registran anomalías recientes.", style={'color': '#94a3b8', 'textAlign': 'center', 'padding': '20px'})
    else:
        df_alerts = pd.DataFrame(alerts_data, columns=['ID', 'Timestamp', 'Tipo', 'Severidad', 'Métrica', 'Valor', 'Derivada', 'Umbral', 'Descripción', 'Origen'])
        df_alerts['Hora'] = pd.to_datetime(df_alerts['Timestamp'], unit='s').dt.strftime('%H:%M:%S')
        df_alerts = df_alerts[['Hora', 'Tipo', 'Severidad', 'Descripción', 'Origen']]
        
        table = dash_table.DataTable(
            data=df_alerts.to_dict('records'), columns=[{'name': i, 'id': i} for i in df_alerts.columns],
            style_table={'overflowX': 'auto', 'borderRadius': '8px'},
            style_cell={'textAlign': 'left', 'padding': '12px', 'backgroundColor': '#0f172a', 'color': '#e2e8f0', 'borderBottom': '1px solid #1e293b', 'borderTop': 'none', 'borderLeft': 'none', 'borderRight': 'none', 'fontFamily': 'Inter'},
            style_header={'backgroundColor': '#1e293b', 'color': '#00f2fe', 'fontWeight': '600', 'borderBottom': '2px solid #00f2fe'},
            style_data_conditional=[
                {'if': {'filter_query': '{Tipo} = "Posible DDoS"'}, 'color': '#ff416c', 'fontWeight': '600'},
                {'if': {'filter_query': '{Tipo} = "Posible Port Scanning"'}, 'color': '#f5af19', 'fontWeight': '600'}
            ]
        )
    return counters_html, table

@app.callback(
    Output('graph-packets', 'figure'), Output('graph-ports', 'figure'), Output('graph-deriv-packets', 'figure'), Output('graph-deriv-ports', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graphs(n_intervals):
    if len(metrics_history) == 0:
        return get_empty_figure("f(t): Paquetes/s"), get_empty_figure("f(t): Puertos Únicos/s"), get_empty_figure("f'(t): Derivada Paquetes"), get_empty_figure("f'(t): Derivada Puertos")
        
    times = [time.strftime('%H:%M:%S', time.localtime(m.timestamp)) for m in metrics_history]
    packets = [m.packets_per_second for m in metrics_history]
    ports = [m.unique_ports_per_second for m in metrics_history]
    deriv_packets = [m.derivative_packets for m in metrics_history]
    deriv_ports = [m.derivative_ports for m in metrics_history]
    
    layout_config = dict(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=30, t=50, b=30), font=dict(color='#94a3b8'), xaxis=dict(showgrid=True, gridcolor='#1e293b'), yaxis=dict(showgrid=True, gridcolor='#1e293b'))
    
    fig_packets = plotly_go.Figure()
    fig_packets.add_trace(plotly_go.Scatter(x=times, y=packets, mode='lines', line=dict(color='#00f2fe', width=2), fill='tozeroy', fillcolor='rgba(0, 242, 254, 0.1)'))
    fig_packets.update_layout(title="f(t): Volumen de Tráfico (Paquetes/s)", **layout_config)
    
    fig_ports = plotly_go.Figure()
    fig_ports.add_trace(plotly_go.Scatter(x=times, y=ports, mode='lines', line=dict(color='#b100ff', width=2), fill='tozeroy', fillcolor='rgba(177, 0, 255, 0.1)'))
    fig_ports.update_layout(title="f(t): Diversidad (Puertos Únicos/s)", **layout_config)
    
    fig_d_packets = plotly_go.Figure()
    fig_d_packets.add_trace(plotly_go.Scatter(x=times, y=deriv_packets, mode='lines', line=dict(color='#ff416c', width=2)))
    fig_d_packets.update_layout(title="f'(t): Tasa de Cambio (Aceleración Paquetes/s)", **layout_config)
    
    fig_d_ports = plotly_go.Figure()
    fig_d_ports.add_trace(plotly_go.Scatter(x=times, y=deriv_ports, mode='lines', line=dict(color='#f5af19', width=2)))
    fig_d_ports.update_layout(title="f'(t): Tasa de Cambio (Aceleración Puertos/s)", **layout_config)
    
    return fig_packets, fig_ports, fig_d_packets, fig_d_ports
