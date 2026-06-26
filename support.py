import textwrap
import time
from dataclasses import dataclass
from datetime import datetime

from classifier import classify


@dataclass
class Ticket:
    id: str
    navn: str
    email: str
    ordre_id: str
    besked: str
    modtaget: str


TICKETS = [
    Ticket(
        id="TKT-001",
        navn="Maria Kjeldsen",
        email="maria.kjeldsen@gmail.com",
        ordre_id="84721",
        besked="Hej, jeg vil gerne have mine penge tilbage for ordre 84721. Produktet var ikke som beskrevet.",
        modtaget=datetime.now().strftime("%Y-%m-%d %H:%M"),
    ),
    Ticket(
        id="TKT-002",
        navn="Anders Holm",
        email="anders.holm@outlook.dk",
        ordre_id="",
        besked="Jeg kan ikke logge ind på min konto. Adgangskoden virker ikke.",
        modtaget=datetime.now().strftime("%Y-%m-%d %H:%M"),
    ),
    Ticket(
        id="TKT-003",
        navn="Sofie Bundgaard",
        email="sofie.b@hotmail.com",
        ordre_id="91003",
        besked="Hvornår kommer min pakke? Den skulle have været leveret i går.",
        modtaget=datetime.now().strftime("%Y-%m-%d %H:%M"),
    ),
]


def behandl(ticket: Ticket) -> dict:
    prompt = f"""Du er en venlig og professionel kundesupport-medarbejder.

Kundens navn: {ticket.navn}
Kundens e-mail: {ticket.email}
Ordre-ID: {ticket.ordre_id or "ikke oplyst"}
Besked: {ticket.besked}

Returner JSON med følgende felter:
- kategori: én af [Refundering, Teknisk support, Levering, Klage]
- prioritet: én af [Høj, Medium, Lav]
- svar: et kort, professionelt svar på dansk direkte til kunden
- løsning: en intern note om hvad der er gjort
- tid_sparet_min: estimeret minutter sparet vs. manuel behandling (heltal)
"""
    return classify(prompt)


def udskriv(ticket: Ticket, result: dict) -> None:
    sep = "─" * 60
    print(f"\n{sep}")
    print(f"  {ticket.id}  |  {ticket.navn}  |  {ticket.modtaget}")
    print(sep)
    print(f"  Besked: {textwrap.fill(ticket.besked, width=56, subsequent_indent='          ')}")
    print(f"\n  Behandler", end="", flush=True)
    time.sleep(0.8)
    print(f" ✓")
    print(f"\n  Kategori:  {result['kategori']}")
    print(f"  Prioritet: {result['prioritet']}")
    print(f"  Løsning:   {result['løsning']}")
    print(f"\n  Svar til kunden:")
    for linje in result["svar"].split("\n"):
        print(f"  {linje}")
    print(f"\n  Tid sparet: ~{result['tid_sparet_min']} min")


def run() -> None:
    print(f"\n  {len(TICKETS)} tickets i kø\n")

    total = 0
    for ticket in TICKETS:
        result = behandl(ticket)
        udskriv(ticket, result)
        total += result["tid_sparet_min"]

    print("\n" + "─" * 60)
    print(f"  Færdig. Tid sparet: ~{total} min")
    print(f"  Skaleret til 50 tickets/dag → {round(total / len(TICKETS) * 50 / 60, 1)} timer")
    print("─" * 60 + "\n")


if __name__ == "__main__":
    run()
