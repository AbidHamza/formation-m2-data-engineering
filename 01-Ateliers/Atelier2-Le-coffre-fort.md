# Atelier 2 — Le coffre-fort

> Format : storytelling + atelier pratique. Durée 3h30. Niveau hétérogène.
> Livrable : **le `contacts.csv` de l'atelier 1 chargé dans une vraie base Postgres**, sans doublon, requêtable en SQL. On relance l'import, et la base ne bouge pas d'une ligne.

---

## 🎬 Le pitch (10 min)

> *« La semaine dernière, vous avez ramené 5000 recruteurs. Beau boulot. Ouvrez le fichier.*
>
> *Maintenant, trouvez-moi tous les DRH de boîtes finance, à Paris, qui recrutent en data, triés par date. Allez. Dans Excel.*
>
> *Vous galérez. Normal. Un CSV de 5000 lignes, c'est un fichier mort. Vous ne pouvez pas l'interroger, vous ne pouvez pas le partager à plusieurs sans le casser, et le jour où une source vous redonne les mêmes contacts, vous vous retrouvez avec 8000 lignes dont 3000 doublons.*
>
> *Aujourd'hui, on transforme ce fichier mort en machine vivante. On le met dans une vraie base. Et après, en une requête, vous sortez exactement qui contacter. »*

L'idée : ils ont senti la douleur du CSV à l'atelier 1 (la fusion, les doublons, les formats incohérents). L'atelier 2 résout cette douleur pour de bon. Le CSV était l'amorce, la base est l'outil qu'ils vont vraiment utiliser pour le reste de la formation.

Pourquoi ça marche : la motivation est directe. Sans base, pas de matching à l'atelier 4, pas de dashboard à l'atelier 6. Le coffre-fort, c'est la fondation de toute la suite.

---

## 🎯 La règle du jeu

- **Objectif Socle** : le `contacts.csv` est chargé dans Postgres (Supabase), une table propre, **zéro doublon**. On relance l'import : la base ne grossit pas. C'est ça, l'idempotence.
- **Le test qui prouve tout** : lancer le script d'import deux fois de suite. Si le `COUNT(*)` est identique après le deuxième passage, c'est gagné. Sinon, il y a un bug d'idempotence.
- **Une requête métier réelle** : à la fin, chacun écrit une requête SQL qui répond à une vraie question (« les recruteurs data dans le 92, par entreprise »). La base doit servir, pas juste exister.

---

## 🗄️ Le modèle de données (le cœur de la séance)

On ne jette pas 10 colonnes dans une table à plat. On modélise. C'est la compétence de l'atelier.

Point de départ minimal (Socle) : une seule table `contacts`, mais avec les bonnes contraintes.

```sql
create table contacts (
    id           bigint generated always as identity primary key,
    prenom       text,
    nom          text,
    fonction     text,
    entreprise   text,
    secteur      text,
    ville        text,
    source       text,
    url_profil   text,
    email        text,
    date_collecte date,
    -- la clé qui empêche les doublons :
    cle_unique   text unique
);
```

La `cle_unique` est ce qui rend l'import idempotent. On la construit à partir de ce qui identifie vraiment un contact : `email` s'il existe, sinon `nom + entreprise` normalisés (minuscules, sans accents, sans espaces superflus). Deux lignes qui produisent la même clé sont le même contact.

Modèle cible (Bonus) : on normalise en deux tables.

```
entreprises (id, nom, secteur, ville)
contacts    (id, prenom, nom, fonction, email, entreprise_id → entreprises.id, ...)
```

Pourquoi : « Capgemini » apparaît 200 fois dans le CSV. Le stocker 200 fois, c'est de la donnée dupliquée. Une table `entreprises` + une clé étrangère, c'est la normalisation relationnelle. On en discute même si tous ne l'implémentent pas.

---

## ⏱️ Le déroulé (3h30)

| Temps | Phase | Ce qui se passe |
|-------|-------|-----------------|
| 0:00 – 0:10 | **Le pitch** | La démo « cherche-moi ça dans Excel ». On pose le problème. |
| 0:10 – 0:40 | **Modélisation** | Au tableau, ensemble : quelles tables, quelles colonnes, quelle clé d'unicité. On dessine avant de coder. |
| 0:40 – 1:10 | **Setup Supabase** | Créer le projet, récupérer l'URL et la clé, se connecter depuis Python. Créer la table. |
| 1:10 – 1:25 | **Pause** | — |
| 1:25 – 2:30 | **L'import idempotent** | Lire le CSV, construire la clé unique, faire un `upsert`. Le cœur technique. |
| 2:30 – 3:00 | **Le test d'idempotence** | On relance l'import. `COUNT(*)` avant / après. On vérifie que rien ne double. |
| 3:00 – 3:30 | **Requêtes métier** | Chacun écrit 2-3 requêtes SQL qui répondent à une vraie question. Restitution. |

---

## 🔧 Le vrai apprentissage : l'idempotence

C'est le mot de la séance. À marteler.

> Un import idempotent, c'est un import qu'on peut relancer 100 fois sans casser la base. Le 100e passage donne le même résultat que le 1er.

Pourquoi c'est central en data engineering : un pipeline plante en cours de route, on le relance. Une source nous renvoie les mêmes données demain, on réimporte. Si chaque relance crée des doublons, le système est inutilisable. L'idempotence, c'est ce qui distingue un script jetable d'un vrai pipeline (et c'est exactement ce qu'on automatise à l'atelier 3).

L'outil concret : `INSERT ... ON CONFLICT (cle_unique) DO UPDATE` (l'upsert Postgres). On insère, et si la clé existe déjà, on met à jour au lieu de créer une ligne en double.

Les problèmes qu'ils vont rencontrer (et qu'on veut qu'ils rencontrent) :
- **Quelle clé d'unicité ?** Beaucoup de lignes n'ont pas d'email. Il faut une clé de repli (nom + entreprise normalisés). C'est une vraie décision de design.
- **Normalisation avant comparaison** : « Dupont » et « DUPONT » doivent produire la même clé, sinon le doublon passe.
- **Types** : `date_collecte` est une vraie date, pas du texte. Postgres est strict, c'est une bonne chose.

---

## ✅ Critères de réussite

- **Socle** (toute la classe) : la table `contacts` contient le CSV chargé, sans doublon. Relancer l'import laisse le `COUNT(*)` identique. Au moins une requête SQL métier qui tourne.
- **Bonus** (équipes rapides) :
  - schéma normalisé (`entreprises` + clé étrangère),
  - index sur les colonnes qu'on interroge souvent (`ville`, `secteur`),
  - une vue SQL qui agrège (nb de contacts par entreprise, par source),
  - gestion des contacts « expirés » (historisation plutôt que suppression).

---

## 🔌 Ce dont chaque poste a besoin (à préparer avant)

- Python 3.11+, `pip install psycopg2-binary pandas python-dotenv` (ou le client `supabase`).
- Un compte Supabase (gratuit) et un projet créé. URL + clé service dans le `.env`, jamais en dur.
- Le `contacts.csv` de l'atelier 1 à portée de main (ou le corrigé fourni si une équipe n'a pas fini).

---

## 🪝 Accroche pour la suite

À la fin : *« Votre base est vivante. 5000 contacts qu'on interroge en une requête. Mais pour l'instant, c'est vous qui lancez l'import à la main. La prochaine fois, on construit le robot qui le fait tout seul, toutes les nuits, même quand vous dormez, et qui se relève tout seul s'il plante. »*

→ enchaîne sur l'atelier 3 (pipeline et orchestration).
