"""
Équipe A — Scraper LinkedIn (Playwright)
=========================================

Objectif SOCLE : extraire 50 recruteurs/DRH data engineer depuis LinkedIn.
Objectif BONUS : automatiser la pagination, ajouter des filtres (entreprise, poste).

⚠️ Avant de lancer :
  1. Créer un compte LinkedIn avec un profil normal (photo, titre, quelques postes)
  2. Lancer ce script une FOIS manuellement : il va demander de se log dans un navigateur
  3. Après login, Playwright garde la session et peut scraper sans se reconnecter

Dépendances :
    pip install playwright pandas
    playwright install chromium
"""

import pandas as pd
from playwright.sync_api import sync_playwright
import time
import json

OUTPUT_FILE = "linkedin_contacts.csv"

def login_and_scrape():
    """
    Lance un navigateur, tu te logs manuellement une fois,
    puis le script scrape les profils trouvés sur la recherche.
    """

    with sync_playwright() as p:
        # Lancer le navigateur en mode headless=False pour voir ce qu'il se passe
        browser = p.chromium.launch(headless=False, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()

        # Aller sur la recherche LinkedIn (talent search pour recruiter)
        print("Navigation vers LinkedIn Talent Search...")
        page.goto("https://www.linkedin.com/talent/search", timeout=30000)

        # TODO SOCLE : attendre le login manuel
        # Si pas connecté, LinkedIn te demande de te login → fais-le manuellement dans le navigateur
        # Le script attend avec input()
        input("👉 Connecte-toi à LinkedIn dans le navigateur, puis appuie sur ENTRÉE ici...")

        # Après login, faire une recherche
        # URL de recherche pour "recruteur" ou "DRH" en Île-de-France
        search_url = (
            "https://www.linkedin.com/search/results/people/"
            "?keywords=recruteur%20data%20engineer&origin=GLOBAL_SEARCH_HEADER"
            "&locationId=105015211"  # Code IDF
        )
        print(f"Recherche : {search_url}")
        page.goto(search_url, timeout=30000)

        # TODO SOCLE : attendre le chargement et scroller
        time.sleep(2)
        page.wait_for_selector(".search-results__list-item", timeout=10000)

        contacts = []

        # TODO BONUS : boucle sur plusieurs pages
        # (actuellement on scrape juste la première page)

        items = page.query_selector_all(".search-results__list-item")
        print(f"Trouvé {len(items)} profils sur cette page")

        for idx, item in enumerate(items[:50]):  # Limiter à 50 pour la démo
            try:
                # TODO SOCLE : extraire les champs du profil
                # Indice : utiliser item.query_selector() et .text_content()
                # Champs à chercher : nom, titre/fonction, entreprise, URL

                # Exemple (incomplet) :
                name_elem = item.query_selector(".search-result__title a")
                name = name_elem.text_content() if name_elem else ""

                subtitle_elem = item.query_selector(".search-result__snippet")
                fonction = subtitle_elem.text_content() if subtitle_elem else ""

                url_elem = item.query_selector(".search-result__title a")
                url = url_elem.get_attribute("href") if url_elem else ""

                # TODO : extraire aussi entreprise, location
                entreprise = ""
                ville = ""

                contact = {
                    "prenom": name.split()[0] if name else "",
                    "nom": " ".join(name.split()[1:]) if name else "",
                    "fonction": fonction,
                    "entreprise": entreprise,
                    "secteur": "Data/Tech",
                    "ville": ville,
                    "source": "LinkedIn",
                    "url_profil": url,
                    "email": "",  # LinkedIn ne l'expose pas sans enrichment
                    "date_collecte": pd.Timestamp.now().strftime("%Y-%m-%d"),
                }

                contacts.append(contact)
                print(f"  {idx+1}. {name}")

                # Pause pour respecter le rate limit (anti-détection)
                time.sleep(0.5)

            except Exception as e:
                print(f"  Erreur sur profil {idx}: {e}")
                continue

        browser.close()

        return contacts


if __name__ == "__main__":
    print("=" * 60)
    print("ÉQUIPE A — LinkedIn Scraper")
    print("=" * 60)

    contacts = login_and_scrape()

    df = pd.DataFrame(contacts)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✅ {len(contacts)} contacts sauvegardés dans {OUTPUT_FILE}")
    print(df.head())
