# kundesupport

Automatiseret behandling af kundehenvendelser. Systemet kategoriserer indkomne tickets, sætter prioritet og genererer et svarudkast klar til gennemsyn.

## Hvad det gør

- Klassificerer henvendelsen (Refundering, Teknisk support, Levering, Klage, Andet)
- Sætter prioritet (Høj, Medium, Lav)
- Genererer et personligt svarudkast til kunden
- Logger en intern note om, hvad der er gjort
- Validerer alt AI-output mod en fast skema, og falder tilbage til en regelbaseret klassificering hvis AI-kaldet fejler eller svarer ugyldigt

## Kør det

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt   # eller requirements.txt uden test-værktøjer
python support.py
```

Sæt `OPENAI_API_KEY` i `.env` for at bruge rigtig AI-klassificering. `OPENAI_MODEL` kan sætte modellen (standard `gpt-4o`). Uden nøgle bruger systemet automatisk den lokale, regelbaserede klassificering, som er deterministisk og ikke koster API-credits.

**Tjek koden:**

```bash
pytest
ruff check . && ruff format --check .
```

## Struktur

```
support.py      # pipeline: demo-tickets, orkestrering, udskrift
classifier.py   # classify_openai (AI), classify_local (regler), classify (vælger og falder tilbage)
models.py       # Ticket og Resultat, inkl. validering af AI-output
tests/          # 22 tests af regelmotor, validering og fallback (AI-kald mockes)
```

## Designvalg

- **Struktureret input hele vejen.** Ticketen sendes som objekt til klassificeringen; prompten bygges først lige før AI-kaldet. Den lokale motor læser felterne direkte i stedet for at parse en prompt tilbage til data.
- **AI-output er upålideligt input.** `Resultat.fra_dict` afviser ukendte kategorier, ugyldige prioriteter, tomme svar og ikke-numeriske tidsestimater. Alt ugyldigt ender i fallback, aldrig i et crash.
- **Kundebeskeden er utroet tekst.** System-prompten instruerer modellen i at behandle beskeden som data, ikke som instruktioner.
- **Ukendte henvendelser er "Andet", ikke "Klage".** En henvendelse der ikke matcher nogen regel sendes til manuel behandling med lav prioritet i stedet for at blive eskaleret som en klage.
- **Fallback-svarene lover ikke noget, koden ikke har gjort.** Svarudkastene siger "registreret" og "bestilt opslag", ikke "behandlet" eller "afsendt".

## Begrænsninger

Det er en demo. Tallet for "tid sparet" er et skøn, ikke en måling, og svarudkastene skal læses af et menneske før afsendelse.
