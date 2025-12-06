import streamlit as st
import requests
import pandas as pd
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_js_eval import get_geolocation

# ---------------------------------------------------------
# 1. CONFIGURACIÓN
# ---------------------------------------------------------
st.set_page_config(page_title="Ibaguiar Pedidos", page_icon="🔥", layout="centered")

# =========================================================
# ⚙️ VARIABLES Y CONFIGURACIÓN
# =========================================================

# TU UBICACIÓN (Ibagué)
UBICACION_BASE = (4.4440508, -75.208976)

URL_SHEETS = "https://script.google.com/macros/s/AKfycbzEa9UwrBhOVaA1QR6ui5VRUTz1oGSzV-WZ7MIN5YbdJUsBrZRUv9l80Jl1kqAbheNDlw/exec"
ARCHIVO_DB = "productos_db.csv"
ARCHIVO_CONSECUTIVO = "consecutivo.txt"
PASSWORD_ADMIN = "1234"

# ---------------------------------------------------------
# 2. LISTA MAESTRA (GLOBAL)
# ---------------------------------------------------------
# La definimos aquí afuera para evitar errores de indentación
PRODUCTOS_INICIALES_DICT = {
    # --- Aguardientes ---
    "Aguardiente Garrafa tapa roja": [98000, 20],
    "Aguardiente Botella tapa roja": [58000, 20],
    "Aguardiente Tapa roja media": [34000, 20],
    "Aguardiente Garrafa tapa special": [102000, 20],
    "Aguardiente Botella tapa special": [60000, 20],
    "Aguardiente Tapa special media": [36000, 20],
    "Aguardiente Amarillo": [67000, 20],
    "Aguardiente Tapa Rosado": [78000, 20],
    "Aguardiente Botella Nectar verde": [50000, 20],
    "Aguardiente Nectar verde media": [33000, 20],
    # --- Rones ---
    "Ron Mojito": [55000, 20],
    "Ron Bacardi Limon": [55000, 20],
    "Ron Botella Viejo de Caldas": [65000, 20],
    "Ron Viejo de Caldas media": [35000, 20],
    # --- Cervezas ---
    "Cerveza Six Heineken": [21000, 20],
    "Cerveza Six Corona 355": [30000, 20],
    "Cerveza Six Costeña": [17000, 20],
    "Cerveza Six Costeñita": [17000, 20],
    "Cerveza Six 330 Aguila": [23000, 20],
    "Cerveza Six Poker": [23000, 20],
    "Cerveza Sixpack Andina": [16000, 20],
    "Cerveza Six Light Aguila": [23000, 20],
    "Cerveza Sixpack Club Colombia": [24000, 20],
    "Cerveza Six Budweiser": [17000, 20],
    # --- Otros ---
    "Four Loco Sandia": [15000, 20],
    "Cigarrillo Mustang": [8000, 20],
    "Cigarrillo Marlboro Rojo": [9000, 20],
    "Whisky Jack Daniels": [147000, 20],
    "Gatorade": [5000, 20],
    "Coca Cola 1.5L": [7500, 20],
    "Hielo": [2000, 20]
}

# ---------------------------------------------------------
# 3. FUNCIONES
# ---------------------------------------------------------

def cargar_productos():
    if not os.path.exists(ARCHIVO_DB):
        # Si no existe, creamos la DB con los productos iniciales
        data_list = [{"Producto": p, "Precio": v[0], "Stock": v[1]} for p, v in PRODUCTOS_INICIALES_DICT.items()]
        df = pd.DataFrame(data_list)
        df.to_csv(ARCHIVO_DB, index=False)
        return df
    else:
        try:
            return pd.read_csv(ARCHIVO_DB)
        except:
            # Si falla, recreamos estructura vacía o base
            return pd.DataFrame(columns=["Producto","Precio","Stock"])

def guardar_productos(df):
    df.to_csv(ARCHIVO_DB, index=False)

def obtener_siguiente_factura():
    if not os.path.exists(ARCHIVO_CONSECUTIVO): return 3001
    try:
        with open(ARCHIVO_CONSECUTIVO, "r") as f: return int(f.read().strip())
    except: return 3001

def actualizar_factura_siguiente(nuevo_numero):
    with open(ARCHIVO_CONSECUTIVO, "w") as f: f.write(str(nuevo_numero))

def calcular_tarifa_domicilio(direccion_texto=None, coordenadas_gps=None):
    """Calcula tarifa y devuelve dirección formateada"""
    geolocator = Nominatim(user_agent="fenix_app_v3")
    coords_destino = None
    direccion_detectada = direccion_texto

    try:
        # CASO A: Coordenadas GPS
        if coordenadas_gps:
            coords_destino = coordenadas_gps
            # Reverse Geocoding para hallar el nombre de la calle
            try:
                location = geolocator.reverse(f"{coords_destino[0]}, {coords_destino[1]}", timeout=5)
                if location:
                    # Intentar limpiar la dirección
                    direccion_detectada = location.address.split(",")[0]
            except:
                direccion_detectada = "Ubicación GPS Exacta"

        # CASO B: Texto manual
        elif direccion_texto and len(direccion_texto) > 3:
            busqueda = f"{direccion_texto}, Ibagué, Tolima, Colombia"
            location = geolocator.geocode(busqueda, timeout=5)
            if location:
                coords_destino = (location.latitude, location.longitude)
        
        # CÁLCULO
        if coords_destino:
            distancia_km = geodesic(UBICACION_BASE, coords_destino).kilometers
            
            # --- TARIFA: Base 4000 + 1500 x Km ---
            tarifa = 4000 + (distancia_km * 1500)
            tarifa = round(tarifa / 100) * 100
            if tarifa < 5000: tarifa = 5000
            
            return int(tarifa), round(distancia_km, 2), direccion_detectada
        else:
            return None, 0, direccion_texto

    except Exception as e:
        return None, 0, direccion_texto

def enviar_a_sheets(data):
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(URL_SHEETS, json=data, headers=headers, timeout=15)
        return resp
    except Exception as e: return f"Error: {e}"

# INICIALIZACIÓN
df_productos = cargar_productos()
PRODUCTOS_DISPONIBLES = dict(zip(df_productos["Producto"], df_productos["Precio"]))

# ---------------------------------------------------------
# 4. INTERFAZ
# ---------------------------------------------------------
st.title("🔥 Fenix Pedidos")
numero_factura_actual = obtener_siguiente_factura()

# --- VARIABLES DE ESTADO (MEMORIA) ---
if 'direccion_final' not in st.session_state: st.session_state['direccion_final'] = ""
if 'link_ubicacion' not in st.session_state: st.session_state['link_ubicacion'] = ""
if 'valor_domi_calculado' not in st.session_state: st.session_state['valor_domi_calculado'] = 7000

# --- FORMULARIO DATOS ---
with st.expander("👤 Datos del Cliente", expanded=True):
    c_f, c_t = st.columns(2)
    with c_f: st.text_input("Factura #", value=str(numero_factura_actual), disabled=True)
    with c_t: celular = st.text_input("Celular")
    
    # --- SECCIÓN GPS ---
    st.write("📍 **Dirección y Ubicación:**")
    col_btn_gps, col_input_dir = st.columns([1, 4])
    
    gps_data = None
    with col_btn_gps:
        # Botón que pide permiso al celular
        gps_data = get_geolocation(component_key='get_gps')

    # Lógica cuando llega el GPS
    if gps_data:
        lat = gps_data['coords']['latitude']
        lon = gps_data['coords']['longitude']
        coords = (lat, lon)
        
        # Si las coordenadas cambiaron, recalculamos
        if 'last_gps' not in st.session_state or st.session_state['last_gps'] != coords:
            st.session_state['last_gps'] = coords
            
            # 1. Crear Link de Google Maps
            link_maps = f"http://googleusercontent.com/maps.google.com/?q={lat},{lon}"
            st.session_state['link_ubicacion'] = link_maps
            
            # 2. Calcular Precio y buscar nombre de calle
            with st.spinner("📍 Obteniendo ubicación..."):
                t, d, dir_txt = calcular_tarifa_domicilio(coordenadas_gps=coords)
                if t:
                    st.session_state['valor_domi_calculado'] = t
                    st.session_state['direccion_final'] = dir_txt
                    st.toast("Ubicación exacta cargada", icon="✅")

    with col_input_dir:
        # Input Dirección (se llena solo o manual)
        direccion = st.text_input("Dirección", value=st.session_state['direccion_final'], key="input_dir_user")
        if direccion != st.session_state['direccion_final']:
            st.session_state['direccion_final'] = direccion

    # --- CAMPOS RESTANTES ---
    # Input Ubicación (se llena con el LINK automáticamente)
    ubicacion = st.text_input("Ubicación (Link GPS)", value=st.session_state['link_ubicacion'], placeholder="El link aparecerá aquí automáticamente")
    
    # Permitir edición manual del link si el usuario quiere
    if ubicacion != st.session_state['link_ubicacion']:
        st.session_state['link_ubicacion'] = ubicacion

    domiciliario = st.selectbox("Domiciliario", ["Sin Domicilio", "Juan", "Pedro", "Empresa"])
    barrio = st.text_input("Barrio")
    observaciones = st.text_area("Notas")

st.divider()

# ---------------------------------------------------------
# 5. CARRITO DE COMPRAS
# ---------------------------------------------------------
st.subheader("🛒 Carrito")

if "carrito" not in st.session_state:
    st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
    st.session_state.carrito = st.session_state.carrito.astype({"Producto":"str","Precio":"int","Cantidad":"int","Total":"int"})

# Buscador
lista_ordenada = sorted(list(PRODUCTOS_DISPONIBLES.keys()))
opc = ["Seleccionar..."] + lista_ordenada
def fmt(x):
    if x == "Seleccionar...": return x
    try: return f"{x} (${float(PRODUCTOS_DISPONIBLES.get(x,0)):,.0f})"
    except: return x

prod_sel = st.selectbox("Buscar Producto", opc, format_func=fmt)

c_cant, c_add = st.columns([1, 1])
with c_cant: cant_sel = st.number_input("Cantidad", min_value=1, value=1)
with c_add: 
    st.write("")
    st.write("")
    if st.button("➕ AGREGAR", use_container_width=True) and prod_sel != "Seleccionar...":
        precio = int(PRODUCTOS_DISPONIBLES[prod_sel])
        df = st.session_state.carrito.copy()
        if prod_sel in df["Producto"].values:
            idx = df.index[df["Producto"] == prod_sel][0]
            df.loc[idx, "Cantidad"] = int(df.loc[idx, "Cantidad"]) + cant_sel
            df.loc[idx, "Total"] = df.loc[idx, "Precio"] * df.loc[idx, "Cantidad"]
        else:
            nuevo = pd.DataFrame([{"Producto": prod_sel, "Precio": precio, "Cantidad": cant_sel, "Total": precio * cant_sel}])
            df = pd.concat([df, nuevo], ignore_index=True)
        st.session_state.carrito = df
        st.rerun()

# Mostrar Carrito
if not st.session_state.carrito.empty:
    idx_borrar = None
    for i, row in st.session_state.carrito.iterrows():
        with st.container():
            st.markdown(f"**{row['Producto']}**")
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            c1.write(f"${row['Precio']:,.0f}")
            nc = c2.number_input("Cant", min_value=1, value=int(row["Cantidad"]), key=f"q_{i}", label_visibility="collapsed")
            if nc != row["Cantidad"]:
                st.session_state.carrito.at[i, "Cantidad"] = nc
                st.session_state.carrito.at[i, "Total"] = nc * row["Precio"]
                st.rerun()
            c3.write(f"**${nc*row['Precio']:,.0f}**")
            if c4.button("🗑️", key=f"d_{i}"): idx_borrar = i
        st.divider()
    if idx_borrar is not None:
        st.session_state.carrito = st.session_state.carrito.drop(idx_borrar).reset_index(drop=True)
        st.rerun()

# ---------------------------------------------------------
# 6. TOTALES Y ENVÍO
# ---------------------------------------------------------
clean_df = st.session_state.carrito.copy()
suma_productos = int(clean_df["Total"].sum()) if not clean_df.empty else 0

st.subheader("🛵 Envío y Totales")

c_geo1, c_geo2 = st.columns([2, 1])
with c_geo2:
    st.write("")
    # Botón de recalculo manual
    if st.button("📍 Recalcular Manual", use_container_width=True):
        if st.session_state['direccion_final']:
             t, d, _ = calcular_tarifa_domicilio(direccion_texto=st.session_state['direccion_final'])
             if t:
                 st.session_state['valor_domi_calculado'] = t
                 st.toast(f"Distancia aprox: {d}km")

with c_geo1:
    valor_domicilio = st.number_input("Costo Domicilio", value=st.session_state['valor_domi_calculado'], step=500)

medio_pago = st.selectbox("💳 Medio de Pago", ["Efectivo", "Nequi", "DaviPlata", "Datafono"])

total_final = suma_productos + int(valor_domicilio)

st.markdown(f"""
<div style="text-align:center; font-size:32px; font-weight:700; padding:15px; border-radius:12px; background:#e8fff1; color:#004d29; margin-bottom: 20px;">
TOTAL: ${total_final:,.0f}
</div>
""", unsafe_allow_html=True)

total_datafono = ""
if medio_pago == "Datafono":
    v_dat = int(total_final * 1.06)
    st.warning(f"Con Datafono (+6%): ${v_dat:,.0f}")
    total_datafono = st.number_input("Cobrar:", value=v_dat)

if st.button("🚀 ENVIAR PEDIDO", type="primary", use_container_width=True):
    if clean_df.empty:
        st.error("Carrito vacío")
    else:
        prods = []
        for _, row in clean_df.iterrows():
            prods.append({"Producto": str(row["Producto"]), "Cantidad": str(row["Cantidad"]), "Total": str(row["Total"])})
        
        data_json = {
            "MedioPago": medio_pago,
            "ValorTotalV": str(total_final),
            "ValorDomi": str(valor_domicilio),
            "TotalData": str(total_datafono),
            "Factura": str(numero_factura_actual),
            "Domiciliario": domiciliario,
            "Celular": celular,
            "Barrio": barrio,
            "Direccion": st.session_state['direccion_final'],
            "Ubicacion": st.session_state['link_ubicacion'],
            "Observaciones": observaciones,
            "Productos": prods
        }
        
        with st.spinner("Enviando..."):
            res = enviar_a_sheets(data_json)
        
        if hasattr(res, 'status_code') and res.status_code == 200:
            st.balloons()
            st.success("Enviado con éxito")
            
            # Descargar Stock
            for item in prods:
                pn = item["Producto"]
                cant = int(item["Cantidad"])
                if pn in df_productos["Producto"].values:
                    idx = df_productos.index[df_productos["Producto"] == pn][0]
                    curr = int(df_productos.at[idx, "Stock"])
                    df_productos.at[idx, "Stock"] = max(0, curr - cant)
            guardar_productos(df_productos)
            actualizar_factura_siguiente(numero_factura_actual + 1)
            
            # Reset
            st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
            st.session_state['direccion_final'] = ""
            st.session_state['link_ubicacion'] = ""
            st.session_state['valor_domi_calculado'] = 7000
            st.rerun()
        else:
            st.error("Error al enviar")



