# Atelier 1 : collecter des milliers de contacts data en Île-de-France

Vous allez construire la première brique de la plateforme : un pipeline de collecte qui produit un fichier `contacts.csv` propre, dédoublonné, avec plusieurs milliers d'offres et de recruteurs data en Île-de-France. Ce fichier alimente toute la suite de la formation. L'atelier 2 le charge en base, l'atelier 3 l'affiche, l'atelier 4 envoie les candidatures. Si le CSV est bancal, tout ce qui suit casse.

Ce README n'est pas un énoncé qui renvoie à une solution. C'est un guide complet : il vous apprend à construire la collecte vous-même. On explique le pourquoi de chaque choix, on pose des questions pour vous faire réfléchir, et on vous laisse écrire le code dans le squelette `starter/`. Vous ne trouverez pas de fichier tout fait à copier. C'est volontaire : la valeur de l'atelier, c'est ce que vous comprenez en le faisant.

Durée visée : 3h30. Travail en binôme ou trinôme.

## 1. Ce qu'on construit

Un seul fichier de sortie, `contacts.csv`. Chaque ligne est une offre ou un recruteur data en Île-de-France, toujours avec les mêmes colonnes. Plusieurs sources alimentent ce fichier, mais elles écrivent toutes le même format.

L'objectif chiffré, c'est plusieurs milliers de lignes. Soyons honnêtes tout de suite sur d'où vient le volume : la grande majorité sort de l'API officielle France Travail. Elle est stable, légale, et ne casse pas. Le scraping (job boards, LinkedIn) est une compétence utile, mais il rapporte peu de lignes et il est fragile. On apprend les deux, on s'appuie sur l'API pour le volume. C'est exactement le raisonnement d'un ingénieur : on choisit la source fiable pour la quantité, on garde le scraping pour les cas où il n'y a pas d'API.

Une chose à retenir avant même d'écrire une ligne de code : la valeur n'est pas dans la collecte brute. N'importe qui peut télécharger des données. La valeur est dans le nettoyage et le dédoublonnage qui donnent un fichier exploitable.

## 2. Les notions à comprendre avant de coder

Lisez cette section en entier. Elle vous évitera de coder dans le mauvais ordre.

### Le schéma commun, à définir AVANT de collecter

C'est la règle numéro un. Si chaque source écrit ses colonnes dans son ordre, avec ses noms, la fusion est impossible. On se met d'accord sur un schéma unique, et toutes les sources s'y plient.

| Colonne | Contenu |
|---|---|
| `prenom` | Prénom du contact (souvent vide côté France Travail) |
| `nom` | Nom du contact, ou intitulé du recruteur |
| `fonction` | Recruteur, RH, responsable recrutement... |
| `entreprise` | Nom de l'entreprise qui recrute |
| `secteur` | Secteur d'activité |
| `ville` | Ville et département, ex. `Paris (75)` |
| `source` | D'où vient la ligne : `france_travail`, `hellowork`, `linkedin`... |
| `url_profil` | Lien vers l'offre ou le profil |
| `email` | Email pro si disponible |
| `date_collecte` | Date de collecte au format `AAAA-MM-JJ` |
| `cle_unique` | Identifiant calculé qui sert au dédoublonnage (voir plus bas) |

Règle d'or : si une valeur est inconnue, la cellule reste vide. On ne décale jamais une colonne. Un CSV mal aligné fait planter toute la fusion, et c'est pénible à diagnostiquer.

Les dix premières colonnes sont remplies par chaque source au moment de la collecte. La colonne `cle_unique` est différente : on la calcule à l'étape de fusion, une fois toutes les données rassemblées. On y revient.

### API REST et OAuth2 : la source du volume

France Travail expose une API REST officielle. Pour l'utiliser, il faut d'abord prouver qui vous êtes. Le mécanisme s'appelle OAuth2 en mode `client_credentials` : vous envoyez votre identifiant client et votre clé secrète à une URL de connexion, et l'API vous répond avec un jeton (token) temporaire, valable une vingtaine de minutes. Ensuite, chaque appel à l'API porte ce token dans son en-tête `Authorization`.

Deux pièges à connaître dès maintenant. Le token n'est valable que pour un certain `scope` (un périmètre de droits) : si le scope est faux, l'API refuse de vous authentifier. Et le token expire : sur une longue collecte, il faut en redemander un.

L'endpoint qui nous intéresse est la recherche d'offres. Comme il peut y avoir des milliers de résultats, l'API ne les renvoie pas d'un coup. Elle les découpe en pages via un paramètre `range` (par exemple `0-149` pour les 150 premières, `150-299` pour les suivantes). C'est la pagination. Vous avancez page par page jusqu'à avoir tout récupéré.

Question à vous poser : pourquoi paginer par tranches de 150 plutôt que demander les 5000 résultats d'un coup ? Qu'est-ce que ça change pour le serveur, pour votre mémoire, pour la gestion d'erreur si une page échoue au milieu ?

### Le scraping HTML : la compétence, pas le volume

Pour les job boards qui n'ont pas d'API ouverte, on récupère la page HTML et on en extrait les informations. C'est le rôle de BeautifulSoup : il parse le HTML et permet de cibler des éléments avec des sélecteurs CSS (les mêmes que vous utilisez en feuille de style : balise, classe, attribut).

Le scraping est fragile par nature. Vos sélecteurs dépendent du HTML exact du site. Le jour où le site change sa mise en page, votre script récupère du vide. C'est normal, c'est le métier. La bonne pratique : ouvrir l'inspecteur du navigateur (F12), repérer la vraie structure de la page, et ajuster vos sélecteurs. Aucun sélecteur n'est correct à vie.

### LinkedIn : volontairement bridé

LinkedIn détecte et bannit les comportements automatiques. On ne va pas y faire du volume. L'objectif est d'apprendre à manipuler un site qui se défend, sur un petit lot (30 à 50 profils), depuis votre propre compte. Le login se fait à la main dans le navigateur : taper le mot de passe par script est le déclencheur numéro un de blocage. Le volume des milliers de lignes vient d'ailleurs, surtout de l'API.

### La clé unique et le dédoublonnage

Plusieurs sources vont renvoyer le même recruteur ou la même entreprise. Sans dédoublonnage, votre fichier final est gonflé de doublons inutiles. Pour repérer deux lignes qui désignent la même personne, on construit une `cle_unique` :

- si la ligne a un email, la clé vaut l'email (c'est l'identifiant le plus fiable) ;
- sinon, la clé vaut le nom et l'entreprise, normalisés (minuscules, sans accents, espaces propres).

Deux lignes avec la même clé sont considérées comme la même entité, on n'en garde qu'une. La normalisation est essentielle : sans elle, `Doctolib` et `doctolib ` (avec un espace) seraient vus comme deux entreprises différentes.

Question : que se passe-t-il si deux sources renvoient le même recruteur, l'une avec son email et l'autre sans ? Laquelle garder, et comment votre logique de clé gère ce cas ?

### La fusion

À la fin, un script ramasse tous les CSV produits par les différentes sources, les empile, normalise les champs, calcule la clé unique, retire les doublons, et écrit le `contacts.csv` final avec un bilan chiffré. C'est le moment data engineering de la séance : vous voyez concrètement combien chaque source a apporté, et combien de doublons ont été éliminés.

## 3. Prérequis et installation

Vous avez besoin de Python 3 (`python --version` doit répondre 3.x) et des paquets suivants :

```bash
pip install requests beautifulsoup4 pandas python-dotenv playwright
playwright install chromium
```

`requests` pour les appels HTTP, `beautifulsoup4` pour parser le HTML, `pandas` pour la fusion, `python-dotenv` pour lire vos clés depuis un fichier `.env`, `playwright` pour piloter un vrai navigateur (LinkedIn).

Pour l'API France Travail :

1. Créez un compte sur [francetravail.io](https://francetravail.io).
2. Déclarez une application et demandez l'accès à l'API Offres d'emploi v2.
3. Récupérez votre identifiant client et votre clé secrète.
4. Le scope à utiliser dans la demande de token est `api_offresdemploiv2 o2dsoffre`.
5. Copiez `starter/.env.example` en `.env` (à la racine de l'atelier, là où vous lancerez vos scripts) et remplissez vos valeurs.

Le `.env` ne doit jamais partir sur Git. Vérifiez qu'il est ignoré. Les clés en clair dans un dépôt, c'est une faute.

## 4. La démarche, de A à Z

Vous travaillez dans le dossier `starter/`. Il contient un squelette par équipe, avec des `TODO` à compléter. Chaque équipe prend une source, mais toutes écrivent le même schéma. Mélangez les niveaux dans votre équipe : quelqu'un tient la technique, quelqu'un remplit et vérifie le CSV.

| Fichier starter | Source | Difficulté |
|---|---|---|
| `equipe_d_francetravail.py`, `atelier1_ingestion.py` | API France Travail (le gros du volume) | API REST, OAuth2 |
| `equipe_b_jobboards.py` | Job boards (HelloWork, APEC, Indeed) | Scraping HTML |
| `equipe_c_wttj.py` | Welcome to the Jungle | Scraping HTML |
| `equipe_a_linkedin.py` | LinkedIn (petit volume) | Navigateur piloté |
| `equipe_e_enrichment.py` | Enrichment des emails | Bonus |
| `equipe_f_annuaires.py` | Annuaires | Scraping HTML |
| `fusion_deduplication.py` | Fusion finale | pandas |

### Étape 0 : fixer le schéma

Avant tout, écrivez en dur la liste des colonnes dans une variable, dans le même ordre, identique pour chaque source. C'est cinq minutes de travail qui vous économisent une heure de débogage à la fusion.

Concept en jeu : un contrat de données. Toutes les sources respectent le même contrat, donc elles sont fusionnables sans surprise.

Question : pourquoi définir le schéma maintenant et pas après avoir vu ce que chaque source renvoie ?

### Étape 1 : obtenir un token France Travail

Dans `atelier1_ingestion.py`, la fonction qui demande le token est déjà esquissée. Comprenez ce qu'elle envoie : une requête POST vers l'URL de connexion, avec `grant_type`, `client_id`, `client_secret` et `scope`. La réponse contient un champ `access_token`.

Vérifiez que ça marche avant d'aller plus loin : affichez le début du token. Si vous obtenez une erreur d'authentification, le problème est presque toujours le scope ou une clé mal copiée.

Concept : OAuth2 client_credentials. Vous échangez un secret durable contre un token court.

Question : pourquoi l'API ne vous donne pas un token éternel ? Que protège l'expiration ?

### Étape 2 : un premier appel de recherche

Toujours dans le starter, la fonction de recherche attend des paramètres que vous devez compléter (les `TODO`). Il vous faut au minimum les mots-clés et le département. Ajoutez le `range` pour la pagination.

Commencez petit : un seul département, une seule page, et regardez la réponse. Faites un `print` du JSON pour comprendre sa structure. Vous verrez qu'une offre contient un bloc `entreprise`, un bloc `lieuTravail`, parfois un bloc `contact` avec un nom et un email, et un bloc `origineOffre` avec l'URL de l'offre.

Concept : explorer une réponse API avant de la traiter. On ne code jamais l'extraction à l'aveugle.

Indice sur les codes de réponse : `200` veut dire que c'était la dernière page, `206` qu'il reste des pages, `204` qu'il n'y a aucun résultat. L'en-tête `Content-Range` ressemble à `offres 0-149/1234` : le nombre après le slash est le total disponible. Servez-vous-en pour savoir quand vous arrêter.

### Étape 3 : transformer une offre en ligne du schéma

Écrivez une fonction qui prend une offre (un dictionnaire JSON) et renvoie une ligne au schéma commun. Toutes les offres n'ont pas de contact nommé : dans ce cas, gardez l'entreprise et l'URL de l'offre, c'est déjà assez pour postuler. Mettez `source` à `france_travail` et `date_collecte` à la date du jour.

Pensez aux champs absents. Un `offre.get("contact")` peut renvoyer `None`. Que se passe-t-il si vous appelez `.get("nom")` sur `None` ? Protégez-vous.

Concept : la transformation (le T d'un pipeline ETL). On passe d'un format source à un format cible normalisé.

Petit nettoyage indispensable : un champ qui contient un retour à la ligne ou une tabulation casse le CSV. Écrivez une fonction qui remplace ces caractères par un espace simple, et appliquez-la à chaque champ.

### Étape 4 : paginer et boucler sur tout l'Île-de-France

Maintenant on cherche le volume. Bouclez sur plusieurs métiers data (data engineer, data analyst, data scientist, big data, business intelligence...) croisés avec les huit départements d'Île-de-France (75, 77, 78, 91, 92, 93, 94, 95). Pour chaque combinaison, paginez par `range` jusqu'à avoir tout vu.

Ce croisement métiers x départements est ce qui fait passer de quelques dizaines de lignes à plusieurs milliers.

Deux garde-fous à prévoir. D'abord, dédoublonnez à la source : utilisez l'identifiant de l'offre comme clé dans un dictionnaire, sinon la même offre remontera sur plusieurs mots-clés. Ensuite, mettez une petite pause (quelques dixièmes de seconde) entre les appels pour respecter le rate limit de l'API.

Concept : le fan-out (multiplier les requêtes pour couvrir l'espace de recherche) et le respect des limites d'un service tiers.

Question : que se passe-t-il si deux mots-clés différents renvoient la même offre ? Pourquoi dédoublonner dès la collecte plutôt qu'attendre la fusion ?

### Étape 5 : écrire le CSV de la source

Écrivez vos lignes dans un fichier CSV propre. Trois détails qui comptent pour que ça s'ouvre correctement dans Excel français :

- encodage `utf-8-sig` (avec BOM), sinon les accents sont cassés sous Windows ;
- séparateur `;` ;
- protection des champs qui contiennent un `;` ou un `"` (le mode `QUOTE_MINIMAL` de la bibliothèque CSV s'en charge).

Vérifiez le résultat en ouvrant le fichier. Les colonnes sont-elles alignées ? Y a-t-il des lignes décalées ?

### Étape 6 : les sources scraping (job boards, WTTJ)

Dans `equipe_b_jobboards.py` et `equipe_c_wttj.py`, la démarche est la même. Vous faites une requête GET sur la page de recherche du site, vous passez la réponse à BeautifulSoup, et vous ciblez les cartes d'offres avec un sélecteur CSS.

Point critique : envoyez un en-tête `User-Agent` réaliste. Sans lui, beaucoup de sites renvoient une erreur. Et mettez une pause d'une à deux secondes entre les pages, on ne martèle pas un serveur.

Les sélecteurs CSS dans le squelette sont un point de départ, probablement déjà périmés. C'est ici que vous ouvrez F12, vous inspectez la vraie page, et vous trouvez les bonnes balises. C'est le coeur de l'exercice scraping, pas un détail.

Concept : extraction de données semi-structurées depuis du HTML, et fragilité associée.

Question : qu'est-ce qui rend cette source moins fiable que l'API ? Que faites-vous le jour où le sélecteur ne renvoie plus rien ?

### Étape 7 : LinkedIn (petit volume, navigateur visible)

Dans `equipe_a_linkedin.py`, vous pilotez un vrai navigateur Chromium avec Playwright. Lancez-le en mode visible (non headless) : c'est plus humain et vous voyez ce qui se passe. Allez sur la page de login, et connectez-vous à la main. Le script attend que vous ayez fini, puis lance la recherche.

Restez modeste : trois pages, des pauses aléatoires entre les actions (un humain ne clique pas toutes les 200 ms). Les sélecteurs LinkedIn changent souvent, même réflexe F12 que pour les job boards.

Concept : automatisation d'un site dynamique et discrétion (éviter les patterns qui trahissent un robot).

### Étape 8 : la fusion et le dédoublonnage

C'est l'aboutissement. Dans `fusion_deduplication.py`, le script lit tous les CSV présents (sauf le `contacts.csv` final lui-même), les empile dans un seul tableau pandas, puis :

1. nettoie tous les champs (purge des retours à la ligne, espaces multiples) ;
2. normalise les champs métier (par exemple, regrouper les variantes de fonction RH sous une seule étiquette) ;
3. supprime les lignes vraiment vides (ni entreprise, ni nom, ni email : elles n'apportent rien) ;
4. calcule la `cle_unique` : email s'il existe, sinon nom et entreprise normalisés ;
5. dédoublonne d'abord par email (le plus fiable), puis par la clé nom+entreprise ;
6. écrit `contacts.csv` et affiche un bilan : total, répartition par source, nombre d'emails, doublons retirés.

Indice utile pour lire des CSV de provenances variées : pandas sait détecter seul le séparateur si vous lui passez `sep=None` avec le moteur Python, et `encoding="utf-8-sig"` gère le BOM. Ça vous évite de casser quand une équipe a sauvegardé en `,` au lieu de `;`.

Concept : c'est tout le data engineering condensé en une étape. Empiler, normaliser, dédoublonner, mesurer.

Question : dans quel ordre dédoublonner, par email puis par nom+entreprise, ou l'inverse ? Pourquoi l'ordre change le résultat ?

## 5. Pièges courants et comment s'en sortir

**Erreur 400 sur la pagination.** L'API limite la profondeur de pagination. Au-delà d'un certain `range` (autour de 1150), elle renvoie un 400. Ne cherchez pas à aller plus loin : arrêtez la boucle sur cette combinaison et passez à la suivante. C'est pour ça qu'on multiplie métiers et départements plutôt que paginer à l'infini sur une seule recherche.

**Token refusé.** Presque toujours un scope incorrect ou une clé mal copiée. Vérifiez que le scope est exactement `api_offresdemploiv2 o2dsoffre`, et qu'il n'y a pas d'espace parasite dans vos clés du `.env`.

**Erreur 500 juste après avoir créé le compte.** Quand l'abonnement à l'API est tout neuf, le compte met un peu de temps à se propager côté France Travail. Une 500 dans les premières minutes peut simplement vouloir dire ça. Attendez, réessayez plus tard.

**Sélecteurs HTML qui ne renvoient rien.** Le site a changé sa structure, ou il sert un contenu chargé en JavaScript que `requests` ne voit pas. Ouvrez F12, comparez le HTML réel à votre sélecteur. Si la page se construit en JavaScript, `requests` ne suffit pas, il faut un navigateur (Playwright).

**Captcha ou blocage LinkedIn.** Vous avez fait trop de requêtes trop vite. Réduisez le volume, augmentez les pauses, et n'enchaînez pas les sessions. LinkedIn n'est pas la source du volume, inutile d'insister.

**CSV décalé à la fusion.** Une source a écrit ses colonnes dans le désordre ou a oublié une colonne. Revenez à l'étape 0 : le schéma doit être identique partout.

## 6. Socle et bonus

**Socle (tout le monde y arrive).** Un `contacts.csv` au schéma commun, dédoublonné, avec plusieurs milliers de lignes. La majorité du volume vient de l'API France Travail, c'est attendu et normal.

**Bonus.**

- Enrichir les emails pro (équipe enrichment) sur un maximum de lignes, à partir du nom et de l'entreprise.
- Croiser réellement plusieurs sources de scraping en plus de l'API.
- Produire des statistiques de qualité en sortie : taux de doublons retirés, taux d'emails trouvés, répartition par source.

## 7. Comment savoir que vous avez réussi

Vous avez réussi quand :

- `contacts.csv` existe et s'ouvre proprement (colonnes alignées, accents corrects) ;
- toutes les lignes respectent le schéma, dans le bon ordre ;
- le fichier est dédoublonné (pas deux fois le même email, pas deux fois le même nom+entreprise) ;
- le fichier contient plusieurs milliers de lignes.

Avant de viser le volume réel, testez votre fusion sur le petit jeu de données fourni. `exemple/contacts.exemple.csv` montre exactement la sortie attendue : dix lignes France Travail, séparateur `;`, schéma complet. On y voit le cas réaliste où beaucoup de lignes n'ont pas de nom de contact (juste l'entreprise et l'URL), et où l'email est souvent vide. C'est normal. Combler ces trous, c'est justement le travail bonus d'enrichment.

Un mot pour finir sur le cadre. Vous collectez des données professionnelles publiques (entreprise, fonction, email pro publié dans une offre) pour des candidatures ciblées, pas pour du spam de masse. Respectez les conditions d'utilisation de chaque source, n'aspirez pas un site qui l'interdit, et gardez en tête qu'une personne doit pouvoir demander le retrait de ses données. L'API officielle est la voie propre, c'est une raison de plus de s'appuyer dessus.
