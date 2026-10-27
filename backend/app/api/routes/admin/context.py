from threading import Lock

from app.repositories.convocatoria_repository import ConvocatoriaRepository
from app.repositories.student_repository import StudentRepository


student_repository = StudentRepository()
convocatoria_repository = ConvocatoriaRepository()
dashboard_lock = Lock()
