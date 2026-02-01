from flask import request, jsonify
from src.services.appointment_service import AppointmentService

class AppointmentController:
    def __init__(self):
        self.service = AppointmentService()
    
    def create(self):
        try:
            data = request.get_json()
            pacienteId = data.get('pacienteId')
            medicoId = data.get('medicoId')
            fechaHora = data.get('fechaHora')
            motivo = data.get('motivo')
            
            if not all([pacienteId, medicoId, fechaHora, motivo]):
                return jsonify({
                    'error': True,
                    'message': 'Todos los campos son obligatorios',
                    'code': 'MISSING_FIELDS'
                }), 400
            
            if len(motivo) < 10:
                return jsonify({
                    'error': True,
                    'message': 'El motivo debe tener al menos 10 caracteres',
                    'code': 'INVALID_MOTIVO'
                }), 400
            
            appointment = self.service.create(data)
            return jsonify(appointment.to_dict()), 201
        except Exception as e:
            return jsonify({
                'error': True,
                'message': str(e),
                'code': 'INTERNAL_ERROR'
            }), 500
    
    def find_all(self):
        try:
            filters = {}
            if request.args.get('pacienteId'):
                filters['pacienteId'] = request.args.get('pacienteId')
            if request.args.get('medicoId'):
                filters['medicoId'] = request.args.get('medicoId')
            if request.args.get('fecha'):
                filters['fecha'] = request.args.get('fecha')
            
            appointments = self.service.find_all(filters)
            return jsonify([a.to_dict() for a in appointments]), 200
        except Exception as e:
            return jsonify({'error': True, 'message': 'Error al obtener citas'}), 500
    
    def find_by_id(self, appointment_id):
        try:
            appointment = self.service.find_by_id(appointment_id)
            if not appointment:
                return jsonify({
                    'error': True,
                    'message': 'Cita no encontrada',
                    'code': 'NOT_FOUND'
                }), 404
            return jsonify(appointment.to_dict()), 200
        except Exception as e:
            return jsonify({'error': True, 'message': 'Error al obtener cita'}), 500
    
    def update(self, appointment_id):
        try:
            data = request.get_json()
            appointment = self.service.update(appointment_id, data)
            return jsonify(appointment.to_dict()), 200
        except Exception as e:
            return jsonify({
                'error': True,
                'message': str(e)
            }), 500
    
    def delete(self, appointment_id):
        try:
            self.service.delete(appointment_id)
            return jsonify({'message': 'Cita cancelada exitosamente'}), 200
        except Exception as e:
            return jsonify({
                'error': True,
                'message': str(e)
            }), 500