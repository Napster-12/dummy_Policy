"""South African (SA) dummy ID number generator for system testing.

Generates valid-format South African ID numbers (13 digits) that pass the
official Luhn-style checksum. These are FOR TESTING ONLY and should never be
used for real identity verification.

SA ID format (13 digits): YYMMDD GSSS C A Z
  YYMMDD - date of birth
  G       - gender digit: 0-4 female, 5-9 male
  SSS     - sequence number (000-999)
  C       - citizenship: 0 = SA citizen, 1 = permanent resident
  A       - race (obsolete) - typically 8 or 9
  Z       - checksum digit (Luhn-style)
"""

from __future__ import annotations

import datetime as _dt
import random as _rnd
from dataclasses import dataclass


@dataclass(frozen=True)
class SAID:
    """A generated South African ID number with its decoded attributes."""

    number: str
    birth_date: _dt.date
    gender: str
    citizenship: str

    def __str__(self) -> str:
        return self.number


def _calculate_checksum(body: str) -> int:
    """Return the SA ID Luhn-style check digit for the first 12 digits."""
    if len(body) != 12:
        raise ValueError("checksum body must be exactly 12 digits")

    odd_sum = sum(int(body[i]) for i in range(0, 12, 2))
    even_concat = "".join(body[i] for i in range(1, 12, 2))
    even_doubled = int(even_concat) * 2
    even_sum = sum(int(d) for d in str(even_doubled))

    total = odd_sum + even_sum
    return (10 - (total % 10)) % 10


def is_valid(id_number: str) -> bool:
    """Return True if the given ID number has a valid format and checksum."""
    if not isinstance(id_number, str) or len(id_number) != 13 or not id_number.isdigit():
        return False

    body, check = id_number[:12], int(id_number[12])
    return _calculate_checksum(body) == check


def generate_id(
    *,
    birth_date: _dt.date | None = None,
    gender: str | None = None,
    citizen: bool = True,
    rng: _rnd.Random | None = None,
) -> SAID:
    """Generate a single dummy SA ID number.

    Args:
        birth_date: Optional date of birth. Defaults to a random date
            between 18 and 90 years ago.
        gender: Optional "male" or "female". Defaults to random.
        citizen: True for SA citizen (0), False for permanent resident (1).
        rng: Optional random.Random instance for deterministic output.

    Returns:
        An SAID instance with the generated number and decoded attributes.
    """
    r = rng or _rnd
    today = _dt.date.today()

    if birth_date is None:
        age = r.randint(18, 90)
        start = today.replace(year=today.year - age)
        days = r.randint(0, 364)
        birth_date = start + _dt.timedelta(days=days)
    else:
        if birth_date > today:
            raise ValueError("birth_date cannot be in the future")

    yy = f"{birth_date.year % 100:02d}"
    mm = f"{birth_date.month:02d}"
    dd = f"{birth_date.day:02d}"

    if gender is None:
        gender = r.choice(("male", "female"))
    gender = gender.lower()
    if gender not in ("male", "female"):
        raise ValueError("gender must be 'male' or 'female'")

    gender_digit = str(r.randint(5, 9) if gender == "male" else r.randint(0, 4))
    sequence = f"{r.randint(0, 999):03d}"
    citizenship_digit = "0" if citizen else "1"
    race_digit = r.choice(("8", "9"))

    body = yy + mm + dd + gender_digit + sequence + citizenship_digit + race_digit
    check = _calculate_checksum(body)
    number = body + str(check)

    return SAID(
        number=number,
        birth_date=birth_date,
        gender=gender,
        citizenship="SA citizen" if citizen else "permanent resident",
    )


def generate_ids(count: int, **kwargs) -> list[SAID]:
    """Generate `count` dummy SA ID numbers as a list."""
    if count < 1:
        raise ValueError("count must be at least 1")
    return [generate_id(**kwargs) for _ in range(count)]


if __name__ == "__main__":
    print("Generated dummy SA ID numbers (for testing only):\n")
    for sid in generate_ids(5):
        print(f"{sid}  | {sid.gender:<6} | {sid.birth_date} | {sid.citizenship}")
