# Atelier 4 : L'envoi des candidatures

C'est le dernier atelier, le bouquet final de la chaîne. Aux ateliers précédents on a collecté les offres, on les a stockées proprement. Plus tard viendront le matching offre/profil et la génération de CV adaptés. Ici on s'occupe du dernier mètre : envoyer une candidature. Mais on l'envoie intelligemment.

L'outil prépare, pour chaque cible, un message personnalisé et un CV adapté en pièce jointe, sous forme de brouillon Gmail. Tout est prêt. Il ne manque qu'un clic humain pour partir.

## Pourquoi pas un bot LinkedIn

La tentation est forte : un bot qui postule tout seul à 200 offres LinkedIn pendant la nuit. Allez sur GitHub, vous en trouverez des dizaines. Ils ont tous le même défaut. LinkedIn détecte ce genre d'automatisation et bannit le compte. Trois mois avant de chercher un poste, vous perdez votre vitrine professionnelle.

L'envoi d'email automatique en masse ne vaut pas mieux. Gmail repère les boîtes qui crachent des centaines de messages identiques, les classe en indésirables, et la réputation de l'expéditeur est grillée.

L'email ciblé fonctionne pour une raison simple : on écrit à l'adresse de contact d'une offre précise, avec un message adapté à cette offre, et en volume raisonnable relu à la main. Ce n'est pas du spam, c'est une vraie candidature. Elle est légitime, donc elle est délivrable.

| Approche | Ce qui se passe |
|----------|-----------------|
| Bot LinkedIn (auto-candidature) | Détecté, compte banni. C'est ce que font la plupart des projets GitHub. À ne pas reproduire. |
| Envoi email automatique en masse | Gmail flague, les mails finissent en indésirables, la réputation d'expéditeur est grillée. |
| Email semi-automatique, personnalisé, validé | Légitime, délivrable, défendable. C'est notre choix. |

## Le principe

Le robot fait tout le travail pénible : il lit la liste des cibles, rédige un message adapté à chacune, joint le bon CV, et crée le brouillon dans Gmail. L'humain ouvre Gmail, relit le brouillon, et clique sur Envoyer.

Garder l'humain dans la boucle au dernier moment n'est pas une limite technique. On sait tout automatiser jusqu'à l'envoi. On choisit de ne pas le faire, parce que le seul instant où l'on engage son nom mérite une relecture. C'est une décision d'architecture.

## L'anti-doublon

Chaque cible déjà traitée est inscrite dans un journal, `deja_contactes.csv`. Au lancement, le script lit ce journal et ignore les adresses qui s'y trouvent déjà.

Conséquence pratique : vous pouvez relancer le script autant de fois que vous voulez, il ne recréera jamais un brouillon déjà fait. Si vous ajoutez trois nouvelles cibles à votre fichier et que vous relancez, seules ces trois-là produiront un brouillon. C'est l'idempotence vue à l'atelier 2, réutilisée telle quelle.

## Prérequis

Il faut un accès à l'API Gmail. La mise en place se fait une seule fois :

- créer un projet sur Google Cloud Console,
- y activer l'API Gmail,
- créer un identifiant OAuth de type "Desktop",
- télécharger le fichier `credentials.json`.

Ce fichier `credentials.json` est votre clé d'accès. Gardez-le, ne le commitez pas.

## Lancer le corrigé

Depuis la racine du dépôt :

```
cd Atelier-4-Envoi/corrige
pip install google-api-python-client google-auth-oauthlib
```

Placez votre `credentials.json` à côté du script.

Préparez votre fichier de cibles. Soit vous utilisez le vôtre, soit vous copiez l'exemple fourni :

```
copy ..\exemple\cibles.exemple.csv cibles.csv
```

Sous macOS ou Linux :

```
cp ../exemple/cibles.exemple.csv cibles.csv
```

Le fichier `cibles.csv` utilise le point-virgule comme séparateur, avec ces colonnes :

```
email;prenom;nom;entreprise;fonction;offre_titre;offre_url;cv_path
```

Lancez l'outil :

```
python envoi_candidatures.py
```

Au premier lancement, le navigateur s'ouvre pour autoriser l'accès à Gmail. Cette autorisation crée un fichier `token.json` qui évite de redemander la connexion ensuite. Les brouillons apparaissent alors dans votre Gmail. Rien n'est envoyé : c'est à vous de relire et de cliquer sur Envoyer.

## L'exemple fourni

Le fichier `exemple/cibles.exemple.csv` contient 6 cibles fictives en `@example.com`. Il sert à voir les brouillons se créer en démonstration, sans risquer d'écrire à de vraies personnes. Copiez-le en `cibles.csv` et lancez le script pour observer le comportement complet, anti-doublon compris.

## Critères de réussite

Socle :

- un brouillon Gmail personnalisé est créé pour chaque cible, avec le CV en pièce jointe,
- l'anti-doublon est vérifié : on relance le script et aucun brouillon n'est dupliqué.

Bonus :

- le corps du message est généré par un LLM plutôt que par un template fixe,
- un brouillon de relance est préparé à J+7 si aucune réponse n'est arrivée,
- un fallback gère le cas sans email : basculer vers le formulaire de candidature de l'entreprise.
