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

**Mantra** : *end-to-end fonctionnel le plus tôt possible, puis on améliore chaque couche.*

- Démo utilisable visée à mi-trimestre, même médiocre en qualité de matching.
- Itérations sur les couches data → ML → produit ensuite.
- Monétisation **différée** : pas de paiement, pas d'auth complexe au MVP.
- Couverture initiale : **3-5 organismes** (Banque Mondiale, BAD, ONU pour démarrer).

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

| Couche | Choix | Notes |
|---|---|---|
| Stockage analytique | Azure Data Lake Storage Gen2 | Bronze / Silver / Gold |
| Base opérationnelle | Azure PostgreSQL Flexible Server + pgvector | Offres actives + embeddings |
| Compute ML | Databricks | Notebooks + Jobs |
| Tracking ML | MLflow (managed Databricks) | Registry inclus |
| Ingestion | GitHub Actions cron (ou Azure Function timer) | **Pas Databricks** (I/O bound) |
| Parsing CV | Azure Document Intelligence ou LLM (ADR-003) | À trancher en M3 |
| LLM labeling | Claude Haiku ou GPT-4o-mini | Modèle économique pour batch |
| API | FastAPI + Docker | |
| Hébergement API | Azure Container Apps | Scale-to-zero = coût ≈ 0 hors usage |
| Frontend | **Streamlit** | Démo visuelle, dev rapide |
| Reporting | Power BI | |
| Secrets | Azure Key Vault | |
| IaC | Bicep *ou* Terraform (ADR-001) | Décision en phase de conception |
| CI/CD | GitHub Actions | Pre-commit + lint + tests + déploiement |
| Observabilité | Application Insights + logs structurés | |

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

## 5. Milestones et tickets

Légende effort : **S** = quelques heures · **M** = 1-2 jours · **L** = 3-5 jours

---

### 🏗️ M0 — Fondations *(semaines 1-2, immédiat)*

Mise en place des fondations techniques avant tout développement métier.

- [ ] **(S)** Init du repo + structure de dossiers + `.gitignore` + licence
- [ ] **(S)** README projet (vision, archi, comment contribuer)
- [ ] **(S)** Diagramme d'architecture cible (draw.io ou Mermaid dans `docs/`)
- [ ] **(S)** ADR-001 : stack technique (justification des choix)
- [ ] **(S)** ADR-002 : Bicep vs Terraform (à trancher en phase conception)
- [ ] **(M)** Provisionnement Azure : Resource Group, ADLS Gen2, Key Vault
- [ ] **(M)** App Registration + Service Principal pour CI/CD
- [ ] **(M)** Configuration IaC initiale (squelette Bicep/Terraform)
- [ ] **(S)** Pre-commit hooks : ruff, black, mypy
- [ ] **(M)** Pipeline CI baseline : lint + format + tests unitaires sur PR
- [ ] **(M)** Workspace Databricks + secret scope branché sur Key Vault
- [ ] **(S)** Brouillon politique de confidentialité + mentions légales (Loi 25)

---

### 📥 M1 — Ingestion des offres *(semaines 2-4)*

Récupérer les offres de 3 organismes et les déposer en Bronze.

- [ ] **(M)** Recherche et documentation des sources : pour chaque organisme, identifier API officielle / RSS / nécessité de scraping
- [ ] **(S)** ADR-003 : stratégie d'ingestion (API > RSS > scraping)
- [ ] **(S)** Définition du schéma Bronze (Parquet partitionné par `source/date`)
- [ ] **(M)** Connecteur Banque Mondiale
- [ ] **(M)** Connecteur Banque Africaine de Développement (BAD)
- [ ] **(M)** Connecteur ONU (ou agence onusienne spécifique)
- [ ] **(M)** Orchestration : workflow GitHub Actions cron (quotidien)
- [ ] **(S)** Logging structuré (JSON) + alertes en cas d'échec
- [ ] **(M)** Tests d'intégration avec fixtures HTTP mockées (`vcrpy` ou `responses`)
- [ ] **(S)** Petit dashboard santé ingestion (compte d'offres / source / jour)

---

### 🥈 M2 — Couche Silver + base opérationnelle *(semaines 3-5)*

Nettoyer, normaliser, et exposer les offres actives dans une base requêtable.

- [ ] **(S)** Définition du modèle canonique d'offre (JSON Schema)
- [ ] **(M)** Notebook Databricks Bronze → Silver (normalisation, parsing dates, etc.)
- [ ] **(M)** Provisionnement Azure PostgreSQL Flexible Server + extension pgvector
- [ ] **(M)** Pipeline Silver → PostgreSQL (offres actives uniquement)
- [ ] **(M)** Logique de déduplication (mêmes offres republiées)
- [ ] **(S)** Politique de rétention + job de purge automatique
- [ ] **(S)** Documentation du modèle de données

---

### 📄 M3 — Traitement de CV *(semaines 5-7)*

Permettre l'upload d'un CV et l'extraction structurée de son contenu.

- [ ] **(S)** ADR-004 : parsing CV — Azure Document Intelligence vs LLM
- [ ] **(M)** Endpoint d'upload (PDF, DOCX) avec stockage chiffré dans ADLS
- [ ] **(L)** Service de parsing → CV structuré (sections, compétences, langues, expérience, mobilité)
- [ ] **(S)** Validation du schéma CV extrait
- [ ] **(S)** Gestion d'erreurs (CV illisible, format non supporté)
- [ ] **(S)** Bandeau de consentement explicite + page mentions légales

---

### 🏷️ M4 — Étiquetage LLM *(semaines 6-8)*

Générer le dataset d'entraînement via scoring LLM des paires CV ↔ offre.

- [ ] **(M)** Création de 15-20 CV synthétiques (personas variés : junior/senior, techniques/programmes, francophones/anglophones, etc.). **Évite tout problème RGPD pendant l'entraînement.**
- [ ] **(M)** Prompt engineering : scoring 1-10 + justification structurée (JSON)
- [ ] **(M)** Évaluation manuelle baseline : tu notes 50 paires à la main, tu compares au LLM
- [ ] **(L)** Pipeline batch sur Databricks : toutes paires CV × offres actives
- [ ] **(S)** Stockage Gold du dataset étiqueté (Parquet)
- [ ] **(S)** Tracking explicite des coûts LLM (budget plafonné)

---

### 🤖 M5 — Modèle de matching *(semaines 8-10, après cours pertinents)*

Entraîner et évaluer un modèle de matching personnalisé.

- [ ] **(M)** Baseline embeddings (sentence-transformers multilingue) + similarité cosinus — **référence à battre**
- [ ] **(S)** Setup MLflow (tracking + registry)
- [ ] **(M)** Feature engineering (embeddings, features structurelles, croisements)
- [ ] **(L)** Entraînement modèle (cross-encoder ou ranker selon cours)
- [ ] **(M)** Évaluation : NDCG@10, MAP, accord avec scores LLM
- [ ] **(S)** Comparaison baseline vs modèle entraîné — *si la baseline gagne, on part en prod avec elle, c'est OK*
- [ ] **(S)** Promotion staging → prod via MLflow Registry
- [ ] **(S)** Documentation du modèle (model card)

---

### 🔌 M6 — API de matching *(semaines 9-11)*

Exposer le modèle via une API conteneurisée et déployée.

- [ ] **(M)** API FastAPI : `POST /match` (input: CV parsé, output: top N offres scorées avec justification)
- [ ] **(S)** Endpoint santé `/health` + métriques `/metrics`
- [ ] **(S)** Dockerfile multi-stage optimisé
- [ ] **(M)** Setup Azure Container Registry + push d'images via CI
- [ ] **(M)** Déploiement Azure Container Apps (scale-to-zero activé)
- [ ] **(S)** Auth simple (clé API en header)
- [ ] **(M)** Cache des embeddings d'offres (recalcul inutile à chaque requête)
- [ ] **(M)** Pipeline CI/CD : auto-déploiement sur push `main`
- [ ] **(S)** Tests d'intégration end-to-end de l'API

---

### 🖥️ M7 — Frontend Streamlit *(semaines 10-12)*

Interface visuelle minimale pour la démo.

- [ ] **(S)** Squelette app Streamlit (multipage)
- [ ] **(M)** Page upload de CV + appel API parsing
- [ ] **(M)** Page résultats : top N offres avec score, justification, tags
- [ ] **(S)** Page détail d'une offre + lien externe vers l'organisme
- [ ] **(S)** Déploiement (Azure Container App ou Streamlit Community Cloud)
- [ ] **(S)** Petit branding (logo, couleurs) pour rendre la démo crédible

---

### 📊 M8 — Reporting Power BI *(semaines 11-13)*

Rapports sur l'état du marché — exploitables en démo et en monétisation B2B.

- [ ] **(S)** Création workspace Power BI + connexion à PostgreSQL (ou ADLS Gold)
- [ ] **(M)** Modèle sémantique (dimensions : temps, organisme, pays, secteur, niveau)
- [ ] **(M)** Dashboard "État du marché" (volume d'offres, évolution, tendances)
- [ ] **(M)** Dashboard "Géographie & secteurs" (carte, répartition sectorielle)
- [ ] **(S)** Versioning des `.pbix` dans le repo
- [ ] **(S)** *(Optionnel)* Embed dans le frontend pour la démo

---

### 🔄 M9 — MLOps & boucle de feedback *(semaines 12-14)*

Industrialiser : retraining, monitoring, feedback utilisateur.

- [ ] **(M)** Job Databricks de réentraînement mensuel automatisé
- [ ] **(M)** Monitoring data drift + fraîcheur des données
- [ ] **(S)** Monitoring API : latence, erreurs (Application Insights)
- [ ] **(M)** Feedback utilisateur 👍/👎 sur recommandations → réinjecté dans dataset
- [ ] **(S)** Dashboard ops (santé pipeline end-to-end)

---

### 🎓 M10 — Démo & livraison *(semaines 14-15)*

Finaliser pour le rendu de cours et préparer la suite.

- [ ] **(M)** Documentation finale (architecture, choix techniques, métriques)
- [ ] **(M)** Vidéo de démo (5 min, scénario clair)
- [ ] **(M)** Présentation académique (slides + speech)
- [ ] **(S)** Backlog V2 documenté : auth utilisateurs, paiement Stripe, plus d'organismes, modèle B2B, etc.

---

## 6. Risques et mitigations

| Risque | Mitigation |
|---|---|
| Sites cibles changent leur structure HTML | Privilégier API/RSS officiels ; tests d'intégration qui détectent vite les ruptures |
| Coût LLM labeling explose | Plafond budget explicite + modèle économique + caching |
| Modèle entraîné moins bon que baseline | Garder baseline en fallback, c'est un résultat valide en soi |
| ToS scraping violés | Privilégier API officielles ; documenter sources et licences |
| Données personnelles (Loi 25 / RGPD) | Consentement explicite, chiffrement at-rest, droit à l'effacement, CV synthétiques pour entraînement |
| Trimestre trop court | Roadmap découpée pour livrable utilisable dès M7 ; M8-M10 = polish |

---

## 7. Critères de succès du MVP

- ✅ Pipeline d'ingestion fonctionnelle pour ≥ 3 organismes, exécutée quotidiennement
- ✅ Au moins 500 offres dans la base opérationnelle
- ✅ Upload de CV → liste d'offres scorées en < 5 secondes
- ✅ Modèle ML entraîné avec métriques tracées dans MLflow
- ✅ Démo end-to-end fonctionnelle (upload réel → résultats réels)
- ✅ Au moins 1 dashboard Power BI exploitable
- ✅ Documentation suffisante pour qu'un tiers reprenne le projet
