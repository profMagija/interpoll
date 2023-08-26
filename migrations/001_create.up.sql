CREATE TABLE polls (
    id            SERIAL             PRIMARY KEY,
    title         TEXT      NOT NULL,
    "desc"        TEXT      NOT NULL,
    manage_token  TEXT      NOT NULL UNIQUE,
    observe_token TEXT      NOT NULL UNIQUE,
    creator_email TEXT      NOT NULL,
    is_anon       BOOLEAN   NOT NULL DEFAULT FALSE,
    is_multiple   BOOLEAN   NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE choices (
    id      SERIAL           PRIMARY KEY,
    poll_id INTEGER NOT NULL REFERENCES polls(id),
    title   TEXT    NOT NULL
);

CREATE TABLE participants (
    id          SERIAL           PRIMARY KEY,
    poll_id     INTEGER NOT NULL REFERENCES polls(id),
    vote_token  TEXT    NOT NULL UNIQUE,
    voter_name  TEXT,
    voter_email TEXT,
    voted       BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE cast_votes (
    id        SERIAL           PRIMARY KEY,
    vote_id   INTEGER          REFERENCES participants(id),
    choice_id INTEGER NOT NULL REFERENCES choices(id)
)