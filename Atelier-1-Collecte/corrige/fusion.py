"""
CORRIGÉ : Fusion de toutes les sources en un seul contacts.csv propre
======================================================================

C'est LE moment data engineering de la séance. Chaque équipe a produit son
CSV (france_travail.csv, hellowork.csv, linkedin.csv, ...). Ce script :
 1. lit tous les CSV présents dans le dossier,
 2. les empile,
 3. nettoie et normalise,
 4. dédoublonne intelligemment,
 5. écrit contacts.csv et affiche le bilan (a-t-on 5000 ?).

Lancement (à projeter en live devant la classe) :
 pip install pandas
 python fusion.py
"""

import glob
import unicodedata
import pandas as pd

COLONNES = [
 "prenom", "nom", "fonction", "entreprise",
 "secteur", "ville", "source", "url_profil", "email", "date_collecte",
]

# Tous les CSV des équipes, SAUF le fichier de sortie lui-même.
FICHIERS = [f for f in glob.glob("*.csv") if f != "contacts.csv"]


def normaliser_texte(s: str) -> str:
 """minuscule + sans accents + espaces propres, pour comparer/dédoublonner."""
 if not isinstance(s, str):
 return ""
 s = s.strip().lower()
 s = unicodedata.normalize("NFKD", s)
 s = "".join(c for c in s if not unicodedata.combining(c))
 return " ".join(s.split())


def normaliser_fonction(f: str) -> str:
 """Regroupe les variantes : 'DRH', 'directrice rh', 'head of people' -> 'rh'."""
 f = normaliser_texte(f)
 if any(k in f for k in ["rh", "ressources humaines", "people", "talent", "recrut", "hr"]):
 return "Recruteur / RH"
 return f.title() if f else ""


def charger() -> pd.DataFrame:
 frames = []
 for fichier in FICHIERS:
 try:
 # sep=None + engine='python' : pandas détecte seul le séparateur
 # (',' ou ';'), donc on tolère les CSV des équipes quel que soit
 # leur format. encoding utf-8-sig : gère le BOM éventuel.
 df = pd.read_csv(
 fichier, dtype=str, sep=None, engine="python",
 encoding="utf-8-sig",
 ).fillna("")
 except Exception as e:
 print(f" ! {fichier} illisible ({e}), ignoré")
 continue
 # On garde uniquement les colonnes du schéma (ajoute les manquantes vides).
 for col in COLONNES:
 if col not in df.columns:
 df[col] = ""
 df = df[COLONNES]
 df["_fichier"] = fichier
 frames.append(df)
 print(f" + {fichier:<28} {len(df):>5} lignes")
 if not frames:
 raise SystemExit("Aucun CSV trouvé. Les équipes ont-elles déposé leurs fichiers ?")
 return pd.concat(frames, ignore_index=True)


def nettoyer(df: pd.DataFrame) -> pd.DataFrame:
 brut = len(df)

 # 0. On purge les retours à la ligne / tabulations dans TOUS les champs :
 # c'est ce qui casse le plus souvent un CSV scrapé.
 for col in COLONNES:
 df[col] = (
 df[col].astype(str)
 .str.replace(r"[\r\n\t]+", " ", regex=True)
 .str.replace(r"\s+", " ", regex=True)
 .str.strip()
 )

 # 1. Normalisation des champs métier
 df["fonction"] = df["fonction"].map(normaliser_fonction)
 for col in ["prenom", "nom", "entreprise", "ville"]:
 df[col] = df[col].str.strip()

 # 2. On vire les lignes vraiment vides (ni entreprise, ni nom, ni email)
 vide = (df["entreprise"] == "") & (df["nom"] == "") & (df["email"] == "")
 df = df[~vide]
 print(f"\n - {vide.sum()} lignes vides supprimées")

 # 3. Clés de dédoublonnage normalisées
 df["_k_email"] = df["email"].map(normaliser_texte)
 df["_k_noment"] = df["nom"].map(normaliser_texte) + "|" + df["entreprise"].map(normaliser_texte)

 # 4. Dédoublonnage : d'abord par email (le plus fiable), puis par nom+entreprise
 avant = len(df)
 # email en doublon (hors vides)
 masque_email = df["_k_email"] != ""
 df = pd.concat([
 df[masque_email].drop_duplicates(subset="_k_email"),
 df[~masque_email],
 ])
 df = df.drop_duplicates(subset="_k_noment")
 print(f" - {avant - len(df)} doublons inter-sources supprimés")

 df = df.drop(columns=["_k_email", "_k_noment", "_fichier"])
 print(f"\n {brut} brut -> {len(df)} propre")
 return df


def bilan(df: pd.DataFrame):
 print("\n" + "=" * 50)
 print(f" CONTACTS UNIQUES : {len(df)}")
 print("=" * 50)
 print("\n Par source :")
 for src, n in df["source"].value_counts().items():
 print(f" {src:<20} {n}")
 print(f"\n Avec email : {(df['email'] != '').sum()}")
 print(f" Avec nom contact: {(df['nom'] != '').sum()}")

 if len(df) >= 5000:
 print(f"\n >>> OBJECTIF ATTEINT : {len(df)} >= 5000")
 else:
 manque = 5000 - len(df)
 print(f"\n >>> Il manque {manque}. Quelle source peut en sortir plus ?")


if __name__ == "__main__":
 print("Fusion des sources...\n")
 df = charger()
 df = nettoyer(df)
 # Bon CSV pour Excel français : BOM (utf-8-sig) + séparateur ';'.
 df.to_csv("contacts.csv", index=False, sep=";", encoding="utf-8-sig")
 bilan(df)
 print("\n Fichier final : contacts.csv")
