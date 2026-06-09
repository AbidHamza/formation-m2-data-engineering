# Guide formateur — Corrigé « Opération 5000 »

> Tout ce qu'il te faut pour animer l'atelier et garantir que le fichier final atteint vraiment 5000 contacts. Lis-le une fois en entier avant la séance.

---

## 1. Ce que contient le corrigé

| Fichier | Rôle | Qui le lance |
|---------|------|--------------|
| `collecte_france_travail.py` | **Le cheval de bataille.** API officielle, sort des milliers d'offres data IDF avec entreprise + contact | Équipe France Travail (et toi, en secours) |
| `collecte_jobboard.py` | Scraping HTML (HelloWork) avec BeautifulSoup | Équipe Job boards |
| `collecte_linkedin.py` | Scraping LinkedIn (Playwright, petit volume) | Équipe LinkedIn |
| `fusion.py` | **La correction finale.** Assemble tous les CSV, dédoublonne, vérifie les 5000 | Toi, en live, à 2h30 |
| `.env` | Les clés API (jamais commité) | Chaque poste |

Chaque script de collecte produit un CSV au **même schéma**. `fusion.py` les avale tous.

---

## 2. La vérité sur les 5000 : d'où vient le volume

Sois clair là-dessus dans ta tête, parce que c'est la question piège des étudiants.

**Le scraping artisanal ne fait PAS le volume. L'API France Travail, oui.**

Décomposition réaliste pour 20 étudiants :

| Source | Volume réaliste | Pourquoi |
|--------|-----------------|----------|
| **France Travail (API)** | **3000 – 5000 à elle seule** | 8 métiers data × 8 départements, paginé. Stable, pas de ban. |
| Job boards (HelloWork, APEC, Indeed) | 500 – 1500 | Scraping HTML, dépend de la résistance du site |
| LinkedIn | 30-50 × nb étudiants ≈ 600 | Volontairement bridé pour ne pas bannir |
| Welcome to the Jungle / annuaires | 300 – 800 | Pages structurées |
| Enrichment (Hunter/Dropcontact) | complète les **emails**, pas le volume de lignes | — |

**Conclusion à assumer devant la classe** : la majorité des 5000 vient de l'API officielle. Le scraping LinkedIn, c'est la *compétence* qu'on apprend, pas le *volume* qu'on produit. C'est une vraie leçon d'ingénieur : on choisit la source fiable pour le résultat, on garde le scraping fragile pour les cas où il n'y a pas d'API.

> Si tu es pressé ou si une classe est petite : **`collecte_france_travail.py` seul peut suffire à dépasser 5000** en élargissant les mots-clés data. Les autres sources deviennent alors du bonus pédagogique.

---

## 3. À préparer AVANT la séance (30 min la veille)

1. **Clés France Travail** (le plus important) :
   - créer un compte sur https://francetravail.io
   - créer une application, demander l'accès à « Offres d'emploi v2 »
   - récupérer `client_id` + `client_secret`
   - **teste le script toi-même la veille** : `python collecte_france_travail.py` doit sortir un CSV de plusieurs milliers de lignes. Si ça marche chez toi, l'atelier est sauvé même si tout le reste casse.

2. **Installs sur les postes** :
   ```
   pip install requests beautifulsoup4 pandas python-dotenv playwright
   playwright install chromium
   ```

3. **Comptes** : LinkedIn (équipe LinkedIn), Hunter.io ou Dropcontact (équipe enrichment, tier gratuit).

4. **Le `.env`** sur chaque poste concerné, avec les clés. Vérifie qu'il est bien dans `.gitignore`.

---

## 4. Dérouler la séance (3h30)

Reprends le minutage de `01-Ateliers/Atelier1-Operation-5000.md`. Les points où le corrigé intervient :

- **1h10 – 2h15, la chasse** : chaque équipe lance son script et complète les `TODO`. Toi tu circules. **Garde `collecte_france_travail.py` qui tourne en fond sur ton poste** : c'est ton filet de sécurité, il remplit le gros du fichier pendant que les équipes galèrent sur leurs sélecteurs.

- **2h30 – 3h10, la fusion (le grand moment)** :
  1. Tu récupères tous les CSV des équipes dans un même dossier (clé USB, partage réseau, ou dossier commun).
  2. Tu lances `python fusion.py` **projeté à l'écran**.
  3. La classe regarde le bilan tomber : nb par source, doublons supprimés, et la ligne finale :
     ```
     >>> OBJECTIF ATTEINT : 5247 >= 5000
     ```
  4. Tu commentes : combien de doublons inter-sources ? (le même recruteur sur LinkedIn ET HelloWork). C'est ça, le vrai travail data engineer.

---

## 5. Si ça coince (anti-galère)

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| France Travail renvoie 400 | profondeur de pagination dépassée | normal, le script s'arrête tout seul à 1150/requête |
| Token France Travail refusé | scope ou clés incorrectes | vérifier `scope=api_offresdemploiv2 o2dsoffre` et les clés |
| Le scraper job board renvoie 0 | sélecteurs HTML changés | F12, inspecter, ajuster le `soup.select(...)`. **C'est l'exercice**, pas un bug. |
| LinkedIn bloque / captcha | trop de requêtes, ou login auto | login manuel uniquement, baisser `NB_PAGES`, étaler les équipes |
| `fusion.py` : 0 CSV trouvé | les fichiers ne sont pas dans le dossier | rassembler tous les `*.csv` à côté de `fusion.py` |
| On n'atteint pas 5000 | sources scraping faibles | élargir `MOTS_CLES_DATA` dans le script France Travail et relancer |

**Règle d'or anti-stress** : si l'atelier part en vrille, `collecte_france_travail.py` seul, lancé sur ton poste avec une liste de mots-clés élargie, dépasse les 5000. Tu finis toujours la séance avec un fichier rempli.

---

## 6. Les points pédagogiques à marteler

- **Le schéma avant la collecte.** Sans format commun, la fusion est impossible. C'est la première chose qu'un data engineer cadre.
- **API > scraping quand l'API existe.** Fiable, légal, stable. Le scraping, c'est pour quand il n'y a pas d'API.
- **La valeur n'est pas dans la collecte, elle est dans le nettoyage.** 5000 lignes brutes ne valent rien. 5000 lignes dédoublonnées et normalisées, c'est un actif.
- **Petit volume sur les sources fragiles.** On ne grille pas un compte LinkedIn pour 50 contacts qu'on aura mieux ailleurs.

---

## 7. La suite

Le `contacts.csv` est le carburant de toute la chaîne :
**Atelier 2** le charge en base → **Atelier 4** le matche aux offres → **Atelier 5** génère le CV adapté → **Atelier 6** prépare l'envoi.

Phrase de fin de séance : *« Vous avez vos 5000 recruteurs. La prochaine fois, on construit la machine qui leur envoie votre candidature pendant que vous dormez. »*
