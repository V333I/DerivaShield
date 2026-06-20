# DerivaShield

**DerivaShield** es una aplicación académica de ciberseguridad defensiva que aplica principios de Cálculo Diferencial para la detección de anomalías en el tráfico de red en tiempo real. Se enfoca en identificar comportamientos compatibles con ataques **DDoS** y **Port Scanning** (Escaneo de puertos) sin depender de firmas estáticas.

Esta herramienta está pensada para entornos de laboratorio y propósitos educativos. **No incluye ninguna capacidad ofensiva**.

## Objetivo Académico y Matemático

El núcleo de DerivaShield se basa en analizar la "tasa de cambio" del tráfico de red utilizando derivadas aproximadas mediante diferencias finitas.

1. **La Función $f(t)$**: Representa la medición en crudo en un momento $t$. 
   - $f_{paquetes}(t)$: Paquetes por segundo.
   - $f_{puertos}(t)$: Puertos destino únicos por segundo.
2. **La Primera Derivada $f'(t)$**: Representa qué tan rápido está cambiando el tráfico.
   - $f'(t) \approx \frac{f(t) - f(t - \Delta t)}{\Delta t}$
   - Un aumento abrupto en paquetes indica un posible ataque de fuerza bruta o DDoS.
   - Un aumento abrupto en puertos únicos indica un comportamiento de mapeo de red (Port Scanning).
3. **El Umbral Dinámico Estadístico ($\mu + k \cdot \sigma$)**: 
   - En lugar de usar un límite fijo (que generaría falsos positivos), el sistema calcula una media móvil ($\mu$) y una desviación estándar móvil ($\sigma$) de la derivada $f'(t)$.
   - Si la tasa de cambio actual supera el umbral dinámico, se lanza una alerta.
   - $k$ es el factor de sensibilidad (por defecto 3, usando la regla empírica de 3-sigma).

## Estructura del Proyecto (Clean Architecture)

```
derivashield/
├── app.py                      # Punto de entrada
├── requirements.txt            # Dependencias
├── README.md                   # Documentación
├── config/                     
│   └── settings.py             # Configuraciones globales
├── domain/                     
│   ├── models.py               # Entidades base (Metric, Alert)
│   ├── detector.py             # Lógica matemática, derivadas y umbrales
│   └── metrics.py              # Cálculo de accuracy, precision, etc.
├── application/                
│   ├── event_bus.py            # Bus de eventos (Pub/Sub)
│   └── services.py             # Orquestador del flujo
├── infrastructure/             
│   ├── database.py             # Persistencia en SQLite
│   ├── packet_capture.py       # Captura real con Scapy
│   ├── traffic_simulator.py    # Simulador de tráfico (Modo Demo)
│   └── dataset_loader.py       # Lector de CIC-IDS-2018 (opcional)
├── presentation/               
│   └── dashboard.py            # Interfaz web con Plotly Dash
└── data/                       # Almacena derivashield.db
```

## Requisitos y Dependencias

- Python 3.11+
- En Windows puede ser necesario tener instalado Npcap (se instala al instalar Wireshark) para la captura real con Scapy.

## Instalación

1. Clona o descarga este repositorio.
2. Abre una terminal y colócate en la carpeta del proyecto.
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

### Modo Demo (Simulador)
Ideal para probar el concepto sin requerir permisos de administrador ni tráfico real. El simulador internamente generará tráfico normal, ataques tipo DDoS y escanéos de puertos de manera alternada.
```bash
python app.py --mode demo
```

### Modo Captura Real
Capturará el tráfico en vivo de tu tarjeta de red usando Scapy. Requiere permisos de administrador/root.
```bash
python app.py --mode real
```
*(Si no tienes permisos suficientes, la aplicación automáticamente caerá en modo demo).*

## Uso del Dashboard

Una vez ejecutado, abre tu navegador web en: `http://127.0.0.1:8050`

Encontrarás:
- **Estado del sistema**: Muestra si estás en modo demo o real.
- **Contadores**: Total de alertas, alertas de DDoS y Port Scanning.
- **Gráficos en tiempo real**: Muestran la evolución de $f(t)$ y $f'(t)$.
- **Configuración de Umbrales**: Puedes modificar dinámicamente el valor de $k$ y el tamaño de la ventana.
- **Alertas Recientes**: Tabla con las últimas anomalías detectadas.

## Flujo Event-Driven

El sistema usa una arquitectura impulsada por eventos:
1. `infrastructure` (Simulador o Captura) emite `nuevo_dato`.
2. `application/services.py` recibe el dato y lo envía a `domain/detector.py`.
3. El detector calcula $f'(t)$, compara con umbrales y si hay anomalía retorna `Alertas`.
4. El servicio guarda la métrica y alertas en SQLite mediante `infrastructure/database.py`.
5. Se emiten eventos `metrica_calculada` y `alerta_guardada`.
6. El Dashboard (Plotly Dash) escucha los eventos y actualiza la UI visualmente.

## Consideraciones Éticas y Limitaciones
- **Herramienta Defensiva:** Este código **no** tiene capacidades ofensivas y **no** puede usarse para atacar a terceros.
- **Dataset:** Se incluye soporte opcional para CIC-IDS-2018 si se sitúa en `data/dataset/dataset.csv`.
- **Limitaciones de rendimiento:** La captura en vivo de paquetes con Scapy en redes de altísima velocidad puede presentar pérdidas de paquetes en Python puro (cuellos de botella por GIL). Es aceptable para laboratorios.
