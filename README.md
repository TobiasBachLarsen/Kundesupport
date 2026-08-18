# kundesupport

Automatiseret behandling af kundehenvendelser. Systemet kategoriserer indkomne tickets, sætter prioritet og genererer et svar klar til afsendelse.

## Hvad det gør

- Klassificerer henvendelsen (refundering, teknisk support, levering, klage)
- Sætter prioritet baseret på indhold
- Genererer et personligt svar til kunden
- Logger intern note om hvad der er gjort

## Kør det

```bash
pip install -r requirements.txt
python3 support.py
```

Sæt en `OPENAI_API_KEY` i `.env` for at bruge rigtig AI-klassificering (GPT-4o). Uden nøgle falder systemet automatisk tilbage til en lokal, regelbaseret klassificering — nyttigt til udvikling og demo uden at bruge API-credits.

## Struktur

```
support.py      # pipeline — læser tickets og orkestrerer behandlingen
classifier.py   # kategorisering og svargeneration (OpenAI, med lokal fallback)
```
