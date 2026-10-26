# Tienda Local (Flask + MySQL)

## Instalación
1. Crear la base de datos y tablas:
   mysql -u root -p < schema.sql   # tablas: users, products
2. Entorno virtual e instalación:
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
3. Copiar `.env.example` a `.env` y poner tus credenciales de MySQL.
4. Ejecutar:
   python app.py
5. Abrir http://127.0.0.1:5000

## Rutas
/ · /registro · /login · /logout
/productos (listar y buscar) · /productos/nuevo · /productos/<id>/editar · /productos/<id>/eliminar (POST)
