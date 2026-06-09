"""
Équipe D — API France Travail → Entreprises recruteuses
=========================================================

Objectif SOCLE : récupérer les offres data engineer IDF, extraire les entreprises,
puis enrichir avec un contact (via équipe E ou annuaires).
Objectif BONUS : associer directement le contact du recruteur publié dans l'offre.

Dépendances :
    pip install requests pandas python-dotenv
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time

load_dotenv()

CLIENT_ID = os.getenv("FT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FT_CLIENT_SECRET")

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

OUTPUT_FILE = "francetravail_contacts.csv"


def get_access_token() -> str:
    """Authentification OAuth2 France Travail."""
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


def search_offres_idf(token: str) -> list:
    """
    Récupère les offres data engineer en Île-de-France.
    L'API retourne aussi les infos du contact (recruteur).
    """
    print("\n📍 API France Travail...")

    headers = {"Authorization": f"Bearer {token}"}
    contacts = []

    # TODO SOCLE : complétez les paramètres
    # Indice : motsCles, departement (75, 77, 78, 91, 92, 93, 94, 95)

    for dept in ["75", "92"]:  # Commencer par 2 dept pour tester, puis étendre
        try:
            params = {
                # TODO : "motsCles": ...,
                # TODO : "departement": ...,
                "range": "0-149",
            }

            resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=10)

            if resp.status_code == 204:
                print(f"  Dept {dept}: aucune offre")
                continue

            resp.raise_for_status()
            data = resp.json()

            offres = data.get("resultats", [])
            print(f"  Dept {dept}: {len(offres)} offres")

            for offre in offres[:50]:  # Par dept
                try:
                    # TODO SOCLE : extraire les champs de contact
                    # Indice : offre.get("contact") contient nom, email, téléphone
                    # offre.get("entreprise") contient le nom de l'entreprise

                    contact_info = offre.get("contact", {})
                    entreprise_info = offre.get("entreprise", {})

                    contact = {
                        "prenom": contact_info.get("prenom", ""),
                        "nom": contact_info.get("nom", ""),
                        "fonction": "Recruteur",
                        "entreprise": entreprise_info.get("nom", ""),
                        "secteur": "Data/Tech",
                        "ville": "Île-de-France",
                        "source": "France Travail API",
                        "url_profil": offre.get("origineOffre", {}).get("urlOrigine", ""),
                        "email": contact_info.get("email", ""),
                        "date_collecte": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    }

                    contacts.append(contact)

                    time.sleep(0.1)

                except Exception as e:
                    print(f"    Erreur offre: {e}")
                    continue

        except Exception as e:
            print(f"  Erreur dept {dept}: {e}")

    return contacts


if __name__ == "__main__":
    print("=" * 60)
    print("ÉQUIPE D — France Travail API")
    print("=" * 60)

    token = get_access_token()
    contacts = search_offres_idf(token)

    df = pd.DataFrame(contacts)
    df = df.drop_duplicates(subset=["email", "entreprise"])
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✅ {len(df)} contacts sauvegardés dans {OUTPUT_FILE}")
    print(df.head())
