from http import HTTPStatus
from flask import request
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector
from email_validator import validate_email, EmailNotValidError

from utils import check_password, hash_password


class UserRegisterResource(Resource) :
    def post(self) :
        
        # {
        #     "username": "홍길동",
        #     "email": "abc@naver.com",
        #     "password": "1234"
        # }

        # 1. 클라이언트가 body 에 보내준 json 을 받아온다.
        data = request.get_json()

        # 2. 이메일 주소 형식이 제대로 된 주소 형식인지 확인하는 코드 작성.

        try :
            validate_email(data['email'])
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'error' : str(e)} , 400 

        # 3. 비밀번호의 길이가 유효한지 체크한다
        # 비번길이는 4자리 이상 12자리 이하로만!
        if len(data['password']) < 4 or len(data['password']) > 12 :
            return {'error' : '비번길이 확인하세요'} , 400

        
        # 4. 비밀번호를 암호화 한다.
        # data['password']

        hashed_password = hash_password(data['password'])
        
        print(hashed_password)

        # 5. 데이터베이스에 회원정보를 저장한다!! 
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''insert into user
                        (username , email , password)
                        values
                        (%s  ,%s , %s) ;'''
                    
            # recode 는 튜플 형태로 만든다.
            recode = (data['username'], data['email'], hashed_password)

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, recode)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 5-1. 디비에 저장된 아이디값 가져오기.
            user_id = cursor.lastrowid

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        
        return {'result' : 'success' , 'user_id' : user_id} , 200


class UserLoginResource(Resource) :

    def post(self) :
        # 1. 클라이언트로부터 body로 넘어온 데이터를 받아온다.
        #{
        #     "email": "abc@naver.com",
        #     "password": "1234"
        # }
        data = request.get_json()

        # 2. 이메일로 DB에 이 이메일과 일치하는 데이터를 가져온다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''select * 
                        from user
                        where email = %s ;'''       
            record = (data['email'] , )       

            # 3. 커서를 가져온다.
            # select를 할 때는 dictionary = True로 설정한다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query , record)

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
                result_list[i]['created_at'] = record['updated_at'].isoformat()
                i = i+1
            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        # 3. result_list 의 행의 갯수가 1개이면
        # 유저 데이터를 정상적으로 받아온것이고
        # 행의 갯수가 0이면, 요청한 이메일은 회원가입이 
        # 되어 있지 않은 이메일이다.
        
        if len(result_list) != 1 :
            return  {'error' : '회원가입이 안된 이메일입니다.'} ,400

        
        # 4. 비밀번호가 맞는지 확인한다.
        user_info = result_list[0]

        # data['password'] 와 user_info['password'] 를 비교한다.

        check = check_password(data['password'], user_info['password'])
        
        if check == False :
            return {'error' : '비밀번호가 맞지 않습니다.'} , 400





        return  {'result' : 'success' , 'user_id' : user_info['id']} , 200

    