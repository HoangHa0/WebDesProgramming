from fastapi import APIRouter

from app.database import SessionDep
from app.models import Mission, MissionCreate, MissionPublic


router = APIRouter(
    prefix="/missions",
    tags=["missions"],
)


@router.post(
    "",
    response_model=MissionPublic,
    status_code=201,
    summary="Create a mission",
)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission
