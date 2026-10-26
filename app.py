import os
from functools import wraps

import pymysql
from dotenv import load_dotenv
from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-cambiar")


# ---------- Base de datos ----------
def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=(), one=False, commit=False):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params)
        if commit:
            db.commit()
            return cur.lastrowid
        return cur.fetchone() if one else cur.fetchall()


# ---------- Autenticación ----------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Inicia sesión para continuar.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirmar = request.form["confirmar"]

        if not name or not email or len(password) < 6:
            flash("Completa todos los campos. La contraseña necesita al menos 6 caracteres.", "error")
        elif password != confirmar:
            flash("Las contraseñas no coinciden.", "error")
        elif query("SELECT id FROM users WHERE email=%s", (email,), one=True):
            flash("Ya existe una cuenta con ese correo.", "error")
        else:
            query(
                "INSERT INTO users (name, email, password_hash) VALUES (%s,%s,%s)",
                (name, email, generate_password_hash(password)),
                commit=True,
            )
            flash("Cuenta creada. Ya puedes iniciar sesión.", "ok")
            return redirect(url_for("login"))
    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = query("SELECT * FROM users WHERE email=%s", (email,), one=True)

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            siguiente = request.args.get("next", "")
            if not siguiente.startswith("/") or siguiente.startswith("//"):
                siguiente = url_for("productos")
            return redirect(siguiente)
        flash("Correo o contraseña incorrectos.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "ok")
    return redirect(url_for("index"))


# ---------- Páginas públicas ----------
@app.route("/")
def index():
    destacados = query("SELECT * FROM products ORDER BY created_at DESC LIMIT 6")
    return render_template("index.html", productos=destacados)


# ---------- CRUD de productos ----------
def leer_formulario():
    f = request.form
    try:
        price = round(float(f["price"]), 2)
        stock = int(f["stock"])
    except ValueError:
        return None, "Precio y stock deben ser números."
    if not f["name"].strip():
        return None, "El nombre es obligatorio."
    if price < 0 or stock < 0:
        return None, "Precio y stock no pueden ser negativos."
    return (f["name"].strip(), f["description"].strip(), price, stock,
            f["category"].strip()), None


@app.route("/productos")
@login_required
def productos():
    q = request.args.get("q", "").strip()
    if q:
        filas = query(
            "SELECT * FROM products WHERE name LIKE %s OR category LIKE %s ORDER BY id DESC",
            (f"%{q}%", f"%{q}%"),
        )
    else:
        filas = query("SELECT * FROM products ORDER BY id DESC")
    return render_template("productos.html", productos=filas, q=q)


@app.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def producto_nuevo():
    if request.method == "POST":
        datos, error = leer_formulario()
        if error:
            flash(error, "error")
        else:
            query(
                "INSERT INTO products (name, description, price, stock, category, created_by) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                datos + (session["user_id"],),
                commit=True,
            )
            flash("Producto creado.", "ok")
            return redirect(url_for("productos"))
    return render_template("producto_form.html", producto=request.form, editar=False)


@app.route("/productos/<int:pid>/editar", methods=["GET", "POST"])
@login_required
def producto_editar(pid):
    producto = query("SELECT * FROM products WHERE id=%s", (pid,), one=True)
    if not producto:
        flash("Ese producto no existe.", "error")
        return redirect(url_for("productos"))

    if request.method == "POST":
        datos, error = leer_formulario()
        if error:
            flash(error, "error")
            producto = {**producto, **request.form}
        else:
            query(
                "UPDATE products SET name=%s, description=%s, price=%s, stock=%s, category=%s "
                "WHERE id=%s",
                datos + (pid,),
                commit=True,
            )
            flash("Cambios guardados.", "ok")
            return redirect(url_for("productos"))
    return render_template("producto_form.html", producto=producto, editar=True)


@app.route("/productos/<int:pid>/eliminar", methods=["POST"])
@login_required
def producto_eliminar(pid):
    query("DELETE FROM products WHERE id=%s", (pid,), commit=True)
    flash("Producto eliminado.", "ok")
    return redirect(url_for("productos"))


if __name__ == "__main__":
    app.run(debug=True)
