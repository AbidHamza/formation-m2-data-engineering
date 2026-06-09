-- Schema de la table contacts (atelier 2).
-- Le point important : la colonne cle_unique porte une contrainte UNIQUE.
-- C'est elle qui rend l'import idempotent (un upsert ON CONFLICT s'appuie dessus).
-- Le script charge_en_base.py cree cette table automatiquement si elle n'existe pas,
-- ce fichier sert de reference et permet de la creer a la main dans Supabase.

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

-- La cle_unique vaut l'email s'il existe, sinon nom + entreprise normalises.
-- Deux lignes qui produisent la meme cle sont consideree comme le meme contact.
