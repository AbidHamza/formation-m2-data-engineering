# Atelier pratique — Plateforme d'automatisation de candidatures (Data Engineering)

> Fil rouge : les étudiants construisent **une seule plateforme** de bout en bout. Chaque atelier ajoute une couche. À la fin, ils ont un produit fonctionnel qui ingère des offres de Data Engineer en Île-de-France, les matche à leur CV, génère un CV adapté par IA et prépare l'envoi.

## Informations générales

- **Public** : M2 Data Engineering, niveau hétérogène (de débutant Python/SQL à confirmé)
- **Prérequis minimum** : bases Python, notion de SQL, savoir cloner un repo Git. Le reste est guidé.
- **Durée totale** : 21h — 6 ateliers de 3h30
- **Modalité** : présentiel, en binômes ou trinômes (mixer les niveaux dans chaque groupe)
- **Objectif général** : maîtriser une chaîne data engineering complète (ingestion → stockage → pipeline → ML/LLM → dashboard → orchestration) sur un cas métier concret et motivant.

### Deux formats possibles (au choix du formateur)

| Format | Découpage | Quand |
|--------|-----------|-------|
| **Hebdomadaire** | 1 atelier de 3h30 par semaine, sur 6 semaines | Cours étalé sur le semestre |
| **Intensif** | 3 jours (2 ateliers/jour) ou semaine hackathon | Module bloqué, séminaire |

## Gérer l'hétérogénéité (clé de la réussite)

Trois leviers appliqués à **chaque** atelier :

1. **Starter code fourni** : chaque atelier démarre d'un squelette qui fonctionne déjà. Les débutants complètent des `TODO`, ils ne partent jamais de la page blanche.
2. **Paliers** : un objectif **Socle** (tout le monde doit l'atteindre) + un objectif **Bonus** (pour les rapides). Personne ne s'ennuie, personne ne décroche.
3. **Binômes mixtes** : un confirmé + un débutant par poste. Le confirmé consolide en expliquant, le débutant suit le rythme.

## Compétences visées

1. **C1** — Concevoir et exploiter une source de données via API (authentification, pagination, rate limiting)
2. **C2** — Modéliser et alimenter une base relationnelle de façon idempotente
3. **C3** — Orchestrer un pipeline automatisé fiable (planification, logs, reprise sur erreur)
4. **C4** — Implémenter une recherche sémantique par embeddings (matching offre/profil)
5. **C5** — Intégrer un LLM en production pour générer un livrable structuré (CV adapté)
6. **C6** — Construire un dashboard web exploitant la donnée et déclencher des actions
7. **C7** — Cadrer un traitement de données personnelles conforme RGPD

## Stack technique

| Couche | Outil | Pourquoi |
|--------|-------|----------|
| Offres d'emploi | **API France Travail** (officielle, gratuite) | Légale, pas de scraping, données riches |
| Stockage | **Supabase** (Postgres + pgvector + Auth) | Gratuit, tout-en-un, hébergé |
| Pipeline / orchestration | **n8n** ou cron + script Python | Visuel (n8n) accessible aux débutants |
| Matching sémantique | **pgvector** + embeddings | Recherche vectorielle dans Postgres |
| Génération CV | **API Claude** (structured output) | Qualité de rédaction, sortie structurée |
| Dashboard | **Next.js + Tailwind** | Clone du style freework-dashboard |
| Envoi | **Gmail API** (brouillon) + validation manuelle | Conforme, pas de ban de compte |

---

## Plan du programme

### Atelier 1 — Ingestion & API (3h30) · C1

**Socle** : récupérer les offres « Data Engineer / Île-de-France » via l'API France Travail et les afficher proprement.
**Bonus** : ajouter des filtres (type de contrat, télétravail), gérer la pagination complète.

**Contenu**
- 1.1 Mise en route : comptes, clés API, repo starter (45 min)
- 1.2 Authentification OAuth2 client credentials (45 min)
- 1.3 Requête, filtrage géographique et métier, parsing JSON (1h)
- 1.4 Rate limiting et gestion d'erreur réseau (30 min)
- 1.5 Restitution : chacun affiche ses offres fraîches (30 min)

**Évaluation formative** : un script qui sort N offres data engineer IDF en JSON propre.

**Notions data engineering** : API REST, OAuth2, pagination, idempotence d'une requête, rate limit.

---

### Atelier 2 — Modélisation & stockage (3h30) · C2

**Socle** : concevoir le schéma Postgres et y charger les offres sans doublons.
**Bonus** : table `entreprises` normalisée + clé étrangère, historisation des offres expirées.

**Contenu**
- 2.1 Modèle de données : offres, entreprises, recruteurs, candidats, candidatures (45 min)
- 2.2 Création des tables dans Supabase (45 min)
- 2.3 Insertion idempotente (upsert sur identifiant offre) (1h)
- 2.4 Déduplication et normalisation (45 min)
- 2.5 Requêtes de vérification SQL (15 min)

**Évaluation formative** : la base se remplit, relancer l'ingestion ne crée pas de doublon.

**Notions** : schéma relationnel, clés, upsert, contrainte d'unicité, normalisation.

---

### Atelier 3 — Pipeline & orchestration (3h30) · C3

**Socle** : automatiser l'ingestion (toutes les X heures) avec logs et reprise sur erreur.
**Bonus** : alerte (mail/Slack) en cas d'échec, métriques (nb offres ingérées par run).

**Contenu**
- 3.1 Du script au pipeline : pourquoi orchestrer (30 min)
- 3.2 Mise en place n8n (ou cron) : déclencheur planifié (1h)
- 3.3 Gestion d'erreur, retry, idempotence du run complet (1h)
- 3.4 Logs structurés et observabilité (45 min)
- 3.5 Démo : le pipeline tourne seul (15 min)

**Évaluation formative** : le pipeline s'exécute en autonomie et survit à une coupure réseau simulée.

**Notions** : orchestration, planification cron, retry/backoff, observabilité. **Cœur du métier data engineer.**

---

### Atelier 4 — Matching offre ↔ profil (3h30) · C4

**Socle** : embarquer le CV de l'étudiant et les offres en vecteurs, sortir le top 10 des offres les plus proches.
**Bonus** : pondérer par compétences clés, filtrer par seuil de similarité.

**Contenu**
- 4.1 Intuition des embeddings et de la similarité cosinus (45 min)
- 4.2 Génération des embeddings (offres + CV) (1h)
- 4.3 Stockage pgvector et index (45 min)
- 4.4 Requête de similarité, top-K (45 min)
- 4.5 Analyse des résultats : pertinents ou non ? (15 min)

**Évaluation formative** : pour un CV donné, la plateforme renvoie un top 10 cohérent.

**Notions** : embeddings, espace vectoriel, similarité cosinus, recherche ANN, pgvector.

---

### Atelier 5 — Génération du CV adapté par LLM (3h30) · C5

**Socle** : à partir d'une offre + du CV de base, l'API Claude produit un CV reformulé pour l'offre + un brouillon de message de candidature.
**Bonus** : sortie structurée (JSON) réinjectée dans un template, score de matching expliqué.

**Contenu**
- 5.1 Intégrer l'API Claude : clé, premier appel (30 min)
- 5.2 Prompt engineering : rôle, contexte offre, CV source, contraintes (1h15)
- 5.3 Structured output : forcer un format exploitable (1h)
- 5.4 Garde-fous : ne pas inventer d'expérience, rester factuel (30 min)
- 5.5 Restitution : un CV adapté généré en direct (15 min)

**Évaluation formative** : génération d'un CV adapté lisible et fidèle au CV source (zéro invention).

**Notions** : intégration LLM, prompt engineering, structured output, hallucination et garde-fous.

> **Point éthique à discuter en classe** : adapter un CV ≠ mentir. Le LLM reformule et met en avant l'existant, il n'invente pas de compétences. C'est un critère d'évaluation.

---

### Atelier 6 — Dashboard & boucle d'envoi (3h30) · C6 · C7

**Socle** : dashboard Next.js façon freework — liste des offres matchées, bouton « générer CV adapté », file d'envoi avec **validation manuelle** avant départ.
**Bonus** : authentification (Supabase Auth), statut des candidatures (envoyée / relance / réponse).

**Contenu**
- 6.1 Démarrage du front (starter Next.js fourni) (45 min)
- 6.2 Affichage des offres et du score de matching (1h)
- 6.3 Action « générer CV adapté » branchée sur l'atelier 5 (45 min)
- 6.4 File d'envoi + brouillon Gmail + validation humaine (45 min)
- 6.5 Démo finale de la plateforme complète (15 min)

**Évaluation sommative** : démonstration du produit complet par chaque groupe.

**Notions** : dashboard data, déclenchement d'action, RGPD opérationnel (validation humaine, minimisation).

---

## Progression pédagogique

| Séance | Atelier | Livrable de fin de séance | Compétence |
|--------|---------|---------------------------|------------|
| 1 | Ingestion & API | Script offres IDF en JSON | C1 |
| 2 | Stockage | Base Supabase alimentée, sans doublon | C2 |
| 3 | Pipeline | Ingestion automatisée fiable | C3 |
| 4 | Matching | Top 10 offres pour un CV | C4 |
| 5 | LLM | CV adapté + message généré | C5 |
| 6 | Dashboard | Plateforme complète démontrée | C6, C7 |

## Modalités d'évaluation

- **Diagnostique** (début atelier 1) : mini-quiz Python/SQL/API pour calibrer les binômes mixtes.
- **Formative** (fin de chaque atelier) : le livrable de la séance fonctionne (vérifié par le formateur).
- **Sommative** (atelier 6) : démonstration du produit + soutenance courte. Grille : fonctionnement (40 %), qualité du code et du pipeline (25 %), pertinence du matching/CV (20 %), conformité RGPD et éthique (15 %).

## Ressources nécessaires

- **Comptes** : France Travail (API), Supabase, Anthropic (API Claude), Google (Gmail API). À créer **avant** l'atelier 1.
- **Postes** : Python 3.11+, Node 20+, Git, VS Code.
- **Documents fournis** : ce programme, les 6 starters de code, la note RGPD, les grilles d'évaluation.
- **Budget API** : France Travail et Supabase gratuits ; Claude à coût faible (prévoir une clé partagée plafonnée ou une clé par groupe).

## Cadrage RGPD (transversal, à poser dès l'atelier 1)

À détailler dans la note RGPD dédiée, mais les principes à enseigner :

- **Offres** : données d'entreprises via API officielle, aucun souci.
- **Recruteurs / DRH** : pas de collecte massive ni de revente. Enrichissement **à la demande** sur une offre précise, base légale « intérêt légitime », minimisation, durée de conservation limitée.
- **Envoi** : toujours une **validation humaine** avant tout envoi. Pas d'automatisation complète sur LinkedIn (ToS + risque juridique). La valeur pédagogique est identique en semi-auto.
- **Étudiants** : leur propre CV est une donnée personnelle, à manipuler proprement (pas de partage hors plateforme).
