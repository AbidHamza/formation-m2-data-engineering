"""
CORRIGÉ — Scraping LinkedIn (la COMPÉTENCE, à petit volume)
============================================================

But pédagogique : apprendre à scraper un site qui se défend. PAS faire du
volume ici (LinkedIn bannit au-delà de ~80 profils/jour). On vise 30-50
contacts par étudiant, sur SA recherche, depuis SON compte. Le volume des
5000 vient des autres sources (surtout l'API France Travail).

Règles qui évitent le ban :
  - login MANUEL (on ne tape jamais le mot de passe par script : c'est le
    déclencheur n°1 de blocage),
  - délais aléatoires, comportement humain,
  - petit volume, usage personnel normal.

Lancement :
    pip install playwright
    playwright install chromium
    python collecte_linkedin.py
"""

import csv
import random
import time
from datetime import date

from playwright.sync_api import sync_playwright

COLONNES = [
    "prenom", "nom", "fonction", "entreprise",
    "secteur", "ville", "source", "url_profil", "email", "date_collecte",
]

# La recherche LinkedIn ciblée (recruteurs data en IDF).
RECHERCHE = "recruteur data engineer Île-de-France"
NB_PAGES = 3                      # 3 pages ~ 30 contacts. Ne pas monter trop haut.


def pause_humaine(mini=2.0, maxi=5.0):
    """Délai aléatoire : un humain ne clique pas toutes les 200 ms."""
    time.sleep(random.uniform(mini, maxi))


def scraper():
    contacts = []
    with sync_playwright() as p:
        # headless=False : on VOIT le navigateur, c'est plus humain et c'est
        # pédagogique (les étudiants voient ce qui se passe).
        navigateur = p.chromium.launch(headless=False)
        page = navigateur.new_page()

        page.goto("https://www.linkedin.com/login")
        print(">>> Connecte-toi À LA MAIN dans la fenêtre, puis reviens ici.")
        input(">>> Appuie sur Entrée une fois connecté...")

        # Recherche "Personnes"
        page.goto(
            "https://www.linkedin.com/search/results/people/"
            f"?keywords={RECHERCHE.replace(' ', '%20')}"
        )
        pause_humaine()

        for num_page in range(1, NB_PAGES + 1):
            print(f"Page {num_page}...")
            pause_humaine(3, 6)

            # TODO ATELIER : ces sélecteurs changent régulièrement sur LinkedIn.
            # Étape d'apprentissage : ouvrir l'inspecteur (F12), trouver la
            # balise des cartes de résultats, ajuster le sélecteur ci-dessous.
            cartes = page.query_selector_all("li.reusable-search__result-container")

            for carte in cartes:
                nom_el = carte.query_selector("span[aria-hidden='true']")
                fonction_el = carte.query_selector(".entity-result__primary-subtitle")
                lien_el = carte.query_selector("a.app-aware-link")

                nom_complet = nom_el.inner_text().strip() if nom_el else ""
                parts = nom_complet.split(" ", 1)

                contacts.append({
                    "prenom": parts[0] if parts else "",
                    "nom": parts[1] if len(parts) > 1 else "",
                    "fonction": fonction_el.inner_text().strip() if fonction_el else "",
                    "entreprise": "",       # à enrichir plus tard (atelier enrichment)
                    "secteur": "",
                    "ville": "",
                    "source": "linkedin",
                    "url_profil": lien_el.get_attribute("href") if lien_el else "",
                    "email": "",
                    "date_collecte": date.today().isoformat(),
                })

            # Page suivante (scroll + clic "Suivant"), avec pause humaine.
            suivant = page.query_selector("button[aria-label='Suivant']")
            if not suivant:
                break
            suivant.click()
            pause_humaine(4, 8)

        navigateur.close()
    return contacts


def nettoyer_champ(v) -> str:
    """Pas de retour à la ligne dans les champs (sinon le CSV casse)."""
    if not isinstance(v, str):
        return ""
    return " ".join(v.replace("\r", " ").replace("\n", " ").split())


if __name__ == "__main__":
    contacts = scraper()
    contacts = [{k: nettoyer_champ(v) for k, v in c.items()} for c in contacts]
    # utf-8-sig + ';' = bon CSV pour Excel français
    with open("linkedin.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";",
                           quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(contacts)
    print(f">>> {len(contacts)} contacts LinkedIn écrits dans linkedin.csv")
