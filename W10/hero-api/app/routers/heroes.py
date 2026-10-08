from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import SessionDep
from app.models import (
    Hero,
    HeroCreate,
    HeroPublic,
    HeroUpdate,
    Mission,
    MissionPublic,
    Team,
)


router = APIRouter(
    prefix="/heroes",
    tags=["heroes"],
)

NOT_FOUND = {
    404: {"description": "Hero not found"},
}


def get_hero_or_404(session: Session, hero_id: int) -> Hero:
    hero = session.get(Hero, hero_id)

    if not hero:
        raise HTTPException(
            status_code=404,
            detail="Hero not found",
        )

    return hero


def check_team_exists(
    session: Session,
    team_id: int | None,
) -> None:
    if team_id is not None and not session.get(Team, team_id):
        raise HTTPException(
            status_code=400,
            detail=f"Team {team_id} does not exist",
        )


@router.get(
    "",
    response_model=list[HeroPublic],
    summary="List heroes",
)
def list_heroes(
    session: SessionDep,
    team_id: int | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    query = select(Hero).order_by(Hero.id)

    if team_id is not None:
        query = query.where(Hero.team_id == team_id)

    return session.exec(query.offset(offset).limit(limit)).all()


@router.post(
    "",
    response_model=HeroPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a hero",
    responses={
        400: {"description": "Team does not exist"},
    },
)
def create_hero(
    hero_in: HeroCreate,
    session: SessionDep,
):
    check_team_exists(session, hero_in.team_id)

    hero = Hero.model_validate(hero_in)

    session.add(hero)
    session.commit()
    session.refresh(hero)

    return hero


@router.get(
    "/{hero_id}",
    response_model=HeroPublic,
    summary="Get a hero",
    responses=NOT_FOUND,
)
def read_hero(hero_id: int, session: SessionDep):
    return get_hero_or_404(session, hero_id)


@router.patch(
    "/{hero_id}",
    response_model=HeroPublic,
    summary="Update a hero partially",
    responses={
        **NOT_FOUND,
        400: {"description": "Team does not exist"},
    },
)
def update_hero(
    hero_id: int,
    hero_in: HeroUpdate,
    session: SessionDep,
):
    hero = get_hero_or_404(session, hero_id)

    # Only update fields explicitly sent by the client.
    changes = hero_in.model_dump(exclude_unset=True)

    check_team_exists(session, changes.get("team_id"))

    hero.sqlmodel_update(changes)

    session.add(hero)
    session.commit()
    session.refresh(hero)

    return hero


@router.post("/{hero_id}/missions/{mission_id}", status_code=204)
def assign_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    mission = session.get(Mission, mission_id)
    if not hero or not mission:
        raise HTTPException(status_code=404, detail="Hero or mission not found")
    if mission not in hero.missions:
        hero.missions.append(mission)
        session.add(hero)
        session.commit()


@router.get(
    "/{hero_id}/missions",
    response_model=list[MissionPublic],
)
def list_hero_missions(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero.missions
