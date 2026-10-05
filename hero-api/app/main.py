from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select

from app.database import SessionDep, engine
from app.models import (
    Hero,
    HeroCreate,
    HeroPublic,
    HeroUpdate,
    Team,
    TeamCreate,
    TeamPublic,
    Mission,
    MissionCreate,
    MissionPublic,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


def get_or_404(session, model, obj_id):
    obj = session.get(model, obj_id)
    if obj is None:
        raise HTTPException(404, f"{model.__name__} not found")
    return obj


def check_team(session, team_id):
    if team_id is not None:
        get_or_404(session, Team, team_id)


@app.post("/heroes", response_model=HeroPublic, status_code=201)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    check_team(session, hero_in.team_id)
    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes", response_model=list[HeroPublic])
def list_heroes(
    session: SessionDep,
    min_age: int | None = None,
    team_id: int | None = None,
    name: str | None = None,
    offset: int = 0,
    limit: int = Query(default=10, le=100),
):
    stmt = select(Hero)
    if min_age is not None:
        stmt = stmt.where(Hero.age >= min_age)
    if team_id is not None:
        stmt = stmt.where(Hero.team_id == team_id)
    if name:
        stmt = stmt.where(Hero.name.ilike(f"%{name}%"))
    return session.exec(stmt.order_by(Hero.id).offset(offset).limit(limit)).all()


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def get_hero(hero_id: int, session: SessionDep):
    return get_or_404(session, Hero, hero_id)


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero = get_or_404(session, Hero, hero_id)
    data = hero_in.model_dump(exclude_unset=True)
    check_team(session, data.get("team_id"))
    hero.sqlmodel_update(data)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    session.delete(get_or_404(session, Hero, hero_id))
    session.commit()


@app.post("/teams", response_model=TeamPublic, status_code=201)
def create_team(team_in: TeamCreate, session: SessionDep):
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Team name already exists")
    session.refresh(team)
    return team


@app.get("/teams", response_model=list[TeamPublic])
def list_teams(session: SessionDep):
    return session.exec(select(Team)).all()


@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def team_heroes(team_id: int, session: SessionDep):
    return get_or_404(session, Team, team_id).heroes


@app.post("/missions", response_model=MissionPublic, status_code=201)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@app.post("/heroes/{hero_id}/missions/{mission_id}", status_code=204)
def assign_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = get_or_404(session, Hero, hero_id)
    mission = get_or_404(session, Mission, mission_id)
    if mission not in hero.missions:
        hero.missions.append(mission)
        session.add(hero)
        session.commit()


@app.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic])
def hero_missions(hero_id: int, session: SessionDep):
    return get_or_404(session, Hero, hero_id).missions
