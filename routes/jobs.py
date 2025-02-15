from fastapi import APIRouter, Depends, HTTPException, status
from routes.auth import get_db, get_current_user, db_dependency
from models import Job, Application
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)

class JobRequest(BaseModel):
    title: str
    description: str
    location: str
    openings: int

class ApplicationRequest(BaseModel):
    applied_at: datetime

@router.post("/")
async def create_job(
    job_request: JobRequest,
    db: db_dependency,
    current_user: dict = Depends(get_current_user)
):
    new_job = Job(
        title=job_request.title,
        description=job_request.description,
        location=job_request.location,
        openings=job_request.openings,
        creator_id=current_user["id"]
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return {"message": "Job created successfully"}

@router.get("/")
async def get_jobs(db: db_dependency):
    jobs = db.query(Job).all()
    return jobs

@router.get("/apply/{loc}")
async def get_jobs_by_location(loc: str, db: db_dependency):
    jobs = db.query(Job).filter(Job.location == loc).all()
    return jobs

@router.post("/apply/{job_id}")
async def apply_for_job(
    job_id: int,
    db: db_dependency,
    application: ApplicationRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
            )
        # Save the current openings value before processing the application.
        job_openings = job.openings

        new_application = Application(
            user_id=current_user["id"],
            job_id=job_id,
            applied_at=application.applied_at
        )
        db.add(new_application)
        db.commit()

        application_count = db.query(Application).filter(Application.job_id == job_id).count()
        if application_count >= job_openings:
            # Re-query the job to ensure we have a valid instance.
            job_to_delete = db.query(Job).filter(Job.id == job_id).first()
            if job_to_delete:
                db.delete(job_to_delete)
                db.commit()
                return {"message": "Application submitted successfully. The job is now closed."}
            else:
                return {"message": "Application submitted successfully. Job was already closed."}

        return {"message": "Application submitted successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job already applied to or job closed"
        )

@router.get("/applications")
async def get_applications(
    db: db_dependency,
    current_user: dict = Depends(get_current_user)
):
    applications = db.query(Application).filter(Application.user_id == current_user["id"]).all()
    results = []
    for app in applications:
        # Try to fetch the job details for this application
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if job:
            results.append({
                "job_id": job.id,
                "title": job.title,
                "description": job.description,
                "location": job.location,
                "applied_at": app.applied_at
            })
        else:
            # In case the job has been deleted, mark it as closed.
            results.append({
                "job_id": app.job_id,
                "title": "Job Closed",
                "description": "This job is no longer available.",
                "location": "N/A",
                "applied_at": app.applied_at
            })
    return results

@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: int,
    db: db_dependency,
    current_user: dict = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.creator_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this job"
        )
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
