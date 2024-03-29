from flask import *
import pymysql
import re

app = Flask("ToDO", static_url_path='/static')  # static 폴더 참조
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'private-key'

rooms = []

@app.route('/', methods=["post", "get"])
def mainpage():
    login = False
    if (session.get('user') != None):
        login = True

    print(login)
    # room search
    word = request.form.get("roomsearch")
    roomtitle = request.form.get("roomtitle")
    print(word)
    if word != None:
        return render_template("main.html", login=login, roomList=searchByWord(word))
    # create room
    if roomtitle is not None and roomtitle != '':
        host = session['user']
        addRoom(host, roomtitle)
        return redirect(url_for('mainpage'))

    return render_template("main.html", login=login,
                           roomList=selectroom())


# ID, PWD를 POST로 받아와서 DB 데이터와 대조
@app.route('/login', methods=["post", "get"])
def loginpage():
    Error = None
    id = request.form.get('id')  # 초기값 = None
    pwd = request.form.get('pwd')
    db_cnt = db_count()[0]['COUNT(*)']
    db = select()
    if id != None and pwd != None:
        for count in range(db_cnt):
            # id not exist error
            Error = "ID does not exist"
            if id not in db[count]['ID']: pass
            # password diff error
            elif db[count]['PWD'] != pwd:
                Error = "Password does not match"; break
            # login success
            else:
                session['user'] = db[count]['ID']
                login = True
                return render_template("main.html",login=login, roomList=selectroom())
    return render_template("login.html", Error=Error)

@app.route('/logout', methods=["get"])
def log_out():
    session.pop('user', None)
    return redirect(url_for('mainpage'))

@app.route('/signin', methods=["post", "get"])
def sign_in_page():
    id = request.form.get('id')

    # 아이디 사용가능
    pwd = request.form.get('pwd')
    # name = request.form.get('name')

    print(id == None,'아이디 출력')
    if id != None:
        if(sign_idCheck(id)):  # 아이디 중복체크
            insert(id, pwd)
            return redirect('/login')
    return render_template('signin.html')


# {/id={room.id}}
@app.route('/todolist')
def todopage():
    return render_template("todolist.html")

@app.route('/emailCheck', methods=['POST'])  
def emailCheck():
    # data를 기준으로 데이터베이스에  있는지 확인 후 있으면 response에 false, 없으면 true
    data = request.get_json()
    id = data['email']
    global response
    response = 'true' # js로 넘어갈 값이기 때문에 소문자 true반환

    response = emailTypeCheck(id) # 정규식 체크
    response = email_idCheck(id) # id중복체크

    return jsonify(ok = response)

@app.route('/tododist/<roomId>')
def loadRoom(roomId):
    if (session.get('user') == None):
        redirect('/login')
    user = session['user']
    roomName = selectroomname(roomId)
    return render_template('room.html',name=user, roomId=roomId, roomName=roomName)

def searchByWord(word):
    word = word.lower()
    results = []
    for room in selectroom():
        if word in room['title'].lower():
            results.append(room)
    return results


########### connect DB
conn = pymysql.connect(
    user='root',
    passwd='jj123100!!',
    # passwd='5180',
    host='app_mysql',
    #host='127.0.0.1',
    db='todolist',
    charset='utf8',
)
# default는 tuple, Dictcurser는 dict
def curs():
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    return cursor


def select():
    cursor=curs()
    sql = "SELECT * FROM `member`;"
    cursor.execute(sql)  # send query
    result = cursor.fetchall()  # get result
    conn.close()
    return result


def selectroom():
    cursor=curs()
    sql = "SELECT * FROM `roomlist`;"
    cursor.execute(sql)  # send query
    result = cursor.fetchall()  # get result
    conn.close()
    return result

def selectroomname(rno):
    cursor=curs()
    sql = f"SELECT title FROM `roomlist` WHERE rno={rno};"
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.close()
    return result


def insert(id, pwd):
    cursor=curs()
    sql = f"INSERT INTO `member`(ID, PWD) VALUES ('{id}', '{pwd}');"
    cursor.execute(sql)
    todo_db.commit()
    conn.close()


def addRoom(host, title):
    cursor=curs()
    sql = f"INSERT INTO roomlist(host, title) VALUES ('{host}', '{title}');"
    cursor.execute(sql)
    todo_db.commit()
    conn.close()


def db_count():
    cursor=curs()
    sql = "SELECT COUNT(*) FROM `member`;"
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    return result


def db_get_id():
    cursor=curs()
    sql = "SELECT ID FROM `member`;"
    cursor.execute(sql)
    m_id = cursor.fetchall()
    conn.close()
    return m_id
  

def emailTypeCheck(id):  # 정규식 체크
    p = re.compile('/^[가-힣a-zA-Z0-9]+$/')  # 이메일 정규식
    reg = p.match(id) != None
    if (reg == False):
        response = 'false'
        return response


def email_idCheck(id):
    cursor=curs()
    sql = f"SELECT id FROM `member` WHERE id = '{id}';"
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.close()
    if (result != None):
        response = 'false'
        return response
    else:
        response = 'true'
        return response


def sign_idCheck(id):
    cursor=curs()
    sql = f"SELECT ID FROM `member` WHERE ID = '{id}';"
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.close()
    if (result != None):  # 아이디가 존재하면
        return False
    else:
        return True


def todoList(methods=['GET', 'POST']):
    print('message wa received!!!')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
