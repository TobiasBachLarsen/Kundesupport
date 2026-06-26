import json

_RESPONSES: dict[str, dict] = {
    "refund": {
        "kategori": "Refundering",
        "prioritet": "Høj",
        "svar": (
            "Hej {navn},\n\n"
            "Tak fordi du kontakter os. Jeg kan se, at du ønsker en refundering på ordre #{ordre}.\n\n"
            "Jeg har behandlet din anmodning, og beløbet vil blive tilbageført til din betalingsmetode "
            "inden for 3-5 hverdage.\n\n"
            "Har du spørgsmål, er du altid velkommen til at skrive igen.\n\n"
            "Med venlig hilsen,\nKundesupport"
        ),
        "løsning": "Refundering godkendt og behandlet automatisk.",
        "tid_sparet_min": 12,
    },
    "login": {
        "kategori": "Teknisk support",
        "prioritet": "Medium",
        "svar": (
            "Hej {navn},\n\n"
            "Det lyder til at du har problemer med at logge ind. Lad os få det løst hurtigt.\n\n"
            "Prøv følgende:\n"
            "1. Klik på 'Glemt adgangskode' og følg trinene.\n"
            "2. Tjek at din e-mail er stavet korrekt: {email}\n"
            "3. Ryd browserens cache og prøv igen.\n\n"
            "Virker ingen af delene, sender vi dig et midlertidigt link.\n\n"
            "Med venlig hilsen,\nKundesupport"
        ),
        "løsning": "Selvhjælpstrin sendt. Eskaleres ved manglende svar inden 24 timer.",
        "tid_sparet_min": 8,
    },
    "levering": {
        "kategori": "Levering",
        "prioritet": "Medium",
        "svar": (
            "Hej {navn},\n\n"
            "Jeg har tjekket din ordre #{ordre} og kan se den er afsendt.\n\n"
            "Forventet levering: 1-2 hverdage. Din sporingskode er: DK{ordre}TRK.\n\n"
            "Hvis pakken ikke ankommer inden for fristen, kontakter du os igen, "
            "så finder vi en løsning med det samme.\n\n"
            "Med venlig hilsen,\nKundesupport"
        ),
        "løsning": "Sporingsinfo sendt til kunden.",
        "tid_sparet_min": 6,
    },
    "klage": {
        "kategori": "Klage",
        "prioritet": "Høj",
        "svar": (
            "Hej {navn},\n\n"
            "Tak for at du skriver til os — jeg er ked af at høre om din oplevelse, "
            "og jeg tager din henvendelse meget seriøst.\n\n"
            "Jeg har videresendt dit spørgsmål til vores specialistteam, som vil kontakte "
            "dig direkte inden for 2 timer.\n\n"
            "Vi sætter stor pris på din tålmodighed.\n\n"
            "Med venlig hilsen,\nKundesupport"
        ),
        "løsning": "Eskaleret til specialistteam med høj prioritet.",
        "tid_sparet_min": 5,
    },
}


def _intent(besked: str) -> str:
    b = besked.lower()
    if any(w in b for w in ("refund", "penge tilbage", "annuller", "tilbagebetaling")):
        return "refund"
    if any(w in b for w in ("log ind", "logge ind", "login", "adgangskode", "password")):
        return "login"
    if any(w in b for w in ("pakke", "levering", "leveret", "sporing", "forsendelse")):
        return "levering"
    return "klage"


def classify(prompt: str) -> dict:
    fields: dict[str, str] = {}
    for line in prompt.split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            fields[key.strip().lower()] = val.strip()

    besked = fields.get("besked", "")
    navn   = fields.get("kundens navn", "").split()[0]
    email  = fields.get("kundens e-mail", "")
    ordre  = fields.get("ordre-id", "")

    entry = _RESPONSES[_intent(besked)]
    return {
        "kategori":       entry["kategori"],
        "prioritet":      entry["prioritet"],
        "svar":           entry["svar"].format(navn=navn, email=email, ordre=ordre),
        "løsning":        entry["løsning"],
        "tid_sparet_min": entry["tid_sparet_min"],
    }
