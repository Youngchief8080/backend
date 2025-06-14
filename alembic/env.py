import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")  # or ".env.production"

# Alembic Config object
config = context.config

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import metadata
from app.db.base import Base
from app.db.model import user, service, sub_service, booking, banner, pastevent, gallery, news, chats, contact, loyalty_point

target_metadata = Base.metadata

# Build SQLAlchemy DB URL from env
def get_url():
    url = os.getenv("DATABASE_URL")

    # If not set directly, build from Railway environment vars
    if not url:
        user = os.getenv("PGUSER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("RAILWAY_PRIVATE_DOMAIN", "postgres.railway.internal")
        db = os.getenv("PGDATABASE")

        if not all([user, password, host, db]):
            raise ValueError("❌ Missing required DB env vars for Alembic")

        url = f"postgresql://{user}:{password}@{host}:5432/{db}"
    
    return url

def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
