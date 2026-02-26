from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# -------------------------------------------------
# INICIALIZAR APP
# -------------------------------------------------

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# -------------------------------------------------
# CONFIGURACIÓN BASE DE DATOS
# -------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")

# Corrección necesaria para Render
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------------------------------------
# MODELO DE DATOS
# -------------------------------------------------

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    humedad = db.Column(db.Float)
    temperatura = db.Column(db.Float)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

# Crear tablas si no existen
with app.app_context():
    db.create_all()

# -------------------------------------------------
# ESTADO GLOBAL DE LEDS
# -------------------------------------------------

led_state = {
    "led1": False,
    "led2": False
}

# -------------------------------------------------
# RUTAS WEB
# -------------------------------------------------

@app.route("/")
def home():
    return "AIoT Backend OK"

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

# -------------------------------------------------
# API - RECIBIR DATOS ESP32
# -------------------------------------------------

@app.route("/api/data", methods=["POST"])
def recibir_datos():
    data = request.json

    hora_honduras = datetime.utcnow() - timedelta(hours=6)

    nuevo = SensorData(
        humedad=data["humedad"],
        temperatura=data["temperatura"],
        fecha=hora_honduras
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({"status": "ok"})

# -------------------------------------------------
# API - OBTENER DATOS
# -------------------------------------------------

@app.route("/api/data", methods=["GET"])
def obtener_datos():
    datos = SensorData.query.order_by(SensorData.fecha.desc()).limit(100).all()

    return jsonify([
        {
            "humedad": d.humedad,
            "temperatura": d.temperatura,
            "fecha": d.fecha.isoformat()
        } for d in datos
    ])

# -------------------------------------------------
# API - CONTROL LED DESDE WEB
# -------------------------------------------------

@app.route("/api/led", methods=["POST"])
def set_led():
    global led_state

    data = request.json

    if "led1" in data:
        led_state["led1"] = data["led1"]

    if "led2" in data:
        led_state["led2"] = data["led2"]

    return jsonify({"status": "updated", "state": led_state})

# -------------------------------------------------
# API - ESP32 CONSULTA ESTADO LED
# -------------------------------------------------

@app.route("/api/led", methods=["GET"])
def get_led():
    return jsonify(led_state)

# -------------------------------------------------
# API - PREDICCIÓN IA BÁSICA
# -------------------------------------------------

@app.route("/api/predict")
def predict():

    datos = SensorData.query.order_by(SensorData.fecha).all()

    if len(datos) < 10:
        return jsonify({"prediction": "Insufficient data"})

    df = pd.DataFrame([{
        "humedad": d.humedad
    } for d in datos])

    X = np.arange(len(df)).reshape(-1, 1)
    y = df["humedad"]

    model = LinearRegression()
    model.fit(X, y)

    futuro = np.array([[len(df) + 10]])
    pred = model.predict(futuro)

    return jsonify({
        "predicted_humidity_10_steps": float(pred[0])
    })

# -------------------------------------------------
# EJECUCIÓN
# -------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)





# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime, timedelta
# import os
# import pytz

# # Inicializa la app
# app = Flask(__name__, template_folder="templates", static_folder="static")

# # Configuración de la base de datos desde la variable de entorno
# DATABASE_URL = os.environ.get("DATABASE_URL")
# app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# # Inicializa SQLAlchemy
# db = SQLAlchemy(app)

# # Modelo de datos
# class SensorData(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     humedad = db.Column(db.Float)
#     temperatura = db.Column(db.Float)
#     fecha = db.Column(db.DateTime, default=datetime.utcnow)

# # Rutas de la API
# # @app.route("/")
# # def home():
# #    return "Servidor IoT funcionando"

# @app.route("/")
# def home():
#     return "AIoT Backend OK"

# @app.route("/dashboard")
# def dashboard():
#     return render_template("index.html")

# @app.route("/api/data", methods=["POST"])
# def recibir_datos():
#     data = request.json

#     # Restamos 6 horas al UTC
#     hora_honduras = datetime.utcnow() - timedelta(hours=6)

#     nuevo = SensorData(
#         humedad=data["humedad"],
#         temperatura=data["temperatura"],
#         # fecha=datetime.utcnow()
#        fecha=hora_honduras
#     )

#     db.session.add(nuevo)
#     db.session.commit()

#     return jsonify({"status": "ok"})

# @app.route("/api/data", methods=["GET"])
# def obtener_datos():
#     datos = SensorData.query.order_by(SensorData.fecha.desc()).limit(100).all()

#     return jsonify([
#         {
#             "humedad": d.humedad,
#             "temperatura": d.temperatura,
#             "fecha": d.fecha.isoformat()
#         } for d in datos
#     ])

# # Ejecuta la app
# if __name__ == "__main__":
#     # Crea las tablas si no existen
#     with app.app_context():
#         db.create_all()
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
