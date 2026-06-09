"""
CORRIGÉ : Atelier 2 : charger contacts.csv en base, de façon idempotente
=========================================================================

On prend le contacts.csv de l'atelier 1 et on le charge dans Postgres (Supabase).
Le point clé : l'import est IDEMPOTENT. On peut le relancer autant de fois qu'on
veut, la base ne crée jamais de doublon. C'est tout l'enjeu de la séance.

Le mécanisme : une colonne `cle_unique` avec une contrainte UNIQUE, et un upsert
(INSERT ... ON CONFLICT DO UPDATE). Si la clé existe déjà, on met à jour la ligne
au lieu d'en créer une deuxième.

La clé : l'email s'il existe, sinon nom + entreprise normalisés. Deux lignes qui
produisent la même clé sont le même contact.

Lancement :
 pip install psycopg2-binary pandas python-dotenv
 # DATABASE_URL=postgresql://... dans le .env (onglet Connect de Supabase)
 python charge_en_base.py
 python charge_en_base.py # relancer : COUNT(*) ne bouge pas -> idempotent
"""

import os
import unicodedata

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

CSV = "contacts.csv"
DATABASE_URL = os.getenv("DATABASE_URL")

SCHEMA = """
create table if not exists contacts (
 id bigint generated always as identity primary key,
 prenom text,
 nom text,
 fonction text,
 entreprise text,
 secteur text,
 ville text,
 source text,
 url_profil text,
 email text,
 date_collecte date,
 cle_unique text unique not null
);
"""

COLONNES = [
 "prenom", "nom", "fonction", "entreprise", "secteur",
 "ville", "source", "url_profil", "email", "date_collecte", "cle_unique",
]


def normaliser(v) -> str:
 """minuscules, sans accents, sans espaces superflus -> pour comparer."""
 if not isinstance(v, str):
 return ""
 v = unicodedata.normalize("NFKD", v)
 v = "".join(c for c in v if not unicodedata.combining(c))
 return " ".join(v.lower().split())


def cle_unique(ligne) -> str:
 """email si présent, sinon nom + entreprise normalisés."""
 email = normaliser(ligne.get("email", ""))
 if email:
 return f"email:{email}"
 return f"noment:{normaliser(ligne.get('nom', ''))}|{normaliser(ligne.get('entreprise', ''))}"


def charger_csv():
 df = pd.read_csv(CSV, sep=None, engine="python", encoding="utf-8-sig", dtype=str)
 df = df.fillna("")
 lignes = []
 for _, row in df.iterrows():
 d = {c: row.get(c, "") for c in COLONNES if c != "cle_unique"}
 d["cle_unique"] = cle_unique(d)
 # date vide -> None, sinon Postgres refuse la chaîne ""
 d["date_collecte"] = d["date_collecte"] or None
 lignes.append(tuple(d[c] for c in COLONNES))
 return lignes


def upsert(conn, lignes):
 """INSERT ... ON CONFLICT : c'est CE qui rend l'import idempotent."""
 sql = f"""
 insert into contacts ({", ".join(COLONNES)})
 values %s
 on conflict (cle_unique) do update set
 fonction = excluded.fonction,
 email = excluded.email,
 url_profil = excluded.url_profil
 """
 with conn.cursor() as cur:
 execute_values(cur, sql, lignes, page_size=500)
 conn.commit()


def compter(conn) -> int:
 with conn.cursor() as cur:
 cur.execute("select count(*) from contacts")
 return cur.fetchone()[0]


if __name__ == "__main__":
 if not DATABASE_URL:
 raise SystemExit("DATABASE_URL manquant dans le .env (onglet Connect de Supabase).")

 lignes = charger_csv()
 print(f"{len(lignes)} lignes lues dans {CSV}")

 conn = psycopg2.connect(DATABASE_URL)
 try:
 with conn.cursor() as cur:
 cur.execute(SCHEMA)
 conn.commit()

 avant = compter(conn)
 upsert(conn, lignes)
 apres = compter(conn)

 print(f"Avant import : {avant} lignes")
 print(f"Apres import : {apres} lignes")
 print(f"Nouveaux contacts : {apres - avant} | doublons ignores : {len(lignes) - (apres - avant)}")
 print(">>> Relance ce script : 'Apres import' ne doit PAS augmenter. C'est l'idempotence.")
 finally:
 conn.close()
