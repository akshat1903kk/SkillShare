from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, event
from sqlalchemy.orm import relationship, Session
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=False)  # Changed to String for flexibility

    applications = relationship("Application", back_populates="user")
    jobs = relationship("Job", back_populates="creator")

    def __repr__(self):
        return f"<User {self.username}>"


class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    applied_at = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")

    def __repr__(self):
        return f"<Application {self.id}>"


class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    openings = Column(Integer, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    creator = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job {self.id}>"


@event.listens_for(Application, 'after_insert')
def check_job_applications(mapper, connection, target):
    session = Session(bind=connection)
    job = session.query(Job).filter(Job.id == target.job_id).first()
    if job:
        application_count = session.query(Application).filter(Application.job_id == job.id).count()
        if application_count >= job.openings:
            session.delete(job)
            session.commit()
