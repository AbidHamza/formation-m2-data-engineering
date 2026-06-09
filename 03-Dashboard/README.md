# Dashboard Data Engineer IDF

Corrigé de l'atelier M2 Data Engineering. Tableau de bord des offres freelance
Data (Data Engineer, Data Analyst, Data Scientist) en Île-de-France, inspiré de
[freework-dashboard](https://freework-dashboard.vercel.app/).

## Stack

- **Next.js 14** (App Router) en **JavaScript/JSX** (pas de TypeScript)
- **Tailwind CSS v3**
- **Recharts** pour les graphiques
- Données en JSON local (aucune base, aucun secret)

## Lancer le projet

```bash
npm install
npm run dev
```

Puis ouvrir http://localhost:3000.

Pour vérifier que tout compile :

```bash
npm run build
```

## Structure

```
03-Dashboard/
├── app/
│   ├── api/offres/route.js   # Route API : renvoie les offres (JSON local)
│   ├── globals.css           # Styles Tailwind
│   ├── layout.js             # Layout racine (html/body)
│   └── page.js               # Page principale : orchestre filtres + tableau + graphiques
├── components/
│   ├── Compteur.jsx          # Ligne "Nombre total d'offres : N"
│   ├── Filtres.jsx           # Panneau de filtres (remote, TJM, xp, ville)
│   ├── Graphiques.jsx        # 3 graphiques Recharts réactifs aux filtres
│   └── TableauOffres.jsx     # Tableau triable + paginé
├── lib/
│   └── offres.js             # Helpers purs : filtrage, tri, agrégations
├── data/
│   └── offres.sample.json    # ~25 offres d'exemple
└── (configs : package.json, tailwind.config.js, etc.)
```

## Fonctionnement

L'état des filtres vit dans `app/page.js` (`useState`). À chaque modification, on
recalcule la liste filtrée (`filtrerOffres`) puis on la passe au tableau **et**
aux graphiques. Tout est donc réactif en live, sans rechargement.

Les fonctions de `lib/offres.js` sont **pures** (elles ne modifient rien) :

- `filtrerOffres` : applique recherche, télétravail, TJM min, expérience, ville
- `trierOffres` : tri par colonne (asc/desc)
- `offresParJour`, `topSkills`, `tjmMoyenParXp` : agrégations pour les graphiques

## Brancher la vraie donnée

Les données viennent de `data/offres.sample.json` via `app/api/offres/route.js`.
Pour passer en production, deux pistes vues en atelier :

1. **Supabase** : dans `route.js`, remplacer la lecture du JSON par une requête
   `supabase.from('offres').select('*')`.
2. **API France Travail** (atelier 1) : appeler l'API, mapper la réponse vers le
   schéma d'offre attendu (voir ci-dessous), puis renvoyer le résultat.

Le reste de l'application (filtres, tableau, graphiques) ne change pas tant que
le schéma de chaque offre est respecté :

```json
{
  "id": "string unique",
  "datePublication": "YYYY-MM-DD",
  "titre": "Data Engineer H/F",
  "tjmMin": 450,
  "tjmMax": 600,
  "remote": "Remote | Partiel | Présentiel | Non précisé",
  "duree": "12 mois",
  "xp": "junior | intermediate | senior | expert",
  "skills": ["Python", "Spark"],
  "softSkills": ["Autonomie"],
  "entreprise": "Capgemini",
  "ville": "Paris (75)"
}
```

## Carte (bonus)

Un emplacement "Carte (bonus)" est laissé en placeholder sur la page. Pour
l'implémenter sans casser le build SSR, utiliser `react-leaflet` via un
`dynamic(() => import(...), { ssr: false })`.
