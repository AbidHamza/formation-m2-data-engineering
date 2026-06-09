"""
Atelier 1 : Ingestion des offres via l'API France Travail
==========================================================

Objectif SOCLE : récupérer les offres "Data Engineer" en Île-de-France.
Objectif BONUS : ajouter des filtres (contrat, télétravail) + pagination complète.

Le squelette fonctionne déjà : remplissez les TODO pour le compléter.
Doc API : https://francetravail.io/data/api/offres-emploi

Prérequis :
 pip install requests python-dotenv
 Créer un fichier .env à partir de .env.example
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Identifiants obtenus sur https://francetravail.io (Application > API Offres d'emploi v2)
CLIENT_ID = os.getenv("FT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FT_CLIENT_SECRET")

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

# Départements d'Île-de-France
IDF_DEPARTEMENTS = ["75", "77", "78", "91", "92", "93", "94", "95"]


def get_access_token() -> str:
 """
 Authentification OAuth2 (client credentials).
 Retourne un token d'accès valable ~25 min.
 """
 response = requests.post(
 TOKEN_URL,
 data={
 "grant_type": "client_credentials",
 "client_id": CLIENT_ID,
 "client_secret": CLIENT_SECRET,
 "scope": "api_offresdemploiv2 o2dsoffre",
 },
 headers={"Content-Type": "application/x-www-form-urlencoded"},
 timeout=10,
 )
 response.raise_for_status()
 return response.json()["access_token"]


def search_offres(token: str, mots_cles: str, departement: str, start: int = 0) -> dict:
 """
 Recherche d'offres pour un département donné.
 L'API renvoie 150 résultats max par page (paramètre 'range').

 TODO SOCLE : compléter les 'params' pour filtrer par mots-clés et département.
 Indice : paramètres 'motsCles' et 'departement'.
 """
 headers = {"Authorization": f"Bearer {token}"}
 params = {
 # TODO : "motsCles": ...,
 # TODO : "departement": ...,
 "range": f"{start}-{start + 149}", # pagination : 150 par page
 }

 response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=10)

 # 204 = aucun résultat ; 206 = résultats partiels (pagination)
 if response.status_code == 204:
 return {"resultats": []}
 response.raise_for_status()
 return response.json()


def extraire_infos(offre: dict) -> dict:
 """
 Garde uniquement les champs utiles (principe de minimisation RGPD).

 TODO SOCLE : compléter avec intitule, entreprise, lieu, type de contrat, url.
 Inspectez la structure d'une offre avec print(offre) au premier run.
 """
 return {
 "id": offre.get("id"),
 "intitule": offre.get("intitule"),
 # TODO : "entreprise": offre.get("entreprise", {}).get("nom"),
 # TODO : "lieu": ...,
 # TODO : "type_contrat": ...,
 # TODO : "url": ...,
 }


def ingest(mots_cles: str = "data engineer") -> list:
 """
 Pipeline d'ingestion : boucle sur les départements IDF, agrège les offres.
 Gère le rate limit avec une petite pause entre les appels.
 """
 token = get_access_token()
 toutes_offres = []

 for dep in IDF_DEPARTEMENTS:
 print(f"Recherche dans le département {dep}...")
 try:
 data = search_offres(token, mots_cles, dep)
 offres = [extraire_infos(o) for o in data.get("resultats", [])]
 toutes_offres.extend(offres)
 print(f" -> {len(offres)} offres")
 except requests.HTTPError as e:
 # Gestion d'erreur : on log et on continue, on ne crashe pas tout le run
 print(f" Erreur sur le département {dep} : {e}")

 time.sleep(0.5) # respect du rate limit

 # TODO BONUS : si la réponse est en 206 (résultats partiels),
 # boucler sur les pages suivantes (start += 150) jusqu'à tout récupérer.

 return toutes_offres


if __name__ == "__main__":
 offres = ingest("data engineer")
 print(f"\nTotal : {len(offres)} offres Data Engineer en Île-de-France")
 for o in offres[:5]:
 print(o)

 # TODO ATELIER 2 : insérer ces offres dans Supabase (upsert sur 'id').
