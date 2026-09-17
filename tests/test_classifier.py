import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import openai
import pytest

import classifier
from models import Resultat, Ticket


def ticket(besked: str, ordre_id: str = "84721") -> Ticket:
    return Ticket("TKT-1", "Maria Kjeldsen", "maria@example.dk", ordre_id, besked, "2026-01-01 10:00")


@pytest.mark.parametrize(
    "besked, kategori, prioritet",
    [
        ("Jeg vil have mine penge tilbage", "Refundering", "Høj"),
        ("Jeg kan ikke logge ind", "Teknisk support", "Medium"),
        ("Hvor er min pakke?", "Levering", "Medium"),
        ("Jeg er virkelig utilfreds med jeres service", "Klage", "Høj"),
        ("Hvad er jeres åbningstider?", "Andet", "Lav"),
    ],
)
def test_local_classifier_maps_message_to_category(besked, kategori, prioritet):
    r = classifier.classify_local(ticket(besked))
    assert (r.kategori, r.prioritet) == (kategori, prioritet)


def test_local_classifier_asks_for_order_number_when_missing():
    r = classifier.classify_local(ticket("Jeg vil have refund", ordre_id=""))
    assert "ordrenummer" in r.svar
    assert r.løsning == "Afventer ordrenummer fra kunden."


def test_local_classifier_fills_in_customer_details():
    r = classifier.classify_local(ticket("Jeg vil have refund"))
    assert r.svar.startswith("Hej Maria,")
    assert "#84721" in r.svar


def test_local_classifier_is_deterministic():
    assert classifier.classify_local(ticket("pakke?")) == classifier.classify_local(ticket("pakke?"))


def _fake_client(content: str) -> MagicMock:
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )
    return client


def test_classify_uses_openai_result_when_valid():
    payload = {
        "kategori": "Klage",
        "prioritet": "Høj",
        "svar": "Hej",
        "løsning": "Eskaleret",
        "tid_sparet_min": 7,
    }
    r = classifier.classify(ticket("Jeg vil have refund"), client=_fake_client(json.dumps(payload)))
    assert r == Resultat(**payload)


def test_classify_falls_back_when_openai_returns_garbage(caplog):
    r = classifier.classify(ticket("Jeg vil have refund"), client=_fake_client("not json"))
    assert r.kategori == "Refundering"
    assert "AI-kald fejlede" in caplog.text


def test_classify_falls_back_when_openai_returns_invalid_category():
    payload = {"kategori": "Spam", "prioritet": "Høj", "svar": "x", "løsning": "y", "tid_sparet_min": 1}
    r = classifier.classify(ticket("pakke?"), client=_fake_client(json.dumps(payload)))
    assert r.kategori == "Levering"


def test_classify_falls_back_on_api_error():
    client = MagicMock()
    client.chat.completions.create.side_effect = openai.APIConnectionError(request=MagicMock())
    r = classifier.classify(ticket("Jeg kan ikke logge ind"), client=client)
    assert r.kategori == "Teknisk support"


def test_classify_without_key_never_touches_network(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(openai, "OpenAI", lambda **kw: pytest.fail("OpenAI client should not be created"))
    assert classifier.classify(ticket("pakke?")).kategori == "Levering"


def test_user_prompt_contains_ticket_fields_and_not_the_system_instructions():
    p = classifier.build_user_prompt(ticket("Hvor er min pakke?", ordre_id=""))
    assert "Maria Kjeldsen" in p
    assert "ikke oplyst" in p
    assert "JSON" not in p


def test_classify_falls_back_when_openai_returns_null_reply_text():
    # str(None) would be "None", which passes the "not empty" check and would be sent to a
    # customer as the reply. A null text field must be rejected like any other bad answer.
    payload = {"kategori": "Klage", "prioritet": "Høj", "svar": None, "løsning": "x", "tid_sparet_min": 3}
    r = classifier.classify(ticket("Jeg er utilfreds"), client=_fake_client(json.dumps(payload)))
    assert r.kategori == "Klage"
    assert "None" not in r.svar


def test_classify_falls_back_when_openai_returns_no_choices():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(choices=[])
    r = classifier.classify(ticket("Hvor er min pakke?"), client=client)
    assert r.kategori == "Levering"


def test_resolve_model_treats_blank_env_as_unset(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "")
    assert classifier.resolve_model() == classifier.DEFAULT_MODEL
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    assert classifier.resolve_model() == "gpt-4o-mini"
    assert classifier.resolve_model("explicit") == "explicit"


def test_make_client_sets_a_short_timeout_and_few_retries():
    # The library default is a 10-minute timeout with 2 retries; a hung API would hold a
    # ticket for half an hour before the local fallback got a chance.
    client = classifier.make_client("sk-test")
    assert client.timeout == classifier.API_TIMEOUT_SECONDS
    assert client.max_retries == classifier.API_MAX_RETRIES
