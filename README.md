# Formation M2 Data Engineering : plateforme d'automatisation de candidatures

Une formation pratique où les étudiants construisent, atelier après atelier, une vraie plateforme. Elle récupère les offres de Data Engineer en Île-de-France, les range dans une base, les affiche dans un tableau de bord, et prépare l'envoi des candidatures.

Le fil rouge n'est pas un exercice scolaire abstrait. C'est leur propre recherche d'emploi. À la fin du parcours, chaque groupe a un produit qui tourne.

## Pour qui

- Public : M2 Data Engineering, niveau hétérogène, du débutant Python/SQL au confirmé.
- Format : ateliers de 3h30, en binômes ou trinômes mixtes (un confirmé avec un débutant).
- Prérequis : bases de Python, notion de SQL, savoir cloner un dépôt. Le reste est guidé.

Le principe qui tient toute la formation : personne ne part de la page blanche. Chaque atelier a un objectif Socle, que tout le monde atteint, et un objectif Bonus, pour ceux qui avancent vite.

## Par où commencer

Commence par le dossier **`Atelier-1-Collecte/`** et lis son `README.md`. Les ateliers s'enchaînent dans l'ordre : la sortie de l'un est l'entrée du suivant.

Chaque atelier est un dossier autonome, organisé de la même façon :

- `README.md` : l'énoncé, ce qu'on construit et comment lancer le corrigé.
- `corrige/` : le code solution, fonctionnel, à lire et à faire tourner.
- `starter/` ou `exemple/` : le squelette à compléter, et un jeu de données d'exemple pour tester sans dépendre d'une vraie collecte.

## Le parcours

| Atelier | Dossier | Ce qu'on construit | Compétence |
|---------|---------|--------------------|------------|
| 1. Collecte | [`Atelier-1-Collecte/`](Atelier-1-Collecte/README.md) | Rassembler des milliers de contacts et offres data d'IDF dans un CSV propre, multi-sources | Ingestion, API, scraping |
| 2. Stockage | [`Atelier-2-Stockage/`](Atelier-2-Stockage/README.md) | Charger ce CSV dans une base Postgres sans jamais créer de doublon | Modélisation, upsert idempotent |
| 3. Dashboard | [`Atelier-3-Dashboard/`](Atelier-3-Dashboard/README.md) | Un tableau de bord Next.js des offres, avec filtres, tri et graphiques | Front, dataviz |
| 4. Envoi | [`Atelier-4-Envoi/`](Atelier-4-Envoi/README.md) | Préparer des candidatures personnalisées en brouillons Gmail, validées à la main | API Gmail, idempotence |

L'enchaînement : l'atelier 1 produit le CSV de contacts, l'atelier 2 le charge en base, l'atelier 3 rend la donnée lisible, l'atelier 4 prépare l'envoi. Deux extensions naturelles prolongent la chaîne : le matching d'un CV aux offres par embeddings, et la génération d'un CV adapté avec un LLM.

## D'où vient le volume à l'atelier 1

C'est la question que les étudiants vont poser, autant l'assumer : le scraping artisanal ne fait pas le volume, l'API France Travail oui.

| Source | Volume réaliste | Pourquoi |
|--------|-----------------|----------|
| France Travail (API officielle) | 3000 à 5000 à elle seule | 8 métiers data sur 8 départements, paginé, stable, légal |
| Job boards (HelloWork, APEC) | 500 à 1500 | Scraping HTML, dépend de la résistance du site |
| LinkedIn | environ 50 par étudiant | Volontairement bridé pour ne pas griller les comptes |
| Annuaires, Welcome to the Jungle | 300 à 800 | Pages structurées |

La leçon d'ingénieur : on choisit la source fiable pour le résultat, on garde le scraping fragile pour les cas où il n'y a pas d'API. Le scraping LinkedIn, c'est la compétence qu'on apprend, pas le volume qu'on produit.

## Secrets et RGPD

- Les clés d'API ne sont jamais commitées. Elles vivent dans un `.env` local, exclu par `.gitignore`. Un modèle est fourni dans `Atelier-1-Collecte/starter/.env.example`.
- Pour les contacts recruteurs : pas de collecte massive ni de revente. On travaille sur des données professionnelles, base légale de l'intérêt légitime, minimisation et conservation limitée.
- Envoi de candidatures : toujours une validation humaine avant départ, jamais d'automatisation complète. La valeur pédagogique est la même en semi-automatique, sans le risque juridique.

## État du dépôt

Les quatre ateliers ci-dessus sont disponibles, énoncé et corrigé compris. Le matching par embeddings et la génération de CV par LLM sont les prolongements prévus de la chaîne.
