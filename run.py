import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

db_host = os.getenv('DB_HOST', 'localhost')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'root')
db_name = os.getenv('DB_NAME', 'megasena')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:3306/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/healthcheck/db")
def healthcheck_db():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "message": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/megasena/ultima")
def get_ultima_sorteio():
    try:
        result = db.session.execute(text("SELECT numero, data, sorteados FROM sorteio ORDER BY numero DESC LIMIT 1"))
        row = result.fetchone()

        if row:
            numero, data, sorteados = row
            response = {
                "numero": numero,
                "data": data.isoformat() if hasattr(data, "isoformat") else data,
                "sorteados": sorteados,
                "next": None,
                "previous": numero - 1
            }
            return jsonify(response)
        else:
            return jsonify({"error": "Nenhum sorteio encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/megasena/<int:numero>")
def get_sorteio_by_numero(numero):
    try:
        result = db.session.execute(
            text("SELECT numero, data, sorteados FROM sorteio WHERE numero = :numero"),
            {"numero": numero}
        )
        row = result.fetchone()

        if row:
            numero, data, sorteados = row
            response = {
                "numero": numero,
                "data": data.isoformat() if hasattr(data, "isoformat") else data,
                "sorteados": sorteados,
                "next": numero + 1,
                "previous": numero - 1
            }
            return jsonify(response)
        else:
            return jsonify({"error": "Sorteio não encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
