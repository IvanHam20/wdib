from flask import Flask,render_template, request, redirect, url_for, session 
from flask_mysqldb import MySQL,MySQLdb
from os import path 
from notifypy import Notify
import re

regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'wdib'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template("contenido.html")

@app.route('/layout', methods = ["GET", "POST"])
def layout():
    session.clear()
    return render_template("contenido.html")

@app.route('/registro', methods = ["GET", "POST"])
def registro():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM rol")
    rol = cur.fetchall()

    cur.close()

    notificacion = Notify()
    
    if request.method == 'GET':
        return render_template("registro.html", rol = rol)
    
    else:
        name = request.form['name']
        email = request.form['email']
        tipo = request.form['rol']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, id_rol, password) VALUES (%s,%s,%s,%s)", (name, email, tipo,password))
        mysql.connection.commit()
        notificacion.title = "Registro Exitoso"
        notificacion.message="Ya te encuentras registrado!!"
        notificacion.send()
        return redirect(url_for('login'))

@app.route('/materiales', methods = ["GET", "POST"])
def materiales():
    if request.method == "GET":
        materiales_id = request.args.get("id")
        print(materiales_id)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM materiales WHERE id_practica = (%s)", (materiales_id,))
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template("materiales.html", materiales=data, practica_id=materiales_id, rol=session["rol"])
    else:
        material = request.form['material']
        cantidad = request.form['cantidad']
        id_practica = request.args.get("id")

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO materiales (material, cantidad, id_practica) VALUES (%s,%s,%s)", (material,cantidad,id_practica))
        mysql.connection.commit()
        cur.close()

        notificacion = Notify()        
        notificacion.title = "Se agrego correctamente"
        notificacion.send()
        return redirect(f"/materiales?id={id_practica}")

@app.route('/home', methods= ["GET", "POST"])
def practicas():
    if request.method == "GET":
        cur = mysql.connection.cursor()
        query = "SELECT * FROM nombre_practicas WHERE id_maestro = (%s)"
        cur.execute(query, (session["id"],))
        data = cur.fetchall()
        cur.close()
        return render_template("profesor/home.html", practicas=data)
    else:    
        nombre = request.form['data']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO nombre_practicas (name, id_maestro) VALUES (%s, %s)", (nombre, session["id"]))
        mysql.connection.commit()
        cur.close()
        return redirect('/home')
    
@app.route('/compartir', methods = ["GET", "POST"])
def compartir():
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id_rol = 2")
        data = cur.fetchall()
        cur.close()
        return render_template("listaAlumnos.html", alumnos=data, practica_id = request.args.get("id"))
    else:
        for id_alumno in request.form:
            cur = mysql.connection.cursor()
            practica_id = request.args.get("id")
            cur.execute("INSERT INTO alumno_practicas (user_id, practica_id) VALUES (%s, %s)", (id_alumno, practica_id))
            mysql.connection.commit()
            cur.close()
        return redirect("/home")

@app.route('/login', methods= ["GET", "POST"])
def login():

    notificacion = Notify()

    if request.method == 'POST':
        email = request.form['email']
        # si el regex no lo valida, enviar un mensaje de error
        if not re.fullmatch(regex, email):
            return redirect("/login")
        
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cur.fetchone()
        cur.close()

        if len(user)>0:
            if password == user["password"]:
                session['id'] = user['id']
                session['name'] = user['name']
                session['email'] = user['email']
                session['rol'] = user['id_rol']

                if session['rol'] == 1:
                    return redirect("/home")
                elif session['rol'] == 2:
                    return redirect("/home-alumno")

            else:
                notificacion.title = "Error de Acceso"
                notificacion.message="Correo o contraseña no valida"
                notificacion.send()
                return render_template("login.html")
        else:
            notificacion.title = "Error de Acceso"
            notificacion.message="No existe el usuario"
            notificacion.send()
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/home-alumno', methods=["GET", "POST"])
def home_alumno():
    if request.method == "GET":
        cur = mysql.connection.cursor()
        query = "SELECT * FROM nombre_practicas WHERE id IN(SELECT practica_id FROM alumno_practicas WHERE user_id = (%s))"
        cur.execute(query, (session["id"],))
        data = cur.fetchall()
        cur.close()
        return render_template("alumno/home2.html", practicas=data, rol=session["rol"])
    else:
        pass

if __name__ == '__main__':
  app.secret_key = "Delfin22"
  app.run(debug=True)