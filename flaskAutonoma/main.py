from flask import Flask
from clases import *
from dao import *
from flask import request
from flask import abort
import json


# Inicializamos la base de datos
Conexion.iniciar_bbdd()
# creamos el servidor flask
app = Flask(__name__)


@app.route("/")
def inicio():
    return "Aplicación de gestión de experimentos científicos en Flask"


# funcion encargada de dar una respuesta a la peticcion GET con esta url /experimentos
@app.route("/experimentos", methods=["GET"])
def experimentos():
    todos_experimentos = ExperimentoDAO.obtener_todos()
    # Array
    datos_todos = []
    for experimento in todos_experimentos:
        datos_todos.append(
            {
                "id": experimento.id,
                "tipo": experimento.tipo,
                "descripcion": experimento.descripcion,
                "experimento.descripcion": experimento.descripcion,
                "rutaCsv": experimento.rutaCsv,
            }
        )
    final = {}
    final["experimentos"] = datos_todos
    return final


@app.route("/experimentos/<int:id>", methods=["DELETE"])
def experimentos_del(id):
    print(request)
    if request.remote_addr != "127.0.0.1":
        abort(403)  # Forbidden

    experimento = ExperimentoDAO.obtener_por_id(id)
    if experimento is None:
        abort(404)

    ExperimentoDAO.eliminar(experimento)
    return {
        "id": experimento.id,
        "tipo": experimento.tipo,
        "descripcion": experimento.descripcion,
        "experimento.descripcion": experimento.descripcion,
        "rutaCsv": experimento.rutaCsv,
    }


@app.route("/experimentos", methods=["POST"])
def experimentos_post(): 
    if request.remote_addr != "127.0.0.1":
        abort(403)  # Forbidden


    byte_data = request.data
    str_data = byte_data.decode('utf-8')
    json_data = json.loads(str_data)
    
    experimento = Experimento()
    experimento.tipo = json_data["tipo"]
    experimento.descripcion = json_data["descripcion"]
    experimento.rutaCsv = json_data["rutaCsv"]

    experimento = ExperimentoDAO.crear(experimento)

    print(json_data)
    return {
        "id": experimento.id,
        "tipo": experimento.tipo,
        "descripcion": experimento.descripcion,
        "experimento.descripcion": experimento.descripcion,
        "rutaCsv": experimento.rutaCsv,
    }

@app.route("/experimentos", methods=["PUT"])
def experimentos_put(): 
    ...