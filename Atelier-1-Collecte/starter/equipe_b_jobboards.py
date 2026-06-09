"""
Équipe B : Scraper les job boards (HelloWork, APEC, Indeed)
============================================================

Objectif SOCLE : extraire 250 contacts depuis 1-2 job boards (nom, entreprise, lien).
Objectif BONUS : scraper 3 boards différents en parallèle.

Stratégie : récupérer les offres data engineer IDF, puis extraire le contact du recruteur.

Dépendances :
 pip install requests beautifulsoup4 pandas lxml
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import re

OUTPUT_FILE = "jobboards_contacts.csv"
HEADERS = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def scrape_hellowork():
 """
 HelloWork est le plus friendly pour le scraping.
 Récupère les offres et extrait les contacts.
 """
 print("\n HelloWork...")
 contacts = []

 base_url = "https://www.hellowork.com/emplois/data-engineer?location=paris"

 for page in range(1, 3): # 2 pages = ~50 offres
 try:
 url = f"{base_url}&page={page}"
 resp = requests.get(url, headers=HEADERS, timeout=10)
 resp.raise_for_status()

 soup = BeautifulSoup(resp.content, "html.parser")

 # TODO SOCLE : inspecter la structure HTML de HelloWork
 # et trouver les sélecteurs pour les offres
 # Indice : classe contenant les offres, lien vers détail, titre, entreprise

 offers = soup.select("[data-test-id='job-card']") # À adapter selon la structure réelle
 print(f" Page {page}: {len(offers)} offres")

 for offer in offers[:25]: # Limiter par page
 try:
 # Exemple : extraire les champs
 company = offer.select_one("[data-test-id='company-name']")
 title = offer.select_one("[data-test-id='job-title']")

 if company and title:
 # TODO : cliquer sur l'offre et scraper le contact du recruteur
 # Ou utiliser des regex pour extraire un email/contact

 contact = {
 "prenom": "",
 "nom": company.text.strip().split()[0] if company else "",
 "fonction": "Recruteur",
 "entreprise": company.text.strip() if company else "",
 "secteur": "Data/Tech",
 "ville": "Île-de-France",
 "source": "HelloWork",
 "url_profil": "",
 "email": "",
 "date_collecte": pd.Timestamp.now().strftime("%Y-%m-%d"),
 }
 contacts.append(contact)

 time.sleep(0.2) # rate limit

 except Exception as e:
 print(f" Erreur offre: {e}")
 continue

 except Exception as e:
 print(f" Erreur page {page}: {e}")
 continue

 return contacts


def scrape_apec():
 """
 APEC : cadres. Accès limité au scraping mais les offres sont publiques.
 """
 print("\n APEC...")
 contacts = []

 # APEC a un endpoint JSON pour les recherches
 url = "https://www.apec.fr/api/offres" # À vérifier/adapter
 params = {
 "motsCles": "data engineer",
 "localisation": "Île-de-France",
 "nbParPage": 50,
 }

 try:
 resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
 resp.raise_for_status()
 data = resp.json()

 # TODO SOCLE : naviguer la réponse JSON
 # Extraire offres et contacts recruteurs

 offers = data.get("offres", [])
 print(f" {len(offers)} offres trouvées")

 for offer in offers[:30]:
 # TODO : extraire contact du recruteur depuis l'offre
 contact = {
 "prenom": "",
 "nom": offer.get("entreprise", "").split()[0] if offer.get("entreprise") else "",
 "fonction": "Recruteur",
 "entreprise": offer.get("entreprise", ""),
 "secteur": "Data/Tech",
 "ville": "Île-de-France",
 "source": "APEC",
 "url_profil": offer.get("urlOffre", ""),
 "email": "",
 "date_collecte": pd.Timestamp.now().strftime("%Y-%m-%d"),
 }
 contacts.append(contact)

 except Exception as e:
 print(f" Erreur APEC: {e}")

 return contacts


def scrape_indeed():
 """
 Indeed : les offres sont visibles mais le contact recruteur est caché.
 Fallback : utiliser l'enrichment API (équipe E) pour récupérer le contact.
 """
 print("\n Indeed...")
 contacts = []

 # Indeed bloque le scraping classique
 # Stratégie : récupérer seulement les noms d'entreprise, puis enrichir avec Hunter/Dropcontact

 # TODO BONUS : intégrer avec l'équipe E pour enrichir les contacts

 return contacts


if __name__ == "__main__":
 print("=" * 60)
 print("ÉQUIPE B : Job Boards Scraper")
 print("=" * 60)

 all_contacts = []
 all_contacts.extend(scrape_hellowork())
 all_contacts.extend(scrape_apec())
 all_contacts.extend(scrape_indeed())

 df = pd.DataFrame(all_contacts)
 df = df.drop_duplicates(subset=["entreprise", "fonction"]) # Dédupliquage basique
 df.to_csv(OUTPUT_FILE, index=False)

 print(f"\n {len(df)} contacts sauvegardés dans {OUTPUT_FILE}")
 print(df.head())
