from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

app = Flask(__name__)

# 加載環境變數
load_dotenv()

def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DATABASE_HOST'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            database=os.getenv('DATABASE_NAME')
        )
        return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

@app.route('/get_all_user', methods=['GET'])
def get_all_user():
    connection = create_db_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to database"}), 500

    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM User"
    try:
        cursor.execute(sql)
        users = cursor.fetchall()
        return jsonify(users), 200
    except Error as e:
        print(f"Error: '{e}'")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
