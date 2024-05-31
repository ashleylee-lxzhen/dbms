from flask import Flask
from flask_restx import Api, Resource, reqparse
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

app = Flask(__name__)
api = Api(app, version=1.0, title='DBMS api')
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

user_id_parser = reqparse.RequestParser()
#創造一個可輸入的格子
user_id_parser.add_argument('user_id', type=int, required=True, help='使用者ID')
#開login的格子
login_parser = reqparse.RequestParser()
login_parser.add_argument('User_Name', type = str, required=True)
login_parser.add_argument('User_Password', type = str, required=True)

enroll_parser = reqparse.RequestParser()
enroll_parser.add_argument('User_ID', type = str, required=True)
enroll_parser.add_argument('User_Name', type = str, required=True)
enroll_parser.add_argument('User_PhoneNo', type = int, required=True)
enroll_parser.add_argument('User_Email', type = str, required=True)
enroll_parser.add_argument('User_Password', type = str, required=True)

searching_parser = reqparse.RequestParser()
searching_parser.add_argument('History_ID', type = str, required = True)
searching_parser.add_argument('History_Keyword', type = str, required = True)

searching_history_parser = reqparse.RequestParser()
searching_history_parser.add_argument()



#開一個新的區域
user_ns = api.namespace('User', description='使用者api')
@user_ns.route('/get_user_from_id')
class GetUserFromID(Resource):
    @user_ns.expect(user_id_parser)
    def get(self):
        '''根據使用者ID取得使用者資料'''
        args = user_id_parser.parse_args()
        user_id = args['user_id']

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                sql = "SELECT * FROM User WHERE User_ID = %s"
                cursor.execute(sql, (user_id, ))
                user = cursor.fetchone()
                if user:
                    return user, 200
                else:
                    return {"error": "User not found"}, 404
            except Error as e:
                return {"error": str(e)}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": "Unable to connect to the database"}, 500
        
@user_ns.route('/login')
class Login(Resource):
    @user_ns.expect(login_parser)
    def get(self):
        '''登入'''
        args = login_parser.parse_args()
        User_Name = args['User_Name']
        User_Password = args['User_Password']

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                sql = "SELECT User_Name, User_Password FROM User WHERE User_Name = %s AND User_Password = %s"
                cursor.execute(sql, (User_Name, User_Password))
                user = cursor.fetchone()
                if user:
                    return user, 200
                else:
                    return {"error": "User not found"}, 404
            except Error as e:
                return {"error": str(e)}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": "Unable to connect to the database"}, 500

@user_ns.route('/enroll')
class Enroll(Resource):
    @user_ns.expect(enroll_parser)
    def post(self):
        '''註冊'''
        args = enroll_parser.parse_args()
        User_ID = args['User_ID']
        User_Name = args['User_Name']
        User_PhoneNo = args['User_PhoneNo']
        User_Email = args['User_Email']
        User_Password = args['User_Password']

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                sql = "INSERT INTO User (User_ID, User_Name, User_PhoneNo, User_Email, User_Password) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (User_ID, User_Name, User_PhoneNo, User_Email, User_Password))
                connection.commit()
                return {"message": "User registered successfully"}, 200
            except Error as e:
                return {"error": str(e)}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": "Unable to connect to the database"}, 500
 
@user_ns.route('/search_keyword')
class SearchKeyword(Resource):
    @user_ns.expect(searching_parser)
    def post(self):
        '''搜索關鍵字並保存搜索歷史'''
        args = searching_parser.parse_args()
        User_ID = args['User_ID']
        History_Keyword = args['History_Keyword']

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                sql_designer = """
                SELECT * FROM Designer
                WHERE Designer_Name LIKE %s
                   OR Special_Skill LIKE %s
                   OR Portfolio LIKE %s
                """
                keyword_pattern = f"%{History_Keyword}%"
                cursor.execute(sql_designer, (keyword_pattern, keyword_pattern, keyword_pattern))
                designers = cursor.fetchall()

                sql_hairsalon = """
                SELECT * FROM Hairsalon
                WHERE Hairsalon_Name LIKE %s
                   OR Hairsalon_Keyword LIKE %s
                """
                cursor.execute(sql_hairsalon, (keyword_pattern, keyword_pattern))
                hairsalons = cursor.fetchall()

                sql_history = "INSERT INTO `Searching_History`(`History_ID`, `User_ID`, `History_Keyword`) VALUES (%s,%s,%s)"
                cursor.execute(sql_history, (User_ID, History_Keyword))
                connection.commit()

                new_history_id = cursor.lastrowid

                return {
                    "new_history_id": new_history_id,
                    "designers": designers,
                    "hairsalons": hairsalons
                }, 200
            except Error as e:
                return {"error": str(e)}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": "Unable to connect to the database"}, 500   

        

if __name__ == '__main__':
    app.run(debug=True)
    