"""
CORRIGÉ : Scraping d'un job board (BeautifulSoup)
==================================================

But pédagogique : scraper du HTML classique (pagination, parsing, requests).
Exemple sur un job board. Les entreprises qui recrutent data = des leads
recruteurs. Plus simple et plus stable que LinkedIn.

IMPORTANT : les sites changent leur HTML. Les sélecteurs ci-dessous sont un
POINT DE DÉPART. L'exercice consiste justement à ouvrir l'inspecteur (F12),
repérer les bonnes balises et ajuster. C'est le coeur du métier de scraping.

Lancement :
 pip install requests beautifulsoup4
 python collecte_jobboard.py
"""

import csv
import time
from datetime import date

import requests
from bs4 import BeautifulSoup

COLONNES = [
 "prenom", "nom", "fonction", "entreprise",
 "secteur", "ville", "source", "url_profil", "email", "date_collecte",
]

# En-tête réaliste : sans User-Agent, beaucoup de sites renvoient une erreur.
HEADERS = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
 "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

# URL de recherche du job board (data + Île-de-France). À adapter au site choisi.
BASE_URL = "https://www.hellowork.com/fr-fr/emploi/recherche.html"
PARAMS_BASE = {"k": "data engineer", "l": "Île-de-France"}
NB_PAGES = 10


def scraper_page(page_num: int) -> list:
 params = {**PARAMS_BASE, "p": page_num}
 r = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
 r.raise_for_status()
 soup = BeautifulSoup(r.text, "html.parser")

 resultats = []
 # TODO ATELIER : ajuster ce sélecteur après inspection (F12) de la page.
 cartes = soup.select("[data-id-storage-target='item']")

 for carte in cartes:
 titre_el = carte.select_one("h3, .ant-typography")
 entreprise_el = carte.select_one("[data-cy='companyName'], .tw-company")
 lieu_el = carte.select_one("[data-cy='localisationCard'], .tw-location")
 lien_el = carte.select_one("a")

 resultats.append({
 "prenom": "",
 "nom": "",
 "fonction": titre_el.get_text(strip=True) if titre_el else "",
 "entreprise": entreprise_el.get_text(strip=True) if entreprise_el else "",
 "secteur": "",
 "ville": lieu_el.get_text(strip=True) if lieu_el else "",
 "source": "hellowork",
 "url_profil": lien_el.get("href", "") if lien_el else "",
 "email": "",
 "date_collecte": date.today().isoformat(),
 })
 return resultats


def collecter() -> list:
 tout = []
 for p in range(1, NB_PAGES + 1):
 try:
 lignes = scraper_page(p)
 except requests.HTTPError as e:
 print(f" page {p} : erreur {e}")
 break
 if not lignes:
 print(f" page {p} : vide, on arrête")
 break
 tout.extend(lignes)
 print(f" page {p} : +{len(lignes)} (cumul {len(tout)})")
 time.sleep(1.5) # on ne martèle pas le serveur
 return tout


def nettoyer_champ(v) -> str:
 """Pas de retour à la ligne dans les champs (sinon le CSV casse)."""
 if not isinstance(v, str):
 return ""
 return " ".join(v.replace("\r", " ").replace("\n", " ").split())


if __name__ == "__main__":
 contacts = collecter()
 contacts = [{k: nettoyer_champ(v) for k, v in c.items()} for c in contacts]
 # utf-8-sig + ';' = bon CSV pour Excel français
 with open("hellowork.csv", "w", newline="", encoding="utf-8-sig") as f:
 w = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";",
 quoting=csv.QUOTE_MINIMAL)
 w.writeheader()
 w.writerows(contacts)
 print(f">>> {len(contacts)} lignes écrites dans hellowork.csv")
