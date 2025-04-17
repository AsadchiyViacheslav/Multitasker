from fastapi import FastAPI
from app.routers import auth, profile, category, projects, task, subtask, my
from app.core.database import engine, Base
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    superuser_email = "admin@example.com"
    superuser = db.query(User).filter_by(email=superuser_email).first()
    if not superuser:
        user = User(
            email=superuser_email,
            hashed_password=get_password_hash("admin123"),  
            is_superuser=True,
            name="Admin"
        )
        db.add(user)
        db.commit()
    db.close()
    
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(category.router)
app.include_router(projects.router)
app.include_router(task.router)
app.include_router(subtask.router)
app.include_router(my.router)