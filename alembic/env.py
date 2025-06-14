import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# ✅ Load environment variables from .env file if it exists
load_dotenv(".env")

# ✅ Alembic Config object
config = context.config

# ✅ Logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Import Base and all models so Alembic can detect them
from app.db.base import Base
from app.db.model import user, service, sub_service, booking, banner, pastevent, gallery, news, chats, contact, loyalty_point

# ✅ Set metadata for autogenerate
target_metadata = Base.metadata

# ✅ Get database URL (from full DATABASE_URL or Railway vars)
def get_url():
    database_url = os.getenv("DATABASE_URL")
    
    # Use Railway-specific variables if DATABASE_URL is not set
    if not database_url:
        pguser = os.getenv("PGUSER")
        pgpassword = os.getenv("POSTGRES_PASSWORD")
        pghost = os.getenv("RAILWAY_PRIVATE_DOMAIN", "postgres.railway.internal")
        pgdb = os.getenv("PGDATABASE")
        if not all([pguser, pgpassword, pgdb]):
            raise ValueError("❌ Missing Railway environment variables (PGUSER, POSTGRES_PASSWORD, PGDATABASE)")
        database_url = f"postgresql://{pguser}:{pgpassword}@{pghost}:5432/{pgdb}"
    
    return database_url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
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

# ✅ Choose mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
