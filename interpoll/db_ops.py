from typing import Optional

import psycopg2

from . import env


def session():
    return psycopg2.connect(env.DATABASE_DSN)


def create_new_poll(
    session: "psycopg2.connection",
    title: str,
    description: str,
    manage_token: str,
    observe_token: str,
    creator_email: str,
    is_anon: bool,
    is_multiple: bool,
) -> int:
    with session.cursor() as cur:
        cur.execute(
            """INSERT INTO
                polls (
                    title,
                    "desc",
                    manage_token,
                    observe_token,
                    creator_email,
                    is_anon,
                    is_multiple
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id""",
            (
                title,
                description,
                manage_token,
                observe_token,
                creator_email,
                is_anon,
                is_multiple,
            ),
        )

        res = cur.fetchone()
        if res is None:
            raise Exception("Failed to create poll")

    return res[0]


def add_choice(session, poll_id: int, title: str):
    with session.cursor() as cur:
        cur.execute(
            """INSERT INTO
                choices (poll_id, title)
                VALUES (%s, %s)""",
            (poll_id, title),
        )


def add_participant(session, poll_id: int, name: str, email: str, token: str):
    with session.cursor() as cur:
        cur.execute(
            """INSERT INTO
                participants (poll_id, voter_name, voter_email, vote_token)
                VALUES (%s, %s, %s, %s)""",
            (poll_id, name, email, token),
        )


def add_participant_anon(session, poll_id: int, token: str):
    with session.cursor() as cur:
        cur.execute(
            """INSERT INTO
                participants (poll_id, vote_token)
                VALUES (%s, %s)""",
            (poll_id, token),
        )


def get_poll_info(session, poll_id: int) -> dict:
    choices = get_poll_choices(session, poll_id)

    with session.cursor() as cur:
        cur.execute(
            """
            SELECT title, "desc", is_anon, is_multiple
            FROM polls
            WHERE id = %s
            """,
            (poll_id,),
        )

        res = cur.fetchone()
        if res is None:
            return {}

        return {
            "title": res[0],
            "desc": res[1],
            "is_anon": res[2],
            "is_multiple": res[3],
            "choices": choices,
        }


def get_poll_choices(session, poll_id: int) -> list[tuple[int, str]]:
    with session.cursor() as cur:
        cur.execute(
            """
            SELECT id, title
            FROM choices
            WHERE poll_id = %s
            """,
            (poll_id,),
        )

        res = cur.fetchall()
        if res is None:
            return []

        return res


def get_vote_id(session, vote_token: str) -> Optional[int]:
    with session.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM cast_votes
            WHERE vote_token = %s
            """,
            (vote_token,),
        )

        res = cur.fetchone()
        if res is None:
            return None

        return res[0]


def get_voted(session, vote_id: int) -> Optional[bool]:
    with session.cursor() as cur:
        cur.execute(
            """
            SELECT voted
            FROM participants
            WHERE id = %s
            """,
            (vote_id,),
        )

        res = cur.fetchone()
        if res is None:
            return None

        return res[0]


def get_ids_for_token(session, vote_token: str) -> Optional[tuple[int, int]]:
    with session.cursor() as cur:
        cur.execute(
            """
            SELECT id, poll_id
            FROM participants
            WHERE vote_token = %s
            """,
            (vote_token,),
        )

        res = cur.fetchone()
        if res is None:
            return None

        return res[1], res[0]


def get_poll_for_observe(session, observe_token: str) -> Optional[int]:
    with session.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM polls
            WHERE observe_token = %s
            """,
            (observe_token,),
        )

        res = cur.fetchone()
        if res is None:
            return None

        return res[0]


def cast_vote(session, vote_id: Optional[int], choice_id: int):
    with session.cursor() as cur:
        cur.execute(
            """
            INSERT INTO cast_votes (vote_id, choice_id)
            VALUES (%s, %s)
            """,
            (vote_id, choice_id),
        )


def mark_voted(session, vote_id: int):
    with session.cursor() as cur:
        cur.execute(
            """
            UPDATE participants
            SET voted = true
            WHERE id = %s
            """,
            (vote_id,),
        )


def get_results_full(session, poll_id: int) -> list[tuple[int, str, int, str]]:
    with session.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.title, p.id, p.voter_name
            FROM choices c, participants p, cast_votes cv
            WHERE c.poll_id = %s
              AND p.poll_id = %s
              AND cv.vote_id = p.id
              AND cv.choice_id = c.id""",
            (poll_id, poll_id),
        )

        res = cur.fetchall()
        if res is None:
            return []

        return res


def get_results_anon(session, poll_id: int) -> list[tuple[int, str, int]]:
    with session.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.title, COUNT(cv.id)
            FROM choices c, cast_votes cv
            WHERE c.poll_id = %s
              AND cv.choice_id = c.id
            GROUP BY c.id, c.title""",
            (poll_id,),
        )

        res = cur.fetchall()
        if res is None:
            return []

        return res


def get_poll_counts(session, poll_id: int) -> tuple[int, int]:
    with session.cursor() as cur:
        cur.execute(
            """
            SELECT 
                (SELECT COUNT(*) FROM participants WHERE poll_id = %s),
                (SELECT COUNT(*) FROM participants WHERE poll_id = %s AND voted)
            """,
            (poll_id, poll_id),
        )

        res = cur.fetchone()
        if res is None:
            return 0, 0

        return res[0], res[1]
