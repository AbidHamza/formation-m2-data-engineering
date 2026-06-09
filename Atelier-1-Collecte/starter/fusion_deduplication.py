"""
SCRIPT DE FUSION : À LANCER À 2H30
==================================

Fusionne les 6 CSV des équipes en un seul `contacts.csv` propre et dédoublonné.
C'EST LE MOMENT CLEF DATA ENGINEERING : montrer qu'un junior collecte du sale,
un data engineer le transforme en or.

Usage :
 python fusion_deduplication.py

Output : contacts.csv (5000 lignes, déduplication, normalisation)
"""

import pandas as pd
import os
import re
import glob

INPUT_DIR = "." # Répertoire courant
OUTPUT_FILE = "contacts.csv"

# Les 6 fichiers CSV des équipes
EQUIPE_FILES = [
 "linkedin_contacts.csv",
 "jobboards_contacts.csv",
 "wttj_contacts.csv",
 "francetravail_contacts.csv",
 "enrichment_contacts.csv",
 "annuaires_contacts.csv",
]


def normaliser_nom(nom: str) -> str:
 """Normalise un nom : minuscules, accents retirés, espaces"""
 if not nom or not isinstance(nom, str):
 return ""
 nom = nom.lower().strip()
 # TODO BONUS : retirer les accents (unidecode)
 return nom


def normaliser_fonction(fonction: str) -> str:
 """Normalise les titres de fonction : DRH = Directrice RH = HR Director"""
 if not fonction or not isinstance(fonction, str):
 return ""

 fonction = fonction.lower().strip()

 # Mapping des variantes
 mappings = {
 r"d\.?r\.?h|directeur.*ressources|head of people|head of hr": "DRH",
 r"recrut|talent|acquisition": "Recruteur",
 r"responsable.*recrutement": "Recruteur",
 r"directeur": "Directeur",
 r"manager": "Manager",
 }

 for pattern, normalized in mappings.items():
 if re.search(pattern, fonction):
 return normalized

 return fonction.title() if fonction else ""


def deduplicateur_email(df: pd.DataFrame) -> pd.DataFrame:
 """
 Déduplique par EMAIL : 1 email = 1 contact.
 Conserve la ligne avec le plus de champs remplis.
 """
 print("\n Dédoublonnage par EMAIL...")

 # Supprimer les lignes sans email
 df_with_email = df[df["email"].notna() & (df["email"] != "")]

 # Garder le premier de chaque email unique
 before = len(df_with_email)
 df_dedup = df_with_email.drop_duplicates(subset=["email"], keep="first")
 after = len(df_dedup)

 removed = before - after
 print(f" {removed} doublons sur EMAIL supprimés ({before} → {after})")

 return df_dedup


def deduplicateur_nom_entreprise(df: pd.DataFrame) -> pd.DataFrame:
 """
 Déduplique par NOM + ENTREPRISE (pour les contacts sans email).
 """
 print("\n Dédoublonnage par NOM + ENTREPRISE...")

 before = len(df)

 # Normaliser pour la comparaison
 df["_nom_norm"] = df["nom"].apply(normaliser_nom)
 df["_ent_norm"] = df["entreprise"].apply(normaliser_nom)

 # Supprimer les doublons basiques
 df = df.drop_duplicates(subset=["_nom_norm", "_ent_norm"], keep="first")

 # Nettoyer les colonnes temporaires
 df = df.drop(columns=["_nom_norm", "_ent_norm"])

 after = len(df)
 removed = before - after
 print(f" {removed} doublons supprimés ({before} → {after})")

 return df


def normaliser_dataframe(df: pd.DataFrame) -> pd.DataFrame:
 """
 Normalise les données : casse, accents, formats incohérents.
 """
 print("\n Normalisation...")

 # Assurer que toutes les colonnes attendues existent
 colonnes_attendues = [
 "prenom",
 "nom",
 "fonction",
 "entreprise",
 "secteur",
 "ville",
 "source",
 "url_profil",
 "email",
 "date_collecte",
 ]

 for col in colonnes_attendues:
 if col not in df.columns:
 df[col] = ""

 # Garder seulement les colonnes attendues (dans l'ordre)
 df = df[colonnes_attendues]

 # Normaliser chaque colonne
 df["nom"] = df["nom"].str.title()
 df["prenom"] = df["prenom"].str.title()
 df["fonction"] = df["fonction"].apply(normaliser_fonction)
 df["entreprise"] = df["entreprise"].str.title()
 df["secteur"] = df["secteur"].str.title()
 df["ville"] = df["ville"].str.title()
 df["email"] = df["email"].str.lower()

 # Supprimer les espaces inutiles
 df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

 print(f" Colonnes alignées")
 print(f" Casse normalisée")
 print(f" Espaces nettoyés")

 return df


def charger_tous_les_csv() -> pd.DataFrame:
 """Charge tous les CSV des 6 équipes."""
 print(" Chargement des CSV...")

 dfs = []
 for file in EQUIPE_FILES:
 if os.path.exists(file):
 try:
 df = pd.read_csv(file)
 dfs.append(df)
 print(f" {file}: {len(df)} lignes")
 except Exception as e:
 print(f" {file}: erreur {e}")
 else:
 print(f" {file}: fichier non trouvé")

 if not dfs:
 print(" Aucun CSV trouvé!")
 return pd.DataFrame()

 # Fusionner tous les dataframes
 df_fusionné = pd.concat(dfs, ignore_index=True)
 print(f"\n Total brut : {len(df_fusionné)} lignes")

 return df_fusionné


def main():
 print("=" * 70)
 print("FUSION & DÉDUPLICATION : Opération 5000")
 print("=" * 70)

 # Charge tous les CSV
 df = charger_tous_les_csv()

 if df.empty:
 print("Aucune donnée à traiter.")
 return

 # Normaliser les données
 df = normaliser_dataframe(df)

 # Déduplique par email (plus fiable)
 df_dedup_email = deduplicateur_email(df)

 # Déduplique par nom + entreprise (pour les sans-email)
 df_without_email = df[df["email"].isna() | (df["email"] == "")]
 df_dedup_name = deduplicateur_nom_entreprise(df_without_email)

 # Fusionner
 df_final = pd.concat([df_dedup_email, df_dedup_name], ignore_index=True)

 # Trier par source + entreprise (pour visualiser facilement)
 df_final = df_final.sort_values(by=["source", "entreprise"]).reset_index(
 drop=True
 )

 # Sauvegarder
 df_final.to_csv(OUTPUT_FILE, index=False)

 print("\n" + "=" * 70)
 print(" RÉSULTATS FINAUX")
 print("=" * 70)
 print(f" Total final : {len(df_final)} contacts")
 print(f" Avec email : {(df_final['email'] != '').sum()}")
 print(f" Sauvé dans : {OUTPUT_FILE}")

 # Stats par source
 print("\n Répartition par source :")
 source_counts = df_final["source"].value_counts()
 for source, count in source_counts.items():
 print(f" {source}: {count}")

 # Top 10 entreprises
 print("\n Top 10 entreprises les plus représentées :")
 top_companies = df_final["entreprise"].value_counts().head(10)
 for company, count in top_companies.items():
 print(f" {company}: {count}")

 # Aperçu des premières lignes
 print("\n Aperçu des 5 premières lignes :")
 print(df_final.head().to_string(index=False))

 return df_final


if __name__ == "__main__":
 df_final = main()
