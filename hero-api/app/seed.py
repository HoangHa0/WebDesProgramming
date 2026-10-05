from sqlmodel import Session, SQLModel, select

from app.database import engine
from app.models import Hero, Mission, Team


def seed():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if session.exec(select(Team)).first():
            print("Database already seeded.")
            return
        avengers = Team(name="Avengers", headquarters="New York")
        xmen = Team(name="X-Men", headquarters="Westchester")
        sokovia = Mission(title="Battle of Sokovia")
        genosha = Mission(title="Genosha Rescue")
        session.add_all(
            [
                Hero(
                    name="Tony",
                    age=45,
                    secret_name="Iron Man",
                    team=avengers,
                    missions=[sokovia],
                ),
                Hero(
                    name="Natasha",
                    age=35,
                    secret_name="Black Widow",
                    team=avengers,
                    missions=[sokovia],
                ),
                Hero(
                    name="Logan",
                    age=150,
                    secret_name="Wolverine",
                    team=xmen,
                    missions=[genosha],
                ),
                Hero(
                    name="Rogue",
                    age=25,
                    secret_name="Anna Marie",
                    team=xmen,
                    missions=[genosha],
                ),
                Hero(
                    name="Peter",
                    age=16,
                    secret_name="Spider-Man",
                    missions=[sokovia, genosha],
                ),
            ]
        )
        session.commit()
        print("Seeded.")


if __name__ == "__main__":
    seed()
