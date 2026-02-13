import time
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import psycopg2

app = FastAPI()

DB_HOST = "db"
DB_NAME = "testdb"
DB_USER = "user"
DB_PASS = "password"


def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            conn.close()
            print("Database is ready!")
            break
        except psycopg2.OperationalError:
            print("Database not ready, waiting...")
            time.sleep(2)


@app.on_event("startup")
def startup():
    wait_for_db()

    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.get("/health")
def health():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        conn.close()
        return {"status": "healthy"}
    except:
        return {"status": "unhealthy"}


@app.get("/", response_class=HTMLResponse)
def home():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    cur.close()
    conn.close()

    user_list_html = ""
    for user in users:
        user_list_html += f"<li>{user[1]} - {user[2]}</li>"

    return f"""
    <html>
        <head>
            <title>Simple Docker App</title>
        </head>
        <body>
            <h1>Добавить пользователя</h1>
            <form action="/users" method="post">
                <label>Имя:</label><br>
                <input type="text" name="name"><br><br>

                <label>Email:</label><br>
                <input type="text" name="email"><br><br>

                <button type="submit">Добавить</button>
            </form>

            <h2>Список пользователей:</h2>
            <ul>
                {user_list_html}
            </ul>
        </body>
    </html>
    """


@app.post("/users")
def add_user(name: str = Form(...), email: str = Form(...)):
    print(f"New user added: {name}, {email}")
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s);",
        (name, email)
    )
    conn.commit()
    cur.close()
    conn.close()

    return HTMLResponse(
        content="""
        <html>
            <body>
                <h3>Пользователь добавлен!</h3>
                <a href="/">Вернуться назад</a>
            </body>
        </html>
        """
    )
