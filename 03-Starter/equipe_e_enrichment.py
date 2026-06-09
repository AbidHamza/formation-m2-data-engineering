"""
Équipe E — Enrichment API (Hunter.io / Dropcontact)
====================================================

Objectif SOCLE : à partir des noms d'entreprise (des autres équipes),
récupérer les emails des recruteurs/DRH via Hunter.io (gratuit).
Objectif BONUS : Dropcontact (français, RGPD), remplir les champs manquants.

Stratégie : les autres équipes collectent le NOM D'ENTREPRISE,
vous enrichissez avec l'EMAIL du recruteur.

Dépendances :
    pip install requests pandas python-dotenv
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")  # Créer un compte https://hunter.io
OUTPUT_FILE = "enrichment_contacts.csv"

# Lire les contacts des autres équipes (optionnel, pour fusion intra-atelier)
INPUT_FILES = [
    "linkedin_contacts.csv",
    "jobboards_contacts.csv",
    "wttj_contacts.csv",
    "francetravail_contacts.csv",
]


def enrich_with_hunter(company_name: str, domain: str = None) -> dict:
    """
    Utilise Hunter.io pour trouver les emails des recruteurs d'une entreprise.
    Tier gratuit : 100 requêtes/mois (assez pour une démo).

    Args:
        company_name: nom de l'entreprise (ex: "Google", "Meta")
        domain: domaine (ex: "google.com") - optionnel, Hunter le trouve

    Returns:
        dict avec emails trouvés
    """
    url = "https://api.hunter.io/v2/domain-search"

    if not domain:
        # Chercher le domaine à partir du nom d'entreprise
        domain_url = "https://api.hunter.io/v2/domain-search"
        params = {"domain": company_name.lower().replace(" ", ""), "limit": 5}
        # TODO : implémenter la recherche de domaine

        # Pour l'instant, fallback : générer un domaine générique
        domain = company_name.lower().replace(" ", "") + ".com"

    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        emails = []
        for email_data in data.get("data", {}).get("emails", [])[:5]:
            emails.append({
                "email": email_data.get("value"),
                "fonction": email_data.get("position", "").lower(),
                "type": email_data.get("type"),  # personal, generic, etc.
            })

        return {"domain": domain, "emails": emails}

    except Exception as e:
        print(f"    Erreur Hunter pour {company_name}: {e}")
        return {"domain": None, "emails": []}


def enrich_contacts():
    """
    Stratégie : enrichir les contacts collectés par les autres équipes.
    """
    print("\n📍 Enrichment (Hunter.io)...")

    # TODO SOCLE : charger les CSV des autres équipes et enrichir
    # Pour le démo, créer une liste manuelle de noms d'entreprises à enrichir

    company_list = [
        "Google France",
        "Meta",
        "Amazon",
        "Microsoft",
        "Salesforce",
        # Ajouter des entreprises de la liste finale
    ]

    all_contacts = []

    for idx, company in enumerate(company_list):
        print(f"  {idx+1}. Enrichissement {company}...")

        enriched = enrich_with_hunter(company)

        if enriched["emails"]:
            # Pour chaque email trouvé, créer un contact
            for email_data in enriched["emails"]:
                # Estimer la fonction du recruteur
                is_recruiter = any(
                    kw in email_data["fonction"].lower()
                    for kw in ["recruiter", "hr", "talent", "rh", "recrutement"]
                )

                if is_recruiter or email_data["type"] == "generic":
                    contact = {
                        "prenom": "",
                        "nom": "",
                        "fonction": email_data.get("fonction", "Recruteur"),
                        "entreprise": company,
                        "secteur": "Data/Tech",
                        "ville": "Île-de-France",
                        "source": "Hunter.io Enrichment",
                        "url_profil": f"https://hunter.io/verify/{email_data['email']}",
                        "email": email_data["email"],
                        "date_collecte": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    }
                    all_contacts.append(contact)

        time.sleep(1)  # rate limit Hunter

    return all_contacts


if __name__ == "__main__":
    print("=" * 60)
    print("ÉQUIPE E — Enrichment API")
    print("=" * 60)

    # TODO BONUS : charger et fusionner les CSV des autres équipes,
    # puis enrichir les contacts manquants d'email

    contacts = enrich_contacts()

    df = pd.DataFrame(contacts)
    df = df.drop_duplicates(subset=["email"])
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✅ {len(df)} contacts enrichis sauvegardés dans {OUTPUT_FILE}")
    print(df.head())
