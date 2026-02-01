from flask import Blueprint
from src.controller.appointment_controller import AppointmentController

appointment_bp = Blueprint('appointments', __name__)
controller = AppointmentController()

@appointment_bp.route('', methods=['POST'])
def create_appointment():
    return controller.create()

@appointment_bp.route('', methods=['GET'])
def get_appointments():
    return controller.find_all()

@appointment_bp.route('/<appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    return controller.find_by_id(appointment_id)

@appointment_bp.route('/<appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    return controller.update(appointment_id)

@appointment_bp.route('/<appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    return controller.delete(appointment_id)