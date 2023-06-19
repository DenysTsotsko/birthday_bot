import sqlite3
import datetime
import main


from main import dp


async def db_start():
    global db, cur

    db = sqlite3.connect('server.db')
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        chat_id INTEGER,
        user_name TEXT,
        dates INTEGER 
    )""")
    db.commit()


async def create_profile(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO users (chat_id, user_name, dates) VALUES(?, ?, ?)", (data['chat_id'], data['user_name'], data['dates']))
        db.commit()


async def delete_birthday(user_name: str):
    cur.execute("DELETE FROM users WHERE user_name = ?", (user_name,))
    db.commit()


async def date_check():
    now = datetime.datetime.now()
    for i in cur.execute(f"SELECT chat_id, user_name FROM users WHERE dates = {now.strftime('%m/%d')}"):
        await main.bot.send_message(chat_id=i[0], text=f"{i[1]} - Happy Birthday!")
        await main.bot.send_message(chat_id='-898768618', text="hello")

    # user = cur.execute("SELECT 1 FROM users WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    # if not user:

#
# async def edit_profile(state, user_id):
#     async with state.proxy() as data:
#         cur.execute("UPDATE users SET chat_id ='{}', user_name ='{}', date_month = '{}', date_day = {} WHERE user_id == '{}' ".format(
#             data['chat_id'], data['user_name'], data['date_month'], data['date_day'], user_id))
#         db.commit()
#
# # async def edit_profile(state, user_id):





# class Database:
#     def __init__(self, db_file):
#         self.connection = sqlite3.connect(db_file)
#         self.cursor = self.connection.cursor()
#
#     def user_exists(self, user_id):
#         with self.connection:
#             result = self.cursor.execute("SELECT * FROM 'users' WHERE 'user_id' = ?", (user_id,)).fetchall()
#             return bool(len(result))
#
#     def add_user(self, user_id):
#         with self.connection: # connection into db
#             return self.connection.execute("INSERT INTO 'users' ('user_id') VALUES (?)", (user_id,))

# async def db_start():
#     global db, cur
#
#     db = sq.connect('info.db')
#     cur = db.cursor()
#
#     cur.execute("CREATE TABLE IF NOT EXISTS profile(user_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date INTEGER)")
#
#     db.commit()
#
#
# async def create_profile(user_id):
#     user = cur.execute("SELECT 1 FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()
#     if not user:
#         cur.execute("INSERT INTO profile VALUES(?, ?, ?)", (user_id, '', ''))
#         db.commit()