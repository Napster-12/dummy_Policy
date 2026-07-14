"""SA Dummy ID Generator - Flask Web System (Icebolethu Group).

A small Flask web application for Icebolethu Group that lets users enter a date
of birth and gender, then generates a valid-format South African ID number for
system testing purposes.

Run:
    python app.py
Then open http://127.0.0.1:8000 in your browser.
"""

from __future__ import annotations

import datetime as _dt
import random as _rnd

from flask import Flask, render_template, request
from sa_id_generator import SAID, generate_id, generate_ids, is_valid

HOST = "127.0.0.1"
PORT = 8000

MIN_QTY = 1
MAX_QTY = 100

DUMMY_FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Dorothy", "Andrew", "Kimberly", "Paul", "Emily", "Joshua", "Donna",
    "Kenneth", "Michelle", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia",
]

DUMMY_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen",
    "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera",
    "Campbell", "Mitchell", "Carter", "Roberts",
]

DUMMY_RELATIONSHIP = ["Spouse", "Parent", "Sibling", "Child", "Partner", "Guardian"]
DUMMY_MARITAL_STATUS = ["Single", "Married", "Divorced", "Widowed", "Separated"]

app = Flask(__name__)


def _make_person() -> dict:
    first = _rnd.choice(DUMMY_FIRST_NAMES)
    last = _rnd.choice(DUMMY_LAST_NAMES)
    return {
        "first_name": first,
        "last_name": last,
        "name": f"{first} {last}",
        "email": f"{first.lower()}.{last.lower()}@test.co.za",
        "marital_status": _rnd.choice(DUMMY_MARITAL_STATUS),
    }


def _make_next_of_kin(birth_date: _dt.date, gender: str) -> dict:
    relationship = _rnd.choice(DUMMY_RELATIONSHIP)
    first = _rnd.choice(DUMMY_FIRST_NAMES)
    last = _rnd.choice(DUMMY_LAST_NAMES)
    nok_gender = _rnd.choice(["Male", "Female"]) if relationship in ("Spouse", "Partner") else gender

    if relationship == "Child":
        nok_birth = _dt.date(
            birth_date.year + _rnd.randint(18, 35),
            _rnd.randint(1, 12),
            _rnd.randint(1, 28),
        )
    elif relationship == "Parent":
        nok_birth = _dt.date(
            birth_date.year - _rnd.randint(20, 40),
            _rnd.randint(1, 12),
            _rnd.randint(1, 28),
        )
    elif relationship == "Sibling":
        nok_birth = _dt.date(
            birth_date.year + _rnd.randint(-10, 10),
            _rnd.randint(1, 12),
            _rnd.randint(1, 28),
        )
    else:
        nok_birth = _dt.date(
            birth_date.year + _rnd.randint(-5, 5),
            _rnd.randint(1, 12),
            _rnd.randint(1, 28),
        )

    nok_birth = min(nok_birth, _dt.date.today())
    nok_id = generate_id(birth_date=nok_birth, gender=nok_gender.lower(), citizen=True)

    return {
        "name": f"{first} {last}",
        "email": f"{first.lower()}.{last.lower()}@test.co.za",
        "dob": nok_birth.isoformat(),
        "gender": nok_gender,
        "relationship": relationship,
        "marital_status": _rnd.choice(DUMMY_MARITAL_STATUS),
        "id_number": nok_id.number,
    }


def _parse_int(value: str, default: int) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _parse_date(value: str) -> _dt.date | None:
    try:
        return _dt.date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _to_dict(sid: SAID) -> dict:
    person = _make_person()
    return {
        "number": sid.number,
        "birth_date": sid.birth_date.isoformat(),
        "gender": sid.gender.title(),
        "citizenship": sid.citizenship,
        "name": person["name"],
        "email": person["email"],
        "marital_status": person["marital_status"],
        "valid": is_valid(sid.number),
        "next_of_kin": _make_next_of_kin(sid.birth_date, sid.gender),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    ctx = {
        "dob": "",
        "gender": "female",
        "citizen": "1",
        "quantity": 1,
        "results": None,
        "error": None,
        "today": _dt.date.today().isoformat(),
    }

    if request.method == "POST":
        dob_raw = request.form.get("dob", "")
        gender = request.form.get("gender", "female")
        citizen = request.form.get("citizen", "1") == "1"
        quantity = _parse_int(request.form.get("quantity", "1"), 1)
        quantity = max(MIN_QTY, min(MAX_QTY, quantity))

        ctx.update(
            dob=dob_raw, gender=gender,
            citizen="1" if citizen else "0", quantity=quantity,
        )

        birth_date = _parse_date(dob_raw)
        if birth_date is None:
            ctx["error"] = "Please enter a valid date of birth."
        elif birth_date > _dt.date.today():
            ctx["error"] = "Date of birth cannot be in the future."
        elif gender not in ("male", "female"):
            ctx["error"] = "Please select a valid gender."
        else:
            ids = generate_ids(quantity, birth_date=birth_date,
                               gender=gender, citizen=citizen)
            ctx["results"] = [_to_dict(sid) for sid in ids]

    return render_template("index.html", **ctx)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
