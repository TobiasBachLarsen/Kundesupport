# kundesupport

Automatiseret behandling af kundehenvendelser. Systemet kategoriserer indkomne tickets, sætter prioritet og genererer et svar klar til afsendelse.

## Hvad det gør

- Klassificerer henvendelsen (refundering, teknisk support, levering, klage)
- Sætter prioritet baseret på indhold
- Genererer et personligt svar til kunden
- Logger intern note om hvad der er gjort

## Kør det

```bash
python3 support.py
```

## Struktur

```
support.py      # pipeline — læser tickets og orkestrerer behandlingen
classifier.py   # kategorisering og svargeneration
```
