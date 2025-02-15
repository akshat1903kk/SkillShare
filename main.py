from fastapi import FastAPI
from database import engine
from models import Base , User, Application, Job
from routes import auth , jobs
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")  # Serve static files from 'static' directory

templates = Jinja2Templates(directory="templates")  # Set up Jinja2 templates, assuming you have a 'templates' folder

app.include_router(auth.router)
app.include_router(jobs.router)

@app.get("/", response_class=HTMLResponse)  # Route for login.html
async def login(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get('/dashboard',response_class=HTMLResponse)
async def dashboard(request:Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/application',response_class=HTMLResponse)
async def applications(request:Request):
    return templates.TemplateResponse("application.html", {"request": request})