# Atelier 3 : construire le tableau de bord

Une table SQL de 5000 lignes, personne ne la lit. On scrolle, on perd le fil, et au final on ne sait toujours pas quelles technos paient le mieux ni où sont les offres. Un tableau de bord répond à la question en trois secondes.

C'est le dernier kilomètre de la donnée. L'atelier 1 a collecté, l'atelier 2 a stocké. Ici on rend la donnée lisible et actionnable. Tout le travail en amont ne sert qu'à rendre ce moment possible : un humain regarde un écran et comprend.

Cette fois, pas de corrigé à recopier. Vous construisez le dashboard vous-mêmes. Ce guide vous explique chaque notion, vous donne la démarche étape par étape, et pose les questions qui comptent. Les réponses, c'est vous qui les écrivez.

## 1. Objectif de l'atelier

Le livrable : un tableau de bord web des offres Data Engineer en Île-de-France, avec recherche, filtres, tableau triable et graphiques. La référence à viser est [freework-dashboard.vercel.app](https://freework-dashboard.vercel.app/). Allez la voir avant de commencer. C'est exactement le même problème (des milliers de missions freelance) traité proprement : une barre de recherche en haut, un panneau de filtres, un grand tableau au centre, des graphiques qui résument l'ensemble.

À quoi ressemble votre version une fois finie :

- une recherche par mots-clés (titre, skills, entreprise) ;
- un panneau de filtres : télétravail, TJM minimum, niveau d'expérience, ville ;
- un tableau d'offres qu'on trie en cliquant sur les en-têtes de colonne ;
- des graphiques : nombre d'offres par jour, top des technos demandées, TJM moyen par niveau ;
- un compteur qui affiche combien d'offres correspondent aux filtres en cours.

La contrainte qui fait tout l'intérêt de l'atelier : filtres, tableau, graphiques et compteur lisent tous la même liste filtrée. Quand vous cochez "Remote", le tableau, le compteur et les graphiques se mettent à jour ensemble. Une seule source de vérité, pas de désynchronisation. C'est cette idée qui décide de toute votre architecture, et c'est là que la plupart des bugs vont apparaître si vous vous y prenez mal.

Les données de test : 25 offres réalistes vivent dans `exemple/offres.sample.json` (Data Engineer, Data Analyst, Data Scientist, MLOps, entreprises et villes crédibles, quelques offres sans TJM pour traiter le cas réel). Vous travaillez sur ce fichier pendant l'atelier. Brancher la vraie base de l'atelier 2 est un bonus.

## 2. Les notions à comprendre avant de coder

Lisez cette section en entier avant d'ouvrir un terminal. Deux idées comptent plus que tout le reste : l'état remonté et les fonctions pures. Si vous tenez ces deux-là, le code suit naturellement.

### Next.js 14, App Router, en JavaScript

On utilise Next.js 14 avec l'App Router, en JavaScript et JSX (pas de TypeScript). Trois choses à retenir.

Chaque dossier dans `app/` est une route. `app/page.js` est la page d'accueil. `app/layout.js` enveloppe toutes les pages : il contient le `<html>` et le `<body>`, et c'est lui qui importe le CSS global. Vous n'écrivez aucune configuration de routeur, l'arborescence des fichiers fait le travail.

Par défaut, Next rend les composants côté serveur (ils s'exécutent une fois, à la génération de la page, et n'ont pas accès aux clics ni à l'état). Dès qu'un composant a besoin d'interactivité (un clic, une saisie, un `useState`), il doit tourner dans le navigateur. On l'indique avec la directive `"use client";` en toute première ligne du fichier. Votre page principale sera un composant client, puisqu'elle gère l'état des filtres.

Le JSX, c'est du HTML dans du JavaScript. Deux différences qui mordent au début : on écrit `className` au lieu de `class`, et toute liste rendue avec `.map()` doit donner une prop `key` unique à chaque élément.

### L'état remonté (lifted state), la notion centrale

Voici le piège dans lequel tomberait quelqu'un qui débute. Le panneau de filtres gère son propre état. Le tableau garde sa propre copie pour savoir quoi afficher. Les graphiques en gardent une troisième. Résultat : trois vérités différentes à l'écran, qui se contredisent dès qu'on touche un filtre.

La bonne approche, c'est de faire remonter l'état au plus petit parent commun. Ici, ce parent commun, c'est `app/page.js`. L'état des filtres vit là, dans un seul `useState`. La page calcule la liste filtrée une fois, puis la passe en props au tableau, aux graphiques et au compteur. Le panneau `Filtres` ne stocke rien : il reçoit l'état et une fonction pour le modifier, et toute saisie remonte immédiatement au parent.

Concrètement, votre page ressemblera à ceci dans sa structure (pas son contenu complet) :

```jsx
const [filtres, setFiltres] = useState({ recherche: "", remote: [], tjmMin: "", xp: [], ville: "" });
const offresFiltrees = /* appliquer filtrerOffres(offres, filtres) */;

// puis passer offresFiltrees à <Tableau>, <Graphiques>, <Compteur>
// et passer { filtres, setFiltres } à <Filtres>
```

Question à vous poser avant d'écrire la moindre ligne : où dois-tu stocker l'état des filtres pour que le tableau et les graphiques restent toujours d'accord ? Et son corollaire : si un composant enfant a besoin de modifier cet état, comment le lui permettre sans qu'il en garde une copie locale ?

### Les fonctions pures de filtre, tri et agrégation

Une fonction pure prend des données en entrée et renvoie de nouvelles données, sans rien modifier au passage et sans effet de bord. Donnez-lui deux fois les mêmes entrées, elle renvoie deux fois la même sortie.

Vous allez isoler toute la logique métier dans un fichier `lib/offres.js` : filtrer la liste, la trier, calculer les agrégations pour les graphiques. Pourquoi les sortir des composants ? Parce qu'une fonction pure se lit en dehors de tout le bruit du JSX, se teste isolément (vous pouvez l'appeler dans la console avec un tableau bidon et vérifier le résultat), et se réutilise partout sans surprise.

Une règle de tri qui mord : `Array.sort()` modifie le tableau sur lequel il opère. Si vous triez directement la liste reçue en props, vous mutez les données du parent, et React peut ne pas voir le changement. Votre fonction de tri doit travailler sur une copie (`[...offres]`) et renvoyer cette copie.

Question : pourquoi isoler le filtrage dans une fonction pure plutôt que de filtrer directement à l'intérieur du composant qui affiche le tableau ?

### Tailwind et Recharts

Tailwind CSS, c'est du style par classes utilitaires écrites directement dans le `className`. Pas de fichier CSS séparé à maintenir pour chaque composant. `px-4` met du padding horizontal, `text-sm` réduit la taille du texte, `rounded-xl` arrondit les coins. Vous composez l'apparence en empilant ces classes.

Recharts dessine les graphiques. Vous lui passez un tableau d'objets et il produit un SVG. Le pattern habituel : un `<ResponsiveContainer>` qui prend toute la largeur, et dedans un `<BarChart>` ou un `<AreaChart>` auquel vous donnez vos données via la prop `data`.

### Hiérarchie visuelle

Un dashboard se lit en trois secondes ou il a raté son rôle. Un seul élément dominant par écran : ici, c'est le tableau. Le reste (filtres, graphiques, compteur) l'entoure sans lui voler la vedette. Gardez une palette sobre, un accent de couleur unique, de l'espace entre les blocs. Allez regarder la référence Freework pour le ressenti, puis faites plus simple si le temps manque.

## 3. Prérequis et installation

Il vous faut Node.js 18 ou plus récent. Vérifiez :

```bash
node --version
```

Créez le projet Next.js. Lancez la commande depuis le dossier `Atelier-3-Dashboard` et nommez le projet (par exemple `app`) :

```bash
npx create-next-app@14
```

L'assistant pose des questions. Pour cet atelier : JavaScript (pas TypeScript), Tailwind CSS oui, App Router oui. Refusez TypeScript et `src/` si on vous le propose, ça colle mieux à ce guide.

Ajoutez Recharts :

```bash
npm install recharts
```

Lancez le serveur de dev pour vérifier que tout démarre :

```bash
npm run dev
```

Ouvrez http://localhost:3000. Vous devez voir la page d'accueil par défaut de Next. À partir de là, vous allez la remplacer pièce par pièce.

## 4. La démarche de A à Z

Avancez dans l'ordre. Chaque étape s'appuie sur la précédente. Pour chacune : ce que vous faites, le concept en jeu, et les questions à vous poser. Aucune étape ne vous donne le composant complet, c'est volontaire.

### Étape 1 : nettoyer et poser la structure

Videz le contenu par défaut de `app/page.js` et de `app/globals.css` (gardez les directives Tailwind en haut du CSS : `@tailwind base; @tailwind components; @tailwind utilities;`). Créez les dossiers que vous allez remplir :

```
app/
  layout.js          (déjà créé par create-next-app)
  page.js            (la page principale, votre orchestrateur)
  globals.css
components/
  Filtres.jsx
  TableauOffres.jsx
  Graphiques.jsx
  Compteur.jsx
lib/
  offres.js
```

Concept : l'arborescence est votre architecture. `page.js` orchestre, `components/` contient les briques d'affichage, `lib/` contient la logique pure. Cette séparation vous évitera de mélanger calcul et affichage.

Question : parmi ces fichiers, lesquels auront besoin de `"use client"` et lesquels peuvent rester côté serveur ?

### Étape 2 : charger les données d'exemple

Récupérez `exemple/offres.sample.json` (25 offres) et rendez-le accessible à votre page. Le plus simple pour démarrer : copiez ce fichier dans votre projet (par exemple `app/data/offres.sample.json`) et importez-le, ou exposez-le via une petite route API `app/api/offres/route.js` qui le renvoie en JSON. Les deux marchent. La route API a l'avantage de préparer le terrain pour brancher la vraie base plus tard.

Dans la page, chargez les offres au premier rendu. Si vous passez par une route API, c'est un `fetch` dans un `useEffect` qui tourne une fois au montage. Si vous importez le JSON directement, les données sont là tout de suite et vous n'avez même pas besoin de `useEffect`.

Voici le schéma d'une offre, à connaître par cœur, car filtres, tri et graphiques s'appuient dessus :

```json
{
  "id": "off-001",
  "datePublication": "2026-06-08",
  "titre": "Data Engineer Senior H/F",
  "tjmMin": 550,
  "tjmMax": 700,
  "remote": "Remote | Partiel | Présentiel",
  "duree": "12 mois",
  "xp": "junior | intermediate | senior | expert",
  "skills": ["Python", "Spark", "Airflow"],
  "softSkills": ["Autonomie"],
  "entreprise": "Capgemini",
  "ville": "Paris (75)"
}
```

`tjmMin` et `tjmMax` valent `null` quand l'offre ne précise pas de tarif. Ce cas existe dans le jeu de données, ne l'oubliez pas dans votre logique.

Concept : un composant client ne doit pas faire son `fetch` pendant le rendu, sinon il le relancerait en boucle. On le fait dans un `useEffect` avec un tableau de dépendances vide, qui veut dire "une seule fois, au montage".

Questions : quel est l'état des offres avant que le `fetch` ait répondu ? Que doit afficher l'écran pendant ce court instant de chargement ? Si vous oubliez de gérer ce premier rendu, que se passe-t-il quand votre tableau essaie de faire `.map()` sur des données pas encore arrivées ?

### Étape 3 : écrire les fonctions pures dans lib/offres.js

Avant tout composant d'affichage, écrivez la logique. Vous aurez besoin de :

- `filtrerOffres(offres, filtres)` : renvoie les offres qui passent tous les critères (recherche, télétravail, TJM minimum, expérience, ville) ;
- `trierOffres(offres, colonne, direction)` : renvoie une copie triée ;
- trois agrégations pour les graphiques : nombre d'offres par jour, comptage des skills les plus fréquents, TJM moyen par niveau d'expérience.

Pour `filtrerOffres`, raisonnez critère par critère. Une offre est gardée seulement si elle passe tous les filtres actifs. Un filtre vide (champ texte vide, aucune case cochée) ne filtre rien. Pour la recherche, décidez de votre règle : tous les mots saisis doivent-ils apparaître, ou un seul suffit ? Dans quel champ cherchez-vous (titre, skills, entreprise) ?

Pour le TJM minimum, attention au cas `null` : une offre sans TJM doit-elle apparaître quand on demande "au moins 500 euros" ? Tranchez et soyez cohérent.

Pour les agrégations, le pattern est toujours le même : parcourir les offres, accumuler des comptes dans un objet, puis transformer cet objet en tableau exploitable par Recharts (souvent `[{ label, valeur }, ...]`). Le top des skills demande en plus un tri décroissant et une coupe aux N premiers.

Concept : ces fonctions ne touchent jamais à React. Vous pouvez les tester dans la console du navigateur avec un petit tableau d'offres écrit à la main, avant même d'avoir un seul composant.

Questions : si tu filtres puis tries, dans quel ordre appliques-tu les deux opérations, et est-ce que l'ordre change le résultat affiché ? Ton `trierOffres` modifie-t-il le tableau reçu, ou en renvoie-t-il une copie ? Pourquoi est-ce que ça compte pour React ?

### Étape 4 : le composant Filtres

`Filtres` est un composant contrôlé : il ne stocke rien lui-même. Il reçoit `filtres` et `setFiltres` du parent, affiche les contrôles (cases à cocher pour le télétravail et l'expérience, champs texte pour la ville et le TJM), et chaque interaction appelle `setFiltres` pour remonter le changement.

La signature à viser :

```jsx
export default function Filtres({ filtres, setFiltres }) {
  // ... champs contrôlés, chaque onChange appelle setFiltres({ ...filtres, champ: valeur })
}
```

Le point délicat, c'est les filtres à choix multiples (télétravail, expérience), stockés en tableau. Cocher une case ajoute la valeur, la décocher la retire. Écrivez une petite fonction qui bascule une valeur dans un tableau sans le muter (vous repartez d'une nouvelle liste à chaque fois).

Concept : un champ contrôlé tire sa valeur de l'état (`value={filtres.ville}`) et renvoie ses changements via `onChange`. L'état reste l'unique source de vérité, jamais le DOM.

Questions : pourquoi `Filtres` ne garde-t-il aucun `useState` à lui ? Si tu mettais l'état des cases à cocher dans `Filtres`, comment les graphiques sauraient-ils qu'un filtre a changé ?

### Étape 5 : le tableau triable

`TableauOffres` reçoit la liste filtrée en props et l'affiche en lignes. Au clic sur un en-tête de colonne, il trie selon cette colonne. Un deuxième clic sur la même colonne inverse le sens (ascendant puis descendant).

Le tri est un état local au tableau (quelle colonne, quel sens), pas un état des filtres. C'est légitime : le sens du tri ne concerne que le tableau, ni les graphiques ni le compteur. Stockez-le dans un `useState` du tableau, du genre `{ colonne, direction }`, et appliquez votre `trierOffres` sur les offres reçues.

Pour l'affichage des lignes, vous faites un `.map()` sur les offres. Chaque ligne a besoin d'une `key` unique : l'`id` de l'offre est parfait. Les skills sont un tableau, affichez-les sous forme de petits badges.

Concept : on distingue l'état partagé (les filtres, qui vivent dans la page) de l'état purement local (le tri, qui ne regarde que le tableau). Tout ne doit pas remonter, seulement ce que plusieurs composants partagent.

Questions : pourquoi le tri peut-il rester local au tableau alors que les filtres doivent remonter à la page ? Que se passe-t-il à l'affichage si tu oublies la prop `key` sur les lignes ? Si l'utilisateur trie le tableau puis change un filtre, le tri doit-il être conservé ou réinitialisé ? Justifie ton choix.

### Étape 6 : les graphiques

`Graphiques` reçoit la même liste filtrée que le tableau et la passe à vos fonctions d'agrégation, puis à Recharts. Trois graphiques suffisent : offres par jour, top des technos, TJM moyen par niveau.

Le pattern Recharts, pour un graphique en barres :

```jsx
<ResponsiveContainer width="100%" height="100%">
  <BarChart data={donnees}>
    {/* axes, grille, tooltip, puis <Bar dataKey="..." /> */}
  </BarChart>
</ResponsiveContainer>
```

Donnez à chaque graphique une hauteur fixe via son conteneur, sinon le `ResponsiveContainer` ne sait pas quelle place prendre et n'affiche rien.

Concept : les graphiques ne refiltrent pas les données. Ils reçoivent déjà la liste filtrée et se contentent d'agréger. C'est tout l'intérêt de l'état remonté : la page filtre une fois, le tableau et les graphiques consomment le même résultat.

Question : si tu donnais à `Graphiques` la liste complète des offres au lieu de la liste filtrée, qu'est-ce qui se casserait quand l'utilisateur active un filtre ?

### Étape 7 : le compteur

Le plus simple. `Compteur` reçoit un nombre (la longueur de la liste filtrée) et l'affiche. Pas d'état, pas de logique.

Concept : un composant peut être minuscule et n'avoir qu'un seul rôle. C'est sain. Mieux vaut un petit composant clair qu'une grosse page qui fait tout.

Question : d'où vient le nombre que reçoit le compteur ? Qui le calcule, et pourquoi pas le compteur lui-même ?

### Étape 8 : remonter le state et tout connecter

C'est l'étape qui transforme quatre composants isolés en un dashboard. Dans `app/page.js` :

1. déclarez l'état des filtres dans un `useState` ;
2. calculez `offresFiltrees` en appliquant `filtrerOffres` à vos offres et vos filtres ;
3. passez `{ filtres, setFiltres }` à `<Filtres>` ;
4. passez `offresFiltrees` à `<TableauOffres>`, `<Graphiques>` et `<Compteur>`.

Une fois branché, testez : cochez "Remote". Le tableau se réduit, les graphiques changent, le compteur baisse, tout en même temps. Si un des trois ne bouge pas, c'est qu'il ne lit pas la même source. C'est exactement le bug que l'état remonté évite.

Concept : `offresFiltrees` est calculé une seule fois, au niveau de la page, et partagé. Pour éviter de le recalculer à chaque rendu sans raison, vous pouvez l'envelopper dans un `useMemo` qui ne se relance que si les offres ou les filtres changent. Pas obligatoire pour 25 offres, mais c'est le bon réflexe.

Questions : combien de fois la liste filtrée est-elle calculée à chaque changement de filtre, et combien de copies de cette liste existent en mémoire ? Si tu voulais ajouter demain un quatrième graphique, combien de lignes faudrait-il toucher dans la page ?

## 5. Pièges courants

Vous allez probablement croiser au moins l'un de ceux-là. Les connaître d'avance fait gagner du temps.

`"use client"` oublié. Un composant qui utilise `useState`, `useEffect` ou un `onClick` plante avec une erreur du type "useState is not a function" ou "you're importing a component that needs useState". La directive `"use client";` doit être la toute première ligne du fichier, avant les imports.

État dupliqué, donc désynchronisé. Si vous mettez l'état des filtres à la fois dans `Filtres` et dans la page (ou dans le tableau), vous aurez deux vérités. L'écran se contredit dès qu'on touche un filtre. La règle : un seul `useState` pour les filtres, dans la page, point.

`key` manquante dans une liste. React affiche un avertissement rouge dans la console et peut mélanger les lignes lors des re-rendus. Chaque élément d'un `.map()` a besoin d'une `key` unique et stable : utilisez l'`id` de l'offre, jamais l'index du tableau si l'ordre peut changer (ce qui est le cas avec le tri).

Données pas encore chargées au premier rendu. Si vous faites `.map()` sur les offres avant que le `fetch` ait répondu, vous travaillez sur un tableau vide (ou pire, sur `undefined`). Initialisez l'état des offres à `[]` et prévoyez un affichage de chargement.

Tri qui mute les données. `Array.sort()` trie sur place. Si vous triez la liste reçue en props directement, vous modifiez les données du parent et créez des bugs difficiles à traquer. Triez toujours une copie.

Graphique invisible. Recharts a besoin d'une hauteur explicite sur le conteneur du `ResponsiveContainer`, sinon il calcule une hauteur de zéro et n'affiche rien.

## 6. Socle et bonus

Socle attendu de tous les binômes :

- le tableau d'offres s'affiche et se trie au clic sur les en-têtes ;
- les filtres (télétravail, TJM minimum, expérience, ville) s'appliquent en live ;
- la recherche par mots-clés fonctionne ;
- au moins un graphique réagit aux filtres en même temps que le tableau ;
- le compteur affiche le nombre d'offres filtrées.

Bonus, dans l'ordre de difficulté croissante :

- les trois graphiques au lieu d'un seul ;
- le tri multi-colonnes (par exemple : d'abord par expérience, puis par TJM à expérience égale) ;
- une pagination du tableau (lignes par page, navigation) ;
- une carte des villes avec Leaflet, chargée via un `dynamic(() => import(...), { ssr: false })` pour ne pas casser le rendu serveur ;
- brancher la vraie base de l'atelier 2 à la place du JSON. Remplacez la source de données (la lecture du JSON ou la route API) par une requête vers votre base. Tant que chaque offre respecte le schéma vu plus haut, ni les filtres, ni le tableau, ni les graphiques ne changent. C'est la récompense d'avoir isolé la logique : on change la source, pas le reste.

## 7. Critère de réussite

Vous avez réussi quand votre dashboard tourne en local avec `npm run dev`, affiche les 25 offres de `exemple/offres.sample.json`, et que filtrer ou trier met à jour le tableau, les graphiques et le compteur ensemble, sans qu'aucun des trois ne se désynchronise des autres.

Avant de dire "c'est fini", faites le test concret : cochez un filtre télétravail, vérifiez que le compteur, le tableau et les graphiques changent au même instant et racontent la même histoire. Si oui, l'état remonté est correct et l'atelier est gagné.
