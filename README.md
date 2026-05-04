# Jobs_wiki

Plateforme de matching CV <-> offres d'emploi d'organismes internationaux
(Banque Mondiale, BAD, ONU, etc.).

## Vision

Construire une plateforme web ou un candidat depose son CV et recoit une liste
personnalisee d'offres pertinentes, avec des rapports sur le marche de l'emploi.

Approche projet: livrer un pipeline end-to-end fonctionnel rapidement, puis
ameliorer chaque couche (data, ML, API, frontend, reporting).

## Architecture cible (resume)

- Ingestion quotidienne des offres (API/RSS/scraping si necessaire)
- Stockage ADLS Gen2 en Bronze / Silver / Gold
- Base operationnelle PostgreSQL + pgvector pour offres actives et embeddings
- Traitements ML sur Databricks + tracking MLflow
- API de matching avec FastAPI
- Frontend demo avec Streamlit
- Reporting marche avec Power BI

## Structure du repo

```
.
├── .github/workflows/
├── docs/
│   └── adr/
├── infra/
├── ingestion/
│   ├── worldbank/
│   ├── afdb/
│   └── un/
├── databricks/
│   ├── notebooks/
│   │   ├── silver/
│   │   ├── gold/
│   │   ├── labeling/
│   │   └── training/
│   └── jobs/
├── ml/
├── api/
├── frontend/
├── powerbi/
└── scripts/
```

## Etat actuel (au 2026-05-03)

Ce qui est deja fait:

- Repository clone et configure dans le dossier existant
- Structure monorepo initiale creee selon le plan
- Fichier de plan disponible: `Plan.md`

Ce qui vient ensuite (M0):

- Completer la documentation architecture dans `docs/`
- Ajouter les ADR (stack, IaC)
- Mettre en place pre-commit (ruff, black, mypy)
- Ajouter une CI baseline dans `.github/workflows/`

## Source de reference

Le planning complet et les milestones sont definis dans `Plan.md`.
