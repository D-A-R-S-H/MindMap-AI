from datetime import date

from app.revision import schedule_revision

TODAY = date(2026, 11, 1)


def test_weak_revises_after_one_day():
    assert schedule_revision("Weak", TODAY) == (date(2026, 11, 2), "high")


def test_developing_revises_after_three_days():
    assert schedule_revision("Developing", TODAY) == (date(2026, 11, 4), "medium")


def test_strong_revises_after_seven_days():
    assert schedule_revision("Strong", TODAY) == (date(2026, 11, 8), "low")