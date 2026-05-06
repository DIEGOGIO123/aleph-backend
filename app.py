# ============================================
# BACKEND ALEPH CONSULTING - API COMPLETA
# Versión optimizada para Railway
# Archivo: app.py
# ============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

DATA_FILE = 'aleph_datos.json'

# ========== DATOS INICIALES ==========
DATOS_INICIALES = {
    "usuarios": [
        {"id": 1, "email": "admin@aleph.com", "password": "admin123", "nombre": "Administrador", "rol": "admin", "firebaseUid": None},
        {"id": 2, "email": "vendedor@aleph.com", "password": "123456", "nombre": "Diego Colchado", "rol": "vendedor", "firebaseUid": None}
    ],
    "productos": [
        {"id": 1, "nombre": "NeoMelubrina", "presentacion": "10 PZS", "precio": 75, "categoria": "medicamento", "imagen": "💊", "stock": 10},
        {"id": 2, "nombre": "NeoMelubrina", "presentacion": "24 PZS", "precio": 130, "categoria": "medicamento", "imagen": "💊", "stock": 10},
        {"id": 3, "nombre": "Ibuprofeno", "presentacion": "20 PZS", "precio": 85, "categoria": "medicamento", "imagen": "💊", "stock": 10},
        {"id": 4, "nombre": "Paracetamol", "presentacion": "30 PZS", "precio": 70, "categoria": "medicamento", "imagen": "💊", "stock": 10},
        {"id": 5, "nombre": "Omeprazol", "presentacion": "14 PZS", "precio": 95, "categoria": "medicamento", "imagen": "💊", "stock": 10},
        {"id": 6, "nombre": "Losartán", "presentacion": "28 PZS", "precio": 180, "categoria": "medicamento", "imagen": "💊", "stock": 10},
        {"id": 7, "nombre": "Metformina", "presentacion": "30 PZS", "precio": 75, "categoria": "medicamento", "imagen": "💊", "stock": 10},
        {"id": 8, "nombre": "Vitamina C", "presentacion": "30 PZS", "precio": 120, "categoria": "vitaminas", "imagen": "🍊", "stock": 10},
        {"id": 9, "nombre": "Jabón Antibacterial", "presentacion": "1 PZ", "precio": 25, "categoria": "higiene", "imagen": "🧼", "stock": 10},
        {"id": 10, "nombre": "Alcohol Gel", "presentacion": "300ml", "precio": 45, "categoria": "higiene", "imagen": "🧴", "stock": 10},
        {"id": 11, "nombre": "Cubrebocas KN95", "presentacion": "10 PZS", "precio": 120, "categoria": "higiene", "imagen": "😷", "stock": 10},
        {"id": 12, "nombre": "Termómetro Digital", "presentacion": "1 PZ", "precio": 220, "categoria": "equipo", "imagen": "🌡️", "stock": 10},
        {"id": 13, "nombre": "Baumanómetro", "presentacion": "1 PZ", "precio": 550, "categoria": "equipo", "imagen": "🩺", "stock": 10}
    ],
    "clientes": [
        {"id": 1, "nombre": "Farmacia Guadalajara", "telefono": "5551112233", "direccion": "Av. Central #123", "vendedorAsignado": 2},
        {"id": 2, "nombre": "Farmacias Similares", "telefono": "5552223344", "direccion": "Insurgentes #456", "vendedorAsignado": 2},
        {"id": 3, "nombre": "Farmacia San Pablo", "telefono": "5553334455", "direccion": "Reforma #789", "vendedorAsignado": 2},
        {"id": 4, "nombre": "Walmart Farmacia", "telefono": "5554445566", "direccion": "Periférico #321", "vendedorAsignado": 2},
        {"id": 5, "nombre": "Farmacia Benavides", "telefono": "5555556677", "direccion": "Universidad #654", "vendedorAsignado": 2}
    ],
    "pedidos": []
}

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return DATOS_INICIALES.copy()

def guardar_datos(datos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

datos = cargar_datos()

def verificar_token(headers):
    auth = headers.get('Authorization', '')
    return True if auth else False

# ========== ENDPOINTS DE AUTENTICACIÓN ==========
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    usuario = None
    for u in datos['usuarios']:
        if u['email'] == email and u['password'] == password:
            usuario = u
            break
    
    if usuario:
        return jsonify({
            'success': True,
            'user': {
                'id': usuario['id'],
                'email': usuario['email'],
                'nombre': usuario['nombre'],
                'rol': usuario['rol']
            }
        })
    return jsonify({'error': 'Credenciales incorrectas'}), 401

@app.route('/api/login/firebase', methods=['POST'])
def login_firebase():
    data = request.json
    email = data.get('email')
    nombre = data.get('nombre', email.split('@')[0])
    firebaseUid = data.get('firebaseUid')
    
    usuario = None
    for u in datos['usuarios']:
        if u['email'] == email or u.get('firebaseUid') == firebaseUid:
            usuario = u
            break
    
    if usuario:
        if not usuario.get('firebaseUid'):
            usuario['firebaseUid'] = firebaseUid
            guardar_datos(datos)
        return jsonify({
            'success': True,
            'user': {
                'id': usuario['id'],
                'email': usuario['email'],
                'nombre': usuario['nombre'],
                'rol': usuario['rol']
            }
        })
    else:
        nuevo_id = max([u['id'] for u in datos['usuarios']]) + 1 if datos['usuarios'] else 1
        nuevo_usuario = {
            'id': nuevo_id,
            'email': email,
            'nombre': nombre,
            'rol': 'vendedor',
            'firebaseUid': firebaseUid,
            'password': None
        }
        datos['usuarios'].append(nuevo_usuario)
        guardar_datos(datos)
        return jsonify({
            'success': True,
            'user': {
                'id': nuevo_id,
                'email': email,
                'nombre': nombre,
                'rol': 'vendedor'
            }
        }), 201

@app.route('/api/registro', methods=['POST'])
def registro():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    nombre = data.get('nombre')
    
    for u in datos['usuarios']:
        if u['email'] == email:
            return jsonify({'error': 'El email ya está registrado'}), 400
    
    nuevo_id = max([u['id'] for u in datos['usuarios']]) + 1 if datos['usuarios'] else 1
    nuevo_usuario = {
        'id': nuevo_id,
        'email': email,
        'password': password,
        'nombre': nombre,
        'rol': 'vendedor',
        'firebaseUid': None
    }
    datos['usuarios'].append(nuevo_usuario)
    guardar_datos(datos)
    
    return jsonify({
        'success': True,
        'user': {
            'id': nuevo_id,
            'email': email,
            'nombre': nombre,
            'rol': 'vendedor'
        }
    }), 201

# ========== ENDPOINTS DE USUARIOS ==========
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    usuarios_safe = [{'id': u['id'], 'email': u['email'], 'nombre': u['nombre'], 'rol': u['rol']} for u in datos['usuarios']]
    return jsonify(usuarios_safe)

# ========== ENDPOINTS DE CLIENTES ==========
@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    return jsonify(datos['clientes'])

@app.route('/api/clientes', methods=['POST'])
def crear_cliente():
    data = request.json
    nuevo_id = max([c['id'] for c in datos['clientes']]) + 1 if datos['clientes'] else 1
    nuevo_cliente = {
        'id': nuevo_id,
        'nombre': data.get('nombre'),
        'telefono': data.get('telefono'),
        'direccion': data.get('direccion', ''),
        'vendedorAsignado': data.get('vendedorAsignado', None)
    }
    datos['clientes'].append(nuevo_cliente)
    guardar_datos(datos)
    return jsonify({'success': True, 'cliente': nuevo_cliente}), 201

# ========== ENDPOINTS DE PRODUCTOS ==========
@app.route('/api/productos', methods=['GET'])
def get_productos():
    return jsonify(datos['productos'])

@app.route('/api/productos', methods=['POST'])
def crear_producto():
    """Crear un nuevo producto"""
    data = request.json
    nuevo_id = max([p['id'] for p in datos['productos']]) + 1 if datos['productos'] else 1
    
    nuevo_producto = {
        'id': nuevo_id,
        'nombre': data.get('nombre'),
        'presentacion': data.get('presentacion', ''),
        'precio': data.get('precio'),
        'stock': data.get('stock', 0),
        'imagen': data.get('imagen', '💊'),
        'categoria': data.get('categoria', 'medicamento')
    }
    
    datos['productos'].append(nuevo_producto)
    guardar_datos(datos)
    
    return jsonify({'success': True, 'producto': nuevo_producto}), 201

@app.route('/api/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    """Actualizar producto (precio, stock, imagen, nombre, presentacion)"""
    data = request.json
    for producto in datos['productos']:
        if producto['id'] == id:
            if 'precio' in data:
                producto['precio'] = data['precio']
            if 'stock' in data:
                producto['stock'] = data['stock']
            if 'imagen' in data:
                producto['imagen'] = data['imagen']
            if 'nombre' in data:
                producto['nombre'] = data['nombre']
            if 'presentacion' in data:
                producto['presentacion'] = data['presentacion']
            guardar_datos(datos)
            return jsonify({'success': True, 'producto': producto})
    return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/api/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    """Eliminar un producto"""
    for i, producto in enumerate(datos['productos']):
        if producto['id'] == id:
            del datos['productos'][i]
            guardar_datos(datos)
            return jsonify({'success': True})
    return jsonify({'error': 'Producto no encontrado'}), 404

# ========== ENDPOINTS DE PEDIDOS ==========
@app.route('/api/pedidos', methods=['GET'])
def get_pedidos():
    return jsonify(datos['pedidos'])

@app.route('/api/pedidos', methods=['POST'])
def crear_pedido():
    data = request.json
    nuevo_pedido = {
        'id': len(datos['pedidos']) + 1,
        'fecha': datetime.now().isoformat(),
        'clienteId': data.get('clienteId'),
        'clienteNombre': data.get('clienteNombre'),
        'vendedor': data.get('vendedor', 'Vendedor'),
        'vendedorId': data.get('vendedorId'),
        'productos': data.get('productos', []),
        'total': data.get('total', 0),
        'formaPago': data.get('formaPago', 'completo'),
        'montoPagado': data.get('montoPagado', 0),
        'correoTicket': data.get('correoTicket', ''),
        'observaciones': data.get('observaciones', ''),
        'estado': 'pendiente',
        'pagado': False
    }
    datos['pedidos'].append(nuevo_pedido)
    guardar_datos(datos)
    return jsonify({'success': True, 'pedido': nuevo_pedido}), 201

@app.route('/api/pedidos/<int:id>/pagar', methods=['POST'])
def pagar_pedido(id):
    data = request.json
    for pedido in datos['pedidos']:
        if pedido['id'] == id:
            pedido['pagado'] = True
            pedido['montoPagado'] = data.get('montoPagado', pedido['total'])
            pedido['fechaPago'] = datetime.now().isoformat()
            guardar_datos(datos)
            return jsonify({'success': True, 'pedido': pedido})
    return jsonify({'error': 'Pedido no encontrado'}), 404

@app.route('/api/pedidos/<int:id>/estado', methods=['PUT'])
def actualizar_estado(id):
    data = request.json
    for pedido in datos['pedidos']:
        if pedido['id'] == id:
            pedido['estado'] = data.get('estado')
            guardar_datos(datos)
            return jsonify({'success': True, 'pedido': pedido})
    return jsonify({'error': 'Pedido no encontrado'}), 404

# ========== ENDPOINTS DE ESTADÍSTICAS ==========
@app.route('/api/estadisticas', methods=['GET'])
def get_estadisticas():
    total_pedidos = len(datos['pedidos'])
    pendientes = len([p for p in datos['pedidos'] if p['estado'] == 'pendiente'])
    total_ventas = sum(p['total'] for p in datos['pedidos'])
    total_pagado = sum(p.get('montoPagado', 0) for p in datos['pedidos'])
    
    return jsonify({
        'totalPedidos': total_pedidos,
        'pedidosPendientes': pendientes,
        'totalVentas': total_ventas,
        'totalPagado': total_pagado,
        'productosActivos': len(datos['productos']),
        'clientesActivos': len(datos['clientes']),
        'vendedoresActivos': len([u for u in datos['usuarios'] if u['rol'] == 'vendedor'])
    })

# ========== ENDPOINTS DE HEALTH Y HOME ==========
@app.route('/')
def home():
    return jsonify({
        'mensaje': 'API de Aleph Consulting funcionando correctamente',
        'estado': 'en linea',
        'endpoints_disponibles': ['/api/health', '/api/productos', '/api/login', '/api/registro', '/api/pedidos']
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()})

# ========== INICIO DEL SERVIDOR (VERSIÓN RAILWAY) ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║   🚀 API ALEPH CONSULTING ACTIVADA                   ║
    ╠══════════════════════════════════════════════════════╣
    ║   Puerto: {port}                                       ║
    ║   Entorno: {'Producción' if port != 5000 else 'Desarrollo'}
    ║   CRUD Productos: ACTIVADO                           ║
    ╚══════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=False)