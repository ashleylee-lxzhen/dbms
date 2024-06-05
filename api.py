from flask import Flask
from flask_restx import Api, Resource, reqparse
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import date

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

search_parser = reqparse.RequestParser()
search_parser.add_argument('User_ID', type=int, required=True)
search_parser.add_argument('History_Keyword', type=str, required=True)

coupon_parser = reqparse.RequestParser()
coupon_parser.add_argument('User_ID', type=int, required=True)

designer_search_parser = reqparse.RequestParser()
designer_search_parser.add_argument('Designer_ID', type=int, required=False)
designer_search_parser.add_argument('Designer_Name', type=str, required=False)

comment_parser = reqparse.RequestParser()
comment_parser.add_argument('User_ID', type=int, required=True)
comment_parser.add_argument('Hairsalon_ID', type=int, required=True)
comment_parser.add_argument('Score', type=float, required =True)
comment_parser.add_argument('Comment', type=str, required =False)

favourite_parser = reqparse.RequestParser()
favourite_parser.add_argument('User_ID', type=int, required=True)
favourite_parser.add_argument('Favourite_ID', type=int, required=True)
favourite_parser.add_argument('Designer_ID', type=int, required=True)
favourite_parser.add_argument('Hairsalon_ID', type=int, required=True)

default_parser = reqparse.RequestParser()
default_parser.add_argument('User_ID', type=int, required=True)





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


def get_max_history_id(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(History_ID) FROM `Searching_History`")
    result = cursor.fetchone()
    max_id = result[0] if result[0] is not None else 0
    cursor.close()
    return max_id

@user_ns.route('/search_keyword')
class SearchKeyword(Resource):
    @user_ns.expect(search_parser)
    def post(self):
        '''搜索關鍵字並保存搜索歷史'''
        args = search_parser.parse_args()
        User_ID = args['User_ID']
        History_Keyword = args['History_Keyword']

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                new_history_id = get_max_history_id(connection) + 1
                print('new_history_id: '+ str(new_history_id))
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
                cursor.execute(sql_history, (new_history_id, User_ID, History_Keyword))
                connection.commit()

                return {
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
        
def get_coupon(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT Coupon_ID FROM `coupon`")
    result = cursor.fetchone()
    coupon = result
    cursor.close()
    return coupon

@user_ns.route('/coupon')
class Coupon(Resource):
    @user_ns.expect(coupon_parser)
    def get(self):
        args = coupon_parser.parse_args()
        User_ID = args['User_ID']

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                sql = "SELECT * FROM Coupon WHERE User_ID = %s"
                cursor.execute(sql, (User_ID,))
                coupons = cursor.fetchall()
                for coupon in coupons:
                    if isinstance(coupon['Coupon_ExpirationDate'], date):
                        coupon['Coupon_ExpirationDate'] = coupon['Coupon_ExpirationDate'].strftime('%Y-%m-%d')
                if coupons:
                    return coupons, 200
                else:
                    return {"error": "Coupon not found"}, 404
            except Error as e:
                return {"error": str(e)}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": "Unable to connect to the database"}, 500

@user_ns.route('/search_designer')
class SearchDesigner(Resource):
    @user_ns.expect(designer_search_parser)
    def get(self):
        args = designer_search_parser.parse_args()
        Designer_ID = args.get('Designer_ID')
        Designer_Name = args.get('Designer_Name')

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                if Designer_ID:
                    sql = "SELECT * FROM Designer WHERE Designer_ID = %s"
                    cursor.execute(sql, (Designer_ID,))
                elif Designer_Name:
                    sql = "SELECT * FROM Designer WHERE Designer_Name LIKE %s"
                    cursor.execute(sql, (f"%{Designer_Name}%",))
                else:
                    return {"error": "Designer_ID or Designer_Name must be provided"}, 400
                
                designers = cursor.fetchall()
                if designers:
                    return designers, 200
                else:
                    return {"error": "Designer not found"}, 404
            except Error as e:
                return {"error": str(e)}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": "Unable to connect to the database"}, 500

def get_max_comment_id(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(comment_id) FROM `Comment`")
    result = cursor.fetchone()
    max_id = result[0] if result[0] is not None else 0
    cursor.close()
    return max_id

@user_ns.route('/comment')
class Comment(Resource):
    @user_ns.expect(comment_parser)
    def post(self):
        '''留言'''
        args = comment_parser.parse_args()
        User_ID = args['User_ID']
        Hairsalon_ID = args['Hairsalon_ID']
        Comment = args['Comment']
        Score = args['Score']

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                new_comment_id = get_max_comment_id(connection) + 1
                print('new_comment_id: ' + str(new_comment_id))
                
                sql_comment = "INSERT INTO `Comment`(`comment_id`, `User_ID`, `Hairsalon_ID`, `Score`, `Comment`)VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql_comment, (new_comment_id, User_ID, Hairsalon_ID, Score, Comment))
                connection.commit()

                return {
                    "comment_id": new_comment_id
                }, 200
            except Error as e:
                return {"error": str(e)}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": "Unable to connect to the database"}, 500

def get_max_favourite_id(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(Favourite_id) FROM `Favourite`")
    result = cursor.fetchone()
    max_id = result[0] if result[0] is not None else 0
    cursor.close()
    return max_id

@user_ns.route('/favourite')
class Favourite(Resource):
    @user_ns.expect(favourite_parser)
    def post(self):
        args = favourite_parser.parse_args()
        Favourite_ID = args['Favourite_ID']
        User_ID = args['User_ID']
        Designer_ID = args['Designer_ID']
        Hairsalon_ID = args['Hairsalon_ID']

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                new_favourite_id = get_max_favourite_id(connection) + 1
                print('new_favourite_id: ' + str(new_favourite_id))
                
                sql_favourite = "INSERT INTO `Favourite`(`favourite_id`, `User_ID`, `Designer_id`, `Hairsalon_ID`)VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_favourite, (new_favourite_id, User_ID, Designer_ID, Hairsalon_ID))
                connection.commit()

                return 200
            except Error as e:
                return {"error": str(e)}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": "Unable to connect to the database"}, 500

def get_max_keyword_id(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(Keyword_id) FROM `Default_Keyword`")
    result = cursor.fetchone()
    max_id = result[0] if result[0] is not None else 0
    cursor.close()
    return max_id

@user_ns.route('/default')
class Default(Resource):
    @user_ns.expect(default_parser)
    def get(self):
        args = default_parser.parse_args()
        User_ID = args['User_ID']

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor(dictionary=True)
                
                sql_default = "SELECT Default_Keyword FROM Default_Keyword WHERE User_ID = %s"
                cursor.execute(sql_default, (User_ID,))
                default = cursor.fetchall()

                if default:
                    return default, 200
                else:
                    return {"message": "No default keywords found"}, 404
            except Error as e:
                return {"error": str(e)}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": "Unable to connect to the database"}, 500







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001, debug=True)