
from logging.config import fileConfig

from alembic import context

from ai_research_assistant.database import Base, engine

# Import all models so their tables are registered in Base.metadata.
from ai_research_assistant.models.paper import Paper
from ai_research_assistant.models.summary import Summary
from ai_research_assistant.models.conversation import Conversation
from ai_research_assistant.models.message import Message
from ai_research_assistant.models.paper_chunk import PaperChunk


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
