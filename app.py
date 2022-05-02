from flask import Flask,render_template, request, redirect, url_for, session 
from flask_mysqldb import MySQL,MySQLdb
from os import path 
from notifypy import Notify

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

@app.route('/login', methods= ["GET", "POST"])
def login():

    notificacion = Notify()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cur.fetchone()
        cur.close()

        if len(user)>0:
            if password == user["password"]:
                session['name'] = user['name']
                session['email'] = user['email']
                session['rol'] = user['id_rol']

                if session['rol'] == 1:
                    return render_template("profesor/home.html")
                elif session['rol'] == 2:
                    return render_template("alumno/home2.html")

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

if __name__ == '__main__':
  app.secret_key = "Delfin22"
  app.run(debug=True)