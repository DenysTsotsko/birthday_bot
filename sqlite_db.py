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
