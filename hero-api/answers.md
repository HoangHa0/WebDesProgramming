# **ANSWERS**

## **Part 1 — SQL Warm-up: Tables, Keys, Relationships**

**❓Question 1.** For each of the fourstatements, which constraint blocked it ( `PRIMARY KEY` , `UNIQUE`, `NOT NULL` , `FOREIGN KEY `) and why?

1. `INSERT INTO team (name, headquarters) VALUES ('Avengers', 'Los Angeles');`

* **Constraint:** `UNIQUE`
* **Why:** The `team` table already has a record with the name 'Avengers', which violates the constraint that all team names must be unique

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

❓ **Question 7.** Compare the CREATE TABLE hero printed by SQLAlchemy with the one you wrote by hand in Part 1. List the differences (types, `NOT NULL `, indexes, constraints).


❓ **Question 8.** Stop and restart the server. Is `CREATE TABLE` printed again? Why? What does `create_all` do when a table already exists?


❓ **Question 9.** `create_all` only knows about models that have been **imported**. Which line in `main.py` makes sure `Hero` and `Team` are registered?


## **Part 5 — CRUD Endpoints for Heroes**
