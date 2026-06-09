"""
Équipe F — Scraper les annuaires (Societe.com, Pages Jaunes)
=============================================================

Objectif SOCLE : extraire 250 entreprises tech IDF de Societe.com.
Objectif BONUS : enrichir avec les contacts (DRH/directeur) depuis les annuaires.

Dépendances :
    pip install requests beautifulsoup4 pandas lxml
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

OUTPUT_FILE = "annuaires_contacts.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def scrape_societe_com():
    """
    Societe.com : annuaire de toutes les entreprises françaises.
    Recherche par secteur / localisation, scrape les infos de contact.
    """
    print("\n📍 Societe.com...")
    contacts = []

    base_url = "https://www.societe.com/cgi-bin/search"

    for page in range(1, 3):  # 2 pages max pour démo
        try:
            params = {
                "champs": "informatique",  # Secteur "Informatique"
                "departement": "75",  # Paris
                "page": page,
            }

            resp = requests.get(
                base_url, params=params, headers=HEADERS, timeout=10
            )
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, "html.parser")

            # TODO SOCLE : inspecter la structure HTML et trouver les sélecteurs
            # pour extraire nom entreprise, localisation, contact

            # Exemple (à adapter selon la structure réelle) :
            results = soup.select(".results tr")  # À vérifier
            print(f"  Page {page}: {len(results)} entreprises")

            for row in results[:50]:  # Limiter par page
                try:
                    # TODO : extraire les colonnes
                    # company_name, address, phone, website, directeur/dri

                    cols = row.select("td")
                    if len(cols) < 3:
                        continue

                    company_name = cols[0].text.strip() if len(cols) > 0 else ""
                    address = cols[1].text.strip() if len(cols) > 1 else ""
                    phone = cols[2].text.strip() if len(cols) > 2 else ""

                    if not company_name:
                        continue

                    # Lien vers la fiche complète
                    company_link = row.select_one("a")
                    company_url = (
                        company_link.get("href") if company_link else ""
                    )

                    # TODO BONUS : cliquer sur le lien et scraper la fiche
                    # pour récupérer directeur, DRI, contacts directs

                    contact = {
                        "prenom": "",
                        "nom": company_name.split()[0],
                        "fonction": "Directeur/DRI",
                        "entreprise": company_name,
                        "secteur": "Informatique",
                        "ville": address.split(",")[-1].strip() if "," in address else "Île-de-France",
                        "source": "Societe.com",
                        "url_profil": company_url,
                        "email": "",  # Pas d'email direct sur Societe
                        "date_collecte": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    }

                    contacts.append(contact)
                    time.sleep(0.2)

                except Exception as e:
                    print(f"    Erreur entreprise: {e}")
                    continue

        except Exception as e:
            print(f"  Erreur page {page}: {e}")

    return contacts


def scrape_pages_jaunes():
    """
    Pages Jaunes : annuaire français.
    Recherche + scrape des fiches entreprise.
    """
    print("\n📍 Pages Jaunes...")
    contacts = []

    # Pages Jaunes : recherche par secteur
    base_url = "https://www.pagesjaunes.fr/search"

    try:
        params = {
            "quoi": "data engineer",
            "ou": "Île-de-France",
        }

        resp = requests.get(base_url, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "html.parser")

        # TODO SOCLE : scraper les résultats
        # Similaire à Societe.com

        # Pour cette démo, fallback simple
        results = soup.select(".result")
        print(f"  {len(results)} résultats")

        for result in results[:30]:
            try:
                name = result.select_one(".name")
                if name:
                    contact = {
                        "prenom": "",
                        "nom": name.text.strip().split()[0],
                        "fonction": "Recruteur",
                        "entreprise": name.text.strip(),
                        "secteur": "Data/Tech",
                        "ville": "Île-de-France",
                        "source": "Pages Jaunes",
                        "url_profil": "",
                        "email": "",
                        "date_collecte": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    }
                    contacts.append(contact)

                time.sleep(0.2)

            except Exception as e:
                print(f"    Erreur: {e}")

    except Exception as e:
        print(f"  Erreur Pages Jaunes: {e}")

    return contacts


if __name__ == "__main__":
    print("=" * 60)
    print("ÉQUIPE F — Annuaires (Societe.com, Pages Jaunes)")
    print("=" * 60)

    all_contacts = []
    all_contacts.extend(scrape_societe_com())
    all_contacts.extend(scrape_pages_jaunes())

    df = pd.DataFrame(all_contacts)
    df = df.drop_duplicates(subset=["entreprise"])
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✅ {len(df)} contacts sauvegardés dans {OUTPUT_FILE}")
    print(df.head())
