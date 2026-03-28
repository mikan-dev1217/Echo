from flask import Flask,render_template,request,redirect,session
from werkzeug.security import generate_password_hash,check_password_hash 
import sqlite3
app=Flask(__name__)
app.secret_key="secret"
def get_db():
    db=sqlite3.connect("database.db")
    db.row_factory=sqlite3.Row
    return db
@app.route("/")
def home():
    user_id=session.get("user_id")
    if not "user_id" in session:
        return redirect("/login")
    db=get_db()
    liked_posts=[]
    if user_id:
        liked_posts=db.execute(
            "SELECT post_id FROM likes WHERE user_id=?",
            (user_id,)
            ).fetchall()
    liked_posts=[lp[0] for lp in liked_posts]
    posts=db.execute("""
    SELECT posts.id,posts.content,posts.created_at,users.username,posts.user_id,posts.likes
    FROM posts
    JOIN users ON posts.user_id=users.id
    ORDER BY posts.created_at DESC
    """).fetchall()
    comments=db.execute("""
    SELECT comments.post_id,comments.content,users.username,users.id
    FROM comments
    JOIN users ON comments.user_id=users.id
    """).fetchall()
    dm_senders=db.execute("""
    SELECT DISTINCT messages.sender_id, users.username 
    FROM messages
    JOIN users ON messages.sender_id=users.id
    WHERE receiver_id=?
    """,(user_id,)).fetchall()
    db.close()
    return render_template("index.html",dm_senders=dm_senders,posts=posts,liked_posts=liked_posts,comments=comments)
@app.route("/delete/<int:post_id>",methods=["POST"])
def delete(post_id):
    db=get_db()
    db.execute(
        "DELETE FROM posts WHERE id=? AND user_id=?",
        (post_id,session["user_id"])
    )
    db.commit()
    db.close()
    return redirect("/")
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        realname=request.form["realname"]
        db=get_db()
        user=db.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        if user:
            return "そのユーザー名は使われている"
        db.execute(
            "INSERT INTO users(username,password,realname)VALUES(?,?,?)",
            (username,generate_password_hash(password),realname)
        )
        db.commit()
        db.close()
        return redirect("/login")
    return render_template("register.html")
@app.route("/follow/<int:user_id>",methods=["POST"])
def follow(user_id):
    if "user_id" not in session:
        return redirect ("/register")
    me=session["user_id"]
    db=get_db()
    db.execute(
        "INSERT INTO follows(follow_id,following_id) VALUES(?,?)",
        (me,user_id)
    )
    db.commit()
    db.close()
    return redirect("/")
@app.route("/messages/send/<int:user_id>",methods=["POST"])
def send_message(user_id):
    if "user_id" not in session:
        return redirect ("/register")
    sender_id=session["user_id"]
    content=request.form["content"]
    db=get_db()
    db.execute(
        "INSERT INTO messages(sender_id,content,receiver_id) VALUES(?,?,?)",
        (sender_id,content,user_id)
    )
    db.commit()
    db.close()
    return redirect(f"/messages/{user_id}")
@app.route("/messages")
def messages():
    if "user_id" not in session:
        return redirect("/register")
    me=session["user_id"]
    db=get_db()
    talks=db.execute("""
        SELECT 
            CASE WHEN sender_id=? THEN receiver_id ELSE sender_id END as partner_id,
            users.username as partner_name,
            MAX(messages.created_at) as last_time,
            SUM(CASE WHEN is_read=0 AND receiver_id=? THEN 1 ELSE 0 END) as unread
        FROM messages
        JOIN users ON users.id=CASE WHEN sender_id=? THEN receiver_id ELSE sender_id END
        WHERE sender_id=? OR receiver_id=?
        GROUP BY partner_id
        ORDER BY last_time DESC
    """,(me,me,me,me,me)).fetchall()
    db.close()
    return render_template("messages.html",talks=talks)
@app.route("/messages/<int:user_id>")
def talking(user_id):
    if "user_id" not in session:
        return redirect("/register")
    sender_id=session["user_id"]
    db=get_db()
    messages=db.execute("""
        SELECT messages.content,messages.created_at,messages.sender_id,messages.receiver_id,
        users.username
        FROM messages
        JOIN users ON messages.sender_id=users.id
        WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)
        ORDER BY messages.created_at ASC
    """,(sender_id,user_id,user_id,sender_id)).fetchall()
    db.execute(
    "UPDATE messages SET is_read=1 WHERE sender_id=? AND receiver_id=?",
    (user_id, sender_id)
    )
    db.commit()
    db.close()
    return render_template("talking.html",messages=messages,user_id=user_id)
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        db=get_db()
        user=db.execute(
            "SELECT id, password FROM users WHERE username=?",
            (username,)
        ).fetchone()
        db.close()
        if user and check_password_hash(user["password"],password):
            session["user_id"]=user[0]
            return redirect("/")
        if not user:
            return redirect("/register")
    return render_template("login.html")
@app.route("/logout",methods=["POST"])
def logout():
    db=get_db()
    user_id=session["user_id"]
    session.clear()
    return render_template("logouted.html")
@app.route("/like/<int:post_id>",methods=["POST"])
def like(post_id):
    if "user_id" not in session:
        return redirect("/register")
    user_id=session["user_id"]
    db=get_db()
    existing=db.execute(
        "SELECT * FROM likes WHERE user_id=? AND post_id=?",
        (user_id,post_id)
    ).fetchone()
    if existing:
        db.execute(
            "DELETE FROM likes WHERE user_id=? AND post_id=?",
            (user_id,post_id)
        )
        db.execute(
            "UPDATE posts SET likes=likes-1 WHERE id=?",
            (post_id,)
        )
    if not existing:
        db.execute(
            "INSERT INTO likes (user_id,post_id)VALUES (?,?)",
            (user_id,post_id)
        )
        db.execute(
            "UPDATE posts SET likes=likes+1 WHERE id=?",
            (post_id,)
        )
    db.commit()
    db.close()
    return redirect("/")
@app.route("/comment/<int:post_id>",methods=["POST"])
def comment(post_id):
    if "user_id" not in session:
        return redirect("/register")
    user_id=session["user_id"]
    content=request.form["content"]
    db=get_db()
    db.execute(
        "INSERT INTO comments(post_id,user_id,content)VALUES(?,?,?)",
        (post_id,user_id,content)
    )
    db.commit()
    db.close()
    return redirect("/")
@app.route("/unfollow/<int:user_id>",methods=["POST"])
def unfollow(user_id):
    if "user_id" not in session:
        return redirect("/register")
    me=session["user_id"]
    db=get_db()
    db.execute(
        "DELETE FROM follows WHERE follow_id=? AND following_id=?",
        (me,user_id)
    )
    db.commit()
    db.close()
    return redirect("/")
@app.route("/user/<int:user_id>")
def profile(user_id):
    db = get_db()
    user = db.execute(
        "SELECT id,username FROM users WHERE id=?", 
        (user_id,)
    ).fetchone()
    posts = db.execute(
        "SELECT content, created_at FROM posts WHERE user_id=? ORDER BY created_at DESC", 
        (user_id,)
    ).fetchall()
    is_following=db.execute(
        "SELECT * FROM follows WHERE follow_id=? AND following_id=?",
        (session.get("user_id"),user_id)
    ).fetchone()
    db.close()
    return render_template("profile.html",is_following=is_following, user=user, posts=posts,user_id=user_id)
@app.route("/edit_profile",methods=["GET","POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect("/register")
    db=get_db()
    user_id=session["user_id"]
    if request.method=="POST":
        new_name=request.form["username"]
        existing=db.execute(
            "SELECT * FROM users WHERE username=? AND id!=?",
            (new_name,user_id)
        ).fetchone()
        if existing:
            db.close()
            return "そのユーザー名は使われている"
        db.execute(
            "UPDATE users SET username=? WHERE id=?",
            (new_name,user_id)
        )
        db.commit()
        db.close()
        return redirect(f"/user/{user_id}")
    user=db.execute(
        "SELECT username FROM users WHERE id=?",
        (user_id,)
    ).fetchone()
    db.close()
    return render_template("edit_profile.html",user=user)
@app.route("/search")
def search():
    if "user_id" not in session:
        return redirect("/register")
    query=request.args.get("q","")
    user_id=session.get("user_id")
    db=get_db()
    users=db.execute(
        "SELECT id,username FROM users WHERE username LIKE ?",
        (f"%{query}%",)
    ).fetchall()
    search_posts=db.execute(
        """SELECT posts.id,posts.content,posts.created_at,users.username,posts.user_id
        FROM posts
        JOIN users ON posts.user_id=users.id
        WHERE posts.content LIKE ?
        ORDER BY posts.created_at DESC""",
        (f"%{query}%",)
    ).fetchall()
    liked_posts=db.execute(
        "SELECT post_id FROM likes WHERE user_id=?",
        (user_id,)
    ).fetchall()
    liked_posts=[lp[0] for lp in liked_posts]
    posts=db.execute("""
    SELECT posts.id,posts.content,posts.created_at,users.username,posts.user_id,posts.likes
    FROM posts
    JOIN users ON posts.user_id=users.id
    ORDER BY posts.created_at DESC
    """).fetchall()
    comments=db.execute("""
    SELECT comments.post_id,comments.content,users.username,users.id
    FROM comments
    JOIN users ON comments.user_id=users.id
    """).fetchall()
    db.close()
    return render_template("index.html",posts=posts,liked_posts=liked_posts,
    comments=comments,users=users,search_posts=search_posts,query=query)
@app.route("/post",methods=["POST"])
def post():
    if "user_id" not in session:
        return redirect("/register")
    text=request.form["content"]
    db=get_db()
    db.execute(
        "INSERT INTO posts(content,user_id)VALUES(?,?)",
        (text,session["user_id"])
    )
    db.commit()
    db.close()
    return redirect("/")
app.run(debug=True)