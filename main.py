from flask import Flask, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = "minha_chave_secreta"

DATABASE = "app.db"

# ---------------------------
# Funções de banco de dados
# ---------------------------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    db.commit()

# ---------------------------
# Rotas
# ---------------------------
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("products"))
    return redirect(url_for("login"))

# Cadastro de usuário
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return """
            <h3 style="color:red;">Usuário já existe!</h3>
            <a href='/register'>Tente novamente</a>
            """
    return """
    <html>
    <head>
        <title>Cadastro</title>
        <style>
            body { font-family: Arial; background: #f4f4f9; display:flex; justify-content:center; align-items:center; height:100vh; }
            .container { background:white; padding:30px; border-radius:10px; box-shadow:0px 0px 10px #aaa; width:350px; }
            input { width:100%; padding:8px; margin:5px 0; border-radius:5px; border:1px solid #ccc; }
            input[type=submit] { background:#4CAF50; color:white; border:none; cursor:pointer; }
            a { text-decoration:none; color:#555; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Cadastro de Usuário</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Usuário" required><br>
                <input type="password" name="password" placeholder="Senha" required><br>
                <input type="submit" value="Cadastrar">
            </form>
            <p>Já tem conta? <a href="/login">Login</a></p>
        </div>
    </body>
    </html>
    """

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            session["user"] = username
            return redirect(url_for("products"))
        else:
            return """
            <h3 style="color:red;">Usuário ou senha incorretos!</h3>
            <a href='/login'>Tente novamente</a>
            """
    return """
    <html>
    <head>
        <title>Login</title>
        <style>
            body { font-family: Arial; background: #f4f4f9; display:flex; justify-content:center; align-items:center; height:100vh; }
            .container { background:white; padding:30px; border-radius:10px; box-shadow:0px 0px 10px #aaa; width:350px; }
            input { width:100%; padding:8px; margin:5px 0; border-radius:5px; border:1px solid #ccc; }
            input[type=submit] { background:#4CAF50; color:white; border:none; cursor:pointer; }
            a { text-decoration:none; color:#555; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Login</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Usuário" required><br>
                <input type="password" name="password" placeholder="Senha" required><br>
                <input type="submit" value="Login">
            </form>
            <p>Não tem conta? <a href="/register">Cadastre-se</a></p>
        </div>
    </body>
    </html>
    """

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# Cadastro de produtos
@app.route("/products", methods=["GET", "POST"])
def products():
    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        cursor.execute("INSERT INTO products (name, description) VALUES (?, ?)", (name, description))
        db.commit()
        return redirect(url_for("products"))

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    html = f"""
    <html>
    <head>
        <title>Produtos</title>
        <style>
            body {{ font-family: Arial; background: #f4f4f9; padding:20px; }}
            .top {{ display:flex; justify-content:space-between; align-items:center; }}
            .top a {{ text-decoration:none; color:white; background:#f44336; padding:5px 10px; border-radius:5px; }}
            .form-container {{ background:white; padding:20px; border-radius:10px; box-shadow:0px 0px 10px #aaa; margin-top:20px; width:400px; }}
            input {{ width:100%; padding:8px; margin:5px 0; border-radius:5px; border:1px solid #ccc; }}
            input[type=submit] {{ background:#4CAF50; color:white; border:none; cursor:pointer; }}
            ul {{ margin-top:20px; }}
            li {{ background:white; margin:5px 0; padding:10px; border-radius:5px; box-shadow:0px 0px 5px #aaa; }}
        </style>
    </head>
    <body>
        <div class="top">
            <h2>Bem-vindo, {session['user']}!</h2>
            <a href='/logout'>Logout</a>
        </div>
        <div class="form-container">
            <h3>Cadastrar Produto</h3>
            <form method="POST">
                <input type="text" name="name" placeholder="Nome do Produto" required><br>
                <input type="text" name="description" placeholder="Descrição" required><br>
                <input type="submit" value="Cadastrar Produto">
            </form>
        </div>
        <h3>Produtos Cadastrados</h3>
        <ul>
    """
    for p in products:
        html += f"<li><b>{p[1]}</b>: {p[2]}</li>"
    html += "</ul></body></html>"

    return html

# ---------------------------
# Inicializa DB e roda app
# ---------------------------
if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)