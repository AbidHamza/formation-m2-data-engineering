# Atelier 1 : collecte de contacts data en Île-de-France

On construit la première brique de la chaîne data engineering : un script de collecte qui remplit un fichier `contacts.csv` propre, au schéma commun, avec quelques milliers d'offres et de recruteurs data en Île-de-France. Tout ce qui suit dans la formation (stockage, enrichissement, automatisation) repose sur ce fichier. S'il est mal foutu, le reste casse.

## Le contexte : opération 5000

Dans quelques mois, vous cherchez un poste de data engineer. La plupart des candidats postulent à la main, envoient le même CV à 5 offres par jour et attendent. Vous, vous allez d'abord construire la base de données des entreprises qui recrutent dans la data en Île-de-France. C'est votre matière première pour la suite : une fois ce fichier en main, on automatise la mise en relation.

L'objectif chiffré, c'est plusieurs milliers de lignes. Soyons honnêtes sur d'où vient le volume : presque tout sort de l'API officielle France Travail. C'est stable, légal, et ça ne casse pas. Le scraping (LinkedIn, job boards, annuaires) est une compétence utile à pratiquer, mais c'est fragile et ça rapporte peu de lignes. On apprend les deux, on s'appuie sur la première pour le volume.

## Ce qu'on construit

Un seul fichier de sortie, `contacts.csv`, où chaque ligne est un contact ou une offre, toujours avec les mêmes colonnes. C'est la règle numéro un en data engineering : on se met d'accord sur le schéma avant de collecter, sinon la fusion des sources est impossible.

| Colonne | Contenu |
|---|---|
| `prenom` | Prénom du contact (souvent vide côté France Travail) |
| `nom` | Nom du contact ou intitulé du recruteur |
| `fonction` | Recruteur, RH, responsable recrutement... |
| `entreprise` | Nom de l'entreprise qui recrute |
| `secteur` | Secteur d'activité |
| `ville` | Ville et département, ex. `Paris (75)` |
| `source` | D'où vient la ligne : `france_travail`, `linkedin`... |
| `url_profil` | Lien vers l'offre ou le profil |
| `email` | Email pro si disponible |
| `date_collecte` | Date de collecte au format `AAAA-MM-JJ` |

Règle d'or : si une valeur est inconnue, on laisse la cellule vide. On ne décale jamais les colonnes. Un CSV mal aligné fait planter toute la fusion.

## Prérequis

- Python 3 installé (`python --version` doit répondre 3.x).
- Un compte développeur sur [francetravail.io](https://francetravail.io) avec une application déclarée donnant accès à l'API Offres d'emploi. Vous obtenez un identifiant client et une clé secrète.
- Les paquets Python : `requests`, `beautifulsoup4`, `pandas`, `python-dotenv`.

## Lancer le corrigé

Le corrigé est le moteur de référence : il fait le gros du volume via l'API France Travail, puis fusionne. Depuis la racine du dépôt :

```bash
cd Atelier-1-Collecte/corrige
pip install requests beautifulsoup4 pandas python-dotenv
```

Créez ensuite un fichier `.env` dans ce dossier `corrige/` avec vos identifiants France Travail :

```
FT_CLIENT_ID=votre_identifiant_client
FT_CLIENT_SECRET=votre_cle_secrete
```

Puis lancez la collecte, puis la fusion :

```bash
python collecte_france_travail.py
python fusion.py
```

`collecte_france_travail.py` interroge l'API sur plusieurs métiers data croisés avec les 8 départements d'Île-de-France, pagine, dédoublonne, et écrit `france_travail.csv`. `fusion.py` ramasse tous les CSV présents dans le dossier, normalise les champs, retire les doublons inter-sources et produit `contacts.csv` avec un bilan chiffré.

## Le travail élève : le dossier `starter/`

Le dossier `starter/` contient un fichier par équipe, avec des `TODO` à compléter. Chaque équipe travaille une source différente, et toutes alimentent le même schéma CSV.

| Fichier starter | Équipe | Source |
|---|---|---|
| `equipe_a_linkedin.py` | LinkedIn | Recherche LinkedIn, petit volume, anti-détection |
| `equipe_b_jobboards.py` | Job boards | HelloWork, APEC, Indeed (scraping HTML) |
| `equipe_c_wttj.py` | Welcome to the Jungle | Pages entreprises et équipes |
| `equipe_d_francetravail.py` | France Travail | API REST, OAuth2 (le gros du volume) |
| `equipe_e_enrichment.py` | Enrichment | Retrouver l'email pro à partir du nom et de l'entreprise |
| `equipe_f_annuaires.py` | Annuaires | Societe.com, Pages Jaunes |

Chaque équipe produit son propre CSV. À la fin, `fusion_deduplication.py` (ou le `fusion.py` du corrigé) assemble tous ces CSV en un seul fichier propre et dédoublonné. Le fichier `atelier1_ingestion.py` sert de point d'entrée commun.

Mélangez les niveaux dans chaque équipe : quelqu'un tient la technique, quelqu'un remplit et nettoie le CSV. L'important est que chaque ligne respecte le schéma commun.

## L'exemple fourni

`exemple/contacts.exemple.csv` montre à quoi ressemble la sortie attendue : 10 lignes France Travail, séparateur `;`, le schéma au complet. Regardez-le avant de coder. On y voit le cas réel où beaucoup de lignes n'ont pas de nom de contact (juste l'entreprise et l'URL de l'offre), et où la colonne `email` est souvent vide. C'est normal, et c'est précisément le travail des équipes enrichment et annuaires de combler ces trous.

## RGPD : le cadre à respecter

On collecte des données professionnelles publiques (entreprise, fonction, email pro publié dans une offre) dans le cadre d'un intérêt légitime de recherche d'emploi, pas de données personnelles sensibles. On ne constitue pas une liste pour du spam de masse : ce fichier sert à des candidatures ciblées. On respecte les conditions d'utilisation de chaque source, et on n'aspire pas un site qui l'interdit explicitement. L'API officielle France Travail est la voie propre, c'est pour ça qu'on s'appuie dessus en priorité. Une personne doit pouvoir demander le retrait de ses données.

## Critères de réussite

**Socle :** un fichier `contacts.csv` au schéma commun, dédoublonné, avec plusieurs milliers de lignes. La majorité du volume vient de l'API France Travail, c'est attendu.

**Bonus :**
- Croiser réellement plusieurs sources (job boards, LinkedIn, annuaires) en plus de France Travail.
- Enrichir les emails pro via l'équipe enrichment sur un maximum de lignes.
- Automatiser la fusion par script plutôt que par copier-coller, avec des statistiques en sortie : nombre de lignes par source, taux de doublons retirés, taux d'emails trouvés.
