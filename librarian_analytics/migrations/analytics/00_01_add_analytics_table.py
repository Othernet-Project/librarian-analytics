SQL = """
create table analytics
(
    session_id varchar primary key,
    timestamp timestamptz not null,
    path varchar not null,
    action integer not null,
    user_agent varchar not null,
    extra_data varchar
);
"""


def up(db, conf):
    db.executescript(SQL)
