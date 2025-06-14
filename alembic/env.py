import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Disable .env loading in production - Railway provides its own vars
if not os.getenv("RAILWAY_ENVIRONMENT"):
    from dotenv import load_dotenv
    load_dotenv(".env")

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.db.base import Base
target_metadata = Base.metadata

def get_url():
    """Get properly formatted database URL for Railway"""
    url = os.getenv("DATABASE_URL")
    
    if not url:
        raise RuntimeError("DATABASE_URL must be set in environment variables")
    
    # Handle Railway's internal URL issue
    if "postgres.railway.internal" in url:
        # Replace with external URL format
        parts = url.split("@")
        if len(parts) == 2:
            creds, rest = parts
            url = f"postgresql://{creds}@containers-us-west-101.railway.app:{rest.split(':')[1]}"
    
    # Ensure postgresql:// prefix
    url = url.replace("postgres://", "postgresql://", 1)
    
    # Add SSL in production
    if os.getenv("RAILWAY_ENVIRONMENT"):
        if "?" in url:
            url += "&sslmode=require"
        else:
            url += "?sslmode=require"
    
    return url

def run_migrations_offline():
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": get_url()},
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