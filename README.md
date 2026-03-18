# Sqorum

## Structure du projet

```text
squorum/
  app/                # streamlit
  squorum_core/
    __init__.py
    io.py             # load/save CSV
    scoring.py        # règles + calculs
    statuses.py       # seuils + labels
    explain.py        # pourquoi ce score
    schemas.py        # dataclasses/pydantic
  data/
    dataset_50_partenaires.csv
    dataset_500_opportunites.csv
  generate_data.py
  tests/
  README.md
  _deprecated/
```

## Lancer l'application

```bash
streamlit run app/Home.py
```
