SQL = """
create table stats
(
    id serial primary key,
    user_id varchar not null,
    timestamp timestamptz not null,
    timezone decimal not null,
    path varchar not null,
    action varchar not null,
    os_family varchar not null,
    agent_type integer not null,
    sent boolean not null default false
);
"""


def up(db, conf):
    db.executescript(SQL)
