# **ANSWERS**

## **Part 1 — SQL Warm-up: Tables, Keys, Relationships**

**❓Question 1.** For each of the four statements, which constraint blocked it ( `PRIMARY KEY` , `UNIQUE`, `NOT NULL` , `FOREIGN KEY` ) and why?

1. `INSERT INTO team (name, headquarters) VALUES ('Avengers', 'Los Angeles');`

* **Constraint:** `UNIQUE`
* **Why:** The `team` table already has a record with the name 'Avengers', which violates the constraint that all team names must be unique.

2. `INSERT INTO hero (name, team_id) VALUES ('Ghost', 99);`

* **Constraint:** `FOREIGN KEY`
* **Why:** The value `99` for `team_id` does not exist in the `team` table.

3. `INSERT INTO hero (age) VALUES (30);`

* **Constraint:** `NOT NULL`
* **Why:** The query attempts to insert a null value into the `name` column, which is explicitly required and cannot be left empty.

4. `DELETE FROM team WHERE id = 1;`

* **Constraint:** `FOREIGN KEY`
* **Why:** You cannot delete the team with `id=1` because there are still records in the `hero` table that refer to this team ID.

**❓Question 2.** The relationship team → hero is **one-to-many**. Why is the foreign key on `hero` and not on
`team`?

Because it is a one-to-many relationship. A single hero belongs to exactly one team, so the `hero` table only needs one `team_id` column to store this connection. If the foreign key were on the `team` table, a single team row would have to store multiple hero IDs, which goes against standard relational database structure.

**❓Question 3.** Heroes can go on many missions and a mission has many heroes (**many-to-many**). Sketch the tables you need (names, columns, PK, FK). Hint: you need a **link table**.

* **`hero`** : Columns must include an `id` (Primary Key).
* **`mission`** : Columns must include an `id` (Primary Key) and a `title`.
* **`heromissionlink`** : This is the link table that connects the two. It contains a `hero_id` (Foreign Key pointing to `hero.id`) and a `mission_id` (Foreign Key pointing to `mission.id`). Together, these two foreign keys create a composite primary key.

## **Part 2 — Project Setup and DATABASE_URL**

**❓Question 4.** Why read the URL from an environment variable instead of writing it in `database.py`? Give two reasons.

* **Security:** It prevents sensitive credentials, such as database passwords, from being hardcoded into the source code and accidentally exposed in version control systems.
* **Flexibility:** It allows the application to seamlessly switch between different environments (like local development, testing, and production) without requiring any modifications to the code.

## **Part 3 — Define the Models**

❓ **Question 5.** Why is `id` typed `int | None` with `default=None`, when every row in the database has an id?

The `id` field is defined this way because a model instance is initially created in the application's memory before it is saved. The database automatically generates and assigns the actual ID only during the insertion process, meaning the ID must be allowed to be `None` until the record is successfully saved.

❓ **Question 6.** Which attributes of `Hero` become **columns**, and which one does not? What is `back_populates` for?

* **Columns:** The standard attributes (`id`, `name`, `age`, `secret_name`, and `team_id`) become physical columns in the database table.
* **Not a column:** The `team` attribute, defined using `Relationship()`, does not become a database column.
* **`back_populates`:** This parameter explicitly links the two sides of a relationship together (such as `Hero.team` and `Team.heroes`). It tells the system to keep these models synchronized in memory, ensuring that modifying the relationship on one model automatically updates the linked attribute on the other.

## **Part 4 — Engine, Tables and Session**

❓ **Question 7.** Compare the CREATE TABLE hero printed by SQLAlchemy with the one you wrote by hand in Part 1. List the differences (types, `NOT NULL`, indexes, constraints).

* **Types:** Same (`VARCHAR`, `INTEGER`, `SERIAL` for `id`).
* **Columns:** SQLAlchemy adds the extra `secret_name VARCHAR NOT NULL` column, and the order differs (`name, age, team_id, id, secret_name`) because the base class fields come first.
* **`NOT NULL`:** `id SERIAL NOT NULL` is explicit, while the hand-written `id SERIAL PRIMARY KEY` implies it.
* **Indexes:** SQLAlchemy also runs `CREATE INDEX ix_hero_name ON hero (name)` because of `Field(index=True)`; the hand-written table had no index on `name`.
* **Constraints:** `PRIMARY KEY (id)` and `FOREIGN KEY(team_id) REFERENCES team (id)` are declared at the end of the table instead of inline.

❓ **Question 8.** Stop and restart the server. Is `CREATE TABLE` printed again? Why? What does `create_all` do when a table already exists?

No. The log only shows two `SELECT ... FROM pg_catalog.pg_class` queries (one for `team`, one for `hero`) followed by `COMMIT`. `create_all` first checks which tables already exist in the database and only creates the missing ones. Existing tables are skipped and never modified.

❓ **Question 9.** `create_all` only knows about models that have been **imported**. Which line in `main.py` makes sure `Hero` and `Team` are registered?

The line `from app.models import Hero, ..., Team, ...`. Importing the classes registers their tables in `SQLModel.metadata`, which `create_all` uses.

## **Part 5 — CRUD Endpoints for Heroes**

❓ **Question 10.** Comment out `session.commit()` in `create_hero` and create a hero. What does the response look like, and is the row in the database (`SELECT * FROM hero;`)? Put the line back. What does add() do on its own, and why do we need `refresh()`?

* **Response:** `500 Internal Server Error` with a plain-text body (`Internal Server Error`) instead of the usual JSON hero, because `refresh()` fails on an object that was never saved.
* **Database:** `SELECT * FROM hero;` returns 0 rows, since nothing was committed.
* **`add()`:** It only places the object in the session as pending; nothing is saved until `commit()`.
* **`refresh()`:** It reloads the object from the database after the commit, so the generated `id` is available for the response.

❓ **Question 11.** Which SQL statement does `echo=True` print for `PATCH` with body `{"age": 17}`? Does it update every column or only `age`? Why?

`UPDATE hero SET age=%(age)s::INTEGER WHERE hero.id = %(hero_id)s::INTEGER` with parameters `{'age': 17, 'hero_id': 2}`. It updates only `age`, because `model_dump(exclude_unset=True)` keeps only the fields the client sent, and SQLAlchemy only updates the attributes that actually changed.

❓ **Question 12.** Look at the JSON returned by `GET /heroes/{id}`. Is `secret_name` there? Which line of code is responsible?

No. The `response_model=HeroPublic` in the `@app.get("/heroes/{hero_id}", ...)` decorator filters the response to the fields of `HeroPublic`, which does not include `secret_name`.

## **Part 6 — Teams, Filtering, Pagination and Errors**

❓ **Question 13.** Call `GET /heroes?min_age=18&team_id=1` and copy the `SELECT` printed by `echo=True`. Where do the values `18` and `1` appear? Why is this safe against SQL injection?

```sql
SELECT hero.name, hero.age, hero.team_id, hero.id, hero.secret_name
FROM hero
WHERE hero.age >= %(age_1)s::INTEGER AND hero.team_id = %(team_id_1)s::INTEGER ORDER BY hero.id
LIMIT %(param_1)s::INTEGER OFFSET %(param_2)s::INTEGER
```

The values `18` and `1` do not appear in the SQL text; they appear only in the parameters dictionary `{'age_1': 18, 'team_id_1': 1, 'param_1': 10, 'param_2': 0}`. The driver sends them separately from the query, so user input is always treated as data and never as SQL code.

❓ **Question 14.** Why filter in the database instead of `[h for h in session.exec(select(Hero)).all() if h.age >= 18]`?

The database returns only the matching rows (and can use indexes), while the Python version loads the entire table into memory first, which is slow and does not scale. It would also crash on heroes with `age = None`.

## **Part 7 — Many-to-Many: Missions**

❓ **Question 15.** On restart, `create_all` did create `mission` and `heromissionlink`. In Part 4 it did nothing for `hero`. What is the rule?

`create_all` creates only the tables that do not exist yet. It never alters or drops existing tables. `mission` and `heromissionlink` were new, while `hero` already existed.

## **Part 8 — Seed Script**

❓ **Question 16.** You never set `team_id` in the seed script. Read the `echo=True` output: in which order were the `INSERT`s executed, and how did `hero.team_id` get its value?

* **Order:** `INSERT INTO team` (both teams in one statement), then `INSERT INTO mission`, then `INSERT INTO hero`, and finally `INSERT INTO heromissionlink`.
* **`team_id`:** SQLAlchemy sorts the inserts by foreign key dependencies. The `INSERT INTO team ... RETURNING team.id` gives back the generated ids, and the relationship (`team=avengers`) copies them into `hero.team_id` before `INSERT INTO hero` runs (the log shows `'team_id__0': 1`, `'team_id__3': 2`, and `None` for Peter, who has no team). The link rows are filled the same way with the new hero and mission ids.

## **Part 9 — Migrations with Alembic**

❓ **Question 17.** Is there a `power` column? Now call `GET /heroes`. What happens and why? Why is "drop all tables and run `create_all` again" not an acceptable fix in production?

* **Column:** No, because `create_all` does not alter existing tables.
* **`GET /heroes`:** It fails with `500 Internal Server Error` (`column hero.power does not exist`), because the model's `SELECT` includes `power` but the table does not have it.
* **Why not drop all:** It would delete all existing production data. We need an incremental schema change that keeps the data.

❓ **Question 18.** Copy the bodies of `upgrade()` and `downgrade()`. What does each one do?

```python
def upgrade() -> None:
    op.add_column('hero', sa.Column('power', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column('hero', 'power')
```

* **`upgrade()`:** Adds the nullable `power` column to the `hero` table.
* **`downgrade()`:** Removes the `power` column, undoing the migration.

❓ **Question 19.** Where does Alembic store "which revision this database is at"? Why should the `migrations/` folder be committed to Git?

* **Storage:** In the `alembic_version` table inside the same database.
* **Git:** It is the versioned history of the schema. Committing it lets every teammate and environment rebuild the same schema with `alembic upgrade head`.

❓ **Question 20.** Rename `secret_name` to `alias` in the model and run `revision --autogenerate` (do not apply it). What did Alembic generate? Why is that dangerous for existing data, and how would you fix the script?

* **Generated:** `op.add_column('hero', sa.Column('alias', ..., nullable=False))` followed by `op.drop_column('hero', 'secret_name')`, because Alembic cannot detect renames. It sees one new column and one missing column.
* **Danger:** Applying it deletes all existing `secret_name` data, and adding a `NOT NULL` column to a table that already has rows fails.
* **Fix:** Replace both operations with `op.alter_column('hero', 'secret_name', new_column_name='alias')`, and the reverse in `downgrade()`.
