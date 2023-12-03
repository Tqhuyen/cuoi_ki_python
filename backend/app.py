
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO
from threading import Lock
import pandas as pd
allow_ip = []
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode="threading")


from transformers import pipeline
model_checkpoint = "nguyenvulebinh/vi-mrc-base"
nlp = pipeline('question-answering', model=model_checkpoint,
                   tokenizer=model_checkpoint, device="cuda:0")

context = '''
Đại học Bách Khoa Đà Nẵng được đánh giá nằm trong TOP 4 trường Đại học Việt Nam lần đầu tiên đạt chuẩn quốc tế về chất lượng đào tạo và nghiên cứu được ghi nhận do Hội đồng cấp cao đánh giá nghiên cứu và giáo dục đại học Châu Âu. Những năm gần đây, DUT đào tạo ra không ít  kỹ sư, cán bộ tài năng, gương mẫu cho tổ quốc.
Trường Đại học Bách khoa - Đại học Đà Nẵng công bố điểm chuẩn trúng tuyển có điều kiện theo phương thức xét tuyển học bạ.

Nhà trường lưu ý, thí sinh cần đăng ký ngành/chuyên ngành với tổ hợp trúng tuyển có điều kiện ở trên vào Hệ thống tuyển sinh của Bộ Giáo dục và Đào tạo để được xét trúng tuyển chính thức.

Thí sinh chỉ trúng tuyển chính thức khi có đồng thời 3 điều kiện sau:

Điều kiện 1: Tốt nghiệp THPT.

Điều kiện 2: Đăng ký ngành/chuyên ngành với tổ hợp trúng tuyển có điều kiện ở trên vào Hệ thống.

Điều kiện 3: Ngành/chuyên ngành trúng tuyển có điều kiện ở trên là nguyện vọng cao nhất trong số các nguyện vọng đủ điều kiện trúng tuyển thí sinh đã đăng ký vào Hệ thống.


'''





## If we wanted to create a new websocket endpoint,
## use this decorator, passing in the name of the
## event we wish to listen out for
@socketio.on('message')
def print_message(message):
    ## When we receive a new event of type
    ## 'message' through a socket.io connection
    ## we print the socket ID and the message
    # print("Socket ID: " , sid)
    print(message)
    
@socketio.on('auth')
def authentication(data):
    db_user = pd.read_csv("username.csv", index_col=None)
    print(request.remote_addr)
    if request.remote_addr in db_user["ip"].values:
        print("ok")
        res = db_user[db_user["ip"] == request.remote_addr][["name","username"]]
        username = res["username"].values[0]
        name = res["name"].values[0]
        response = {
            "status": 200,
            "data" : {
                "name": name,
                "email": username
            }
        }
        
    else:
        print("not ok")
        response = {
            "status": 201
        }
    socketio.emit('auth', response)
        
        
@socketio.on('logout')
def logout(data):
    print("logging out")
    db_user = pd.read_csv("username.csv", index_col=None)
    print(db_user.head())
    print(request.remote_addr)
    if request.remote_addr in db_user["ip"].values:
        print(db_user[db_user["ip"] == request.remote_addr].head())
        res = db_user[db_user["ip"] == request.remote_addr][["name","username"]]
        username = res["username"].values[0]
        name = res["name"].values[0]
        db_user["ip"].replace(request.remote_addr, 1, inplace=True)
        print(db_user.head())
        response = {
            "status": 200,
            "data" : {
                "name": name,
                "email": username
            }
        }
        
    else:
        response = {
            "status": 201
        }
    db_user.to_csv("username.csv", index=False)
    socketio.emit('logout', response)
        
@socketio.on("login")
def login(data):
    db_user = pd.read_csv("username.csv", index_col=None)
    request.remote_addr
    if data["username"] in db_user["username"].values:
        print(db_user.loc[db_user["username"] == data["username"], "password"].values[0])
        if data["password"] == str(db_user.loc[db_user["username"] == data["username"], "password"].values[0]):
            print("login sucess")
            print(request.remote_addr)
            allow_ip.append(request.remote_addr)
            response = {
                "status": 200,
                "data" : {
                    "name": data["username"],
                    "email": data["password"]
                }
            }
            print(response)
        else:
            response = {
                "status": 404
            }
    else:
        response = {
            "status": 404
        }
        print(response)
    socketio.emit("login", response)
    print(data)
    
    
    
@socketio.on("signup")
def signup(data):
    db_user = pd.read_csv("username.csv", index_col=None)
    print(db_user)
    print(data)
    name = data["name"]
    username = data["username"]
    password = data["password"]
    confirm_password = data["password"]
    new_user = pd.DataFrame({"name":[name] ,"username":[username], "password": [password], "ip":[request.remote_addr]})
    if password == confirm_password:
        db_user = pd.concat([db_user, new_user], ignore_index=True)
        response = {
            "status": 200,
            "data": {
                "name": name,
                "email": username
            }
        }
    else:
        response = {
            "status": 404
        }
    print(response)
    socketio.emit("signup", response)
    print(db_user)
    db_user.to_csv("username.csv", index=False)
    
@socketio.on("chat")
def chat(data):
    question = data["message"]
    QA_input = {
    'question': f"{question}?",
    'context': f"{context}"
    }
    res = nlp(QA_input)
    ans = res["answer"]
    print(ans)
    response = {
        "status": 200,
        "data" : {
            "chats": ans
        }
    }
    socketio.emit("chat", response)

        
@app.route("/")
def main():
    return render_template("index.html")


if __name__ == '__main__':
  socketio.run(app, port=6968, debug=True, host="0.0.0.0")