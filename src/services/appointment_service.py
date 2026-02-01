from datetime import datetime
from sqlalchemy import and_, Date  
from src.models.appointment import Appointment, AppointmentStatus
from src.config.database import SessionLocal
from src.services.queue_service import QueueService
import requests
import os

class AppointmentService:
    def __init__(self):
        self.db = SessionLocal()
        self.queue_service = QueueService()
    
    def create(self, data):
        # Convertir fechaHora a datetime si es string
        if isinstance(data.get('fechaHora'), str):
            try:
                fecha_hora = datetime.fromisoformat(data['fechaHora'].replace('Z', '+00:00'))
                data['fechaHora'] = fecha_hora
            except:
                raise Exception('Formato de fecha inválido')
        
        # Validar médico y paciente
        self.validate_doctor(data['medicoId'])
        self.validate_patient(data['pacienteId'])
        
        # Validar horario laboral
        self.validate_working_hours(data['fechaHora'])
        
        # Verificar disponibilidad con lock pesimista
        conflict = self.db.query(Appointment).with_for_update().filter(
            and_(
                Appointment.medicoId == data['medicoId'],
                Appointment.fechaHora == data['fechaHora'],
                Appointment.estado != AppointmentStatus.CANCELADA
            )
        ).first()
        
        if conflict:
            raise Exception('El médico ya tiene una cita agendada en ese horario')
        
        # Crear cita
        data['estado'] = AppointmentStatus.AGENDADA
        appointment = Appointment(**data)
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        
        # Publicar evento
        self.queue_service.publish('audit.appointment.created', appointment.to_dict())
        
        return appointment
    
    def validate_doctor(self, doctor_id):
        try:
            USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:3001')
            response = requests.get(f'{USER_SERVICE_URL}/api/users/doctors/{doctor_id}')
            response.raise_for_status()
        except:
            raise Exception('Médico no encontrado')
    
    def validate_patient(self, patient_id):
        try:
            USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:3001')
            response = requests.get(f'{USER_SERVICE_URL}/api/users/patients/{patient_id}')
            response.raise_for_status()
        except:
            raise Exception('Paciente no encontrado')
    
    def validate_working_hours(self, fecha):
        day = fecha.weekday()
        hour = fecha.hour
        
        # Lunes(0) a Viernes(4), 8AM a 6PM
        if day in [5, 6]:  # Sábado, Domingo
            raise Exception('No se pueden agendar citas los fines de semana')
        
        if hour < 8 or hour >= 18:
            raise Exception('Las citas deben ser entre 8:00 AM y 6:00 PM')
    
    def find_all(self, filters=None):
        query = self.db.query(Appointment)
        
        if filters:
            if filters.get('pacienteId'):
                query = query.filter(Appointment.pacienteId == filters['pacienteId'])
            if filters.get('medicoId'):
                query = query.filter(Appointment.medicoId == filters['medicoId'])
            if filters.get('fecha'):
                query = query.filter(Appointment.fechaHora.cast(Date) == filters['fecha'])
        
        return query.all()
    
    def find_by_id(self, appointment_id):
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    def update(self, appointment_id, data):
        appointment = self.find_by_id(appointment_id)
        if not appointment:
            raise Exception('Cita no encontrada')
        
        # Si se actualiza fechaHora y viene como string
        if data.get('fechaHora') and isinstance(data['fechaHora'], str):
            try:
                data['fechaHora'] = datetime.fromisoformat(data['fechaHora'].replace('Z', '+00:00'))
            except:
                raise Exception('Formato de fecha inválido en actualización')
        
        for key, value in data.items():
            setattr(appointment, key, value)
        
        self.db.commit()
        self.db.refresh(appointment)
        
        self.queue_service.publish('audit.appointment.updated', appointment.to_dict())
        
        return appointment
    
    def delete(self, appointment_id):
        appointment = self.find_by_id(appointment_id)
        if not appointment:
            raise Exception('Cita no encontrada')
        
        appointment.estado = AppointmentStatus.CANCELADA
        self.db.commit()
        
        self.queue_service.publish('audit.appointment.deleted', appointment.to_dict())
    
    def __del__(self):
        self.db.close()