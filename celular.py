import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# 1. CONFIGURACIÓN
# ---------------------------------------------------------
st.set_page_config(page_title="Fenix Pedidos", page_icon="🔥", layout="centered")

# ⚠️ TU URL DE GOOGLE APPS SCRIPT
URL_SHEETS = "https://script.google.com/macros/s/AKfycbzEa9UwrBhOVaA1QR6ui5VRUTz1oGSzV-WZ7MIN5YbdJUsBrZRUv9l80Jl1kqAbheNDlw/exec"

# ---------------------------------------------------------
# 2. LISTA DE PRODUCTOS (COMPLETA)
# ---------------------------------------------------------
PRODUCTOS_DISPONIBLES = {
    # --- Aguardientes ---
    "Aguardiente Garrafa tapa roja": 98000,
    "Aguardiente Botella tapa roja": 58000,
    "Aguardiente Tapa roja media": 34000,
    "Aguardiente Garrafa tapa special": 102000,
    "Aguardiente Botella tapa special": 60000,
    "Aguardiente Tapa special media": 36000,
    "Aguardiente Amarillo": 67000,
    "Aguardiente Tapa Rosado": 78000,
    "Aguardiente Botella Nectar verde": 50000,
    "Aguardiente Nectar verde media": 33000,

    # --- Rones ---
    "Ron Mojito": 55000,
    "Ron Bacardi Limon": 55000,
    "Ron Botella Viejo de Caldas": 65000,
    "Ron Viejo de Caldas media": 35000,

    # --- Cervezas ---
    "Cerveza Six Heineken": 21000,
    "Cerveza Six Corona 355": 30000,
    "Cerveza Six Costeña": 17000,
    "Cerveza Six Costeñita": 17000,
    "Cerveza Six 330 Aguila": 23000,
    "Cerveza Six Poker": 23000,
    "Cerveza Sixpack Andina": 16000,
    "Cerveza Six Light Aguila": 23000,
    "Cerveza Sixpack Club Colombia": 24000,
    "Cerveza Six Budweiser": 17000,

    # --- Otros Licores / Bebidas ---
    "Four Loco Sandia": 15000,
    "Four Loco Purple": 15000,
    "Four Loco Blue": 15000,
    "Four Loco Gold": 15000,

    # --- Cigarrillos ---
    "Cigarrillo Mustang": 8000,
    "Cigarrillo Marlboro Rojo": 9000,
    "Cigarrillo Boston": 8000,
    "Cigarrillo Marlboro Sandia": 9000,
    "Cigarrillo Marlboro Fusion": 9000,
    "Cigarrillo Lucky Verde": 9000,
    "Cigarrillo Lucky Alaska": 9000,
    "Cigarrillo Green": 8000,

    # --- Whiskys ---
    "Whisky Jack Daniels": 147000,
    "Whisky Jack Daniels Honey": 147000,
    "Whisky Chivas": 155000,
    "Whisky Buchannas Botella": 183000,
    "Whisky Buchannas Media": 104000,
    "Whisky Grans": 73000,
    "Whisky Old Parr Botella": 164000,
    "Whisky Old Parr Media": 116000,
    "Whisky Haig Club": 116000,
    "Whisky Black White Botella": 60000,
    "Whisky Black White Media": 33000,
    "Whisky Something Botella": 76000,
    "Whisky Sello Rojo Litro": 104000,
    "Whisky Sello Rojo Botella": 80000,
    "Whisky Sello Rojo Media": 51000,

    # --- Cremas ---
    "Crema de Whisky Black Jack": 58000,
    "Crema de Whisky Baileys Litro": 116000,
    "Crema de Whisky Baileys Botella": 85000,
    "Crema de Whisky Baileys Media": 53000,

    # --- Tequilas / Ginebra / Vodka ---
    "Tequila Jose Cuervo Botella": 96000,
    "Tequila Jose Cuervo Media": 60000,
    "Tequila Jimador Botella": 125000,
    "Tequila Jimador Media": 76000,
    "Ginebra Tanqueray": 135000,
    "Ginebra Bombay": 120000,
    "Vodka Absolut Litro": 120000,
    "Vodka Absolut Botella": 92000,
    "Vodka Absolut Media": 58000,
    "Smirnoff Ice Lata": 9500,
    "Smirnoff Manzana Lata": 9500,
    "Smirnoff Lulo Botella": 52000,
    "Smirnoff Lulo Media": 29000,
    "Jagermaister Hiervas": 130000,

    # --- Vinos ---
    "Vino Gato Tinto Tetrapack": 27000,
    "Vino Gato Negro Merlot": 47000,
    "Vino Gato Negro Sauvignon": 47000,
    "Vino Gato Negro Malbec": 47000,
    "Vino Casillero del Diablo": 75000,
    "Vino Finca Las Moras Sauvignon": 58000,
    "Vino Finca Las Moras Malbec": 58000,
    "Vino Duvoned": 73000,
    "Vino Espumoso JP Chanet Blanco": 70000,
    "Vino Espumoso JP Chanet Rosado": 70000,
    "Vino Espumoso JP Chanet Morado": 70000,
    "Vino Espumoso JP Chanet Syrah": 65000,
    "Vino Espumoso JP Chanet Brut": 65000,
    "Vino Espumoso JP Chanet Chardonnay": 65000,

    # --- Bebidas sin Alcohol / Energizantes ---
    "Gatorade": 5000,
    "Agua con Gas": 2500,
    "Agua sin Gas": 2000,
    "Redbull": 7000,
    "Coca Cola 1.5L": 7500,
    "Gaseosa Ginger 1.5L": 7500,
    "Gaseosa Soda Bretaña 1.5L": 7500,
    "Jugo Naranja Del Valle": 7000,
    "Electrolit Naran/Mandarina": 9500,
    "Electrolit Maracuya": 9500,

    # --- Snacks / Varios ---
    "Detodito Natural 165gr": 8500,
    "Detodito BBQ 165gr": 8500,
    "Detodito Mix 165gr": 8500,
    "Chicles Trident": 2000,
    "Encendedor": 1000,
    "Bonfiest": 4000,
    "Preservativos": 3000,
    "Sildenafil Viagra": 7000,
    "Salchichas": 7000,
    "Bombombunes": 600,
    "Hielo": 2000
    
}

# ---------------------------------------------------------
# 3. FUNCIÓN DE ENVÍO
# ---------------------------------------------------------
def enviar_a_sheets(data):
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(URL_SHEETS, json=data, headers=headers, timeout=20)
        return resp
    except Exception as e:
        return f"Error de conexión: {e}"

# ---------------------------------------------------------
# 4. INTERFAZ: DATOS CLIENTE
# ---------------------------------------------------------
st.title("🔥 Nuevo Pedido")

with st.expander("👤 Datos del Cliente", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        factura = st.text_input("Factura #")
    with col_b:
        celular = st.text_input("Celular")
    
    domiciliario = st.selectbox("Domiciliario", ["Sin Domicilio", "Juan", "Pedro", "Empresa"])
    col_c, col_d = st.columns(2)
    with col_c:
        barrio = st.text_input("Barrio")
    with col_d:
        direccion = st.text_input("Dirección")
    ubicacion = st.text_input("Ubicación")
    observaciones = st.text_area("Observaciones", height=68)

st.divider()

# ---------------------------------------------------------
# 5. CARRITO Y LÓGICA DE AGREGAR
# ---------------------------------------------------------
st.subheader("🛒 Productos")

# Inicializar estado seguro
if "carrito" not in st.session_state:
    st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
    # Forzar tipos iniciales
    st.session_state.carrito = st.session_state.carrito.astype({"Producto":"str","Precio":"int","Cantidad":"int","Total":"int"})

# --- BUSCADOR ---
col1, col2, col3 = st.columns([3,1,1])
with col1:
    opc = ["Seleccionar..."] + list(PRODUCTOS_DISPONIBLES.keys())
    prod_sel = st.selectbox("Producto", opc, label_visibility="collapsed")
with col2:
    cant_sel = st.number_input("Cant.", min_value=1, value=1, label_visibility="collapsed")
with col3:
    add_btn = st.button("➕", type="primary", use_container_width=True)

# Lógica robusta de agregar
if add_btn and prod_sel != "Seleccionar...":
    precio = int(PRODUCTOS_DISPONIBLES[prod_sel])
    cant = int(cant_sel)
    df = st.session_state.carrito.copy()

    # Si ya existe, sumamos cantidad
    if prod_sel in df["Producto"].values:
        idx = df.index[df["Producto"] == prod_sel][0]
        df.loc[idx, "Cantidad"] = int(df.loc[idx, "Cantidad"]) + cant
        df.loc[idx, "Precio"] = precio
        df.loc[idx, "Total"] = df.loc[idx, "Precio"] * df.loc[idx, "Cantidad"]
    else:
        # Si es nuevo
        nuevo = pd.DataFrame([{
            "Producto": prod_sel,
            "Precio": precio,
            "Cantidad": cant,
            "Total": precio * cant
        }])
        df = pd.concat([df, nuevo], ignore_index=True)
    
    st.session_state.carrito = df
    st.rerun()

# ---------------------------------------------------------
# 6. TABLA EDITABLE Y LIMPIEZA AUTOMÁTICA
# ---------------------------------------------------------
st.write("Resumen:")

edited_df = st.data_editor(
    st.session_state.carrito,
    num_rows="dynamic",
    column_config={
        "Producto": st.column_config.TextColumn("Producto", required=True),
        "Precio": st.column_config.NumberColumn("Precio", min_value=0, format="$%d"),
        "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=1),
        "Total": st.column_config.NumberColumn("Total", disabled=True, format="$%d"),
    },
    key="editor_carrito"
)

# --- FASE DE LIMPIEZA Y CÁLCULO (LA PARTE CRÍTICA) ---
# Copiamos para no mutar directamente mientras editamos
clean_df = edited_df.copy()

# 1. Convertir a string y limpiar basura ($ , espacios)
clean_df["Producto"] = clean_df["Producto"].astype(str)
# Eliminar filas vacías
clean_df = clean_df[clean_df["Producto"].str.strip() != ""]
clean_df = clean_df[clean_df["Producto"].str.lower() != "nan"]

# 2. Limpiar columnas numéricas (quitar $ y , si el editor los pone)
for col in ["Precio", "Cantidad"]:
    clean_df[col] = clean_df[col].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce').fillna(0).astype(int)

# 3. Recalcular la columna Total matemáticamente
clean_df["Total"] = clean_df["Precio"] * clean_df["Cantidad"]

# 4. Sincronizar estado si hubo cambios por la limpieza
# (Esto asegura que la suma final use números limpios)
if not clean_df.equals(edited_df):
    pass 

# Guardamos el limpio en session_state para la próxima recarga
st.session_state.carrito = clean_df

# ---------------------------------------------------------
# 7. TOTALES SEPARADOS (TU SOLICITUD)
# ---------------------------------------------------------
st.divider()

# A. Calcular Suma de Productos
suma_productos = int(clean_df["Total"].sum())

st.subheader("💰 Totales")

# Inputs necesarios para que las variables existan
valor_domicilio = st.number_input("Valor Domicilio", min_value=7000, step=1000, value=7000, key="val_domi_input")
medio_pago = st.selectbox("Medio de Pago", ["Efectivo", "Nequi", "DaviPlata", "Datafono"], key="medio_pago_input")

# --- VERSIÓN DEBUG SOLICITADA ---
total_final = suma_productos + int(valor_domicilio)
st.markdown(f"""
<div style="
text-align:center;
font-size:32px;
font-weight:700;
padding:12px;
margin-top:10px;
border-radius:10px;
background:#e8fff1;
color:#004d29;">
TOTAL: ${total_final:,.0f}
</div>
""", unsafe_allow_html=True)

# =======================================================
#   BLOQUE DATAFONO - Cálculo Automático + Entrada editable
# =======================================================

total_datafono = ""  # siempre inicializado

if medio_pago == "Datafono":
    # --- 6% adicional por pago con Datafono ---
    valor_dat_calculado = int(total_final * 1.06)

    # Caja título
    st.markdown(
        """
        <div style="
            font-size:16px; 
            font-weight:900; 
            color:#8B0000;
            background:#FFE4E4;
            border:2px solid #E57373;
            padding:12px 5px;
            border-radius:10px;
            text-align:center;
            margin-top:18px;
            margin-bottom:10px;
        ">
            💳 Pago con Datafono (6% adicional)
        </div>
        """,
        unsafe_allow_html=True
    )

    # Campo editable con valor calculado
    total_datafono = st.number_input(
        "Valor Datafono",
        value=valor_dat_calculado,
        step=500,
        key="datafono_valor"
    )

    # Texto aclaratorio
    st.markdown(
        f"""
        <div style="
            font-size:24px; 
            color:#333; 
            text-align:center; 
            margin-top:6px;
        ">
            Cálculo automático:<br>
            <b>${total_final:,.0f}</b> × <b>6%</b> = 
            <b style="color:#C62828;">${valor_dat_calculado:,.0f}</b>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# 8. ENVIAR
# ---------------------------------------------------------
if st.button("🚀 ENVIAR PEDIDO", type="primary", use_container_width=True):
    # Preparar JSON final
    productos_envio = []
    for _, row in clean_df.iterrows():
        productos_envio.append({
            "Producto": str(row["Producto"]),
            "Precio": str(row["Precio"]),
            "Cantidad": str(row["Cantidad"]),
            "Total": str(row["Total"])
        })
    
    if not productos_envio:
        st.error("⚠️ Carrito vacío")
    else:
        data_json = {
            "MedioPago":      medio_pago,
            "ValorTotalV":    str(total_final),
            "ValorDomi":      str(valor_domicilio),
            "TotalData":      total_datafono,
            "Factura":        factura,
            "Domiciliario":   domiciliario,
            "Celular":        celular,
            "Barrio":         barrio,
            "Direccion":      direccion,
            "Ubicacion":      ubicacion,
            "Observaciones":  observaciones,
            "Productos":      productos_envio
        }
        
        with st.spinner("Enviando..."):
            res = enviar_a_sheets(data_json)
        
        if hasattr(res, 'status_code') and res.status_code == 200:
            st.balloons()
            st.success("✅ Enviado correctamente")
            # Limpiar
            st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
            st.rerun()
        else:
            st.error("❌ Error al enviar")
            st.write(res)

        #streamlit run celular.py
