# routes/entidad_routes.py
from flask import Blueprint, jsonify, request
from config import db

class EntidadRoutes:
    """Clase base para manejar rutas CRUD genéricas para cualquier entidad."""

    def __init__(self, nombre, modelo):
        self.bp = Blueprint(f'{nombre}_bp', __name__)  # Crea un Blueprint con el nombre de la entidad
        self.modelo = modelo

        # Rutas comunes
        self.bp.add_url_rule('/', 'get_all', self.get_all, methods=['GET'])
        self.bp.add_url_rule('/', 'create', self.create, methods=['POST'])
        self.bp.add_url_rule('/<string:id>', 'get_one', self.get_one, methods=['GET'])
        self.bp.add_url_rule('/<string:id>', 'update', self.update, methods=['PUT'])
        self.bp.add_url_rule('/<string:id>', 'delete', self.delete, methods=['DELETE'])

    def get_all(self):
        """Obtener todos los registros de la entidad."""
        registros = self.modelo.query.all()
        return jsonify([r.to_dict() for r in registros])

    def create(self):
        """Crear un nuevo registro."""
        data = request.json
        nuevo_registro = self.modelo()
        nuevo_registro.from_dict(data)

        db.session.add(nuevo_registro)
        db.session.commit()
        return jsonify(nuevo_registro.to_dict()), 201

    def get_one(self, id):
        """Obtener un registro por su ID."""
        registro = self.modelo.query.get(id)
        if not registro:
            return jsonify({"error": f"{self.modelo.__name__} no encontrado"}), 404
        return jsonify(registro.to_dict())

    def update(self, id):
        """Actualizar un registro existente."""
        registro = self.modelo.query.get(id)
        if not registro:
            return jsonify({"error": f"{self.modelo.__name__} no encontrado"}), 404

        data = request.json
        registro.from_dict(data)

        db.session.commit()
        return jsonify(registro.to_dict()), 200

    def delete(self, id):
        """Eliminar un registro."""
        registro = self.modelo.query.get(id)
        if not registro:
            return jsonify({"error": f"{self.modelo.__name__} no encontrado"}), 404

        db.session.delete(registro)
        db.session.commit()
        return jsonify({"mensaje": f"{self.modelo.__name__} eliminado"}), 200

