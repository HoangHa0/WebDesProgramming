import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
args = {"check_same_thread": False} if url.startswith("sqlite") else {}
engine = create_engine(url, echo=True, connect_args=args)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
