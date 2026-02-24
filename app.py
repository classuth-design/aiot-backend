from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import pytz

# Inicializa la app
app = Flask(__name__)

# Configuración de la base de datos desde la variable de entorno
DATABASE_URL = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa SQLAlchemy
db = SQLAlchemy(app)

# Modelo de datos
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    humedad = db.Column(db.Float)
    temperatura = db.Column(db.Float)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

# Rutas de la API
@app.route("/")
def home():
    return "Servidor IoT funcionando"

@app.route("/api/data", methods=["POST"])
def recibir_datos():
    data = request.json

    # Restamos 6 horas al UTC
    hora_honduras = datetime.utcnow() - timedelta(hours=6)

    nuevo = SensorData(
        humedad=data["humedad"],
        temperatura=data["temperatura"],
        # fecha=datetime.utcnow()
       fecha=hora_honduras
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({"status": "ok"})

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

# Ejecuta la app
if __name__ == "__main__":
    # Crea las tablas si no existen
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
