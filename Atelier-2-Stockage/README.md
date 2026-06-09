# Atelier 2 : charger un CSV en base sans jamais créer de doublon

À l'atelier 1, vous avez produit un `contacts.csv`. Un fichier, c'est pratique pour regarder, mais ça reste mort : on ne l'interroge pas vraiment, on ne le partage pas à plusieurs sans le casser, et le jour où une source vous redonne les mêmes contacts, vous accumulez les doublons.

Ici, vous allez charger ce CSV dans une base Postgres (hébergée sur Supabase). Une fois en base, les données s'interrogent en SQL et alimentent la suite : le dashboard de l'atelier 3, l'envoi de l'atelier 4. Mais le vrai sujet de la séance est ailleurs : votre import doit être idempotent. Relancer le chargement ne doit jamais ajouter de doublon.

Ce guide ne vous donne pas le code à recopier. Il vous explique les notions, la démarche étape par étape, et vous pose les questions qui vous mettent sur la piste. Vous écrivez le script vous-même. C'est à ce prix que vous comprendrez ce que vous fabriquez.

## 1. Ce que vous devez produire

Un script Python qui :

1. lit le `contacts.csv` de l'atelier 1 ;
2. se connecte à une base Postgres sur Supabase ;
3. crée la table `contacts` si elle n'existe pas ;
4. insère les contacts de telle sorte que relancer le script ne change pas le nombre de lignes en base.

Preuve de réussite : charger le fichier d'exemple fourni donne 5 lignes en base (pas 6), et relancer l'import laisse 5 lignes. On y revient à la fin.

## 2. Les notions à comprendre avant de coder

Ne commencez pas à taper du code tout de suite. Ces deux idées sont le cœur de l'atelier. Si elles sont claires, le reste suit.

### L'idempotence

Un import idempotent est un import qu'on peut relancer autant de fois qu'on veut sans changer le résultat. Le dixième passage laisse la base exactement dans l'état du premier.

Pourquoi ça compte vraiment. Un pipeline plante en cours de route : on le relance. Une source renvoie les mêmes données le lendemain : on réimporte. Si chaque relance crée des doublons, le système est inutilisable au bout de quelques jours. L'idempotence, c'est la frontière entre un script jetable et un vrai pipeline de production.

Question à vous poser : dans votre tête, à quel moment précis du chargement le doublon est-il évité ? Au moment de lire le CSV, ou au moment d'écrire en base ? La réponse oriente toute votre conception.

### La clé unique métier

Pour ne jamais dupliquer un contact, il faut d'abord savoir reconnaître que deux lignes désignent le même contact. C'est le rôle d'une clé. Pas l'`id` auto-incrémenté de la table (celui-là est différent à chaque insertion, il ne sert à rien pour comparer), mais une clé construite à partir des données métier.

La règle qu'on propose : la clé vaut l'email si le contact en a un, sinon le couple nom + entreprise. Et pas bruts : normalisés. `DUBOIS` et `dubois ` doivent produire la même clé, donc on passe en minuscules, on retire les accents, on supprime les espaces superflus avant de comparer.

Questions à vous poser :

- Pourquoi une clé métier plutôt que de se reposer sur l'`id` auto-incrémenté ? Qu'est-ce que l'`id` ne sait pas faire ?
- Deux contacts sans email, même nom mais dans deux entreprises différentes : même clé ou pas ? Et même nom, même entreprise, mais deux personnes différentes dans la vraie vie : votre clé les distingue-t-elle ? (Indice : non, et c'est un compromis assumé. À quel moment ce compromis devient-il un problème ?)
- Si un contact a un email un jour et pas le lendemain dans la source, sa clé change-t-elle ? Que se passe-t-il alors en base ?

## 3. Prérequis et installation

### Compte Supabase

Supabase, c'est un Postgres hébergé, gratuit pour ce dont vous avez besoin ici. Créez un compte sur supabase.com, puis un nouveau projet. Notez le mot de passe de la base au moment de la création, vous en aurez besoin et il n'est plus affiché ensuite.

Une fois le projet prêt, ouvrez l'onglet **Connect** (en haut du projet). Vous y trouvez la chaîne de connexion, une URL qui ressemble à :

```
postgresql://postgres:VOTRE_MOT_DE_PASSE@db.xxxx.supabase.co:5432/postgres
```

C'est cette URL qui permet à votre script de se connecter.

### Python et bibliothèques

Vous avez besoin de Python 3 et de trois bibliothèques :

```bash
pip install pandas psycopg2-binary python-dotenv
```

- `pandas` lit le CSV.
- `psycopg2` parle à Postgres.
- `python-dotenv` charge les variables d'un fichier `.env`.

### Le fichier .env

Ne mettez jamais votre chaîne de connexion en dur dans le code. Elle contient un mot de passe, et un fichier de code finit toujours par être partagé, commité, envoyé. Créez un fichier `.env` à côté de votre script :

```
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@db.xxxx.supabase.co:5432/postgres
```

Votre script lit ensuite cette valeur via `python-dotenv` et `os.getenv("DATABASE_URL")`. Pensez à ajouter `.env` à votre `.gitignore`.

Question : que doit faire votre script si `DATABASE_URL` est absent ou vide ? Planter avec un message clair, ou continuer en silence ? Lequel vous fait perdre le moins de temps en cas d'oubli ?

## 4. La démarche, étape par étape

Construisez votre script morceau par morceau. Testez après chaque étape, ne gardez pas tout pour la fin.

### Étape 1 : modéliser la table

Une seule table, `contacts`. Voici les colonnes à prévoir :

`id`, `prenom`, `nom`, `fonction`, `entreprise`, `secteur`, `ville`, `source`, `url_profil`, `email`, `date_collecte`, `cle_unique`.

Deux colonnes méritent votre attention :

- `id` : la clé primaire technique, en auto-incrément (`bigint generated always as identity primary key`). C'est l'identité interne de la ligne, gérée par Postgres.
- `cle_unique` : la clé métier décrite plus haut, de type `text`. Elle doit porter une contrainte `UNIQUE` et être `not null`.

La contrainte `UNIQUE` sur `cle_unique` est la pièce centrale. C'est elle qui interdit physiquement à la base d'avoir deux lignes avec la même clé. Sans elle, aucun mécanisme d'idempotence ne tient : la base accepterait les doublons.

Vous pouvez créer la table de deux façons : laisser votre script l'exécuter au démarrage (`create table if not exists ...`), ou la créer à la main dans l'éditeur SQL de Supabase. Le schéma complet, prêt à copier, est dans `exemple/schema.sql` : ouvrez-le, c'est votre référence.

Question : pourquoi `if not exists` plutôt qu'un simple `create table` ? Que se passe-t-il au deuxième lancement du script sinon ?

### Étape 2 : lire le CSV

Chargez le CSV avec `pandas`. Deux pièges classiques vous attendent ici.

Le séparateur. Ouvrez `exemple/contacts.exemple.csv` dans un éditeur de texte et regardez : les colonnes sont séparées par des `;`, pas des `,`. Beaucoup de CSV produits en France utilisent le point-virgule (Excel français en tête). Ne supposez pas, vérifiez. `pandas` sait détecter le séparateur automatiquement si vous le lui demandez.

L'encodage. Un CSV venu de Windows ou Excel contient souvent un BOM (un caractère invisible en tête de fichier) et des accents qui s'affichent mal si l'encodage est mal lu. L'encodage `utf-8-sig` gère le BOM proprement. Sans ça, votre première colonne peut se retrouver avec un nom à rallonge bizarre.

Pensez aussi à lire toutes les colonnes en texte et à remplacer les valeurs manquantes par des chaînes vides, pour ne pas vous retrouver avec des `NaN` qui traînent.

Question : votre CSV d'atelier 1 a-t-il forcément le même séparateur et le même encodage que l'exemple ? Comment votre code peut-il rester robuste si ça change d'un fichier à l'autre ?

### Étape 3 : calculer la clé unique de chaque ligne

Le CSV n'a pas de colonne `cle_unique`. C'est à votre code de la fabriquer, ligne par ligne, à partir des données.

Écrivez d'abord une petite fonction de normalisation : elle prend un texte et renvoie sa version comparable (minuscules, sans accents, espaces nettoyés). Pour retirer les accents, le module `unicodedata` de la bibliothèque standard fait le travail.

Écrivez ensuite la fonction qui produit la clé d'une ligne. Sa logique : si l'email normalisé n'est pas vide, la clé est basée dessus ; sinon, elle combine nom et entreprise normalisés. Préfixer chaque type de clé (par exemple `email:...` ou `nament:...`) évite qu'un email puisse par hasard entrer en collision avec un couple nom+entreprise.

```python
def cle_unique(ligne) -> str:
    ...
```

Petit détail qui mord : une `date_collecte` vide doit devenir `None`, pas la chaîne `""`, sinon Postgres refuse d'insérer une chaîne vide dans une colonne de type `date`.

Questions :

- Que se passe-t-il si une ligne n'a ni email, ni nom, ni entreprise ? Quelle clé obtenez-vous, et est-ce un problème ?
- Deux lignes différentes peuvent-elles produire la même clé alors qu'il s'agit de personnes différentes ? Comment limiteriez-vous ce risque ?

### Étape 4 : insérer en base de façon idempotente

C'est l'étape qui fait ou défait l'atelier.

Première intuition, naïve : pour chaque ligne, vérifier si la clé existe déjà avec un `SELECT`, et n'insérer que si elle est absente. Ça marche, mais c'est fragile (deux imports simultanés peuvent passer la vérification en même temps) et lent (une requête par ligne). Postgres offre mieux.

La bonne approche : un upsert, avec `INSERT ... ON CONFLICT`.

```sql
insert into contacts (...) values (...)
on conflict (cle_unique) do update set ...
```

Le principe : vous tentez d'insérer la ligne. Si la contrainte `UNIQUE` sur `cle_unique` détecte un conflit (la clé existe déjà), au lieu de planter, Postgres exécute la clause `ON CONFLICT`. C'est la base elle-même qui arbitre, de façon atomique.

Deux variantes existent :

- `ON CONFLICT (cle_unique) DO NOTHING` : en cas de conflit, on ne touche à rien.
- `ON CONFLICT (cle_unique) DO UPDATE SET ...` : en cas de conflit, on met à jour la ligne existante avec les nouvelles valeurs.

Préférez `DO UPDATE` ici. Réfléchissez à pourquoi : si la source vous redonne un contact dont la fonction ou l'email a changé entre deux collectes, voulez-vous garder la vieille valeur ou la rafraîchir ? `DO NOTHING` fige la première version vue ; `DO UPDATE` garde la donnée à jour tout en restant idempotent (relancer avec les mêmes données réécrit les mêmes valeurs, donc le résultat ne bouge pas).

Quand vous écrivez votre `DO UPDATE SET`, choisissez les colonnes à rafraîchir (par exemple `fonction`, `email`, `url_profil`) et utilisez le pseudo-enregistrement `excluded` pour référencer la valeur qu'on tentait d'insérer.

Questions :

- Pourquoi `ON CONFLICT` est-il préférable à un `SELECT` puis `INSERT` séparés ? Pensez à ce qui se passe si deux personnes lancent l'import en même temps.
- Avec `DO UPDATE`, relancer le script deux fois de suite produit-il le même état final ? Pourquoi est-ce toujours idempotent même si on écrit à chaque passage ?

### Étape 5 : compter et prouver l'idempotence

Avant et après l'insertion, faites un `SELECT count(*) from contacts` et affichez les deux nombres. C'est votre instrument de mesure.

Au premier import : le compte passe de 0 au nombre de contacts uniques. Au deuxième import (script relancé) : le compte ne doit pas bouger. Affichez aussi le nombre de nouveaux contacts et de doublons ignorés, ça rend la démonstration parlante.

## 5. Pièges courants

- **Mauvais séparateur.** Vous lisez le CSV avec `,` alors qu'il est en `;` : tout se retrouve dans une seule colonne. Vérifiez le fichier à l'œil avant de coder.
- **Encodage.** Sans `utf-8-sig`, le BOM colle un préfixe invisible au nom de la première colonne, et `df["prenom"]` lève une `KeyError` mystérieuse. Les accents peuvent aussi s'afficher en charabia.
- **Clé vide.** Si une ligne n'a ni email ni nom ni entreprise, votre clé peut être quasi vide et entrer en collision avec une autre ligne vide. Décidez quoi faire de ces lignes plutôt que de les subir.
- **Date vide.** Insérer `""` dans une colonne `date` fait planter Postgres. Convertissez en `None`.
- **Contrainte UNIQUE oubliée.** Si `cle_unique` n'a pas sa contrainte `UNIQUE`, le `ON CONFLICT` n'a rien sur quoi s'appuyer : soit la requête échoue, soit (sans `ON CONFLICT`) vous insérez tranquillement des doublons. C'est l'erreur qui casse l'idempotence en silence.
- **Connexion refusée.** Vérifiez le mot de passe dans `DATABASE_URL`, et que vous utilisez bien la chaîne de l'onglet Connect du bon projet Supabase.

## 6. Socle et bonus

Socle, à atteindre par tout le monde :

- la table `contacts` existe et contient les contacts du CSV ;
- l'idempotence est vérifiée : relancer l'import ne change pas le nombre de lignes.

Bonus, pour aller plus loin :

- afficher le nombre de doublons évités à chaque import (lignes lues moins nouveaux contacts insérés) ;
- gérer proprement les mises à jour : modifiez à la main la `fonction` ou l'`email` d'un contact dans le CSV, relancez, et vérifiez que la base a bien repris la nouvelle valeur sans créer de ligne en plus ;
- ajouter un index sur une colonne souvent interrogée (`ville`, `secteur`) et écrire une requête SQL qui répond à une vraie question métier, par exemple les entreprises qui recrutent le plus.

## 7. Critère de réussite

Le fichier `exemple/contacts.exemple.csv` contient 6 lignes, mais la ligne Doctolib / DUBOIS y figure deux fois (mêmes nom, entreprise et email). C'est volontaire, c'est votre cas de test.

Au premier import, vous devez obtenir **5 contacts, pas 6** : les deux lignes DUBOIS produisent la même `cle_unique` et n'en forment qu'une en base. En relançant le script, le compte **reste à 5**.

Si vous obtenez 6 au premier passage, votre clé ne reconnaît pas les deux DUBOIS comme un seul contact. Si le compte augmente au second passage, votre insertion n'est pas idempotente. Dans les deux cas, vous savez exactement quoi corriger. C'est la preuve concrète que vous cherchez.
