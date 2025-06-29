import os
import time
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

# ✅ Load environment variables in development
if not os.getenv("RAILWAY_ENVIRONMENT"):
    from dotenv import load_dotenv
    load_dotenv(".env")

# ✅ Alembic config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Import Base and models
from app.db.base import Base
from app.db.model import (
    user, service, sub_service, booking, banner,
    pastevent, gallery, news, chats, contact, loyalty_point , teams ,testimonial , getintouch
)

target_metadata = Base.metadata

# ✅ Corrected and safe URL parser
def get_url():
    """Get properly formatted and validated database URL"""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is required")

    # Parse and validate URL
    parsed = urlparse(url)

    # Fix the scheme
    if parsed.scheme == "postgres":
        parsed = parsed._replace(scheme="postgresql")

    # Replace internal Railway host if needed
    if "railway.internal" in parsed.netloc:
        netloc_parts = parsed.netloc.split("@")
        if len(netloc_parts) == 2:
            credentials = netloc_parts[0]
            host_port = netloc_parts[1].replace(
                "postgres.railway.internal", "containers-us-west-101.railway.app"
            )
            parsed = parsed._replace(netloc=f"{credentials}@{host_port}")

    # Parse existing query string and add sslmode safely
    query_params = dict(parse_qsl(parsed.query))
    if os.getenv("RAILWAY_ENVIRONMENT"):
        query_params["sslmode"] = "require"

    # Rebuild the final URL
    query = urlencode(query_params)
    final_url = urlunparse(parsed._replace(query=query))

    return final_url

# ✅ Offline migration mode
def run_migrations_offline():
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# ✅ Online migration mode with retry logic
def run_migrations_online():
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            connectable = engine_from_config(
                {"sqlalchemy.url": get_url()},
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
                connect_args={
                    "connect_timeout": 10,
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 5
                }
            )

            with connectable.connect() as connection:
                context.configure(
                    connection=connection,
                    target_metadata=target_metadata,
                    compare_type=True,
                )
                with context.begin_transaction():
                    context.run_migrations()
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"⚠️  Connection attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

# ✅ Run the appropriate mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
