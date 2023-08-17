from flask import Flask, request, jsonify
import psycopg2
from urllib.parse import urlparse
from flask_cors import CORS
from decouple import config  # Importe a função config

app = Flask(__name__)
CORS(app, origins=[config('FRONTEND_URL')])

URL_DATABASE = config('DATABASE_URL')
# Extrair informações da URL do banco de dados
url = urlparse(URL_DATABASE)
db_connection = psycopg2.connect(
    dbname=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

@app.route('/messages', methods=['POST'])
def add_data():
    try:
        data = request.get_json()
        email = data['email']
        title = data['title']
        description = data['description']

        cursor = db_connection.cursor()
        insert_query = "INSERT INTO tb_messages (email, title, description) VALUES (%s, %s, %s);"
        cursor.execute(insert_query, (email, title, description))
        db_connection.commit()
        cursor.close()

        return jsonify({"message": "Message added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/messages', methods=['GET'])
def get_all_messages():
    try:
        cursor = db_connection.cursor()
        select_query = "SELECT * FROM tb_messages;"
        cursor.execute(select_query)
        messages = cursor.fetchall()
        cursor.close()

        message_list = []
        for message in messages:
            message_dict = {
                "id": message[0],
                "email": message[1],
                "title": message[2],
                "description": message[3]
            }
            message_list.append(message_dict)

        return jsonify(message_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    try:
        cursor = db_connection.cursor()
        select_query = "SELECT * FROM tb_messages WHERE id = %s;"
        cursor.execute(select_query, (message_id,))
        message = cursor.fetchone()
        cursor.close()

        if message:
            message_dict = {
                "id": message[0],
                "email": message[1],
                "title": message[2],
                "description": message[3]
            }
            return jsonify(message_dict), 200
        else:
            return jsonify({"message": "Message not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/messages/<int:message_id>', methods=['PUT'])
def update_message(message_id):
    try:
        data = request.get_json()
        email = data['email']
        title = data['title']
        description = data['description']

        cursor = db_connection.cursor()
        update_query = "UPDATE tb_messages SET email = %s, title = %s, description = %s WHERE id = %s;"
        cursor.execute(update_query, (email, title, description, message_id))
        db_connection.commit()
        cursor.close()

        return jsonify({"message": "Message updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    try:
        cursor = db_connection.cursor()
        delete_query = "DELETE FROM tb_messages WHERE id = %s;"
        cursor.execute(delete_query, (message_id,))
        db_connection.commit()
        cursor.close()

        return jsonify({"message": "Message deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
