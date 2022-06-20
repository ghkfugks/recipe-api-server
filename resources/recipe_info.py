from http import HTTPStatus
from unittest import result
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector
from mysql_connection import get_connection

class RecipeResource(Resource) :
    # 클라이언트로부터 /recipes/3 과 같은 식의 경로를 처리하므로
    # 숫자는 바뀌므로, 변수로 처리해준다.
    def get(self, recipe_id) :


        
        # 디비에서, recipeid 에 들어있는 값에 해당되는
        # 데이터를 select 해온다.
        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리해준다.
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        # 디비로부터 데이터를 받아서, 클라이언트에 보내준다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''select * from recipe
                    where id = %s;'''                 

            record = (recipe_id, )
            # 3. 커서를 가져온다.
            # select를 할 때는 dictionary = True로 설정한다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)

            # 5. select 문은, 아래 함수를 이용해서, 데이터를 받아온다.
            result_list = cursor.fetchall()

            print(result_list)
            
            # 중요! 디비에서 가져온 timstamp는 
            # 파이썬의 datetime 으로 자동 변경된다.
            # 문제는 이 데이터를 json으로 바로 보낼 수 없으므로,
            # 문자열로 바꿔서 다시 저장해서 보낸다.

            result_list[0]['created_at'] = str(result_list[0]['created_at'])
            result_list[0]['d_at'] = str(result_list[0]['d_at'])

            # 6. 자원 해제
            cursor.close()
            connection.close()



        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        return {
            "result" : "success",
            "result_list" : result_list[0]}, 200


    # 데이터를 업데이트하는 API들은 put 함수를 사용한다.
    @jwt_required()
    def put(self,recipe_id) :
        
        # body에서 전달된 데이터를 처리
        data = request.get_json()

        user_id = get_jwt_identity()

        # 디비 업데이트 실행코드
        try :
            # 데이터 업데이트
            # 1. DB에 연결
            connection = get_connection()

            ### 먼저 recipe_id 에 들어있는 user_id 가
            ### 이 사람인지 먼저 확인한다.

            query = '''select user_id
                        from recipe
                        where id = %s'''
            record = (recipe_id , )

            cursor = connection.cursor(dictionary = True)

            cursor.execute(query , record)

            result_list = cursor.fetchall()

            recipe = result_list[0]

            if recipe['user_id'] != user_id :
                cursor.close()
                connection.close()
                return {'error' : '남의 레시피를 수정할수 없습니다.'} , 401


            # 2. 쿼리문 만들기
            query = ''' recipe
                    set name = %s,
                    description = %s, 
                    cook_time = %s, 
                    directions = %s
                    where id = %s;'''

            recode = (data['name'], data['description'],
                        data['cook_time'],data['directions'],
                        recipe_id)

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query , recode)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'error':str(e)},503

        return {'result': 'success'},200

    # 삭제하는 delete 함수 
    def delete(self,recipe_id) :

        try :
            # 데이터 삭제
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''delete from recipe
                        where id = %s ;'''

                        

            recode = (recipe_id , )

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query , recode)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'error':str(e)},503

        return {'result' : 'success'}, 200

    