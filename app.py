# 初始化資料庫連線
import pymongo

# 連線到 MongoDB 雲端資料庫
from pymongo.mongo_client import MongoClient  

uri = "mongodb+srv://root:root123@mycluster.xh86oqc.mongodb.net/?retryWrites=true&w=majority&appName=MyCluster"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# 把資料放進資料庫中
db = client.member_system

# 初始化 Flask 伺服器
from flask import *

# 建立 Application 物件，可以設定靜態檔案的路徑處理
app = Flask(__name__, static_folder="public", static_url_path="/")

# 設定 Session 的密鑰
app.secret_key="any string but secret"

# 處理路由
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/member")
def member():
    if "nickname" in session:
        return render_template("member.html")
    else:
        return redirect("/")

@app.route("/error")  # /error?msg=錯誤訊息
def error():
    message = request.args.get("msg", "發生錯誤，請聯繫客服")
    return render_template("error.html", message = message)

@app.route("/signup", methods=["POST"])
def signup():
    # 從前端接收資料
    nickname = request.form["nickname"]
    email = request.form["email"]
    password = request.form["password"]
    
    # 根據接收到的資料，和資料庫互動
    collection = db.user
    
    # 檢查會員集合中是否有相同 Email 的文件資料
    result = collection.find_one({
        "email" : email
    })
    if result != None:
        return redirect("/error?msg=信箱已經被註冊")
    
    # 把資料放進資料庫，完成註冊
    collection.insert_one({
        "nickname" : nickname,
        "email" : email,
        "password" : password
    })
    return redirect("/")

@app.route("/signin", methods=["POST"])
def signin():
    # 從前端接收使用者的輸入
    email = request.form["email"]
    password = request.form["password"]
    
    # 和資料庫做互動
    collection = db.user
    # 檢查信箱密碼是否正確
    result = collection.find_one({
        "$and":[
            {"email" : email},
            {"password" : password}
        ]
    })
    # 找不到對應的資料，登入失敗，導向到錯誤頁面
    if result == None:
        return redirect("/error?msg=帳號落密碼輸入錯誤")
    # 登入成功，在 Session 紀錄會員資訊，導向到會員頁面
    session["nickname"] = result["nickname"]
    return redirect("/member")

@app.route("/signout")
def signout():
    # 移除 Session 中的會員資訊
    del session["nickname"]
    return redirect("/")

# 啟動伺服器
app.run(port=3000)