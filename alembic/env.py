import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Load environment variables only in local development
if os.getenv("RAILWAY_ENVIRONMENT") != "production":
    from dotenv import load_dotenv
    load_dotenv(".env")

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models' MetaData object for 'autogenerate' support
from app.db.base import Base
target_metadata = Base.metadata

def get_url():
    """Get the database URL with Railway-specific adjustments."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("❌ DATABASE_URL environment variable is not set")
    
    # Convert postgres:// to postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    # Add SSL requirement in production
    if os.getenv("RAILWAY_ENVIRONMENT") == "production":
        if "?" in url:
            url += "&sslmode=require"
        else:
            url += "?sslmode=require"
    
    return url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
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