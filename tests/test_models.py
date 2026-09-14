import pytest

from models import Resultat, Ticket


def test_fornavn_falls_back_when_name_is_empty():
    assert Ticket("T", "", "a@b.dk", "", "hej", "nu").fornavn == "kunde"
    assert Ticket("T", "Maria Kjeldsen", "a@b.dk", "", "hej", "nu").fornavn == "Maria"


def test_fra_dict_coerces_numeric_string_to_int():
    r = Resultat.fra_dict(
        {"kategori": "Refundering", "prioritet": "Høj", "svar": "x", "løsning": "y", "tid_sparet_min": "12"}
    )
    assert r.tid_sparet_min == 12


@pytest.mark.parametrize(
    "bad",
    [
        {"kategori": "Spam", "prioritet": "Høj", "svar": "x", "løsning": "y", "tid_sparet_min": 1},
        {"kategori": "Klage", "prioritet": "Kritisk", "svar": "x", "løsning": "y", "tid_sparet_min": 1},
        {"kategori": "Klage", "prioritet": "Høj", "svar": "", "løsning": "y", "tid_sparet_min": 1},
        {"kategori": "Klage", "prioritet": "Høj", "svar": "x", "løsning": "y", "tid_sparet_min": "mange"},
        {"kategori": "Klage", "prioritet": "Høj", "svar": "x", "løsning": "y", "tid_sparet_min": -3},
        {"kategori": "Klage", "prioritet": "Høj", "svar": "x"},
    ],
)
def test_fra_dict_rejects_invalid_ai_output(bad):
    with pytest.raises(ValueError):
        Resultat.fra_dict(bad)
