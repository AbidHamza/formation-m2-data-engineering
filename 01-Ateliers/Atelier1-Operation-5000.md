# Atelier 1 — Opération 5000

> Format : storytelling + atelier pratique collaboratif. Durée 3h30. Niveau hétérogène.
> Livrable : **un fichier `contacts.csv` de 5000 recruteurs/DRH du secteur data en Île-de-France**, collecté par toute la classe, multi-sources, fusionné et nettoyé.

---

## 🎬 Le pitch (à lire/raconter en intro, 10 min)

> *« Dans quelques mois, vous cherchez un poste de Data Engineer. Vous savez comment ça se passe ?*
>
> *Vous postulez à 5 offres par jour. Sur LinkedIn, sur Indeed. Vous envoyez le même CV. Et vous attendez. Comme les 300 autres candidats sur la même offre. La plupart n'auront jamais de réponse.*
>
> *Sauf vous. Parce que vous, vous êtes data engineers. Pendant que les autres postulent à la main, vous, vous allez construire la machine qui trouve les 5000 recruteurs data d'Île-de-France, qui adapte votre CV à chaque offre, et qui vous met en relation directe avec la bonne personne. »*
>
> *« Aujourd'hui, étape 1 : on récupère les 5000 recruteurs. Vos 5000 recruteurs. »*

L'idée : ce n'est pas un exercice abstrait, c'est **leur propre recherche d'emploi**. Le fichier de 5000 contacts, c'est *leur* arme pour décrocher un poste dans quelques mois. Chaque source est un terrain de chasse. Le CSV final, ils vont vraiment s'en servir.

Pourquoi ça marche : l'enjeu est personnel et concret. Ils ne bossent pas pour une note, ils bossent pour leur futur job. Et l'objectif chiffré (5000) n'est atteignable qu'en s'organisant à plusieurs, ce qui force la collaboration (cœur du métier).

---

## 🎯 La règle du jeu

- **Objectif collectif** : 5000 lignes dans le CSV final. Non négociable, c'est la mission.
- **Le calcul qui les rassure** : 5000 ÷ 20 = **250 contacts par personne**. C'est faisable. Personne ne porte tout.
- **Multi-sources imposé** : interdit de tout prendre sur LinkedIn. Chaque équipe a **sa source**. La diversité des sources, c'est ce qui rend la base solide et c'est ce qui les protège (pas 20 bots sur la même IP LinkedIn).
- **Format unique** : tout le monde produit le **même schéma CSV**, sinon la fusion est impossible. C'est la première leçon data eng : *on se met d'accord sur le schéma avant de collecter.*

### Le schéma CSV (à imposer dès le début)

```
prenom, nom, fonction, entreprise, secteur, ville, source, url_profil, email, date_collecte
```

Règle : si une colonne est inconnue, on laisse vide, **on ne décale jamais**. Un CSV mal aligné = la fusion casse.

---

## 🗺️ Les terrains de chasse (répartition des équipes)

5-6 équipes, chacune sa source. Toutes alimentent le **même** CSV.

| Équipe | Source | Technique enseignée | Volume réaliste |
|--------|--------|---------------------|-----------------|
| **A — LinkedIn** | Recherche LinkedIn (leur compte) | Playwright, login manuel, anti-détection, **petit volume** | ~50/pers |
| **B — Job boards** | HelloWork, APEC, Indeed | Scraping HTML, pagination, BeautifulSoup | ~250/pers |
| **C — Welcome to the Jungle** | Pages entreprises + équipes | Scraping de pages structurées | ~200/pers |
| **D — France Travail** | API offres → entreprises qui recrutent data | API REST, OAuth2 (le starter Python) | ~300/pers |
| **E — Enrichment** | Hunter.io / Dropcontact (tiers gratuit) | API d'enrichment : nom+boîte → email pro | ~200/pers |
| **F — Annuaires** | Societe.com, Pages Jaunes | Scraping d'annuaires | ~250/pers |

> Le formateur ajuste selon la taille de classe. L'important : **plusieurs sources en parallèle**.

Mélanger les niveaux dans chaque équipe : un confirmé tient la technique, un débutant remplit le CSV et nettoie. Tout le monde produit.

---

## ⏱️ Le déroulé (3h30)

| Temps | Phase | Ce qui se passe |
|-------|-------|-----------------|
| 0:00 – 0:10 | **Le pitch** | Tu racontes la mission. Tu écris « 5000 » au tableau. |
| 0:10 – 0:25 | **Le schéma** | On fige ensemble le format CSV. Tu expliques pourquoi le schéma d'abord. |
| 0:25 – 0:40 | **Affectation** | Chaque équipe choisit/reçoit sa source. Comptes et clés à créer. |
| 0:40 – 1:10 | **Setup technique** | Chaque équipe installe son outil (Playwright, requests, BeautifulSoup, clé API). Le formateur tourne. |
| 1:10 – 2:15 | **La chasse** | Collecte. Compteur live au tableau : chaque équipe annonce son total. La barre monte vers 5000. |
| 2:15 – 2:30 | **Pause** | — |
| 2:30 – 3:10 | **La fusion** | LE moment data eng : on agrège les CSV de toutes les équipes, on **dédoublonne**, on **normalise**. |
| 3:10 – 3:30 | **Le débrief** | On ouvre le `contacts.csv` final. 5000 lignes ? Combien de doublons retirés ? Quelle source a été la plus rentable ? |

L'astuce du **compteur live** au tableau (un chiffre par équipe qui monte) : ça transforme la séance en course collective. Ils s'encouragent, ça vit.

---

## 🔧 Le vrai apprentissage data engineering : la fusion

C'est là que tu places le contenu sérieux. Collecter, c'est l'amorce. **Fusionner proprement, c'est le métier.**

Les problèmes qu'ils vont rencontrer (et que tu veux qu'ils rencontrent) :
- **Doublons inter-sources** : le même recruteur trouvé sur LinkedIn ET sur HelloWork. Comment les détecter ? (nom + entreprise, ou email).
- **Formats incohérents** : « DRH » vs « Directrice des Ressources Humaines » vs « Head of People ». Normalisation.
- **Casse et accents** : « dupont » vs « DUPONT » vs « Dupont ». Standardiser.
- **Lignes pourries** : champs vides, colonnes décalées. Nettoyage.

Le livrable final n'est pas « 5000 lignes brutes », c'est **5000 lignes propres et dédoublonnées**. Différence entre un junior et un data engineer.

---

## ✅ Critères de réussite

- **Socle** (toute la classe) : un `contacts.csv` fusionné de ~5000 lignes au bon schéma, dédoublonné.
- **Bonus** (équipes rapides) :
  - colonne `email` remplie via enrichment sur un max de lignes,
  - script de fusion **automatisé** (et pas un copier-coller manuel des CSV),
  - statistiques : nb par source, taux de doublons, taux d'emails trouvés.

---

## 🔌 Ce dont chaque équipe a besoin (à préparer avant)

- **Toutes** : Python 3.11+, `pip install requests beautifulsoup4 pandas playwright`
- **Équipe A** : un compte LinkedIn par personne (profil correct)
- **Équipe D** : clés API France Travail (compte sur francetravail.io)
- **Équipe E** : clé Hunter.io ou Dropcontact (tier gratuit)

---

## 🪝 Accroche pour la suite

À la fin, tu lâches : *« Bravo, vous avez les 5000 contacts. Mais un fichier CSV, ça dort. La semaine prochaine, on construit la machine qui transforme ces contacts en candidatures envoyées automatiquement. »*

→ enchaîne sur l'atelier 2 (stockage en base) puis le reste de la chaîne.
