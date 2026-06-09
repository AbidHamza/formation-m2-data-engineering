"""
CORRIGÉ : Collecte SANS AUCUNE CLÉ (100 % scraping)
====================================================

Aucun compte, aucune clé API. On scrape directement les pages publiques des
job boards. Chaque entreprise qui recrute data = un lead recruteur.

Sources (toutes sans clé) :
 - HelloWork
 - APEC
 - Welcome to the Jungle

 Honnêteté d'ingénieur : sans API, c'est FRAGILE. Les sites changent leur
HTML et certains se protègent (Cloudflare). Les sélecteurs ci-dessous sont un
POINT DE DÉPART : l'exercice est d'ouvrir l'inspecteur (F12), trouver les
bonnes balises et ajuster. C'est précisément la compétence "scraping".

Lancement :
 pip install requests beautifulsoup4
 python collecte_sans_cle.py
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

# Un vrai User-Agent : sans ça, beaucoup de sites renvoient une erreur.
HEADERS = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
 "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
 "Accept-Language": "fr-FR,fr;q=0.9",
}


def nettoyer(v) -> str:
 """Pas de retour à la ligne dans les champs (sinon le CSV casse)."""
 if not isinstance(v, str):
 return ""
 return " ".join(v.replace("\r", " ").replace("\n", " ").split())


def ligne(fonction="", entreprise="", ville="", source="", url="", secteur=""):
 """Construit une ligne au schéma commun, déjà nettoyée."""
 d = {
 "prenom": "", "nom": "", "fonction": fonction, "entreprise": entreprise,
 "secteur": secteur, "ville": ville, "source": source,
 "url_profil": url, "email": "", "date_collecte": date.today().isoformat(),
 }
 return {k: nettoyer(v) for k, v in d.items()}


def get_soup(url, params=None):
 r = requests.get(url, params=params, headers=HEADERS, timeout=20)
 r.raise_for_status()
 return BeautifulSoup(r.text, "html.parser")


# ---------------------------------------------------------------------------
# Source 1 : HelloWork
# ---------------------------------------------------------------------------
def scraper_hellowork(nb_pages=15):
 out = []
 for p in range(1, nb_pages + 1):
 try:
 soup = get_soup(
 "https://www.hellowork.com/fr-fr/emploi/recherche.html",
 params={"k": "data engineer", "l": "Île-de-France", "p": p},
 )
 except requests.HTTPError as e:
 print(f" hellowork p{p} : {e}")
 break
 # TODO : ajuster après inspection (F12).
 cartes = soup.select("[data-id-storage-target='item']")
 if not cartes:
 break
 for c in cartes:
 titre = c.select_one("h3, .ant-typography")
 ent = c.select_one("[data-cy='companyName']")
 lieu = c.select_one("[data-cy='localisationCard']")
 a = c.select_one("a")
 out.append(ligne(
 fonction=titre.get_text(strip=True) if titre else "",
 entreprise=ent.get_text(strip=True) if ent else "",
 ville=lieu.get_text(strip=True) if lieu else "",
 source="hellowork",
 url=a.get("href", "") if a else "",
 ))
 print(f" hellowork p{p} : +{len(cartes)} (cumul {len(out)})")
 time.sleep(1.5)
 return out


# ---------------------------------------------------------------------------
# Source 2 : APEC (cadres : beaucoup de postes data)
# ---------------------------------------------------------------------------
def scraper_apec(nb_pages=15):
 out = []
 for p in range(nb_pages):
 try:
 soup = get_soup(
 "https://www.apec.fr/candidat/recherche-emploi.html/emploi",
 params={"motsCles": "data engineer", "page": p},
 )
 except requests.HTTPError as e:
 print(f" apec p{p} : {e}")
 break
 # TODO : ajuster après inspection (F12).
 cartes = soup.select("div.card-offer, .offer-card")
 if not cartes:
 break
 for c in cartes:
 titre = c.select_one("h2, .card-title")
 ent = c.select_one(".card-offer__company, .company-name")
 lieu = c.select_one(".card-offer__location, .location")
 a = c.select_one("a")
 out.append(ligne(
 fonction=titre.get_text(strip=True) if titre else "",
 entreprise=ent.get_text(strip=True) if ent else "",
 ville=lieu.get_text(strip=True) if lieu else "",
 source="apec",
 url=a.get("href", "") if a else "",
 ))
 print(f" apec p{p} : +{len(cartes)} (cumul {len(out)})")
 time.sleep(1.5)
 return out


# ---------------------------------------------------------------------------
# Source 3 : Welcome to the Jungle
# ---------------------------------------------------------------------------
def scraper_wttj(nb_pages=10):
 out = []
 for p in range(1, nb_pages + 1):
 try:
 soup = get_soup(
 "https://www.welcometothejungle.com/fr/jobs",
 params={"query": "data engineer", "aroundQuery": "Île-de-France", "page": p},
 )
 except requests.HTTPError as e:
 print(f" wttj p{p} : {e}")
 break
 # TODO : ajuster après inspection (F12).
 cartes = soup.select("[data-testid='search-results-list-item-wrapper']")
 if not cartes:
 break
 for c in cartes:
 titre = c.select_one("h4, [role='heading']")
 ent = c.select_one("span.sc-company, .company")
 a = c.select_one("a")
 out.append(ligne(
 fonction=titre.get_text(strip=True) if titre else "",
 entreprise=ent.get_text(strip=True) if ent else "",
 source="wttj",
 url=a.get("href", "") if a else "",
 ))
 print(f" wttj p{p} : +{len(cartes)} (cumul {len(out)})")
 time.sleep(1.5)
 return out


if __name__ == "__main__":
 contacts = []
 print("Scraping HelloWork..."); contacts += scraper_hellowork()
 print("Scraping APEC..."); contacts += scraper_apec()
 print("Scraping WTTJ..."); contacts += scraper_wttj()

 # Bon CSV : utf-8-sig (BOM, accents Excel) + séparateur ';'.
 with open("sans_cle.csv", "w", newline="", encoding="utf-8-sig") as f:
 w = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";",
 quoting=csv.QUOTE_MINIMAL)
 w.writeheader()
 w.writerows(contacts)
 print(f"\n>>> {len(contacts)} lignes écrites dans sans_cle.csv")
 print(" (fusionne ensuite avec fusion.py)")
