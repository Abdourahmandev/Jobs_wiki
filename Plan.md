# Plateforme de Matching CV ↔ Offres d'Emploi (Organismes Internationaux)

> **Vision** : plateforme web où les candidats déposent leur CV et reçoivent
> une liste personnalisée d'offres d'emploi pertinentes provenant
> d'organismes internationaux (Banque Mondiale, BAD, ONU, etc.), accompagnée
> de rapports sur le marché.
>
> **Contexte** : projet de cours Machine Learning, conçu pour être réellement
> utilisable et monétisable à terme.

---

## 1. Stratégie globale

**Mantra** : *local-first, source unique, process complet, puis réplication.*

- Priorité immédiate : ingestion + préparation + training en local.
- Source pilote : **ONU (ReliefWeb)** pour valider le process complet.
- Reporting non prioritaire à ce stade.
- Azure et industrialisation cloud reportés après validation locale.
- Une fois la source pilote stabilisée, réplication à World Bank puis BAD.

---

## 2. Architecture cible

```
┌─────────────────┐
│  Sources web    │  (APIs officielles, RSS, scraping si nécessaire)
│  BM, BAD, ONU   │
└────────┬────────┘
         │  ingestion (GitHub Actions cron ou Azure Function)
         ▼
┌─────────────────────────────────────────────┐
│  ADLS Gen2 — Bronze / Silver / Gold         │
│  (Parquet partitionné par date+source)      │
└──────┬──────────────────────────────┬───────┘
       │                              │
       │ silver→OLTP                  │ gold pour ML
       ▼                              ▼
┌──────────────┐              ┌──────────────────┐
│  PostgreSQL  │              │  Databricks      │
│  + pgvector  │              │  - feature eng.  │
│  (offres     │              │  - labeling LLM  │
│   actives,   │              │  - entraînement  │
│   embeddings)│              │  - MLflow        │
└──────┬───────┘              └────────┬─────────┘
       │                               │
       │                               │ modèle promu
       │      ┌────────────────────────┘
       ▼      ▼
┌──────────────────────┐         ┌─────────────────┐
│  API Matching        │◄────────│  Frontend       │
│  FastAPI / Container │         │  Streamlit      │
│  Apps (scale-to-zero)│         │  (upload CV +   │
└──────────────────────┘         │   résultats)    │
                                  └─────────────────┘
┌──────────────────────┐
│  Power BI            │  ← lit Postgres / ADLS Gold
│  (rapports marché)   │
└──────────────────────┘
```

---

## 3. Stack technique

| Couche | Choix court terme (maintenant) | Cible long terme | Notes |
|---|---|---|---|
| Stockage | Fichiers locaux (`data/raw`, `data/silver`, `data/gold`) | ADLS Gen2 | Même logique Bronze/Silver/Gold |
| Base opérationnelle | CSV/Parquet local pour démarrer | PostgreSQL + pgvector | Migration après validation pipeline |
| Compute ML | Python local (scripts) | Databricks | Priorité au process et à la reproductibilité |
| Tracking ML | Fichiers metadata JSON locaux | MLflow | Suffisant pour baseline initiale |
| Ingestion | Scripts Python exécutés localement | GitHub Actions cron / Azure Function | Une source d'abord |
| Parsing CV | Hors scope immédiat | Azure Document Intelligence ou LLM | Repris après pipeline offres |
| API | Hors scope immédiat | FastAPI + Docker | Repris après qualité data/model |
| Frontend | Hors scope immédiat | Streamlit | Repris après API minimale |
| Reporting | Hors scope immédiat | Power BI | Non prioritaire actuellement |
| Secrets | Variables d'environnement locales | Azure Key Vault | Pas de secrets cloud pour l'instant |
| IaC | Hors scope immédiat | Bicep ou Terraform | Décision reportée |
| CI/CD | Simple check local (lint/tests) | GitHub Actions complet | À renforcer après M3R |
| Observabilité | Logs JSON locaux | Application Insights + logs structurés | Minimal d'abord |

---

## 4. Structure du repo (monorepo)

```
.
├── .github/workflows/      # CI/CD
├── docs/
│   ├── PLAN.md             # ce fichier
│   ├── architecture.md
│   └── adr/                # Architecture Decision Records
├── infra/                  # Bicep ou Terraform
├── ingestion/              # un module par organisme
│   ├── worldbank/
│   ├── afdb/
│   └── un/
├── databricks/
│   ├── notebooks/
│   │   ├── silver/
│   │   ├── gold/
│   │   ├── labeling/
│   │   └── training/
│   └── jobs/               # définitions YAML/JSON des jobs
├── ml/                     # code modèle (importable par notebooks)
├── api/                    # service FastAPI
├── frontend/               # app Streamlit
├── powerbi/                # .pbix versionnés
└── scripts/
```

---

## 5. Milestones

### 🧭 M0R — Re-cadrage exécution *(immédiat)*

Objectif: valider officiellement le mode local-first avec source unique.

Livrable attendu: périmètre gelé (pas de reporting/cloud au départ), source pilote choisie, critères de validation définis.

---

### 📥 M1R — Ingestion locale source pilote *(semaine 1)*

Objectif: récupérer les offres de la source pilote de manière fiable en local.

Livrable attendu: flux d'ingestion reproductible avec stockage brut daté et logs d'exécution.

---

### 🥈 M2R — Préparation locale des données *(semaine 1-2)*

Objectif: transformer le brut en dataset propre et exploitable pour le ML.

Livrable attendu: dataset silver validé (schéma canonique, déduplication, qualité minimale documentée).

---

### 🤖 M3R — Baseline training local *(semaine 2)*

Objectif: entraîner une baseline locale pour prouver la chaîne data -> ML.

Livrable attendu: artefacts gold générés et mesures minimales reproductibles.

---

### 🔁 M4R — Réplication multi-sources *(semaine 3)*

Objectif: reproduire le même processus sur d'autres sources sans refonte.

Livrable attendu: extension du pipeline à World Bank puis BAD avec schéma harmonisé.

---

### ☁️ M5R — Migration cloud progressive *(après validation locale)*

Objectif: industrialiser la solution uniquement après preuve locale complète.

Livrable attendu: migration progressive vers ADLS/Databricks/orchestration cloud, puis réactivation API/frontend/reporting.

---

## 6. Risques et mitigations

| Risque | Mitigation |
|---|---|
| API source change (schéma, pagination, limites) | Contrat d'ingestion explicite + tests de non-régression sur connecteur pilote |
| Qualité données insuffisante pour training | Validation silver obligatoire + règles de complétude avant entraînement |
| Trop de scope en parallèle | Principe strict: 1 source, 1 pipeline, 1 baseline avant extension |
| Blocage cloud précoce (temps/coût/config) | Exécution 100% locale d'abord, migration cloud uniquement après preuve de fonctionnement |
| Régression en ajoutant d'autres sources | Répliquer le même pattern validé, sans refonte, avec check qualité inter-sources |
| Pression calendrier | Jalons courts M1R/M2R/M3R avec critères d'acceptation mesurables |

---

## 7. Critères de succès du MVP

- ✅ Pipeline local exécutable de bout en bout en une commande (source pilote)
- ✅ Données `raw` et `silver` produites avec schéma canonique validé
- ✅ Baseline training locale exécutée avec artefacts `gold` générés
- ✅ Mesures minimales de performance disponibles et reproductibles
- ✅ Process suffisamment documenté pour être répliqué à World Bank et BAD
- ✅ Migration cloud déclenchée uniquement après validation locale complète
