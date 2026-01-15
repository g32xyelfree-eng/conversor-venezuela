import streamlit as st
import requests

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Conversor Pro Venezuela",
    page_icon="logo.png",  # <--- Aquí pones el nombre de tu archivo
    layout="centered"
)

# --- FUNCIÓN PARA OBTENER TASAS (API) ---
def cargar_tasas_api():
    """Intenta obtener tasas de internet, si falla devuelve las por defecto"""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        rates = data['rates']
        
        return {
            "USD": 1.0,
            "USDT": 1.00,
            "VES": rates.get('VES', 60.0),
            "COP": rates.get('COP', 4000.0),
            "BRL": rates.get('BRL', 5.50)
        }
    except:
        st.error("⚠️ No hay conexión. Usando modo offline.")
        return {"USD": 1.0, "USDT": 1.0, "VES": 60.0, "COP": 4100.0, "BRL": 5.80}

# --- GESTIÓN DE ESTADO (MEMORIA) ---
# Esto es vital: Streamlit necesita recordar las tasas si tú las editas manualmente.
if 'tasas' not in st.session_state:
    st.session_state['tasas'] = cargar_tasas_api()

# --- INTERFAZ GRÁFICA ---

st.title("💸 Conversor Multi-Divisa")
st.markdown("Calculadora con tasas del día (Monitor/BCV/Cripto)")

# SECCIÓN 1: CONFIGURACIÓN DE TASAS (Manual / Híbrido)
with st.expander("⚙️ Configurar/Editar Tasas (Click aquí)", expanded=True):
    st.caption("Puedes editar estas tasas manualmente si el precio cambió hace un minuto.")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Creamos las cajitas para editar. 
    # Usamos st.session_state para guardar lo que escribas.
    with col1:
        st.session_state['tasas']['USD'] = st.number_input("USD", value=float(st.session_state['tasas']['USD']), disabled=True)
    with col2:
        new_usdt = st.number_input("USDT", value=float(st.session_state['tasas']['USDT']))
        st.session_state['tasas']['USDT'] = new_usdt
    with col3:
        new_ves = st.number_input("Bs (VES)", value=float(st.session_state['tasas']['VES']))
        st.session_state['tasas']['VES'] = new_ves
    with col4:
        new_cop = st.number_input("Pesos (COP)", value=float(st.session_state['tasas']['COP']))
        st.session_state['tasas']['COP'] = new_cop
    with col5:
        new_brl = st.number_input("Reales (BRL)", value=float(st.session_state['tasas']['BRL']))
        st.session_state['tasas']['BRL'] = new_brl

    if st.button("🔄 Actualizar desde Internet"):
        st.session_state['tasas'] = cargar_tasas_api()
        st.rerun()

# SECCIÓN 2: CALCULADORA
st.divider()

c1, c2 = st.columns([1, 2])

with c1:
    moneda_origen = st.selectbox("Tengo esta moneda:", list(st.session_state['tasas'].keys()), index=2) # Por defecto VES

with c2:
    monto = st.number_input("Monto a convertir:", min_value=0.0, value=100.0, step=10.0, format="%.2f")

# --- LÓGICA DE CÁLCULO ---
# 1. Convertir a Dólar Base
tasa_origen = st.session_state['tasas'][moneda_origen]
monto_en_usd = monto / tasa_origen

# 2. Mostrar Resultados
st.subheader("Equivalentes:")

fila1 = st.columns(3)
fila2 = st.columns(2)
cols = fila1 + fila2 # Unimos las columnas en una lista para recorrerlas

contador = 0
for moneda, tasa_destino in st.session_state['tasas'].items():
    if moneda == moneda_origen:
        continue # No mostrar conversión a sí mismo
    
    valor_final = monto_en_usd * tasa_destino
    
    # Mostrar tarjeta con resultado
    try:
        cols[contador].metric(label=f"En {moneda}", value=f"{valor_final:,.2f}")
        contador += 1
    except:
        pass # Si sobran columnas, no pasa nada

