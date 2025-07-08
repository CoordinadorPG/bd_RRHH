import pandas as pd
import io
import os

from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from models import db, Usuario, Temperatura, AceiteQuemado, Limpieza, BPM, Recepcion
from datetime import datetime
from passlib.hash import bcrypt

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Configura la conexión a tu base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    pestañas = []
    rol = session['rol']
    if rol == 'admin':
        pestañas = []
    elif rol == 'cocina':
        pestañas = ['temperatura', 'aceite', 'limpieza']
    elif rol == 'barra':
        pestañas = ['bpm']
    elif rol == 'bodega':
        pestañas = ['recepcion']

    session['pestañas'] = pestañas

    # Obtener mensajes de la sesión (y limpiarlos después)
    mensaje = session.pop('mensaje', None)
    error = session.pop('error', None)

    #usuarios = Usuario.query.all() if rol == 'admin' else None
    pestaña_activa = request.args.get('pestaña_activa')
    if not pestaña_activa:
        pestaña_activa = "visualizacion" if rol == "admin" else pestañas[0]

    # ⚠️ Obtener usuarios solo si es la pestaña correspondiente
    usuarios = Usuario.query.all() if rol == 'admin' and pestaña_activa == 'gestionar_usuarios' else []


    pestaña_activa = request.args.get('pestaña_activa')
    if not pestaña_activa:
        pestaña_activa = "visualizacion" if rol == "admin" else pestañas[0]
        
    print("Usuarios disponibles:", usuarios)
    
    return render_template('dashboard.html',
        username=session['username'],
        rol=rol,
        pestaña_activa=pestaña_activa,
        registros=None,
        columnas=None,
        titulos={},
        pestañas=pestañas,
        usuarios=usuarios,
        mensaje=mensaje,
        error=error
    )



@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if 'username' not in session or session.get('rol') != 'admin':
        return redirect(url_for('login'))

    mensaje = error = None

    if request.method == 'POST':
        nom_usuario = request.form['nom_usuario'].strip()
        pwd_usuario = request.form['pwd_usuario'].strip()
        rol_usuario = request.form['rol_usuario'].strip()

        if Usuario.query.filter_by(nom_usuario=nom_usuario).first():
            error = '❌ El nombre de usuario ya existe.'
        else:
            hashed_pwd = bcrypt.hash(pwd_usuario)
            nuevo_usuario = Usuario(
                nom_usuario=nom_usuario,
                pwd_usuario=hashed_pwd,
                rol_usuario=rol_usuario
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            mensaje = '✅ Usuario creado exitosamente.'

    pestañas_visibles = obtener_pestañas_por_rol(session['rol'])
    pestañas_visibles.append('crear_usuario')

    return render_template('dashboard.html',
        username=session['username'],
        rol=session['rol'],
        pestaña_activa='crear_usuario',
        registros=None,
        columnas=None,
        titulos={},
        pestañas=pestañas_visibles,
        mensaje=mensaje,
        error=error
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['username'].strip()
        clave = request.form['password'].strip()

        print("Usuario ingresado:", usuario)
        print("Contraseña ingresada:", clave)

        user = Usuario.query.filter_by(nom_usuario=usuario).first()

        if user:
            print("Hash guardado en BD:", user.pwd_usuario)

            try:
                if bcrypt.verify(clave, user.pwd_usuario):
                    print("✅ Contraseña verificada correctamente")
                    session['username'] = user.nom_usuario
                    session['rol'] = user.rol_usuario
                    return redirect(url_for('index'))
                else:
                    print("❌ Contraseña incorrecta")
                    error = 'Credenciales incorrectas'
            except Exception as e:
                error = f'Error al verificar: {e}'
        else:
            print("❌ Usuario no encontrado")
            error = 'Usuario no encontrado'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --------------------- RUTAS DE GUARDADO ----------------------

@app.route('/guardar_temperatura', methods=['POST'])
def guardar_temperatura():
    t = Temperatura(
        fecha=request.form['fecha'],
        referencia_equipo=request.form['referencia_equipo'],
        toma_inicio=request.form['toma_inicio'],
        toma_mediodia=request.form['toma_mediodia'],
        toma_final=request.form['toma_final'],
        responsable=request.form['responsable']
    )
    db.session.add(t)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/guardar_aceite', methods=['POST'])
def guardar_aceite():
    a = AceiteQuemado(
        fecha=request.form['fecha'],
        nombre_freidora=request.form['nombre_freidora'],
        filtracion='filtracion' in request.form.getlist('accion'),
        cambio_de_aceite='cambio' in request.form.getlist('accion'),
        responsable=request.form['responsable']
    )
    db.session.add(a)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/guardar_limpieza', methods=['POST'])
def guardar_limpieza():
    l = Limpieza(
        fecha=request.form['fecha'],
        tampra_grasas='trampa_grasas' in request.form.getlist('tipo_area'),
        tanque_aguas='tanque_aguas' in request.form.getlist('tipo_area'),
        limpieza='limpieza' in request.form,
        desinfeccion='desinfeccion' in request.form,
        responsable=request.form['responsable']
    )
    db.session.add(l)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/guardar_bpm', methods=['POST'])
def guardar_bpm():
    b = BPM(
        nombre_aux=request.form['nombre_aux'],
        fecha=request.form['fecha'],
        barra_maquillaje=request.form['barba_maquillaje'] == 'sí',
        cabello_gorro=request.form['cabello_gorro'] == 'sí',
        ausencia_heridas=request.form['ausencia_heridas'] == 'sí',
        joyas_accesorios=request.form['joyas_accesorios'] == 'sí',
        perfumes=int(request.form['perfumes']),
        unas_manos=request.form['unas_manos'] == 'sí',
        uniforme=request.form['uniforme'] == 'sí',
        zapatos=request.form['zapatos'] == 'sí',
        observaciones=request.form.get('observaciones'),
        responsable=request.form['responsable']
    )
    db.session.add(b)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/guardar_recepcion', methods=['POST'])
def guardar_recepcion():
    r = Recepcion(
        temperatura=request.form['temperatura'],
        lote=request.form['lote'],
        fecha_vencimiento=request.form['fecha_vencimiento'],
        num_factura=request.form['num_factura'],
        certificado_calidad=request.form['certificado_calidad'] == 'sí',
        se_acepta=request.form['se_acepta'] == 'sí',
        transporte_carro_moto=request.form['transporte_carro_moto'] == 'sí',
        transporte_termoking=request.form['transporte_termoking'] == 'sí',
        responsable=request.form['responsable'],
        observaciones=request.form.get('observaciones')
    )
    db.session.add(r)
    db.session.commit()
    return redirect(url_for('index'))
    
# Función que retorna pestañas según el rol
def obtener_pestañas_por_rol(rol):
    if rol == 'admin':
        return []
    elif rol == 'cocina':
        return ['temperatura', 'aceite', 'limpieza']
    elif rol == 'barra':
        return ['bpm']
    elif rol == 'bodega':
        return ['recepcion']
    else:
        return []
        
@app.route('/exportar_excel')
def exportar_excel():
    if 'username' not in session or session.get('rol') != 'admin':
        return redirect(url_for('login'))

    tabla = request.args.get('tabla')

    modelo_map = {
        'temperatura': Temperatura,
        'aceite': AceiteQuemado,
        'limpieza': Limpieza,
        'bpm': BPM,
        'recepcion': Recepcion
    }

    modelo = modelo_map.get(tabla)
    if not modelo:
        return "Tabla no válida", 400

    datos = modelo.query.all()
    registros = [d.__dict__ for d in datos]
    for r in registros:
        r.pop('_sa_instance_state', None)

    df = pd.DataFrame(registros)

    # 🔤 Formatear encabezados legibles
    df.columns = [col.replace("_", " ").title() for col in df.columns]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=tabla.capitalize())
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'{tabla}.xlsx'
    )

# --------------------- RUTA DE VISUALIZACIÓN ----------------------

@app.route('/visualizar')
def visualizar():
    if 'username' not in session:
        return redirect(url_for('login'))

    tabla = request.args.get('tabla')
    registros, columnas, titulos = [], [], {}

    if tabla == 'temperatura':
        datos = Temperatura.query.all()
        columnas = ['fecha', 'referencia_equipo', 'toma_inicio', 'toma_mediodia', 'toma_final', 'responsable']
    elif tabla == 'aceite':
        datos = AceiteQuemado.query.all()
        columnas = ['fecha', 'nombre_freidora', 'filtracion', 'cambio_de_aceite', 'responsable']
    elif tabla == 'limpieza':
        datos = Limpieza.query.all()
        columnas = ['fecha', 'tampra_grasas', 'tanque_aguas', 'limpieza', 'desinfeccion', 'responsable']
    elif tabla == 'bpm':
        datos = BPM.query.all()
        columnas = ['fecha', 'nombre_aux', 'barra_maquillaje', 'cabello_gorro', 'ausencia_heridas',
                    'joyas_accesorios', 'perfumes', 'unas_manos', 'uniforme', 'zapatos',
                    'observaciones', 'responsable']
    elif tabla == 'recepcion':
        datos = Recepcion.query.all()
        columnas = ['temperatura', 'lote', 'fecha_vencimiento', 'num_factura', 'certificado_calidad',
                    'se_acepta', 'transporte_carro_moto', 'transporte_termoking', 'responsable', 'observaciones']
    else:
        datos = []

    registros = [d.__dict__ for d in datos]
    titulos = {col: col.replace('_', ' ').title() for col in columnas}
    for r in registros:
        r.pop('_sa_instance_state', None)

    return render_template('dashboard.html',
        username=session['username'],
        rol=session['rol'],
        pestaña_activa="visualizacion",
        registros=registros,
        columnas=columnas,
        titulos=titulos
    )

@app.route('/gestionar_usuarios', methods=['POST'])
def gestionar_usuarios():
    print("FORMULARIO:", request.form)
    usuario_id = request.form.get('usuario_id')
    nueva_clave = request.form.get('nueva_clave')
    accion = request.form.get('accion')

    if not usuario_id:
        session['error'] = "Debe seleccionar un usuario"
        return redirect(url_for('index', pestaña_activa='gestionar_usuarios'))

    usuario = Usuario.query.get(usuario_id)
    
    if not usuario:
        session['error'] = "Usuario no encontrado"
        return redirect(url_for('index', pestaña_activa='gestionar_usuarios'))

    if accion == 'actualizar':
        if nueva_clave:
            usuario.pwd_usuario = bcrypt.hash(nueva_clave)
            db.session.commit()
            flash("Contraseña actualizada correctamente.", "success")
        else:
            flash("No se ingresó una nueva contraseña.", "error")
    elif accion == 'eliminar':
        db.session.delete(usuario)
        db.session.commit()
        session['mensaje'] = f" Usuario {usuario.nom_usuario} eliminado"
    else:
        session['mensaje'] = "No se realizó ninguna acción"

    return redirect(url_for('index', pestaña_activa='gestionar_usuarios'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
