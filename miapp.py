from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector  #Conexion de base de datos
import mysql.connector.errorcode
from werkzeug.utils import secure_filename
import os
import time
app = Flask(__name__)
CORS(app)

class Catalogo:
    
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )

        self.cursor = self.conn.cursor()
        
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
                self.conn.database = database
            else:
                raise err
            
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                            codigo INT AUTO_INCREMENT PRIMARY KEY,
                            descripcion varchar(225) NOT NULL,
                            cantidad INT NOT NULL,
                            precio DECIMAL(10, 2) NOT NULL,
                            imagen_url varchar(225) NOT NULL,
                            proveedor INT(4))''')
        self.conn.commit()
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)


#Funciones para la gestion del arreglo con datos de productos.
#agregar un producto, consultando su existencia en primer lugar.
    def agregar_producto(self, descripcion, cantidad, precio, imagen, proveedor):
        '''if self.consultar_producto(codigo):
                return False'''
        sql = "INSERT INTO productos (descripcion, cantidad, precio, imagen_url, proveedor) VALUES (%s, %s, %s, %s, %s)"
        valores = (descripcion, cantidad, precio, imagen,proveedor)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.lastrowid    
#Parámetros: codigo(int), descripcion(str), cantidad(int), precio(float), imagen(str), proovedor(int).

#consultar un producto.
    def consultar_producto(self, codigo):
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
        return self.cursor.fetchone()
# La funcion comienza recorriendo la lista de productos a travez de un bucle "for" examina cada producto.
# verifica si el valor de la clave 'codigo' del diccionario coincide con el valor proporcionado por parametro.
# si se encuentra el codigo del producto solicitado la funcion retorna el diccionario que representa ese producto.
# si no se encuentra el producto deseado retorna false.

#modificar productos.
    def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor):
        sql = "UPDATE productos SET descripcion = %s, cantidad = %s, precio = %s, imagen_url = %s, proveedor = %s WHERE codigo = %s"
        valores = (nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0
# Realiza la misma tarea que consultar, recorriendo la lista de productos.
# verifica que el valor de la clave del diccionario 'codigo' coincida con el valor proporcionado en el parametro codigo.
# Se efectua la misma tarea de busqueda para determinar el producto correcto a modificar.
# Retorna true si la modificacion fue llevada a cabo con exito, y false si no se encuentra el producto deseado.

#listar productos
    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        productos = self.cursor.fetchall()
        return productos
#Separador visual (linea de "-" repetida 50 veces).
#Bucle for recorre la lista de productos, y por cada interaccion se procesa un producto e imprimen sus detalles en pantalla.
#No requiere parametros ni retorna valores.

#eliminar producto
    def eliminar_producto(self, codigo):
        self.cursor.execute(f"DELETE FROM productos WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0
            
#se pasa por parametro el codigo para identificar el producto a eliminar.
#el bucle for recorre la lista en busqueda de la coincidencia entre el valor de la clave diccionario'codigo', y el valor pasado por argumento.
#una vez hallada la coincidencia se procede a la eliminacion a travez del metodo remove.
#si se realiza la eliminacion con exito retorna true, si no se halla la coincidencia, retorna false.

#mostrar producto
    def mostrar_producto(self, codigo):
        producto = self.consultar_producto(codigo)
        if producto:
            print("-" * 40)
            print(f"Código.....:{producto['codigo']}")
            print(f"Descripción:{producto['descripcion']}")
            print(f"Cantidad...:{producto['cantidad']}")
            print(f"Precio.....:{producto['precio']}")
            print(f"Imagen.....:{producto['imagen']}")
            print(f"Proveedor..:{producto['proveedor']}")
            print("-" * 40)
        else:
            print("Producto no econtrado")



catalogo = Catalogo(host='localhost', user='root', password='', database='miapp')
ruta_destino = './static/img/'

#corroboracion de funcionamiento.
'''
#agregar producto
catalogo.agregar_producto('Teclado USB 101 teclas', 10, 4500, '', 101)
catalogo.agregar_producto('Mouse Inalambrico 3 botones', 5, 2500, '', 102)
catalogo.agregar_producto('Monitor LED', 5, 25000, '', 102)
#consultar producto
cod_prod = int(input("Ingrese el código del producto: "))
producto = catalogo.consultar_producto(cod_prod)
if producto:
    print(f"Producto encontrado: {producto['codigo']} - {producto['descripcion']}")
else:
    print(f'Producto {cod_prod} no encontrado.')
#modificar y mostrar
catalogo.mostrar_producto(1)
catalogo.modificar_producto(1, 'Teclado mecánico', 20, 34000, 'tecmec.jpg', 106)
catalogo.mostrar_producto(1)
#listar productos
productos = catalogo.listar_productos()
for producto in productos:
    print(producto)
#eliminar producto
catalogo.eliminar_producto(2)
productos = catalogo.listar_productos()
for producto in productos:
    print(producto)
'''
@app.route("/productos", methods = ["GET"])
def listar_productos():
    productos = catalogo.listar_productos()
    return jsonify(productos)
# http://localhost:5000/productos ruta de acceso por localhost
if __name__ == "__main__":
    app.run(debug=True)

@app.route("/productos/<int:codigo>", methods=["GET"])
def mostrar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto:
        return jsonify(producto), 201
    else:
        return "Producto no encontrado", 404
    
@app.route("/productos", methods=["POST"])
def agregar_producto():
    descripcion = request.form['descripcion']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    imagen = request.files['imagen']
    proveedor = request.form['proveedor']
    nombre_imagen = ""

    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"

    nuevo_codigo = catalogo.agregar_producto(descripcion, cantidad, precio, nombre_imagen, proveedor)
    if nuevo_codigo:
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        return jsonify({"mensaje": "Producto agregado correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:
        return jsonify({"mensaje": "Error al agregar producto"}), 500
    
@app.route("/productos/<int:codigo>", methods=["PUT"])
def modificar_producto(codigo):
    nueva_descripcion = request.form.get['descripcion']
    nueva_cantidad = request.form.get['cantidad']
    nuevo_precio = request.form.get['precio']
    nuevo_proveedor = request.form.get['proveedor']
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        nombre_imagen = secure_filename(imagen.filename)
        nombre_base, extension = os.path.splitext(nombre_imagen)
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
        imagen.save = os.path.join(ruta_destino, nombre_imagen)

        producto = catalogo.consultar_producto(codigo)
        if producto:
            imagen_vieja = producto["imagen_url"]
            ruta_imagen = os.path.join(ruta_destino, imagen_vieja)
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    else:
        producto = catalogo.consultar_producto(codigo)
        if producto:
            nombre_imagen = producto["imagen_url"]
    if catalogo.modificar_producto(codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nombre_imagen, nuevo_proveedor):
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 403
    
@app.route("/productos/<int:codigo", methods=["DELETE"])
def eliminar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto:
        ruta_imagen = os.path.join(ruta_destino, producto['imagen_url'])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        if catalogo.eliminar_producto(codigo):
            return jsonify({"mensaje": "Producto eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar producto"}), 500
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404