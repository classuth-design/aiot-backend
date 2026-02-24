from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    humedad = db.Column(db.Float)
    temperatura = db.Column(db.Float)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/")
def home():
    return "Servidor IoT funcionando"

@app.route("/api/data", methods=["POST"])
def recibir_datos():
    data = request.json

    nuevo = SensorData(
        humedad=data["humedad"],
        temperatura=data["temperatura"],
        fecha=datetime.utcnow()
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

if __name__ == "__main__":
    app.run()
