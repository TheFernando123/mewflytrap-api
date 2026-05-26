import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv

# Buscar y cargar el archivo .env
load_dotenv(find_dotenv())

app = Flask(__name__)
CORS(app)

# Variables de entorno
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Headers obligatorios para que Supabase nos deje entrar
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "proyecto": "MEWFLYTRAP API Dinámica",
        "cultivador_contacto": "+52 5563258488"
    })

# Endpoint para obtener TODAS las plantas
@app.route('/api/plantas', methods=['GET'])
def get_todas_plantas():
    try:
        # Petición directa a tu tabla usando PostgREST de Supabase
        endpoint = f"{url}/rest/v1/blog_plantas?select=*"
        respuesta = requests.get(endpoint, headers=headers)
        
        if respuesta.status_code == 200:
            return jsonify({"success": True, "data": respuesta.json()})
        else:
            return jsonify({"success": False, "error": respuesta.text}), respuesta.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
# Endpoint POST para AGREGAR una nueva planta
@app.route('/api/plantas', methods=['POST'])
def agregar_planta():
    try:
        # 1. Recibir los datos en formato JSON
        datos_nueva_planta = request.get_json()

        # 2. Validar que al menos venga el nombre y la especie (campos obligatorios)
        if not datos_nueva_planta or 'nombre' not in datos_nueva_planta or 'especie' not in datos_nueva_planta:
            return jsonify({"success": False, "error": "Faltan datos obligatorios: 'nombre' y 'especie' son requeridos."}), 400
        
        # 3. Preparar la petición hacia Supabase (para hacer un INSERT)
        endpoint = f"{url}/rest/v1/blog_plantas"
        
        # Le decimos a Supabase que queremos que nos devuelva el registro recién creado
        headers_post = headers.copy()
        headers_post["Prefer"] = "return=representation"

        # 4. Enviar los datos
        respuesta = requests.post(endpoint, headers=headers_post, json=datos_nueva_planta)

        if respuesta.status_code in [200, 201]:
            # Si todo salió bien, devolvemos el nuevo registro
            return jsonify({"success": True, "mensaje": "Planta agregada exitosamente", "data": respuesta.json()}), 201
        else:
            return jsonify({"success": False, "error": respuesta.text}), respuesta.status_code

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    # Endpoint PATCH para ACTUALIZAR una planta existente
@app.route('/api/plantas/<id_planta>', methods=['PATCH'])
def actualizar_planta(id_planta):
    try:
        # 1. Recibir solo los datos que queremos cambiar
        datos_actualizar = request.get_json()
        
        # 2. Apuntar al registro exacto usando eq. (equals) en Supabase
        endpoint = f"{url}/rest/v1/blog_plantas?id=eq.{id_planta}"
        
        headers_patch = headers.copy()
        headers_patch["Prefer"] = "return=representation"

        # 3. Enviar la petición de actualización
        respuesta = requests.patch(endpoint, headers=headers_patch, json=datos_actualizar)

        if respuesta.status_code == 200:
            return jsonify({"success": True, "mensaje": "Planta actualizada con éxito", "data": respuesta.json()})
        else:
            return jsonify({"success": False, "error": respuesta.text}), respuesta.status_code

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Endpoint DELETE para BORRAR una planta
@app.route('/api/plantas/<id_planta>', methods=['DELETE'])
def eliminar_planta(id_planta):
    try:
        # Apuntar al registro exacto
        endpoint = f"{url}/rest/v1/blog_plantas?id=eq.{id_planta}"
        
        # Enviar la petición de borrado
        respuesta = requests.delete(endpoint, headers=headers)

        # Supabase devuelve 204 (No Content) si se borró con éxito
        if respuesta.status_code in [200, 204]:
            return jsonify({"success": True, "mensaje": f"La planta con ID '{id_planta}' ha sido eliminada del catálogo."})
        else:
            return jsonify({"success": False, "error": respuesta.text}), respuesta.status_code

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)