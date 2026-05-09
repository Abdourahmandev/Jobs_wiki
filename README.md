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

Le pipeline pilote ReliefWeb est **entierement implemente et teste** (28 tests, 0 echecs).

La seule action bloquante avant la premiere execution reelle est l'approbation
de l'appname `jobs_wiki` aupres de ReliefWeb (demande envoyee le 2026-05-09,
delai de reponse 24h).

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

## Etat actuel (2026-05-09)

### Fait — M1R pipeline pilote ReliefWeb (branch `feat/task-4-pipeline-wiring`)

- [x] Structure monorepo et package Python (`pyproject.toml`, `ingestion/un/`)
- [x] Client ReliefWeb API v2 (`reliefweb_client.py`) — requete, extraction, stockage brut date
- [x] Normalisation silver (`normalize.py`) — schema canonique 16 champs, robustesse aux champs malformes
- [x] Controles qualite (`quality.py`) — doublons, champs manquants, volume
- [x] Orchestration complete (`pipeline.py`) — fetch -> raw JSON -> silver CSV -> resume JSON
- [x] Point d'entree CLI (`scripts/run_reliefweb_pipeline.py`)
- [x] Suite de tests : **28 tests, 0 echecs**
- [x] README mis a jour avec les instructions d'execution

### Bloquant — en attente

- [ ] Approbation de l'appname `jobs_wiki` par ReliefWeb (demande envoyee le 2026-05-09)
  — une fois approuve, mettre a jour `RELIEFWEB_APP_NAME` dans `ingestion/un/reliefweb_client.py`
  et lancer `python scripts/run_reliefweb_pipeline.py` pour valider l'execution reelle

### A venir — M2R et au-dela

- Renforcement des controles qualite silver
- Generation des features gold pour le modele baseline
- Training et evaluation locale (M3R)
- Replication World Bank et BAD (M4R)
- Migration cloud (M5R)

## Execution locale du pipeline pilote

### Prerequis

Enregistrer un `appname` approuve aupres de ReliefWeb:
<https://apidoc.reliefweb.int/parameters#appname>

Puis mettre a jour la constante `RELIEFWEB_APP_NAME` dans
`ingestion/un/reliefweb_client.py` avec votre appname approuve.

### Installation

```bash
python -m pip install -e .[dev]
```

### Lancer le pipeline

```bash
python scripts/run_reliefweb_pipeline.py
```

### Sorties attendues

```
data/raw/reliefweb/<YYYY-MM-DD>/<run-id>.json    # payload brut de l'API
data/silver/reliefweb/<YYYY-MM-DD>/<run-id>.csv  # dataset canonique 16 champs
data/runs/reliefweb/<YYYY-MM-DD>/<run-id>.json   # resume qualite de l'execution
```

### Lancer les tests

```bash
python -m pytest -q
```

## Sources de reference

- Roadmap et milestones: `Plan.md`
- Architecture cible: `docs/architecture.md`
- Design du pilote ReliefWeb:
  `docs/superpowers/specs/2026-05-07-reliefweb-pilot-design.md`

## Diagramme d architecture

- Version editable draw.io: [docs/architecture.drawio](docs/architecture.drawio)
- Version image SVG: [docs/architecture.svg](docs/architecture.svg)
