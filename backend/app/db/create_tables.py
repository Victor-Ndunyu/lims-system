from app.db.base import Base
from app.db.session import engine
# Import models so they are registered with SQLAlchemy's metadata
import app.models  # noqa: F401

if __name__ == '__main__':
    print('Creating database tables...')
    Base.metadata.create_all(bind=engine)
    print('Tables created.')
