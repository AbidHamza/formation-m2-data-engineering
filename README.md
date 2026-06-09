# Formation M2 Data Engineering — Plateforme d'automatisation de candidatures

Une formation pratique de 6 ateliers où les étudiants construisent, de bout en bout, une vraie plateforme : elle récupère les offres de Data Engineer en Île-de-France, les range dans une base, les matche à un CV, génère un CV adapté avec un LLM, et prépare l'envoi depuis un dashboard.

Le fil rouge n'est pas un exercice scolaire. C'est leur propre recherche d'emploi. À la fin du module, chaque groupe a un produit qui tourne.

## Pour qui

- Public : M2 Data Engineering, niveau hétérogène (du débutant Python/SQL au confirmé).
- Format : 6 ateliers de 3h30, en binômes ou trinômes mixtes (un confirmé + un débutant par poste).
- Prérequis : bases Python, notion de SQL, savoir cloner un repo. Le reste est guidé par un starter qui fonctionne déjà.

Le principe qui tient toute la formation : personne ne part de la page blanche, et chaque atelier a un objectif **Socle** (que tout le monde atteint) et un objectif **Bonus** (pour ceux qui avancent vite).

## Les 6 ateliers

| # | Atelier | Ce qu'on construit | Compétence |
|---|---------|--------------------|------------|
| 1 | **Opération 5000** | Collecter 5000 recruteurs/DRH data d'IDF dans un `contacts.csv` propre, multi-sources | Ingestion, API, scraping |
| 2 | **Le coffre-fort** | Charger ce CSV dans une vraie base Postgres, sans doublon, requêtable | Modélisation, upsert idempotent |
| 3 | Pipeline | Automatiser l'ingestion (planifiée, avec logs et reprise sur erreur) | Orchestration |
| 4 | Matching | Embeddings + pgvector : sortir le top 10 des offres proches d'un CV | Recherche sémantique |
| 5 | CV adapté | L'API Claude reformule le CV pour une offre précise, sans rien inventer | Intégration LLM |
| 6 | Dashboard | Front Next.js façon freework + file d'envoi avec validation humaine | Dashboard, RGPD opérationnel |

Le `contacts.csv` de l'atelier 1 est le carburant de toute la chaîne : l'atelier 2 le charge en base, l'atelier 4 le matche aux offres, l'atelier 5 génère le CV, l'atelier 6 prépare l'envoi.

## Structure du dépôt

```
00-Programme/      Le programme complet (objectifs, progression, évaluation)
01-Ateliers/       Les briefs détaillés à animer en séance (storytelling + déroulé minuté)
02-Corrige/        Le code corrigé, fonctionnel, prêt à projeter
02-RGPD/           La note de cadrage RGPD (transversale, posée dès l'atelier 1)
03-Starter/        Les squelettes distribués aux étudiants (avec des TODO à compléter)
```

## Atelier 1 — Opération 5000 : d'où vient vraiment le volume

C'est le point que les étudiants vont questionner, autant l'assumer franchement : **le scraping artisanal ne fait pas les 5000. L'API France Travail, oui.**

| Source | Volume réaliste | Pourquoi |
|--------|-----------------|----------|
| France Travail (API officielle) | 3000 à 5000 à elle seule | 8 métiers data × 8 départements, paginé, stable, légal |
| Job boards (HelloWork, APEC) | 500 à 1500 | Scraping HTML, dépend de la résistance du site |
| LinkedIn | ~50 par étudiant | Volontairement bridé pour ne pas griller les comptes |
| Annuaires, Welcome to the Jungle | 300 à 800 | Pages structurées |

La leçon d'ingénieur derrière : on choisit la source fiable pour le résultat (l'API), on garde le scraping fragile pour les cas où il n'y a pas d'API. Le scraping LinkedIn, c'est la *compétence* qu'on apprend, pas le *volume* qu'on produit.

### Lancer la collecte (atelier 1)

```bash
pip install requests beautifulsoup4 pandas python-dotenv playwright
playwright install chromium

# Clés France Travail dans 02-Corrige/.env (non commité) :
#   FT_CLIENT_ID=...
#   FT_CLIENT_SECRET=...

cd 02-Corrige
python collecte_france_travail.py   # le gros du volume
python fusion.py                    # agrège tous les CSV, dédoublonne, vérifie les 5000
```

`fusion.py` affiche le bilan : nombre par source, doublons retirés, et la ligne finale `OBJECTIF ATTEINT` ou `Il manque`. C'est le moment fort de la séance, à projeter en direct.

Pour obtenir les clés : créer un compte sur https://francetravail.io, créer une application, demander l'accès à « Offres d'emploi v2 », récupérer le `client_id` et le `client_secret`. Compter quelques minutes de propagation après l'abonnement avant que l'API réponde.

## Secrets et RGPD

- Les clés API ne sont **jamais** commitées. Elles vivent dans un `.env` local, exclu par `.gitignore`.
- Pour les recruteurs/DRH : pas de collecte massive ni de revente. Enrichissement à la demande sur une offre précise, base légale « intérêt légitime », minimisation, conservation limitée. Détails dans `02-RGPD/`.
- Envoi de candidatures : toujours une validation humaine avant départ. Pas d'automatisation complète. La valeur pédagogique est la même en semi-auto, sans le risque juridique.

## État du projet

Atelier 1 et atelier 2 disponibles (brief + corrigé). Ateliers 3 à 6 décrits dans le programme, briefs détaillés à venir.
