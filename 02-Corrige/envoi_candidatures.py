"""
CORRIGÉ — Envoi de candidatures par email, en SEMI-AUTOMATIQUE
==============================================================

Le robot prépare tout (message personnalisé + CV adapté en pièce jointe) et crée
des BROUILLONS Gmail. C'est l'humain qui ouvre Gmail, relit, et clique "Envoyer".

Pourquoi des brouillons et pas un envoi direct en masse :
  - zéro risque de bannissement (on ne pilote pas LinkedIn, et Gmail ne flague
    pas une boite qui envoie quelques mails relus à la main),
  - zéro spam : chaque message est personnalisé et validé,
  - conforme RGPD : ciblage individuel sur une offre précise, pas d'envoi de masse.

C'est le contraire des bots LinkedIn Easy Apply (qui font bannir les comptes).
On envoie là où c'est légitime : l'email de contact d'une offre, ou un email pro.

Anti-doublon : un journal `deja_contactes.csv` empêche de recontacter deux fois
la même personne, même si on relance le script. (L'idempotence de l'atelier 2.)

Préparation (une fois) :
  pip install google-api-python-client google-auth-oauthlib
  # Console Google Cloud > activer Gmail API > créer un OAuth client "Desktop"
  # télécharger credentials.json à côté de ce script.

Lancement :
  python envoi_candidatures.py            # crée les brouillons (rien n'est envoyé)
  # puis : ouvrir Gmail, relire, envoyer à la main.

Entrée attendue — cibles.csv (séparateur ';') :
  email;prenom;nom;entreprise;fonction;offre_titre;offre_url;cv_path
"""

import base64
import csv
import os
import time
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
CIBLES = "cibles.csv"
JOURNAL = "deja_contactes.csv"
MON_PRENOM = "Prénom Étudiant"   # à personnaliser
MON_NOM = "Nom Étudiant"


def service_gmail():
    """Auth OAuth installée. Crée token.json au premier lancement."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def deja_contactes() -> set:
    """Emails déjà traités, pour ne jamais recontacter deux fois."""
    if not os.path.exists(JOURNAL):
        return set()
    with open(JOURNAL, encoding="utf-8-sig") as f:
        return {l["email"].strip().lower() for l in csv.DictReader(f, delimiter=";") if l.get("email")}


def journaliser(cible):
    nouveau = not os.path.exists(JOURNAL)
    with open(JOURNAL, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        if nouveau:
            w.writerow(["email", "entreprise", "offre_titre"])
        w.writerow([cible["email"], cible.get("entreprise", ""), cible.get("offre_titre", "")])


def rediger(cible) -> tuple[str, str]:
    """Sujet + corps personnalisés. À l'atelier 5, le corps vient du LLM."""
    prenom = cible.get("prenom", "").strip()
    salutation = f"Bonjour {prenom}," if prenom else "Bonjour,"
    poste = cible.get("offre_titre", "").strip() or "votre poste en data"
    entreprise = cible.get("entreprise", "").strip()
    chez = f" chez {entreprise}" if entreprise else ""

    sujet = f"Candidature : {poste}"
    corps = (
        f"{salutation}\n\n"
        f"Votre offre de {poste}{chez} correspond précisément à mon profil de "
        f"data engineer. J'ai adapté mon CV à vos besoins, vous le trouverez en "
        f"pièce jointe.\n\n"
        f"Je serais ravi d'en échanger lors d'un court appel cette semaine.\n\n"
        f"Bien cordialement,\n{MON_PRENOM} {MON_NOM}"
    )
    return sujet, corps


def creer_brouillon(svc, cible):
    sujet, corps = rediger(cible)
    msg = EmailMessage()
    msg["To"] = cible["email"]
    msg["Subject"] = sujet
    msg.set_content(corps)

    cv = cible.get("cv_path", "").strip()
    if cv and os.path.exists(cv):
        with open(cv, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf",
                               filename=os.path.basename(cv))
    elif cv:
        print(f"  ! CV introuvable: {cv} (brouillon créé sans pièce jointe)")

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    svc.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()


def main():
    if not os.path.exists(CIBLES):
        raise SystemExit(f"{CIBLES} manquant. Colonnes attendues : "
                         "email;prenom;nom;entreprise;fonction;offre_titre;offre_url;cv_path")

    vus = deja_contactes()
    svc = service_gmail()

    crees, ignores = 0, 0
    with open(CIBLES, encoding="utf-8-sig") as f:
        for cible in csv.DictReader(f, delimiter=";"):
            email = (cible.get("email") or "").strip().lower()
            if not email:
                continue
            if email in vus:
                ignores += 1
                continue
            creer_brouillon(svc, cible)
            journaliser(cible)
            vus.add(email)
            crees += 1
            print(f"  brouillon -> {email}  ({cible.get('entreprise', '')})")
            time.sleep(0.5)  # on reste poli avec l'API

    print(f"\n>>> {crees} brouillons créés, {ignores} ignorés (déjà contactés).")
    print(">>> Ouvre Gmail, relis chaque brouillon, et clique Envoyer. "
          "Aucun mail n'est parti sans toi.")


if __name__ == "__main__":
    main()
