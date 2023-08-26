from functools import wraps
from flask import Flask, render_template, request
from secrets import token_urlsafe

from . import db_ops, mailing, env

app = Flask(__name__)


def _with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db_ops.session() as ses:
            return func(ses, *args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new_poll")
def new_poll():
    return render_template("new_poll.html")


@app.route("/new_poll/post", methods=["POST"])
@_with_session
def new_poll_post(session):
    form = request.form

    title = form.get("title", None)
    description = form.get("description", None)
    choices = form.get("choices", None)
    email = form.get("email", None)
    participants = form.get("participants", None)
    is_multiple_choice = bool(form.get("isMultipleChoice", False))
    is_anonymous = bool(form.get("isAnonymous", False))

    if not title:
        return render_template("error.html", text="Title is required")

    if not description:
        return render_template("error.html", text="Description is required")

    if not choices or not choices.strip():
        return render_template("error.html", text="Choices are required")

    choices = choices.splitlines()

    if not email:
        return render_template("error.html", text="Email is required")

    if not participants or not participants.strip():
        return render_template("error.html", text="Participants are required")

    participants = _make_participants_list(participants)

    manage_token = token_urlsafe()
    observe_token = token_urlsafe()

    vote_id = db_ops.create_new_poll(
        session,
        title=title,
        description=description,
        manage_token=manage_token,
        observe_token=observe_token,
        creator_email=email,
        is_anon=is_anonymous,
        is_multiple=is_multiple_choice,
    )

    for choice in choices:
        db_ops.add_choice(session, vote_id, choice)

    for part_name, part_email, token in participants:
        if is_anonymous:
            db_ops.add_participant_anon(session, vote_id, token)
        else:
            db_ops.add_participant(session, vote_id, part_name, part_email, token)

    mailing.send_manage_email(email, manage_token, observe_token, title)

    for part_name, part_email, token in participants:
        mailing.send_vote_email(part_email, token, title)

    return render_template(
        "new_poll_success.html",
        base_url=env.BASE_URL,
        observe_token=observe_token,
    )


def _make_participants_list(participants: str) -> list[tuple[str, str, str]]:
    result = []

    for part in participants.splitlines():
        part = part.strip()

        if not part:
            continue

        name_email = part.rsplit(" ", 1)

        if len(name_email) == 1:
            name = name_email[0]
            email = name_email[0]
        else:
            name, email = name_email

        name = name.strip()
        email = email.strip()

        vote_token = token_urlsafe()

        result.append((name, email, vote_token))

    return result


@app.route("/vote/<vote_token>")
@_with_session
def vote(session, vote_token):
    ids = db_ops.get_ids_for_token(session, vote_token)
    if not ids:
        return render_template("error.html", text="Poll not found.")

    poll_id, vote_id = ids

    voted = db_ops.get_voted(session, vote_id)

    if voted is None:
        return render_template("error.html", text="Poll not found.")

    if voted:
        return render_template(
            "error.html", text="You have already voted for this poll."
        )

    poll_info = db_ops.get_poll_info(session, poll_id)

    return render_template(
        "vote.html",
        poll=poll_info,
        vote_token=vote_token,
    )


@app.route("/vote/<vote_token>/post", methods=["POST"])
@_with_session
def vote_post(session, vote_token):
    ids = db_ops.get_ids_for_token(session, vote_token)
    if not ids:
        return "Not found", 404

    poll_id, vote_id = ids

    voted = db_ops.get_voted(session, vote_id)

    if voted != False:
        return render_template(
            "error.html", text="You have already voted for this poll."
        )

    poll_info = db_ops.get_poll_info(session, poll_id)

    if poll_info["is_multiple"]:
        choices = []

        for k, v in request.form.items():
            if v and k.startswith("choice-"):
                choices.append(int(k[7:]))
    else:
        choices = [int(request.form["choice"])]

    for choice in choices:
        cast_id = None if poll_info["is_anon"] else vote_id
        db_ops.cast_vote(session, cast_id, choice)

    db_ops.mark_voted(session, vote_id)

    return "ok", 200


@app.route("/results/<observe_token>")
@_with_session
def results(session, observe_token):
    poll_id = db_ops.get_poll_for_observe(session, observe_token)
    if not poll_id:
        return render_template("error.html", text="Poll not found.")

    poll_info = db_ops.get_poll_info(session, poll_id)

    if not poll_info["is_anon"]:
        full_results = db_ops.get_results_full(session, poll_id)
    else:
        full_results = None

    results = db_ops.get_results_anon(session, poll_id)

    total, participated = db_ops.get_poll_counts(session, poll_id)

    return render_template(
        "results.html",
        poll=poll_info,
        results=results,
        full_results=full_results,
        total=total,
        participated=participated,
    )
