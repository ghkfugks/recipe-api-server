from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector


### API 를 만들기 위한 클래스 작성
### class(클래스) 란 변수와 함수로 구성된 묶음 !
### 클래스는 상속이 가능하다.
### API를 만들기 위한 클래스는 flask_restful 라이브러리의
### Resource 클래스를 상속해서 만들어야 한다.

class RecipeListResource(Resource) :
    # restful api 의 method 에 해당하는 함수 작성

    @jwt_required()
    def post(self) :
        # api 실행 코드를 여기에 작성
        
        # 클라이언트에서 body 부분에 작성한 json을 
        # 받아오는 코드
        data = request.get_json()

        user_id = get_jwt_identity()


        # 받아온 데이터를 디비 저장하면 된다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''insert into recipe
                    (name, description, cook_time, directions , user_id)
                    values
                    (%s, %s, %s, %s , %s);'''
                    
            # recode 는 튜플 형태로 만든다.
            recode = (data['name'], data['description'], data['cook_time'], data['directions'], user_id)

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, recode)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        # 숫자는 HTTPStatus 번호이다.
        return {"result" : "success"}, 200
    
    def get(self) :
        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리해준다.
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        # 디비로부터 데이터를 받아서, 클라이언트에 보내준다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''select * 
                        from recipe
                        where is_publish = 1
                        limit;''' +offset+''','''+limit+''';'''              

            # 3. 커서를 가져온다.
            # select를 할 때는 dictionary = True로 설정한다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query)

            # 5. select 문은, 아래 함수를 이용해서, 데이터를 받아온다.
            result_list = cursor.fetchall()

            print(result_list)
            
            # 중요! 디비에서 가져온 timstamp는 
            # 파이썬의 datetime 으로 자동 변경된다.
            # 문제는 이 데이터를 json으로 바로 보낼 수 없으므로,
            # 문자열로 바꿔서 다시 저장해서 보낸다.
            i=0
            for record in result_list :
                result_list[i]['created_at'] = record['created_at'].isoformat()
                result_list[i]['d_at'] = record['d_at'].isoformat()
                i = i+1
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
            "count" : len(result_list),
            "result_list" : result_list}, 200
        