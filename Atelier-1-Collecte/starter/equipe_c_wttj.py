"""
Équipe C : Scraper Welcome to the Jungle
=========================================

Objectif SOCLE : extraire 200 contacts depuis les pages entreprises WTTJ.
Objectif BONUS : extraire aussi les infos "équipe" avec les noms des membres.

WTTJ est très bien structuré (HTML + JSON dans la page), c'est le plus facile à scraper.

Dépendances :
 pip install requests beautifulsoup4 pandas lxml
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import re
import time

OUTPUT_FILE = "wttj_contacts.csv"
HEADERS = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def scrape_wttj_companies():
 """
 Stratégie WTTJ :
 1. Trouver les offres data engineer en IDF
 2. Pour chaque offre, accéder à la page entreprise
 3. Scraper les infos entreprise et l'équipe RH/recrutement
 """
 print("\n Welcome to the Jungle...")
 contacts = []

 # WTTJ expose un endpoint de recherche en JSON
 base_url = "https://www.welcometothejungle.com/api/v1/search/jobs"
 params = {
 "query": "data engineer",
 "location_ids": ["fr_paris"], # IDF
 "per_page": 50,
 "page": 1,
 }

 try:
 # TODO SOCLE : faire la requête API WTTJ
 # Indice : réponse en JSON, contient les offres avec liens vers entreprises

 resp = requests.get(base_url, params=params, headers=HEADERS, timeout=10)
 resp.raise_for_status()
 data = resp.json()

 jobs = data.get("jobs", [])
 print(f" {len(jobs)} offres trouvées")

 # Pour chaque offre, récupérer l'entreprise
 for job in jobs[:30]:
 try:
 company_id = job.get("company", {}).get("id", "")
 company_name = job.get("company", {}).get("name", "")

 if not company_id:
 continue

 # Scraper la page entreprise pour récupérer l'équipe
 company_url = f"https://www.welcometothejungle.com/companies/{company_id}"

 comp_resp = requests.get(company_url, headers=HEADERS, timeout=10)
 comp_resp.raise_for_status()
 comp_soup = BeautifulSoup(comp_resp.content, "html.parser")

 # TODO : extraire les membres de l'équipe RH/recrutement
 # WTTJ affiche une section "Équipe", chercher les noms/titres

 # Fallback : au minimum, avoir le nom de l'entreprise et un générique
 contact = {
 "prenom": "",
 "nom": company_name.split()[0] if company_name else "",
 "fonction": "Recruteur",
 "entreprise": company_name,
 "secteur": "Data/Tech",
 "ville": "Île-de-France",
 "source": "WTTJ",
 "url_profil": company_url,
 "email": "",
 "date_collecte": pd.Timestamp.now().strftime("%Y-%m-%d"),
 }
 contacts.append(contact)

 time.sleep(0.3) # rate limit

 except Exception as e:
 print(f" Erreur entreprise: {e}")
 continue

 except Exception as e:
 print(f" Erreur requête: {e}")

 return contacts


def scrape_wttj_team_pages():
 """
 Alternative BONUS : scraper directement les pages "équipe" des entreprises.
 Permet d'extraire les vrais noms des recruteurs/DRH.
 """
 print("\n Bonus: extraction des noms d'équipe...")
 # TODO BONUS : implémenter l'extraction des noms depuis les pages équipe
 return []


if __name__ == "__main__":
 print("=" * 60)
 print("ÉQUIPE C : Welcome to the Jungle Scraper")
 print("=" * 60)

 all_contacts = []
 all_contacts.extend(scrape_wttj_companies())
 all_contacts.extend(scrape_wttj_team_pages())

 df = pd.DataFrame(all_contacts)
 df = df.drop_duplicates(subset=["entreprise"])
 df.to_csv(OUTPUT_FILE, index=False)

 print(f"\n {len(df)} contacts sauvegardés dans {OUTPUT_FILE}")
 print(df.head())
