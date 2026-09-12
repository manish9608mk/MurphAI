from backend.app.database.database import SessionLocal


# MurphAI Database Session Dependency

def get_db():
    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()