from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from src.config.database import Base

class AppointmentStatus(enum.Enum):
    AGENDADA = 'AGENDADA'
    COMPLETADA = 'COMPLETADA'
    CANCELADA = 'CANCELADA'

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pacienteId = Column(UUID(as_uuid=True), nullable=False)
    medicoId = Column(UUID(as_uuid=True), nullable=False)
    fechaHora = Column(DateTime, nullable=False)
    motivo = Column(String(500), nullable=False)
    estado = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.AGENDADA, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'pacienteId': str(self.pacienteId),
            'medicoId': str(self.medicoId),
            'fechaHora': self.fechaHora.isoformat() if self.fechaHora else None,
            'motivo': self.motivo,
            'estado': self.estado.value if self.estado else None,
            'version': self.version,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None
        }