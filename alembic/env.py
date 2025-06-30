import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add path to app directory
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'app')))
from app.database import Base  # Your models Base
from app.models import Project  # Import all models here
from dotenv import load_dotenv

load_dotenv()

# Alembic Config object
config = context.config

# Get DB URL from environment
config.set_main_option('sqlalchemy.url', os.getenv("DATABASE_URL"))

# Configure logging
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=os.getenv("DATABASE_URL"),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
