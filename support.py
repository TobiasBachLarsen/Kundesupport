"""Kører en kø af kundehenvendelser gennem klassificering og udskriver resultatet."""

import logging
import textwrap
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from classifier import classify
from models import Resultat, Ticket

TICKETS_PER_DAG = 50
SEP = "─" * 60


def demo_tickets() -> list[Ticket]:
    nu = datetime.now().strftime("%Y-%m-%d %H:%M")
    return [
        Ticket(
            id="TKT-001",
            navn="Maria Kjeldsen",
            email="maria.kjeldsen@gmail.com",
            ordre_id="84721",
            besked="Hej, jeg vil gerne have mine penge tilbage for ordre 84721. "
            "Produktet var ikke som beskrevet.",
            modtaget=nu,
        ),
        Ticket(
            id="TKT-002",
            navn="Anders Holm",
            email="anders.holm@outlook.dk",
            ordre_id="",
            besked="Jeg kan ikke logge ind på min konto. Adgangskoden virker ikke.",
            modtaget=nu,
        ),
        Ticket(
            id="TKT-003",
            navn="Sofie Bundgaard",
            email="sofie.b@hotmail.com",
            ordre_id="91003",
            besked="Hvornår kommer min pakke? Den skulle have været leveret i går.",
            modtaget=nu,
        ),
    ]


def udskriv(ticket: Ticket, result: Resultat) -> None:
    print(f"\n{SEP}")
    print(f"  {ticket.id}  |  {ticket.navn}  |  {ticket.modtaget}")
    print(SEP)
    print(f"  Besked: {textwrap.fill(ticket.besked, width=56, subsequent_indent='          ')}")
    print(f"\n  Kategori:  {result.kategori}")
    print(f"  Prioritet: {result.prioritet}")
    print(f"  Løsning:   {result.løsning}")
    print("\n  Svar til kunden:")
    print(textwrap.indent(result.svar, "  "))
    print(f"\n  Tid sparet: ~{result.tid_sparet_min} min")


def run(tickets: list[Ticket]) -> int:
    """Behandl alle tickets og returnér samlet estimeret tid sparet i minutter."""
    print(f"\n  {len(tickets)} tickets i kø\n")
    total = 0
    for ticket in tickets:
        result = classify(ticket)
        udskriv(ticket, result)
        total += result.tid_sparet_min

    timer_per_dag = total / len(tickets) * TICKETS_PER_DAG / 60 if tickets else 0
    print(f"\n{SEP}")
    print(f"  Færdig. Tid sparet: ~{total} min")
    print(f"  Skaleret til {TICKETS_PER_DAG} tickets/dag: {timer_per_dag:.1f} timer")
    print(f"{SEP}\n")
    return total


def main() -> None:
    load_dotenv(Path(__file__).parent / ".env")
    logging.basicConfig(level=logging.WARNING, format="  [%(levelname)s] %(message)s")
    run(demo_tickets())


if __name__ == "__main__":
    main()
