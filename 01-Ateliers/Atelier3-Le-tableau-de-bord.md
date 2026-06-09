# Atelier 3 — Le tableau de bord

> Format : storytelling + atelier pratique. Durée 3h30. Niveau hétérogène.
> Livrable : **un dashboard web** des offres data en Île-de-France, avec recherche, filtres, tableau triable/paginé et graphiques. Inspiré de [freework-dashboard.vercel.app](https://freework-dashboard.vercel.app/).

> Position dans la chaîne : on a collecté (atelier 1), on a stocké (atelier 2). Maintenant on **rend la donnée lisible**. Un CSV de 5000 lignes ne se lit pas. Un tableau de bord, si.

---

## 🎬 Le pitch (10 min)

> *« Vous avez une base avec des milliers d'offres. Bravo. Maintenant, ouvrez-la. C'est illisible. Personne ne prend une décision en scrollant un fichier de 5000 lignes.*
>
> *Allez voir freework-dashboard.vercel.app. C'est exactement le même problème que vous : des milliers de missions freelance. Et regardez ce qu'ils en font. Une recherche, des filtres, un tableau qu'on trie d'un clic, des graphiques qui répondent en direct. En trente secondes vous savez quelles technos paient le mieux et où sont les offres.*
>
> *Aujourd'hui on construit le vôtre. La donnée que vous avez collectée devient un outil de décision. »*

L'idée : la donnée n'a de valeur que rendue lisible. La dataviz n'est pas de la déco, c'est la dernière étape qui transforme une table SQL en réponse à une question.

---

## 🎯 La règle du jeu

- **Socle** : afficher les offres dans un tableau triable et paginé, avec un panneau de filtres (télétravail, TJM minimum, expérience, ville) et une recherche par mots-clés. Les filtres s'appliquent en live.
- **La contrainte clé** : filtres et graphiques lisent la **même** liste filtrée. Quand on coche "Remote", le tableau ET les graphiques se mettent à jour ensemble. Une seule source de vérité.
- **Les graphiques** : au moins trois. Offres par jour, top des technos demandées, TJM moyen par niveau.

---

## ⏱️ Le déroulé (3h30)

| Temps | Phase | Ce qui se passe |
|-------|-------|-----------------|
| 0:00 – 0:15 | **Le pitch + visite de la référence** | On dissèque freework : qu'est-ce qui en fait un bon dashboard ? On liste les briques. |
| 0:15 – 0:45 | **Scaffold Next.js + Tailwind** | `npx create-next-app`, Tailwind, un premier écran qui affiche "Hello". On comprend App Router : `app/page.js`, `layout.js`. |
| 0:45 – 1:30 | **Les données + le tableau** | Charger les offres (JSON puis API route), afficher un tableau brut. Colonnes : Publication, Titre, TJM, Remote, Durée, Xp, Skills, Entreprise, Ville. |
| 1:30 – 1:45 | **Pause** | — |
| 1:45 – 2:15 | **Tri + pagination** | Cliquer un en-tête trie la colonne. Pagination 10/15/20/25 lignes. La logique vit dans des fonctions pures (`trierOffres`). |
| 2:15 – 2:50 | **Le panneau de filtres** | `useState` pour l'état des filtres. `filtrerOffres` applique recherche + télétravail + TJM + xp + ville. Réactif en live. |
| 2:50 – 3:20 | **Les graphiques (Recharts)** | Offres/jour, top 10 technos, TJM moyen par niveau. Ils lisent la liste **filtrée** : tout bouge ensemble. |
| 3:20 – 3:30 | **Démo + débrief** | On filtre "senior + Remote + Python", on regarde le tableau et les courbes réagir. On discute : comment brancher la vraie base ? |

---

## 🔧 Le vrai apprentissage

- **Next.js App Router** : la structure `app/`, le rendu côté serveur vs client (`"use client"`), une route API qui sert les données.
- **L'état remonté (lifted state)** : les filtres vivent dans la page parente, pas dans chaque composant. Une seule source de vérité, partagée entre tableau et graphiques. C'est LE pattern React à comprendre.
- **Fonctions pures pour la logique métier** : filtrer, trier, agréger sont des fonctions qui ne touchent à rien et renvoient du neuf. Faciles à tester, réutilisables. La logique n'est pas noyée dans le JSX.
- **La dataviz comme réponse à une question**, pas comme décoration : chaque graphique répond à une vraie question (où sont les offres ? quelles technos ? quel TJM ?).

---

## ✅ Critères de réussite

- **Socle** : tableau triable + paginé, panneau de filtres fonctionnel en live, recherche par mots-clés, au moins trois graphiques qui réagissent aux filtres.
- **Bonus** :
  - une **carte** des offres par ville (Leaflet + OpenStreetMap, via `dynamic` import `ssr: false`),
  - brancher la **vraie base** (Supabase ou l'API France Travail de l'atelier 1) à la place du JSON,
  - une page de **détail d'offre** (clic sur "Voir"),
  - **déploiement** sur Vercel, comme la référence,
  - export CSV de la vue filtrée.

---

## 🔌 À préparer avant

- Node.js 18+ installé (`node --version`).
- De quoi alimenter le dashboard : soit le CSV/la base de l'atelier 2, soit le jeu d'exemple fourni (`data/offres.sample.json`).
- Le corrigé complet est dans `02-Corrige/../03-Dashboard/` (à la racine du repo) : il se lance avec `npm install && npm run dev`.

---

## 🪝 Mot de la fin

*« Vous venez de transformer une table SQL en outil de décision. C'est ça, le dernier kilomètre de la data : pas la collecte, pas le stockage, mais le moment où un humain regarde l'écran et comprend en trois secondes. Tout le pipeline en amont ne sert qu'à rendre cet instant-là possible. »*
