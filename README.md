# Jobs_wiki

Plateforme de matching CV <-> offres d'emploi d'organismes internationaux
(Banque Mondiale, BAD, ONU, etc.).

## Vision

Construire une plateforme web ou un candidat depose son CV et recoit une liste
personnalisee d'offres pertinentes, avec des rapports sur le marche de l'emploi.

## Direction actuelle

Le projet est actuellement en mode **local-first**.

L'objectif n'est pas encore de construire l'API, le frontend ou l'infrastructure
cloud. La priorite immediate est de prouver un pipeline local, reproductible, sur
une seule source reelle avant d'etendre le scope.

### Source pilote

- **ReliefWeb Jobs**: <https://reliefweb.int/jobs>
- API: <https://api.reliefweb.int/>

## Priorite immediate

Le prochain milestone est un **pipeline pilote ReliefWeb** qui doit:

1. recuperer des offres reelles depuis ReliefWeb
2. stocker les donnees brutes localement avec une partition datee
3. produire un dataset silver avec un schema canonique
4. executer des controles qualite minimaux
5. generer un resume d'execution reproductible

## Hors scope pour l'instant

- API FastAPI
- Frontend Streamlit
- Reporting Power BI
- Infrastructure cloud
- Orchestration GitHub Actions / Azure
- Multi-sources
- Training modele tant que la base data n'est pas stabilisee

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

## Etat actuel

Ce qui est deja fait:

- structure monorepo initiale creee
- roadmap locale recentree dans `Plan.md`
- architecture cible documentee dans `docs/architecture.md`
- design du pilote ReliefWeb documente dans
  `docs/superpowers/specs/2026-05-07-reliefweb-pilot-design.md`

Ce qui vient ensuite:

- definir le contrat d'ingestion ReliefWeb
- implementer le pipeline local raw -> silver
- ajouter les controles qualite minimaux
- valider une execution reproductible sur donnees reelles

## Sources de reference

- Roadmap et milestones: `Plan.md`
- Architecture cible: `docs/architecture.md`
- Design du pilote ReliefWeb:
  `docs/superpowers/specs/2026-05-07-reliefweb-pilot-design.md`

## Diagramme d architecture

- Version editable draw.io: [docs/architecture.drawio](docs/architecture.drawio)
- Version image SVG: [docs/architecture.svg](docs/architecture.svg)
