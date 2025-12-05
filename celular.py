import streamlit as st
import requests
import pandas as pd
import os

# ---------------------------------------------------------
# 1. CONFIGURACIÓN
# ---------------------------------------------------------
st.set_page_config(page_title="Ibaguiar Pedidos", page_icon="🔥", layout="centered")



# =========================================================
# 🟢 INICIO DE LA APLICACIÓN
# =========================================================

# ⚠️ TU URL DE GOOGLE APPS SCRIPT
URL_SHEETS = "https://script.google.com/macros/s/AKfycbzEa9UwrBhOVaA1QR6ui5VRUTz1oGSzV-WZ7MIN5YbdJUsBrZRUv9l80Jl1kqAbheNDlw/exec"

# ARCHIVOS LOCALES
ARCHIVO_DB = "productos_db.csv"
ARCHIVO_CONSECUTIVO = "consecutivo.txt"
PASSWORD_ADMIN = "1234"  

# ---------------------------------------------------------
# 2. LISTA MAESTRA INICIAL
# ---------------------------------------------------------
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
    # --- Otros Licores / Bebidas ---
    "Four Loco Sandia": [15000, 20],
    "Four Loco Purple": [15000, 20],
    "Four Loco Blue": [15000, 20],
    "Four Loco Gold": [15000, 20],
    # --- Cigarrillos ---
    "Cigarrillo Mustang": [8000, 20],
    "Cigarrillo Marlboro Rojo": [9000, 20],
    "Cigarrillo Boston": [8000, 20],
    "Cigarrillo Marlboro Sandia": [9000, 20],
    "Cigarrillo Marlboro Fusion": [9000, 20],
    "Cigarrillo Lucky Verde": [9000, 20],
    "Cigarrillo Lucky Alaska": [9000, 20],
    "Cigarrillo Green": [8000, 20],
    # --- Whiskys ---
    "Whisky Jack Daniels": [147000, 20],
    "Whisky Jack Daniels Honey": [147000, 20],
    "Whisky Chivas": [155000, 20],
    "Whisky Buchannas Botella": [183000, 20],
    "Whisky Buchannas Media": [104000, 20],
    "Whisky Grans": [73000, 20],
    "Whisky Old Parr Botella": [164000, 20],
    "Whisky Old Parr Media": [116000, 20],
    "Whisky Haig Club": [116000, 20],
    "Whisky Black White Botella": [60000, 20],
    "Whisky Black White Media": [33000, 20],
    "Whisky Something Botella": [76000, 20],
    "Whisky Sello Rojo Litro": [104000, 20],
    "Whisky Sello Rojo Botella": [80000, 20],
    "Whisky Sello Rojo Media": [51000, 20],
    # --- Cremas ---
    "Crema de Whisky Black Jack": [58000, 20],
    "Crema de Whisky Baileys Litro": [116000, 20],
    "Crema de Whisky Baileys Botella": [85000, 20],
    "Crema de Whisky Baileys Media": [53000, 20],
    # --- Tequilas / Ginebra / Vodka ---
    "Tequila Jose Cuervo Botella": [96000, 20],
    "Tequila Jose Cuervo Media": [60000, 20],
    "Tequila Jimador Botella": [125000, 20],
    "Tequila Jimador Media": [76000, 20],
    "Ginebra Tanqueray": [135000, 20],
    "Ginebra Bombay": [120000, 20],
    "Vodka Absolut Litro": [120000, 20],
    "Vodka Absolut Botella": [92000, 20],
    "Vodka Absolut Media": [58000, 20],
    "Smirnoff Ice Lata": [9500, 20],
    "Smirnoff Manzana Lata": [9500, 20],
    "Smirnoff Lulo Botella": [52000, 20],
    "Smirnoff Lulo Media": [29000, 20],
    "Jagermaister Hiervas": [130000, 20],
    # --- Vinos ---
    "Vino Gato Tinto Tetrapack": [27000, 20],
    "Vino Gato Negro Merlot": [47000, 20],
    "Vino Gato Negro Sauvignon": [47000, 20],
    "Vino Gato Negro Malbec": [47000, 20],
    "Vino Casillero del Diablo": [75000, 20],
    "Vino Finca Las Moras Sauvignon": [58000, 20],
    "Vino Finca Las Moras Malbec": [58000, 20],
    "Vino Duvoned": [73000, 20],
    "Vino Espumoso JP Chanet Blanco": [70000, 20],
    "Vino Espumoso JP Chanet Rosado": [70000, 20],
    "Vino Espumoso JP Chanet Morado": [70000, 20],
    "Vino Espumoso JP Chanet Syrah": [65000, 20],
    "Vino Espumoso JP Chanet Brut": [65000, 20],
    "Vino Espumoso JP Chanet Chardonnay": [65000, 20],
    # --- Bebidas sin Alcohol / Energizantes ---
    "Gatorade": [5000, 20],
    "Agua con Gas": [2500, 20],
    "Agua sin Gas": [2000, 20],
    "Redbull": [7000, 20],
    "Coca Cola 1.5L": [7500, 20],
    "Gaseosa Ginger 1.5L": [7500, 20],
    "Gaseosa Soda Bretaña 1.5L": [7500, 20],
    "Jugo Naranja Del Valle": [7000, 20],
    "Electrolit Naran/Mandarina": [9500, 20],
    "Electrolit Maracuya": [9500, 20],
    # --- Snacks / Varios ---
    "Detodito Natural 165gr": [8500, 20],
    "Detodito BBQ 165gr": [8500, 20],
    "Detodito Mix 165gr": [8500, 20],
    "Chicles Trident": [2000, 20],
    "Encendedor": [1000, 20],
    "Bonfiest": [4000, 20],
    "Preservativos": [3000, 20],
    "Sildenafil Viagra": [7000, 20],
    "Salchichas": [7000, 20],
    "Bombombunes": [600, 20],
    "Hielo": [2000, 20]
}

# ---------------------------------------------------------
# 3. GESTIÓN DE BASE DE DATOS Y CONSECUTIVO
# ---------------------------------------------------------

def cargar_productos():
    if not os.path.exists(ARCHIVO_DB):
        data_list = [{"Producto": p, "Precio": v[0], "Stock": v[1]} for p, v in PRODUCTOS_INICIALES_DICT.items()]
        df = pd.DataFrame(data_list)
        df.to_csv(ARCHIVO_DB, index=False)
        return df
    else:
        try:
            return pd.read_csv(ARCHIVO_DB)
        except:
            data_list = [{"Producto": p, "Precio": v[0], "Stock": v[1]} for p, v in PRODUCTOS_INICIALES_DICT.items()]
            df = pd.DataFrame(data_list)
            df.to_csv(ARCHIVO_DB, index=False)
            return df

def guardar_productos(df):
    df.to_csv(ARCHIVO_DB, index=False)

def obtener_siguiente_factura():
    if not os.path.exists(ARCHIVO_CONSECUTIVO): return 3001
    try:
        with open(ARCHIVO_CONSECUTIVO, "r") as f: return int(f.read().strip())
    except: return 3001

def actualizar_factura_siguiente(nuevo_numero):
    with open(ARCHIVO_CONSECUTIVO, "w") as f: f.write(str(nuevo_numero))

# Inicialización
df_productos = cargar_productos()
PRODUCTOS_DISPONIBLES = dict(zip(df_productos["Producto"], df_productos["Precio"]))
STOCK_DISPONIBLE = dict(zip(df_productos["Producto"], df_productos["Stock"]))

# ---------------------------------------------------------
# 4. PANEL DE ADMINISTRACIÓN (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Admin")
    activar_admin = st.checkbox("Administrar Productos")
    
    if activar_admin:
        password = st.text_input("Contraseña", type="password")
        
        if password == PASSWORD_ADMIN:
            st.success("Acceso Admin")
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Stock", "Crear", "Editar", "Borrar", "CSV"])
            
            with tab1:
                st.info("Editar Stock:")
                df_stock_edit = st.data_editor(
                    df_productos[["Producto", "Stock"]],
                    column_config={
                        "Producto": st.column_config.TextColumn(disabled=True),
                        "Stock": st.column_config.NumberColumn("Unds", min_value=0, step=1)
                    },
                    hide_index=True,
                    key="editor_stock_admin"
                )
                if st.button("💾 Guardar"):
                    for index, row in df_stock_edit.iterrows():
                        df_productos.loc[df_productos["Producto"] == row["Producto"], "Stock"] = row["Stock"]
                    guardar_productos(df_productos)
                    st.success("Guardado")
                    st.rerun()

            with tab2:
                new_name = st.text_input("Nombre", key="new_name")
                c_n1, c_n2 = st.columns(2)
                with c_n1: new_price = st.number_input("Precio", min_value=0, step=500, key="new_price")
                with c_n2: new_stock = st.number_input("Stock", min_value=0, step=1, key="new_stock_init")
                
                if st.button("Crear"):
                    if new_name and new_name not in df_productos["Producto"].values:
                        nuevo_row = pd.DataFrame([{"Producto": new_name, "Precio": new_price, "Stock": new_stock}])
                        df_productos = pd.concat([df_productos, nuevo_row], ignore_index=True)
                        guardar_productos(df_productos)
                        st.success("Creado")
                        st.rerun()

            with tab3:
                lista_prods = sorted(list(df_productos["Producto"]))
                prod_a_editar = st.selectbox("Editar:", ["Seleccionar..."] + lista_prods)
                if prod_a_editar != "Seleccionar...":
                    row = df_productos[df_productos["Producto"] == prod_a_editar].iloc[0]
                    edit_name = st.text_input("Nombre", value=prod_a_editar)
                    c_e1, c_e2 = st.columns(2)
                    with c_e1: e_price = st.number_input("Precio", value=int(row["Precio"]), step=500)
                    with c_e2: e_stock = st.number_input("Stock", value=int(row.get("Stock",0)), step=1)
                    if st.button("Actualizar"):
                        idx = df_productos.index[df_productos["Producto"] == prod_a_editar][0]
                        df_productos.at[idx, "Producto"] = edit_name
                        df_productos.at[idx, "Precio"] = e_price
                        df_productos.at[idx, "Stock"] = e_stock
                        guardar_productos(df_productos)
                        st.rerun()

            with tab4:
                prod_del = st.selectbox("Borrar:", ["Seleccionar..."] + sorted(list(df_productos["Producto"])), key="del_sel")
                if st.button("Eliminar"):
                    if prod_del != "Seleccionar...":
                        df_productos = df_productos[df_productos["Producto"] != prod_del]
                        guardar_productos(df_productos)
                        st.rerun()

            with tab5:
                with open(ARCHIVO_DB, "rb") as f:
                    st.download_button("⬇️ Descargar CSV", f, "inventario.csv", "text/csv")
                uploaded = st.file_uploader("⬆️ Subir CSV", type=["csv"])
                if uploaded and st.button("Reemplazar"):
                    try:
                        df_new = pd.read_csv(uploaded)
                        if all(c in df_new.columns for c in ["Producto","Precio","Stock"]):
                            guardar_productos(df_new)
                            st.rerun()
                    except: pass
        elif password:
            st.error("Error")

# ---------------------------------------------------------
# 5. INTERFAZ (OPTIMIZADA PARA MÓVIL)
# ---------------------------------------------------------
def enviar_a_sheets(data):
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(URL_SHEETS, json=data, headers=headers, timeout=20)
        return resp
    except Exception as e: return f"Error: {e}"

st.title("🔥 Fenix Pedidos")
numero_factura_actual = obtener_siguiente_factura()

# --- DATOS CLIENTE (VERTICAL STACK) ---
with st.expander("👤 Datos del Cliente", expanded=False):
    c_f, c_t = st.columns(2)
    with c_f: st.text_input("Factura #", value=str(numero_factura_actual), disabled=True)
    with c_t: celular = st.text_input("Celular")
    
    # Apilados para mejor uso en móvil
    domiciliario = st.selectbox("Domiciliario", ["Sin Domicilio", "Juan", "Pedro", "Empresa"])
    barrio = st.text_input("Barrio")
    direccion = st.text_input("Dirección")
    ubicacion = st.text_input("Ubicación")
    observaciones = st.text_area("Notas", height=68)

st.divider()

# ---------------------------------------------------------
# 6. PEDIDO (INTERFAZ MÓVIL)
# ---------------------------------------------------------
st.subheader("🛒 Realizar Pedido")

if "carrito" not in st.session_state:
    st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
    st.session_state.carrito = st.session_state.carrito.astype({"Producto":"str","Precio":"int","Cantidad":"int","Total":"int"})

# --- BUSCADOR OPTIMIZADO ---
# Fila 1: Producto (Ancho completo)
lista_ordenada = sorted(list(PRODUCTOS_DISPONIBLES.keys()))
opc = ["Seleccionar..."] + lista_ordenada
def fmt(x):
    if x == "Seleccionar...": return x
    try: return f"{x} (${float(PRODUCTOS_DISPONIBLES.get(x,0)):,.0f})"
    except: return x

prod_sel = st.selectbox("Buscar Producto", opc, format_func=fmt)

# Fila 2: Cantidad y Botón (Mitad y mitad)
c_cant, c_add = st.columns([1, 1])
with c_cant:
    cant_sel = st.number_input("Cantidad", min_value=1, value=1)
with c_add:
    st.write("") # Espaciador para alinear botón
    st.write("") 
    add_btn = st.button("➕ AGREGAR", type="primary", use_container_width=True)

if add_btn and prod_sel != "Seleccionar...":
    precio = int(PRODUCTOS_DISPONIBLES[prod_sel])
    cant = int(cant_sel)
    df = st.session_state.carrito.copy()
    if prod_sel in df["Producto"].values:
        idx = df.index[df["Producto"] == prod_sel][0]
        df.loc[idx, "Cantidad"] = int(df.loc[idx, "Cantidad"]) + cant
        df.loc[idx, "Precio"] = precio 
        df.loc[idx, "Total"] = df.loc[idx, "Precio"] * df.loc[idx, "Cantidad"]
    else:
        nuevo = pd.DataFrame([{"Producto": prod_sel, "Precio": precio, "Cantidad": cant, "Total": precio * cant}])
        df = pd.concat([df, nuevo], ignore_index=True)
    st.session_state.carrito = df
    st.rerun()

# ---------------------------------------------------------
# 7. CARRITO TIPO TARJETA (MEJOR PARA MÓVIL)
# ---------------------------------------------------------
st.markdown("### Resumen del Pedido")

if st.session_state.carrito.empty:
    st.info("El carrito está vacío")
else:
    idx_borrar = None
    for i, row in st.session_state.carrito.iterrows():
        # Tarjeta de producto
        with st.container():
            # Línea 1: Nombre del producto destacado
            st.markdown(f"**{row['Producto']}**")
            
            # Línea 2: Controles en una sola fila
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            
            # Precio Unitario
            c1.caption("Precio")
            c1.write(f"${row['Precio']:,.0f}")
            
            # Cantidad Editable
            nueva_cant = c2.number_input("Cant", min_value=1, value=int(row["Cantidad"]), key=f"q_{i}", label_visibility="collapsed")
            if nueva_cant != row["Cantidad"]:
                st.session_state.carrito.at[i, "Cantidad"] = nueva_cant
                st.session_state.carrito.at[i, "Total"] = nueva_cant * row["Precio"]
                st.rerun()
            
            # Total
            total_fila = nueva_cant * row["Precio"]
            c3.caption("Total")
            c3.write(f"**${total_fila:,.0f}**")
            
            # Borrar
            c4.write("")
            if c4.button("🗑️", key=f"d_{i}"):
                idx_borrar = i
            
        st.divider()

    if idx_borrar is not None:
        st.session_state.carrito = st.session_state.carrito.drop(idx_borrar).reset_index(drop=True)
        st.rerun()

# ---------------------------------------------------------
# 8. TOTALES Y PAGO
# ---------------------------------------------------------
clean_df = st.session_state.carrito.copy()
suma_productos = int(clean_df["Total"].sum()) if not clean_df.empty else 0

valor_domicilio = st.number_input("🛵 Domicilio", min_value=0, step=1000, value=7000)
medio_pago = st.selectbox("💳 Medio de Pago", ["Efectivo", "Nequi", "DaviPlata", "Datafono"], key="medio_pago_input")

total_final = suma_productos + int(valor_domicilio)

st.markdown(f"""
<div style="text-align:center; font-size:32px; font-weight:700; padding:15px; border-radius:12px; background:#e8fff1; color:#004d29; margin-bottom: 20px;">
TOTAL: ${total_final:,.0f}
</div>
""", unsafe_allow_html=True)

total_datafono = ""
if medio_pago == "Datafono":
    valor_dat = int(total_final * 1.06)
    st.warning(f"Pago con Datafono (+6%): **${valor_dat:,.0f}**")
    total_datafono = st.number_input("Cobrar en Datafono:", value=valor_dat)

# ---------------------------------------------------------
# 9. ENVIAR
# ---------------------------------------------------------
if st.button("🚀 ENVIAR PEDIDO", type="primary", use_container_width=True):
    if clean_df.empty:
        st.error("⚠️ Carrito vacío")
    else:
        # Preparar JSON
        prods = []
        for _, row in clean_df.iterrows():
            prods.append({
                "Producto": str(row["Producto"]),
                "Precio": str(row["Precio"]),
                "Cantidad": str(row["Cantidad"]),
                "Total": str(row["Total"])
            })
            
        data_json = {
            "MedioPago": medio_pago,
            "ValorTotalV": str(total_final),
            "ValorDomi": str(valor_domicilio),
            "TotalData": total_datafono,
            "Factura": str(numero_factura_actual),
            "Domiciliario": domiciliario,
            "Celular": celular,
            "Barrio": barrio,
            "Direccion": direccion,
            "Ubicacion": ubicacion,
            "Observaciones": observaciones,
            "Productos": prods
        }
        
        with st.spinner("Enviando..."):
            res = enviar_a_sheets(data_json)
        
        if hasattr(res, 'status_code') and res.status_code == 200:
            st.balloons()
            st.success(f"✅ Pedido #{numero_factura_actual} enviado!")
            
            # Actualizar Stock
            for item in prods:
                pn = item["Producto"]
                cant = int(item["Cantidad"])
                if pn in df_productos["Producto"].values:
                    idx = df_productos.index[df_productos["Producto"] == pn][0]
                    curr = int(df_productos.at[idx, "Stock"])
                    df_productos.at[idx, "Stock"] = max(0, curr - cant)
            guardar_productos(df_productos)
            
            # Actualizar Factura
            actualizar_factura_siguiente(numero_factura_actual + 1)
            
            # Limpiar
            st.session_state.carrito = pd.DataFrame(columns=["Producto","Precio","Cantidad","Total"])
            if "medio_pago_input" in st.session_state: del st.session_state["medio_pago_input"]
            st.rerun()
        else:
            st.error("❌ Error al enviar")



