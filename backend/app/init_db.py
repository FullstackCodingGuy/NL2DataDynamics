from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed initial data
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password="admin123",
            is_active=True,
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    db.close()

if __name__ == "__main__":
    init_db()