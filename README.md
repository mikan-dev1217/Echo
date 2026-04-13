[README.md](https://github.com/user-attachments/files/26654024/README.md)
# 📢 Echo
**諫早高校附属中学校 学年専用SNS**

> 招待制・学年限定のクローズドSNS。部活、勉強、雑談をトピック別に投稿できる。

---

## 🚀 機能一覧

### 投稿・コミュニケーション
- 投稿・削除
- コメント
- いいね（トグル式）
- トピック別スレッド（部活 / 勉強 / 雑談）

### ユーザー
- 招待コード制登録
- ログイン・ログアウト
- プロフィール・アイコン編集
- フォロー・フォロワー

### メッセージ
- ダイレクトメッセージ（DM）
- 未読バッジ表示

### 通知
- いいね・コメント・DMの通知

### 管理者機能
- ユーザー一覧（本名確認）
- 招待コード発行
- NGワードフィルター（自動***置換）

---

## 🛠️ 使用技術

| 項目 | 技術 |
|------|------|
| バックエンド | Python / Flask |
| データベース | SQLite |
| フロントエンド | HTML / CSS / JavaScript |
| 認証 | werkzeug（パスワードハッシュ化） |

---

## ⚙️ セットアップ

### 1. 必要なライブラリをインストール
```bash
pip install flask werkzeug
```

### 2. DBを初期化
```bash
python init_db.py
```

### 3. 管理者アカウントを設定
```bash
python -c "import sqlite3; db=sqlite3.connect('database.db'); db.execute('UPDATE users SET is_admin=1 WHERE username=?',('ユーザー名',)); db.commit(); db.close()"
```

### 4. サーバー起動
```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセス。

---

## 🗄️ DB設計

| テーブル | 説明 |
|---------|------|
| users | ユーザー情報（username, password, realname, icon, is_admin） |
| posts | 投稿（content, topic, likes, user_id） |
| comments | コメント（post_id, user_id, content） |
| likes | いいね（user_id, post_id） |
| follows | フォロー関係（follow_id, following_id） |
| messages | DM（sender_id, receiver_id, content, is_read） |
| notices | 通知（user_id, type, from_user_id, is_read） |
| invite_codes | 招待コード（code, is_used, used_by） |
| ng_words | NGワード一覧（word） |

---

## 🔒 セキュリティ
- パスワードはハッシュ化して保存（werkzeug）
- 招待コード制による登録制限
- サーバー側でフォロー・アンフォローの本人チェック
- 環境変数による`SECRET_KEY`管理

---

## 👤 開発者
**wataru shiraishi** - 諫早高校附属中学校 2年生

> プログラミング歴1ヶ月半で開発。
