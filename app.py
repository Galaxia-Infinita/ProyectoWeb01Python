import os
from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory

app=Flask(__name__)
app.secret_key="develoteca"
#variable de conexion y credenciales
mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_PORT'] = 3307
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='pythonweblibrosdb'
mysql.init_app(app)
#/

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

#para obtener url de imagen de carpeta img y poder mostrarla en tabla
@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'), imagen)

#para usar tema bootswatch descargado de la web(tema vapor)
@app.route('/css/<archivocss>')
def css_link(archivocss):
    return send_from_directory(os.path.join("templates/sitio/css"),archivocss)

#para usar tema bootswatch descargado de la web(tema vapor en administrador)
@app.route('/css/<archivocss2>')
def css_link2(archivocss2):
    return send_from_directory(os.path.join("templates/admin/css"),archivocss2)

@app.route('/libros')
def libros():
    conexion= mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros`") #consultando libros
    libros=cursor.fetchall() #almacenando libros
    conexion.commit()

    return render_template('sitio/libros.html', libros=libros)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    #restringe acceso si no se ha iniciado sesion
    if not 'login' in session:
        return redirect("/admin/login")
    #
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

#login que valida (inicio sesion), el otro solo redirecciona
@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    print(_usuario)
    print(_password)

    if _usuario=="admin" and _password=="123":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template("admin/login.html", mensaje="Acceso denegado")

#cerrar sesion
@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')

#obteniendo datos de DB y mostrando en tabla bootstrap
@app.route('/admin/libros')
def admin_libros():
    #restringe acceso si no se ha iniciado sesion
    if not 'login' in session:
        return redirect("/admin/login")
    #
    
    conexion= mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()
    print(libros)

    return render_template("admin/libros.html", libros=libros)

#metodo post
@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():
    #restringe acceso si no se ha iniciado sesion
    if not 'login' in session:
        return redirect("/admin/login")
    #

    #recuperando valores del formulario
    _nombre= request.form['txtNombre']
    _url=request.form['txtURL']
    _archivo=request.files['txtImagen']

    #variables para controlar tiempo para adjuntar archivos
    tiempo=datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')

    #creando variable que dará nuevo nombre al archivo(img)
    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)

    sql="INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL, %s, %s, %s);"
    datos=(_nombre,nuevoNombre,_url)

    conexion= mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    print(_nombre)
    print(_url)
    print(_archivo)
    
    return redirect('/admin/libros')

#eliminar registros
@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar():
    #restringe acceso si no se ha iniciado sesion
    if not 'login' in session:
        return redirect("/admin/login")
    #

    _id=request.form['txtID']
    print(_id)

    conexion= mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT imagen FROM `libros` WHERE id=%s",(_id))
    libro=cursor.fetchall()
    conexion.commit()
    print(libro)

    #para borrar imagen de carpeta img ademas de la db
    if os.path.exists("templates/sitio/img/"+str(libro[0][0])):
        os.unlink("templates/sitio/img/"+str(libro[0][0]))
    #

    conexion= mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id=%s",(_id))
    conexion.commit()

    return redirect('/admin/libros')


if __name__=='__main__':
    app.run(debug=True)