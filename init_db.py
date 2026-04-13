import sqlite3
from werkzeug.security import generate_password_hash

db = sqlite3.connect("database.db")
db.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    realname TEXT
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS invite_codes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    is_used INTEGER DEFAULT 0,
    used_by INTEGER
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS posts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT (DATETIME('now','localtime'))
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS ng_words(
           id INTEGEr PRIMARY KEY AUTOINCREMENT,
           word TEXT
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS comments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    post_id INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT (DATETIME('now','localtime'))
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    post_id INTEGER
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS follows(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    follow_id INTEGER,
    following_id INTEGER
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER,
    receiver_id INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT (DATETIME('now','localtime'))
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS notices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    post_id INTEGER,
    from_user_id INTEGER,
    is_read INTEGER DEFAULT 0,
    created_At TIMESTAMP DEFAULT (DATETIME('now','localtime'))
)
""")

try:
    db.execute("ALTER TABLE posts ADD COLUMN likes INTEGER DEFAULT 0;")
except sqlite3.OperationalError:
    print("postsテーブルにlikesカラムはすでにあるのでスキップしました")

try:
    db.execute("ALTER TABLE comments ADD COLUMN likes INTEGER DEFAULT 0;")
except sqlite3.OperationalError:
    print("commentsテーブルにlikesカラムはすでにあるのでスキップしました")
try:
    db.execute("ALTER TABLE posts ADD COLUMN topic TEXT DEFAULT 'general'")
except sqlite3.OperationalError:
    print("postsテーブルにtopicカラムはすでにあるのでスキップしました")
try:
    db.execute("ALTER TABLE messages ADD COLUMN is_read INTEGER DEFAULT 0;")
except sqlite3.OperationalError:
    print("messagesテーブルにis_readカラムはすでにあるのでスキップしました")
try:
    db.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;")
except sqlite3.OperationalError:
    print("すでにあるのでスキップ")
try:
    db.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0;")
except sqlite3.OperationalError:
    print("usersテーブルにis_bannedカラムはすでにあるのでスキップしました")
try:
    db.execute("ALTER TABLE users ADD COLUMN icon TEXT;")
except sqlite3.OperationalError:
    print("usersテーブルにiconカラムはすでにあるのでスキップしました")
db.commit()

# 初期管理者ユーザーを作成
try:
    db.execute(
        "INSERT INTO users(username, password, realname, is_admin) VALUES(?, ?, ?, ?)",
        ("admin", generate_password_hash("admin123"), "管理者", 1)
    )
    db.commit()
    print("初期管理者ユーザーを作成しました (username: admin, password: admin123)")
except sqlite3.IntegrityError:
    print("初期管理者ユーザーはすでに存在します")

# 初期招待コードを作成
try:
    db.execute(
        "INSERT INTO invite_codes(code, is_used) VALUES(?, ?)",
        ("INVITE001", 0)
    )
    db.commit()
    print("初期招待コード INVITE001 を作成しました")
except sqlite3.IntegrityError:
    print("初期招待コードはすでに存在します")

db.close()
print("DBの準備が完了しました！")