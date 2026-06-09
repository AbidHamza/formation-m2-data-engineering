# Atelier 3 : le tableau de bord

Une table SQL de 5000 lignes, personne ne la lit. On scrolle, on perd le fil, et au final on ne sait toujours pas quelles technos paient le mieux ni où sont les offres. Un tableau de bord répond à la question en trois secondes.

C'est le dernier kilomètre de la donnée. L'atelier 1 a collecté, l'atelier 2 a stocké. Ici on rend la donnée lisible et actionnable. Tout le travail en amont ne sert qu'à rendre ce moment possible : un humain regarde un écran et comprend.

Le livrable : un tableau de bord web des offres data en Île-de-France, avec recherche, filtres, tableau triable et graphiques. La référence à viser est [freework-dashboard.vercel.app](https://freework-dashboard.vercel.app/). Allez la voir avant de commencer, c'est exactement le même problème (des milliers de missions freelance) traité proprement.

## Ce qu'on construit

Stack : Next.js 14 (App Router), Tailwind CSS, Recharts. Les briques :

- une recherche par mots-clés (titre, skills, entreprise) ;
- un panneau de filtres : télétravail, TJM minimum, niveau d'expérience, ville ;
- un tableau d'offres triable au clic sur les en-têtes et paginé ;
- trois graphiques : offres par jour, top des technos demandées, TJM moyen par niveau.

La contrainte qui fait tout l'intérêt : filtres, tableau et graphiques lisent la même liste filtrée. Quand on coche "Remote", le tableau et les trois courbes se mettent à jour ensemble. Une seule source de vérité, pas de désynchronisation.

## Les notions React/Next à comprendre

Quatre idées suffisent pour lire et écrire ce code, même si React est nouveau pour vous.

**App Router et la structure `app/`.** Avec Next.js 14, chaque dossier dans `app/` est une route. `app/page.js` est la page d'accueil, `app/layout.js` enveloppe toutes les pages (le `<html>` et le `<body>`), `app/api/offres/route.js` est une route API qui renvoie les offres. Pas de configuration de routeur à écrire, l'arborescence des fichiers fait office de routeur.

**Le composant client (`"use client"`).** Par défaut, Next rend les composants côté serveur. Mais dès qu'un composant a besoin d'état ou d'interactivité (un clic, une saisie), il doit s'exécuter dans le navigateur. On l'indique avec la directive `"use client"` tout en haut du fichier. La page principale en est un, car elle gère l'état des filtres.

**L'état remonté (lifted state).** C'est le pattern central. Les filtres ne vivent pas dans le composant `Filtres`, ni dupliqués dans le tableau et les graphiques. Ils vivent dans la page parente (`app/page.js`), dans un seul `useState`. La page calcule la liste filtrée une fois, puis la passe au tableau et aux graphiques. Quand un filtre change, un seul endroit est modifié, et tout ce qui en dépend se recalcule. C'est ce qui garantit que rien ne se contredit à l'écran.

**Les fonctions pures de `lib/offres.js`.** Filtrer, trier et agréger sont écrits comme des fonctions qui prennent des données et renvoient de nouvelles données, sans rien modifier au passage. `filtrerOffres`, `trierOffres`, `offresParJour`, `topSkills`, `tjmMoyenParXp`. La logique métier reste hors du JSX, facile à lire et à tester isolément.

## Lancer le corrigé

Depuis la racine du dépôt :

```bash
cd Atelier-3-Dashboard/corrige
npm install
npm run dev
```

Ouvrir ensuite http://localhost:3000.

Le détail technique (structure complète, route API, et surtout comment brancher la vraie donnée à la place du JSON, via Supabase ou l'API France Travail de l'atelier 1) est dans `corrige/README.md`.

## L'exemple fourni

Le dashboard tourne sans base de données grâce à `corrige/data/offres.sample.json` : 25 offres data réalistes en Île-de-France (Data Engineer, Data Analyst, Data Scientist, MLOps), entreprises et villes crédibles, quelques offres sans TJM pour gérer le cas réel.

Chaque offre suit ce schéma. Si vous branchez votre propre source, c'est ce format que vos données doivent respecter pour que filtres, tableau et graphiques fonctionnent sans changement.

```json
{
  "id": "off-001",
  "datePublication": "2026-06-08",
  "titre": "Data Engineer Senior H/F",
  "tjmMin": 550,
  "tjmMax": 700,
  "remote": "Remote | Partiel | Présentiel | Non précisé",
  "duree": "12 mois",
  "xp": "junior | intermediate | senior | expert",
  "skills": ["Python", "Spark", "Airflow"],
  "softSkills": ["Autonomie", "Communication"],
  "entreprise": "Capgemini",
  "ville": "Paris (75)"
}
```

`tjmMin` et `tjmMax` valent `null` quand l'offre ne précise pas de tarif.

## Critères de réussite

Socle attendu de tous :

- tableau d'offres triable au clic et paginé ;
- filtres appliqués en live (télétravail, TJM minimum, expérience, ville) ;
- recherche par mots-clés ;
- au moins trois graphiques qui réagissent aux filtres en même temps que le tableau.

Bonus pour aller plus loin :

- une carte des villes avec Leaflet (via un `dynamic` import en `ssr: false`) ;
- brancher la vraie base à la place du JSON (Supabase ou API France Travail) ;
- une page de détail d'offre au clic ;
- un déploiement sur Vercel, comme la référence.
