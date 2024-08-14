import streamlit as st
import psycopg2
import bcrypt
import pandas as pd
import re
from psycopg2 import errors
from datetime import date
from datetime import timedelta

## Genera los menú en el sidebar
def generarMenu(usuario = None):
    with st.sidebar:
        if usuario == None: # Si el usuario NO ha iniciado sesión
            st.write(f'**Bienvenido avicultor**')
            st.page_link('Home.py', label= 'Inicio', icon= ':material/home:')
            st.subheader('Iniciar sesión o Registrarse')
            st.page_link('pages/iniciar_sesion.py', label= 'Inicia sesión', icon= ':material/login:')
            st.page_link('pages/registrarse.py', label= 'Crea una cuenta', icon=':material/person_add:')
        
        # Si el usuario ya inició sesión   
        else: 
            st.write(f'Bienvenido, **:red[{usuario}]**')
            st.page_link('Home.py', label= 'Inicio', icon= ':material/home:')
            st.subheader('Gestiona tu granja')
            st.page_link('pages/granja.py', label='Tu granja', icon=':material/agriculture:')
            st.page_link('pages/camada.py', label='Tus camadas', icon=':material/gite:')
            st.page_link('pages/faenas.py', label='Faenas', icon=':material/food_bank:')
            st.subheader('Vende tu producto')
            st.page_link('pages/ventas.py', label='Ventas', icon=':material/payments:')
            st.subheader('Evalúa tu desempeño')
            st.page_link('pages/estadistica.py', label='Analíticas', icon=':material/analytics:')
            st.subheader('Gestiona tus proveedores')
            st.page_link('pages/proveedores.py', label='Proveedores', icon=':material/approval_delegation:')
            btnSalir=st.button("Cerrar Sesión")
            
            # Boton para cerrar sesión
            if btnSalir: 
                st.session_state.clear() # Se borra el session_state
                st.switch_page('Home.py')
                st.rerun()

## Valida que el correo ingresado si tenga forma de correo electrónico
def validador_email(email):
    if re.search(r'[\w.]+\@[\w.]+\.+[\w.]', email):
        return True
    else:
        return False

## Agrega usuarios nuevos a la base de datos
def agregarUsuario(nombre, apellido, email, username, password):
    db_config = st.secrets['database']
    conn = psycopg2.connect(
        host = db_config['host'],
        port=db_config['port'],
        database=db_config['database'],
        user=db_config['username'],
        password=db_config['password']
    )
    try:
        c = conn.cursor()
        
        # Verificar si el email ya está registrado
        c.execute("SELECT 1 FROM usuario WHERE email = %s", (email,))
        if c.fetchone():
            conn.close()
            return {"success": False, "error": "El email ya está registrado."}
        
        # Verificar si el username ya está registrado
        c.execute("SELECT 1 FROM usuario WHERE username = %s", (username,))
        if c.fetchone():
            conn.close()
            return {"success": False, "error": "El username ya está registrado."}
        
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        fecha_union = date.today()
        c.execute('''
            INSERT INTO usuario (nombre, apellido, email, username, password, fecha_union) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (nombre, apellido, email, username, hashed_password, fecha_union))
        conn.commit()
        conn.close()
        return {"success": True}
    
    except errors.UniqueViolation:
        conn.rollback()
        conn.close()
        return {"success": False, 'error': "El email o username ya está registrado."}
    
    except Exception as e:
        conn.close()
        return {"success": False, 'error': f"Error al agregar usuario a la base de datos: {e}"}


## Incia sesión de los usuarios registrados
def validarUsuario(username, password):
    db_config = st.secrets['database']
    conn = psycopg2.connect(
        host = db_config['host'],
        port=db_config['port'],
        database=db_config['database'],
        user=db_config['username'],
        password=db_config['password']
    )
    try:
        c = conn.cursor()
        c.execute('''SELECT password, id 
                    FROM usuario 
                    WHERE username = %s''', (username,))
        result = c.fetchone()
        
        if result and bcrypt.checkpw(password.encode('utf-8'), bytes(result[0])):
            user_id = result[1]
            c.execute('UPDATE usuario SET ultimo_login = %s WHERE username = %s', (date.today(), username))
            conn.commit()
            return {'success':True, 'id': user_id}
        return {'success':False, 'id': None}
    except Exception as e:
        st.error(f"Error al autenticar usuario: {e}")
        return {'success':False, 'id': None}
    finally:
        c.close()
        conn.close()

# Conexión a la base de datos
def conectarDB():
    db_config = st.secrets['database']
    try:
        conn = psycopg2.connect(
            host = db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['username'],
            password=db_config['password']
        )
        c = conn.cursor()
        return conn, c
    except Exception as e:
        st.error(f'Error al conectar con la base de datos: {e}')
        return None, None

# Agregar granja a la base de datos
def agregarGranja(usuario_id, nombre_granja, ubicacion):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            fecha = date.today()
            c.execute('''
                        INSERT INTO granja ( 
                            usuario_id, 
                            nombre_granja, 
                            ubicacion,
                            fecha,
                            es_activa)
                        VALUES(%s, %s, %s, %s, %s)
                    ''', (usuario_id, nombre_granja, ubicacion, fecha, True))
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            st.error(f"Error al agregar la granja: {e}")
            return {'success':False}
    else:
        st.write('No se pudo conectar a la base de datos')

# Consulta departamentos y municipios de colombia. Los devuelve en un dataframe
def consultaMunicipios():
    conn, c = conectarDB()
    
    if conn is not None and c is not None:
        try:
            # Consulto los departamentos
            c.execute(''' SELECT UPPER(NOMBRE) as nombre,
                            COD_DEPARTAMENTO
                        FROM PUBLIC.UBICACION_DEPARTAMENTO
                        ORDER BY NOMBRE ASC
                    ''')
            departamentos = c.fetchall()
            columnas_departamentos = [desc[0] for desc in c.description]
            df_departamentos = pd.DataFrame(departamentos, columns=columnas_departamentos)
            
            c.execute('''SELECT DEPARTAMENTO,
                        UPPER(NOMBRE) as nombre,
                        MUNICIPIO,
                        COD_MUNICIPIO
                    FROM PUBLIC.UBICACION
                    JOIN PUBLIC.UBICACION_DEPARTAMENTO ON UBICACION_DEPARTAMENTO.COD_DEPARTAMENTO = UBICACION.DEPARTAMENTO
                    ''')
            municipios = c.fetchall()
            columnas_municipios = [desc[0] for desc in c.description]
            df_municipios = pd.DataFrame(municipios, columns= columnas_municipios)
            c.close()
            conn.close()
            
            return df_departamentos, df_municipios
            
        except Exception as e:
            st.write(f'Error al ejecutar la consulta: {e}')

# Agrega galpones a la base de datos
def agregarGalpon(granja_id, capacidad, nombre):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute('''
                        INSERT INTO galpon ( 
                            granja_id, 
                            capacidad, 
                            nombre)
                        VALUES(%s, %s, %s)
                    ''', (granja_id, capacidad, nombre))
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            st.error(f"Error al agregar el galpón: {e}")
            return {'success':False}
    else:
        st.write('No se pudo conectar a la base de datos')

## Devuelve DF con las granjas y galpones que tenga el usuario

def listaGranjaGalpones(user_id):
    conn, c  = conectarDB()

    if conn is not None and c is not None:
        try:
            c.execute(''' SELECT
                    id,
                    nombre_granja, 
                    ubicacion, 
                    fecha
                FROM PUBLIC.GRANJA
                WHERE (USUARIO_ID = %s) AND
                    (es_activa = True)
                    ''', (user_id,))
            granjas = c.fetchall()
            columnas = [desc[0] for desc in c.description]
            df_granjas = pd.DataFrame(granjas, columns=columnas)
            
            #Se hacen transformaciones al df_granjas
            # df_granjas_merged = pd.merge(df_granjas, df_municipios, how='left', left_on='ubicacion', right_on='cod_municipio')
            # df_granjas_show = df_granjas_merged[['nombre_granja', 'nombre', 'municipio', 'fecha']]
            # df_granjas_show.rename(columns={'nombre_granja':'Granja','nombre':'Departamento' ,'fecha':'Fecha de creación', 'municipio':'Municipio'}, inplace=True)
            
            c.execute('''
                SELECT 
                    NOMBRE AS "Galpón",
                    GRANJA.NOMBRE_GRANJA AS "Granja",
                    CAPACIDAD AS "Capacidad",
                    GALPON.ID AS "galpon_id",
                    GRANJA_ID,
                    UBICACION,
                    DEPARTAMENTO,
                    FECHA
                FROM PUBLIC.GALPON
                JOIN PUBLIC.GRANJA ON GRANJA.ID = GALPON.GRANJA_ID
                JOIN PUBLIC.UBICACION ON UBICACION.COD_MUNICIPIO = GRANJA.UBICACION
                WHERE (USUARIO_ID = %s) AND
                    (GALPON_ACTIVO = TRUE)
            ''', (user_id,))
            galpones = c.fetchall()
            columnas = [desc[0] for desc in c.description]
            df_galpones = pd.DataFrame(galpones, columns=columnas)
            
            c.close()
            conn.close()
            
            return df_granjas, df_galpones
            # st.write(df_granjas)
        except Exception as e:
            st.write(f'Error al ejecutar la consulta: {e}')
    else:
        st.write('No se pudo conectar a la base de datos')


# Elimina granjas
def quitarGranja(id_granja):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute('''
                    UPDATE GRANJA
                    SET ES_ACTIVA = FALSE
                    WHERE ID = %s
                    ''', (id_granja,))
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            st.error(f"Error al eliminar la granja: {e}")
            return {'success':False}

# Elimina galpones
def quitarGalpon(id_galpon):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute('''
                    UPDATE GALPON
                    SET GALPON_ACTIVO = FALSE
                    WHERE ID = %s
                    ''', (id_galpon,))
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            st.error(f"Error al eliminar la granja: {e}")
            return {'success':False}

# Devuelve un df con las camadas activas
def consultarCamadas(user_id):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute('''
                    SELECT *
                    FROM PUBLIC.CAMADA
                    WHERE (USER_ID = %s)
	                    AND (CAMADA_ACTIVA = TRUE)
                    ''', (user_id,))
            camadas = c.fetchall()
            columnas = [desc[0] for desc in c.description]
            df_camadas = pd.DataFrame(camadas, columns=columnas)
            conn.commit()
            conn.close()
            return df_camadas
        
        except Exception as e:
            st.error(f"Error al eliminar la granja: {e}")
            return {'success':False}
        
# Devuelve una lista de las razas
def listaRazas():
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute('''
                    SELECT *
                    FROM PUBLIC.RAZAS
                    ''')
            camadas = c.fetchall()
            columnas = [desc[0] for desc in c.description]
            df_razas = pd.DataFrame(camadas, columns=columnas)
            conn.commit()
            conn.close()
            return df_razas
        except Exception as e:
            st.error(f"Error al eliminar la granja: {e}")
            return {'success':False}

# Agrega camada a la base de datos
def agregarCamada(granja_id, galpon_id, cant_camada, raza_id, fecha_ent_camada, fecha_faena_camada, user_id):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute('''
                        INSERT INTO camada(
                            granja_id,
                            galpon_id,
                            cantidad, 
                            raza,
                            fecha_inicio,
                            fecha_estimada_sacrificio,
                            user_id)
                        VALUES(%s, %s, %s, %s, %s, %s, %s)
                    ''', (granja_id,galpon_id, cant_camada, raza_id, fecha_ent_camada, fecha_faena_camada, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error al agregar la camada: {e}")
            return {'success':False}
    else:
        st.write('No se pudo conectar a la base de datos')

def sumaDias(inicial):
    final = inicial + timedelta(days=45)
    return final

# Elimina la camada de la base de datos
def quitarCamada(id_galpon):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute('''
                    UPDATE CAMADA
                    SET CAMADA_ACTIVA = FALSE
                    WHERE ID = %s
                    ''', (id_galpon,))
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            st.error(f"Error al eliminar la granja: {e}")
            return {'success':False}

def cosnultaQuery(query):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute(query)
            resultado_consulta = c.fetchall()
            columnas = [desc[0] for desc in c.description]
            df_consulta = pd.DataFrame(resultado_consulta, columns=columnas)
            conn.commit()
            conn.close()
            return df_consulta
        
        except Exception as e:
            st.error(f"Error al eliminar la granja: {e}")
            return {'success':False}

def consultarProveedores(user_id):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute('''
                    SELECT
                    id,
                    nombre as "Nombre",
                    nit as "Nit",
                    contacto as "Contacto",
                    telefono as "Teléfono",
                    user_id,
                    prov_activo
                    FROM PUBLIC.PROVEEDOR
                    WHERE (USER_ID = %s)
	                    AND (PROV_ACTIVO = TRUE)
                    ''', (user_id,))
            proveedores = c.fetchall()
            columnas = [desc[0] for desc in c.description]
            df_proveedores = pd.DataFrame(proveedores, columns=columnas)
            conn.commit()
            conn.close()
            return df_proveedores
        
        except Exception as e:
            st.error(f"Error al eliminar la granja: {e}")
            return {'success':False}

def agregarPropveedor(nombre_proveedor,nit_proveedor, contacto_proveedor, tel_proveedor, user_id):
    conn, c = conectarDB()
    if conn is not None and c is not None:
        try:
            c.execute('''
                        INSERT INTO proveedor(
                            nombre,
                            nit,
                            contacto,
                            telefono,
                            user_id)
                        VALUES(%s, %s, %s, %s, %s)
                    ''', (nombre_proveedor,nit_proveedor, contacto_proveedor, tel_proveedor, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error al agregar el proveedor: {e}")
            return {'success':False}
    else:
        st.write('No se pudo conectar a la base de datos')