# Guide formateur : atelier 1, la collecte

Tout ce qu'il faut pour animer l'atelier 1 et garantir que le fichier final atteint vraiment plusieurs milliers de contacts. À lire une fois en entier avant la séance. Les fichiers cités sont dans `Atelier-1-Collecte/`.

## 1. Ce que contient le corrigé

Le corrigé est dans `Atelier-1-Collecte/corrige/`.

| Fichier | Rôle | Qui le lance |
|---------|------|--------------|
| `collecte_france_travail.py` | Le cheval de bataille. API officielle, sort des milliers d'offres data IDF avec entreprise et contact | Équipe France Travail, et toi en secours |
| `collecte_jobboard.py` | Scraping HTML (HelloWork) avec BeautifulSoup | Équipe job boards |
| `collecte_linkedin.py` | Scraping LinkedIn (Playwright, petit volume) | Équipe LinkedIn |
| `fusion.py` | La correction finale. Assemble tous les CSV, dédoublonne, vérifie le total | Toi, en live |
| `.env` | Les clés d'API, jamais commité | Chaque poste |

Chaque script de collecte produit un CSV au même schéma. `fusion.py` les avale tous. Le squelette à compléter par les élèves est dans `Atelier-1-Collecte/starter/`, un fichier par équipe.

## 2. La vérité sur le volume

Sois clair là-dessus dans ta tête, c'est la question piège des étudiants. Le scraping artisanal ne fait pas le volume, l'API France Travail oui.

Décomposition réaliste pour 20 étudiants :

| Source | Volume réaliste | Pourquoi |
|--------|-----------------|----------|
| France Travail (API) | 3000 à 5000 à elle seule | 8 métiers data sur 8 départements, paginé, stable, pas de ban |
| Job boards (HelloWork, APEC, Indeed) | 500 à 1500 | Scraping HTML, dépend de la résistance du site |
| LinkedIn | 30 à 50 par étudiant | Volontairement bridé pour ne pas bannir |
| Welcome to the Jungle, annuaires | 300 à 800 | Pages structurées |
| Enrichment (Hunter, Dropcontact) | complète les emails, pas le volume de lignes | sans objet |

Conclusion à assumer devant la classe : la majorité du volume vient de l'API officielle. Le scraping LinkedIn, c'est la compétence qu'on apprend, pas le volume qu'on produit. On choisit la source fiable pour le résultat, on garde le scraping fragile pour les cas sans API.

Si tu es pressé ou si une classe est petite, `collecte_france_travail.py` seul peut suffire à dépasser plusieurs milliers de lignes en élargissant les mots-clés data. Les autres sources deviennent alors du bonus.

## 3. À préparer avant la séance (30 min la veille)

1. Clés France Travail, le plus important :
   - créer un compte sur https://francetravail.io
   - créer une application, demander l'accès à "Offres d'emploi v2"
   - récupérer `client_id` et `client_secret`
   - tester le script toi-même la veille. `python collecte_france_travail.py` doit sortir un CSV de plusieurs milliers de lignes. Si ça marche chez toi, l'atelier est sauvé même si le reste casse.

2. Installs sur les postes :
   ```
   pip install requests beautifulsoup4 pandas python-dotenv playwright
   playwright install chromium
   ```

3. Comptes : LinkedIn pour l'équipe LinkedIn, Hunter.io ou Dropcontact pour l'équipe enrichment (offre gratuite).

4. Le `.env` dans `Atelier-1-Collecte/corrige/`, avec les clés. Vérifie qu'il est bien ignoré par `.gitignore`. Un modèle est dans `Atelier-1-Collecte/starter/.env.example`.

## 4. Dérouler la séance (3h30)

Reprends le minutage de `Atelier-1-Collecte/README.md`. Les points où le corrigé intervient :

- La chasse (environ 1h10-2h15) : chaque équipe lance son script et complète les TODO du starter. Toi tu circules. Garde `collecte_france_travail.py` qui tourne en fond sur ton poste, c'est ton filet de sécurité, il remplit le gros du fichier pendant que les équipes ajustent leurs sélecteurs.

- La fusion (environ 2h30-3h10), le grand moment :
  1. Tu récupères tous les CSV des équipes dans un même dossier, à côté de `fusion.py`.
  2. Tu lances `python fusion.py` projeté à l'écran.
  3. La classe regarde le bilan tomber : nombre par source, doublons supprimés, total final.
  4. Tu commentes : combien de doublons entre sources ? Le même recruteur sur LinkedIn et HelloWork. C'est ça, le vrai travail de data engineer.

## 5. Si ça coince

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| France Travail renvoie 400 | profondeur de pagination dépassée | normal, le script s'arrête seul à 1150 par requête |
| Token France Travail refusé | scope ou clés incorrectes | vérifier `scope=api_offresdemploiv2 o2dsoffre` et les clés |
| API renvoie 500 juste après l'abonnement | propagation de l'application neuve | attendre, ça peut prendre 30 min à quelques heures, réessayer ensuite |
| Le scraper job board renvoie 0 | sélecteurs HTML changés | F12, inspecter, ajuster le `soup.select(...)`. C'est l'exercice, pas un bug |
| LinkedIn bloque ou captcha | trop de requêtes, ou login auto | login manuel uniquement, baisser le nombre de pages, étaler les équipes |
| `fusion.py` ne trouve aucun CSV | les fichiers ne sont pas dans le dossier | rassembler tous les `*.csv` à côté de `fusion.py` |
| On n'atteint pas le total visé | sources de scraping faibles | élargir `MOTS_CLES_DATA` dans le script France Travail et relancer |

Règle d'or anti-stress : si l'atelier part en vrille, `collecte_france_travail.py` seul, avec une liste de mots-clés élargie, dépasse l'objectif. Tu finis toujours la séance avec un fichier rempli.

## 6. Les points pédagogiques à marteler

- Le schéma avant la collecte. Sans format commun, la fusion est impossible. C'est la première chose qu'un data engineer cadre.
- API plutôt que scraping quand l'API existe : fiable, légal, stable. Le scraping, c'est pour quand il n'y a pas d'API.
- La valeur n'est pas dans la collecte, elle est dans le nettoyage. 5000 lignes brutes ne valent rien, 5000 lignes dédoublonnées et normalisées sont un actif.
- Petit volume sur les sources fragiles. On ne grille pas un compte LinkedIn pour 50 contacts qu'on aura mieux ailleurs.

## 7. La suite

Le `contacts.csv` est le carburant de toute la chaîne. L'atelier 2 le charge en base, l'atelier 3 le rend lisible dans un tableau de bord, l'atelier 4 prépare l'envoi des candidatures. Le matching d'un CV aux offres et la génération d'un CV adapté par LLM sont les prolongements naturels.
