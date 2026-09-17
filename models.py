"""Datamodeller for kundesupport-pipelinen."""

from dataclasses import dataclass
from typing import Any

KATEGORIER = ("Refundering", "Teknisk support", "Levering", "Klage", "Andet")
PRIORITETER = ("Høj", "Medium", "Lav")


@dataclass(frozen=True)
class Ticket:
    id: str
    navn: str
    email: str
    ordre_id: str
    besked: str
    modtaget: str

    @property
    def fornavn(self) -> str:
        dele = self.navn.split()
        return dele[0] if dele else "kunde"


@dataclass(frozen=True)
class Resultat:
    kategori: str
    prioritet: str
    svar: str
    løsning: str
    tid_sparet_min: int

    def __post_init__(self) -> None:
        if self.kategori not in KATEGORIER:
            raise ValueError(f"Ugyldig kategori: {self.kategori!r}")
        if self.prioritet not in PRIORITETER:
            raise ValueError(f"Ugyldig prioritet: {self.prioritet!r}")
        if not isinstance(self.tid_sparet_min, int) or self.tid_sparet_min < 0:
            raise ValueError(f"tid_sparet_min skal være et ikke-negativt heltal: {self.tid_sparet_min!r}")
        if not self.svar.strip():
            raise ValueError("svar må ikke være tomt")

    @classmethod
    def fra_dict(cls, data: dict[str, Any]) -> "Resultat":
        """Byg et Resultat fra et JSON-objekt (typisk fra AI'en) og validér det."""
        manglende = {"kategori", "prioritet", "svar", "løsning", "tid_sparet_min"} - data.keys()
        if manglende:
            raise ValueError(f"Svar mangler felter: {sorted(manglende)}")
        # str(None) er "None", som ville gå igennem tomheds-tjekket og ende hos kunden som
        # svar. Tekstfelterne skal derfor faktisk være tekst, ikke bare noget der kan blive det.
        for felt in ("kategori", "prioritet", "svar", "løsning"):
            if not isinstance(data[felt], str):
                raise ValueError(f"{felt} skal være tekst, fik {type(data[felt]).__name__}")
        tid_raa = data["tid_sparet_min"]
        if isinstance(tid_raa, bool) or not isinstance(tid_raa, int | float | str):
            raise ValueError(f"tid_sparet_min er ikke et tal: {tid_raa!r}")
        try:
            tid = int(tid_raa)
        except (TypeError, ValueError) as e:
            raise ValueError(f"tid_sparet_min er ikke et tal: {tid_raa!r}") from e
        return cls(
            kategori=data["kategori"].strip(),
            prioritet=data["prioritet"].strip(),
            svar=data["svar"],
            løsning=data["løsning"],
            tid_sparet_min=tid,
        )
