from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'tbl_usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nom_usuario = db.Column(db.String, nullable=False)
    pwd_usuario = db.Column(db.String, nullable=False)
    rol_usuario = db.Column(db.String, nullable=True)

class Temperatura(db.Model):
    __tablename__ = 'tbl_temperatura'
    id_temperatura = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    referencia_equipo = db.Column(db.String, nullable=True)
    toma_inicio = db.Column(db.Numeric, nullable=True)
    toma_mediodia = db.Column(db.Numeric, nullable=True)
    toma_final = db.Column(db.Numeric, nullable=True)
    responsable = db.Column(db.String, nullable=False)

class AceiteQuemado(db.Model):
    __tablename__ = 'tbl_manejo_aceite_quemado'
    id_maq = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    nombre_freidora = db.Column(db.String, nullable=True)
    filtracion = db.Column(db.Boolean, nullable=True)
    cambio_de_aceite = db.Column(db.Boolean, nullable=True)
    responsable = db.Column(db.String, nullable=False)

class Limpieza(db.Model):
    __tablename__ = 'tbl_limpieza_trampa_tanques'
    id_ltt = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=True)
    tampra_grasas = db.Column(db.Boolean, nullable=True)
    tanque_aguas = db.Column(db.Boolean, nullable=True)
    limpieza = db.Column(db.Boolean, nullable=True)
    desinfeccion = db.Column(db.Boolean, nullable=True)
    responsable = db.Column(db.String, nullable=True)

class BPM(db.Model):
    __tablename__ = 'tbl_bpm'
    id_bpm = db.Column(db.Integer, primary_key=True)
    nombre_aux = db.Column(db.String, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    barra_maquillaje = db.Column(db.Boolean, nullable=False)
    cabello_gorro = db.Column(db.Boolean, nullable=False)
    ausencia_heridas = db.Column(db.Boolean, nullable=False)
    joyas_accesorios = db.Column(db.Boolean, nullable=False)
    perfumes = db.Column(db.Integer, nullable=False)
    unas_manos = db.Column(db.Boolean, nullable=False)
    uniforme = db.Column(db.Boolean, nullable=False)
    zapatos = db.Column(db.Boolean, nullable=False)
    observaciones = db.Column(db.String, nullable=True)
    responsable = db.Column(db.String, nullable=False)

class Recepcion(db.Model):
    __tablename__ = 'tbl_recepcion_materiasprimas'
    cantidas = db.Column(db.Integer, primary_key=True)
    temperatura = db.Column(db.Numeric, nullable=False)
    lote = db.Column(db.Integer, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    num_factura = db.Column(db.Integer, nullable=False)
    certificado_calidad = db.Column(db.Boolean, nullable=False)
    se_acepta = db.Column(db.Boolean, nullable=False)
    transporte_carro_moto = db.Column(db.Boolean, nullable=False)
    transporte_termoking = db.Column(db.Boolean, nullable=False)
    responsable = db.Column(db.String, nullable=False)
    observaciones = db.Column(db.String, nullable=True)
