"""
CORRIGÉ : Collecte France Travail (le cheval de bataille pour le volume)
=========================================================================

Ce script génère VRAIMENT du volume : il interroge l'API officielle France
Travail sur plusieurs métiers data × plusieurs départements d'Île-de-France,
pagine, dédoublonne, et écrit un CSV au schéma de l'atelier.

Pourquoi c'est lui qui fait le gros du fichier 5000 :
- API officielle = stable, pas de scraping qui casse, pas de ban.
- En croisant ~8 métiers data × 8 départements, on récupère des milliers
 d'offres, donc des milliers d'entreprises qui recrutent, beaucoup avec
 un contact recruteur.

Lancement :
 pip install requests python-dotenv
 # remplir .env avec FT_CLIENT_ID et FT_CLIENT_SECRET
 python collecte_france_travail.py
"""

import os
import csv
import time
from datetime import date

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("FT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FT_CLIENT_SECRET")

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

# On élargit le filtre "data" pour maximiser le volume.
MOTS_CLES_DATA = [
 "data engineer",
 "ingénieur data",
 "data analyst",
 "data scientist",
 "big data",
 "ingénieur big data",
 "business intelligence",
 "data architect",
]

# Île-de-France : les 8 départements.
IDF_DEPARTEMENTS = ["75", "77", "78", "91", "92", "93", "94", "95"]

# Schéma commun à toutes les sources de l'atelier.
COLONNES = [
 "prenom", "nom", "fonction", "entreprise",
 "secteur", "ville", "source", "url_profil", "email", "date_collecte",
]


def get_token() -> str:
 """OAuth2 client credentials. Token valable ~25 min."""
 r = requests.post(
 TOKEN_URL,
 data={
 "grant_type": "client_credentials",
 "client_id": CLIENT_ID,
 "client_secret": CLIENT_SECRET,
 "scope": "api_offresdemploiv2 o2dsoffre",
 },
 timeout=15,
 )
 r.raise_for_status()
 return r.json()["access_token"]


def chercher_page(token: str, mots_cles: str, departement: str, debut: int) -> tuple:
 """
 Une page de résultats (max 150). Retourne (liste_offres, total_dispo).
 L'API répond 206 quand il reste des pages, 200 quand c'est la dernière,
 204 quand il n'y a rien.
 """
 headers = {"Authorization": f"Bearer {token}"}
 params = {
 "motsCles": mots_cles,
 "departement": departement,
 "range": f"{debut}-{debut + 149}",
 }
 r = requests.get(SEARCH_URL, headers=headers, params=params, timeout=20)

 if r.status_code == 204: # aucun résultat
 return [], 0
 if r.status_code == 400: # on a dépassé la profondeur max autorisée
 return [], 0
 r.raise_for_status()

 offres = r.json().get("resultats", [])
 # En-tête Content-Range : "offres 0-149/1234" -> on récupère le total.
 total = 0
 cr = r.headers.get("Content-Range", "")
 if "/" in cr:
 total = int(cr.split("/")[-1])
 return offres, total


def nettoyer_champ(valeur) -> str:
 """
 Rend un champ propre pour le CSV : pas de retour à la ligne ni de
 tabulation (qui casseraient les lignes), espaces normalisés.
 """
 if not isinstance(valeur, str):
 return ""
 return " ".join(valeur.replace("\r", " ").replace("\n", " ").split())


def offre_vers_contact(offre: dict) -> dict:
 """
 Transforme une offre en une ligne 'contact' au schéma commun.
 Toutes les offres n'ont pas un contact nommé : dans ce cas on garde
 l'entreprise et l'URL de candidature (suffisant pour postuler).
 """
 entreprise = offre.get("entreprise", {}) or {}
 lieu = offre.get("lieuTravail", {}) or {}
 contact = offre.get("contact", {}) or {}
 origine = offre.get("origineOffre", {}) or {}

 nom_contact = contact.get("nom", "") or ""
 # France Travail met souvent "Mme MARTIN - Responsable RH" dans un seul champ.
 prenom, nom = "", nom_contact

 ligne = {
 "prenom": prenom,
 "nom": nom,
 "fonction": "Recruteur" if nom_contact else "",
 "entreprise": entreprise.get("nom", "") or "",
 "secteur": offre.get("secteurActiviteLibelle", "") or "",
 "ville": lieu.get("libelle", "") or "",
 "source": "france_travail",
 "url_profil": origine.get("urlOrigine", "") or "",
 "email": contact.get("courriel", "") or "",
 "date_collecte": date.today().isoformat(),
 }
 return {k: nettoyer_champ(v) for k, v in ligne.items()}


def collecter() -> list:
 token = get_token()
 contacts = {} # clé = id offre, pour dédoublonner à la source
 appels = 0

 for mots in MOTS_CLES_DATA:
 for dep in IDF_DEPARTEMENTS:
 debut = 0
 while True:
 try:
 offres, total = chercher_page(token, mots, dep, debut)
 except requests.HTTPError as e:
 print(f" Erreur {mots}/{dep} @ {debut} : {e}")
 break

 for o in offres:
 contacts[o["id"]] = offre_vers_contact(o)

 appels += 1
 print(f" {mots:<22} dep {dep} : +{len(offres):<3} "
 f"(total dispo {total}) | cumul unique : {len(contacts)}")

 debut += 150
 # On s'arrête quand on a tout vu, ou à la profondeur max de l'API.
 if not offres or debut >= total or debut >= 1150:
 break

 time.sleep(0.4) # respect du rate limit

 return list(contacts.values())


def ecrire_csv(contacts: list, chemin: str = "france_travail.csv"):
 # utf-8-sig (BOM) -> accents corrects dans Excel Windows
 # delimiter ';' -> séparateur attendu par Excel français
 # QUOTE_MINIMAL -> les champs contenant ';' ou '"' sont protégés
 with open(chemin, "w", newline="", encoding="utf-8-sig") as f:
 writer = csv.DictWriter(
 f, fieldnames=COLONNES, delimiter=";", quoting=csv.QUOTE_MINIMAL
 )
 writer.writeheader()
 writer.writerows(contacts)
 print(f"\n>>> {len(contacts)} contacts écrits dans {chemin}")


if __name__ == "__main__":
 print("Collecte France Travail en cours...\n")
 contacts = collecter()
 ecrire_csv(contacts)

 avec_contact = sum(1 for c in contacts if c["nom"])
 avec_email = sum(1 for c in contacts if c["email"])
 print(f" dont {avec_contact} avec un nom de contact, {avec_email} avec un email")
