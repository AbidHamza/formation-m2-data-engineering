# Atelier 2 : du CSV à une base interrogeable

À l'atelier 1, vous avez produit un `contacts.csv`. C'est pratique pour regarder, mais un CSV reste un fichier mort : on ne peut pas vraiment l'interroger, on ne peut pas le partager à plusieurs sans le casser, et le jour où une source vous redonne les mêmes contacts, vous vous retrouvez avec des doublons partout.

Ici, on charge ce CSV dans une base Postgres (via Supabase). Une fois en base, vous interrogez les données en SQL et vous en faites quelque chose. Mais le vrai objectif de la séance est ailleurs : l'import doit être idempotent. Relancer le chargement ne doit jamais créer de doublon.

## Le concept clé : l'idempotence

Un import idempotent est un import qu'on peut relancer autant de fois qu'on veut sans changer le résultat. Le dixième passage laisse la base dans le même état que le premier.

Pourquoi ça compte en data engineering : un pipeline plante en cours de route, on le relance. Une source renvoie les mêmes données le lendemain, on réimporte. Si chaque relance crée des doublons, le système devient inutilisable au bout de quelques jours. L'idempotence sépare le script jetable du vrai pipeline.

Comment on l'obtient ici, en deux pièces :

1. Une colonne `cle_unique` avec une contrainte `UNIQUE`. Cette clé identifie un contact : l'email s'il existe, sinon le nom et l'entreprise normalisés (minuscules, sans accents, sans espaces superflus). Deux lignes qui produisent la même clé sont le même contact.
2. Un upsert à l'insertion : `INSERT ... ON CONFLICT (cle_unique) DO UPDATE`. On insère la ligne, et si la clé existe déjà, on met à jour la ligne existante au lieu d'en créer une seconde.

C'est tout. La contrainte `UNIQUE` détecte le conflit, le `ON CONFLICT DO UPDATE` décide quoi en faire.

## Le schéma de la table

Une seule table `contacts`. Le détail qui rend tout possible, c'est la dernière colonne et sa contrainte `UNIQUE`.

```sql
create table if not exists contacts (
    id            bigint generated always as identity primary key,
    prenom        text,
    nom           text,
    fonction      text,
    entreprise    text,
    secteur       text,
    ville         text,
    source        text,
    url_profil    text,
    email         text,
    date_collecte date,
    cle_unique    text unique not null
);
```

Le schéma complet est dans `exemple/schema.sql`. Le script crée la table automatiquement si elle n'existe pas, donc vous n'avez pas besoin de la créer à la main, mais le fichier sert de référence.

## Prérequis

- Un projet Supabase gratuit (un Postgres hébergé, gratuit pour ce qu'on en fait), ou un Postgres local si vous préférez.
- Python 3.

## Lancer le corrigé

Depuis la racine du dépôt, placez-vous dans le dossier du corrigé et installez les dépendances :

```bash
cd Atelier-2-Stockage/corrige
pip install psycopg2-binary pandas python-dotenv
```

Créez un fichier `.env` dans ce dossier avec votre chaîne de connexion. Sur Supabase, elle se trouve dans l'onglet Connect du projet :

```
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@db.xxxx.supabase.co:5432/postgres
```

Récupérez le `contacts.csv` produit à l'atelier 1 et placez-le dans ce dossier. Si vous ne l'avez pas, copiez l'exemple fourni :

```bash
copy ..\exemple\contacts.exemple.csv contacts.csv   # Windows
cp ../exemple/contacts.exemple.csv contacts.csv       # macOS / Linux
```

Lancez l'import :

```bash
python charge_en_base.py
```

Puis relancez-le une seconde fois :

```bash
python charge_en_base.py
```

Au second passage, le nombre de lignes affiché après import ne doit pas bouger. Si le compte augmente, l'import n'est pas idempotent et il y a un bug à corriger.

## L'exemple fourni

Le fichier `exemple/contacts.exemple.csv` contient 6 lignes, mais la ligne Doctolib / DUBOIS y figure deux fois (mêmes nom, entreprise et email). C'est volontaire.

Au premier import, vous obtenez 5 contacts, pas 6 : les deux lignes DUBOIS produisent la même `cle_unique` et n'en forment qu'une en base. En relançant le script, le compte reste à 5. C'est la démonstration concrète de l'idempotence sur un cas que vous pouvez vérifier à la main.

## Critères de réussite

Socle (à atteindre par tout le monde) :

- la table `contacts` est créée et contient le CSV chargé ;
- l'idempotence est vérifiée en relançant l'import : le nombre de lignes ne change pas.

Bonus (pour aller plus loin) :

- ajouter un index sur les colonnes qu'on interroge souvent, par exemple `ville` ou `secteur` ;
- écrire quelques requêtes SQL utiles répondant à une vraie question métier ;
- créer une vue qui agrège, par exemple les entreprises qui recrutent le plus (nombre de contacts par entreprise, triés du plus grand au plus petit).
