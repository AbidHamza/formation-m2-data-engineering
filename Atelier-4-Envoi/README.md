# Atelier 4 : L'envoi des candidatures

Dernier atelier de la chaine. Aux precedents, vous avez collecte des offres et vous les avez stockees proprement dans une base. Ici, vous vous occupez du dernier metre : transformer une cible (une offre, une entreprise, un contact) en candidature prete a partir.

Ce guide ne vous donne pas le code a recopier. Il vous explique les notions, la demarche etape par etape, et il vous pose les bonnes questions. Le code, c'est vous qui l'ecrivez. C'est tout l'interet : a la fin, vous saurez vraiment comment ca marche, pas juste lancer un script tout fait.

Vous travaillez en binome ou trinome, sur 3h30. Prenez le temps de comprendre chaque etape avant de passer a la suivante.

## 1. Objectif de l'atelier

Construire un outil qui, pour chaque cible, prepare un message personnalise avec le CV en piece jointe, et le depose sous forme de brouillon Gmail. Tout est pret. Il ne manque qu'un clic humain pour que la candidature parte.

Le cadre est non negociable :

- semi-automatique. Le robot prepare, l'humain valide et envoie.
- validation humaine systematique. On ne declenche jamais l'envoi depuis le code.
- jamais d'envoi sauvage. Pas de candidature en masse, pas de bot qui postule tout seul la nuit.

Si a un moment vous vous dites "et si on automatisait aussi le clic Envoyer", arretez-vous. C'est exactement ce qu'on ne fait pas, et la section suivante explique pourquoi.

## 2. Les notions a comprendre avant de coder

### Pourquoi pas un bot LinkedIn

La tentation est forte : un bot qui postule a 200 offres LinkedIn pendant la nuit. Vous en trouverez des dizaines sur GitHub. Ils ont tous le meme defaut. LinkedIn detecte ce type d'automatisation et bannit le compte. Trois mois avant de chercher un poste, vous perdez votre vitrine professionnelle. C'est aussi un probleme legal : vous violez les conditions d'utilisation de la plateforme.

L'envoi d'email automatique en masse ne vaut pas mieux. Gmail repere les boites qui crachent des centaines de messages identiques, les classe en indesirables, et la reputation de l'expediteur est grillee.

L'email cible fonctionne pour une raison simple : on ecrit a l'adresse de contact d'une offre precise, avec un message adapte a cette offre, en volume raisonnable, relu a la main. Ce n'est pas du spam, c'est une vraie candidature. Elle est legitime, donc elle est delivrable.

| Approche | Ce qui se passe |
|----------|-----------------|
| Bot LinkedIn (auto-candidature) | Detecte, compte banni, probleme legal. C'est ce que font la plupart des projets GitHub. A ne pas reproduire. |
| Envoi email automatique en masse | Gmail flague, les mails finissent en indesirables, la reputation d'expediteur est grillee. |
| Email semi-automatique, personnalise, valide | Legitime, delivrable, defendable. C'est notre choix. |

A retenir : on reste en semi-automatique avec validation humaine. Ce n'est pas une faiblesse technique, c'est une decision.

### Brouillon contre envoi direct

Le code peut tout faire jusqu'a l'envoi. On choisit de s'arreter juste avant. Au lieu d'envoyer, le robot cree un brouillon dans votre Gmail. Vous l'ouvrez, vous le relisez, et c'est vous qui cliquez sur Envoyer.

La valeur pedagogique est la meme : vous apprenez a piloter l'API Gmail, a personnaliser un message, a gerer une piece jointe. Mais sans le risque d'envoyer une betise a un vrai recruteur. Le seul moment ou vous engagez votre nom merite une relecture humaine.

Question a vous poser : pourquoi un brouillon plutot qu'un envoi direct ? Trouvez au moins deux raisons (une technique, une humaine) avant de continuer.

### API Gmail et OAuth2

Pour qu'un programme agisse sur votre boite Gmail, Google doit etre sur que vous l'autorisez. C'est le role d'OAuth2, un protocole d'autorisation utilisateur.

Le mecanisme se passe en deux temps :

- vous telechargez un fichier `credentials.json` depuis Google Cloud. Il identifie votre application aupres de Google.
- au premier lancement, votre navigateur s'ouvre, vous vous connectez, vous autorisez l'acces. Google renvoie alors un jeton, stocke dans `token.json`. Les lancements suivants reutilisent ce jeton sans redemander la connexion.

Le point crucial est le scope, c'est-a-dire l'etendue de la permission que vous demandez. Vous demanderez `gmail.compose`, qui autorise la creation de brouillons. Vous ne demandez surtout pas un scope d'envoi automatique. Le code ne pourra donc techniquement pas envoyer un mail tout seul, meme par erreur. La permission elle-meme materialise le garde-fou.

Question : si le scope demande etait `gmail.send`, qu'est-ce que ca changerait au niveau du risque ? Pourquoi se limiter volontairement ?

### Personnalisation par fusion

Un message generique ("Bonjour, je postule a votre offre") finit a la corbeille. Le recruteur voit tout de suite que c'est un copier-coller envoye a 50 entreprises.

L'idee de la fusion : vous ecrivez un modele de message avec des trous, et vous remplissez ces trous avec les donnees de chaque cible (le prenom du contact, le nom de l'entreprise, l'intitule de l'offre). Un meme modele produit donc un message different, et credible, pour chaque cible.

Question : comment personnaliser sans tomber dans le robotique ? Un modele trop mecanique ("Votre offre de [POSTE] chez [ENTREPRISE] m'interesse") se repere aussi. Reflechissez a ce qui rend un message reellement adapte.

### Anti-doublon et idempotence

Vous allez relancer votre script plusieurs fois pendant l'atelier (pour debugger, pour ajouter des cibles). Sans precaution, chaque relance recreerait des brouillons pour les memes adresses. Resultat : dix brouillons identiques pour Sophie Martin.

La solution : un journal, un fichier `deja_contactes.csv`, qui enregistre chaque adresse traitee. Au lancement, le script lit ce journal et ignore les adresses qui s'y trouvent deja.

C'est exactement l'idempotence vue a l'atelier 2 : relancer l'operation ne change rien de plus. Ajoutez trois nouvelles cibles, relancez, seules ces trois produiront un brouillon.

Question : que se passe-t-il si vous relancez le script sans journal ? Et avec le journal ? Decrivez les deux comportements avant de coder.

## 3. Prerequis et installation

### Cote Google Cloud (une seule fois)

1. Allez sur Google Cloud Console et creez un projet (n'importe quel nom).
2. Activez l'API Gmail pour ce projet (cherchez "Gmail API" dans la bibliotheque d'API, puis "Activer").
3. Configurez l'ecran de consentement OAuth. En mode test, ajoutez votre propre adresse Gmail comme utilisateur autorise. Sans cette etape, l'autorisation echouera.
4. Creez un identifiant OAuth de type "Application de bureau" (Desktop).
5. Telechargez le fichier, renommez-le `credentials.json`, et placez-le a cote de votre script.

Ce `credentials.json` est votre cle d'acces. Ne le commitez jamais.

### Cote Python

```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib pandas
```

Les trois premiers paquets servent a parler a l'API Google avec OAuth. `pandas` aide a lire le CSV de cibles, mais vous pouvez aussi vous contenter du module `csv` de la bibliotheque standard si vous preferez.

## 4. La demarche de A a Z

Construisez votre script etape par etape. Apres chaque etape, testez avant de passer a la suivante. Ne codez pas tout d'un bloc.

### Etape 1 : s'authentifier aupres de Gmail

Objectif : obtenir un objet "service" qui represente votre acces autorise a Gmail.

Le concept : votre fonction d'authentification doit gerer trois cas.

- pas de `token.json` : c'est le premier lancement, il faut declencher le flux OAuth qui ouvre le navigateur, puis sauvegarder le jeton.
- `token.json` present et valide : on le reutilise directement.
- `token.json` present mais expire : on le rafraichit avec le refresh token, sans redemander la connexion.

Les briques cote bibliotheque : `Credentials.from_authorized_user_file` pour relire un jeton, `InstalledAppFlow.from_client_secrets_file(...)` puis `.run_local_server(...)` pour le premier login, et `build("gmail", "v1", credentials=...)` pour obtenir le service.

Definissez votre scope en constante :

```python
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
```

Testez cette etape seule : lancez, autorisez dans le navigateur, verifiez que `token.json` apparait. Relancez : le navigateur ne doit plus s'ouvrir.

Question : pourquoi sauvegarder le jeton dans un fichier plutot que de le redemander a chaque fois ? Et pourquoi ce fichier ne doit-il jamais etre commite ?

### Etape 2 : lire les cibles

Objectif : charger la liste des cibles, depuis le CSV ou depuis la base de l'atelier 2.

Le fichier d'exemple `exemple/cibles.exemple.csv` utilise le point-virgule comme separateur, avec ces colonnes :

```
email;prenom;nom;entreprise;fonction;offre_titre;offre_url;cv_path
```

Deux pieges classiques :

- l'encodage. Les fichiers CSV Windows portent souvent un BOM (un marqueur invisible en debut de fichier). Lisez en `utf-8-sig` pour qu'il soit absorbe proprement, sinon votre premiere colonne s'appellera `﻿email` et rien ne marchera.
- le separateur. Ici c'est `;`, pas la virgule. Precisez-le a votre lecteur CSV.

Vous pouvez lire le fichier avec `csv.DictReader` (chaque ligne devient un dictionnaire) ou avec `pandas`. Les deux conviennent.

Alternative : au lieu du CSV, branchez la requete sur la base de l'atelier 2. Le reste du script ne change pas tant que chaque cible expose les memes champs.

Testez : affichez simplement les cibles lues. Verifiez que vous avez bien 6 lignes et que les colonnes sont correctes.

### Etape 3 : ecrire un modele de message personnalisable

Objectif : une fonction qui prend une cible et renvoie un sujet et un corps adaptes.

Le concept de la fusion : votre fonction lit les champs de la cible (`prenom`, `entreprise`, `offre_titre`) et les insere dans un texte. Pensez aux cas ou un champ est vide. Plusieurs cibles d'exemple n'ont pas de prenom (adresses generiques comme `recrutement@`). Votre salutation doit s'adapter : "Bonjour Sophie," si le prenom existe, "Bonjour," sinon.

Une signature de fonction possible :

```python
def rediger(cible) -> tuple[str, str]:
    ...  # renvoie (sujet, corps)
```

Soignez le texte. Un recruteur lit en trois secondes. Le message doit montrer que vous avez lu son offre precise, pas envoye le meme texte partout.

Question : comment gerer proprement un champ manquant sans que le message devienne ridicule ("Bonjour ,") ? Testez votre fonction sur une cible avec prenom et une cible sans.

### Etape 4 : creer le brouillon via l'API

Objectif : a partir du sujet, du corps, de l'adresse et du CV, deposer un brouillon dans Gmail.

Le concept : un email est un objet structure (destinataire, sujet, corps, pieces jointes). En Python, `email.message.EmailMessage` construit cet objet. Pour la piece jointe, vous lisez le PDF du CV (`cv_path`) et vous l'attachez. Gerez le cas ou le fichier n'existe pas : creez quand meme le brouillon, mais signalez l'absence de piece jointe plutot que de planter.

L'API Gmail attend le message encode en base64 url-safe. L'appel qui cree le brouillon ressemble a :

```python
service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
```

`drafts().create` cree un brouillon. Remarquez qu'il n'existe pas d'appel `send` dans votre code : c'est volontaire, et coherent avec le scope `gmail.compose`.

Testez sur une seule cible. Ouvrez Gmail, verifiez que le brouillon est la, avec le bon destinataire, le bon texte, et le CV joint.

Question : ou, dans votre code, pourriez-vous accidentellement transformer ce brouillon en envoi ? Verifiez qu'aucun chemin ne le permet.

### Etape 5 : journaliser pour l'anti-doublon

Objectif : apres avoir cree un brouillon, enregistrer l'adresse dans `deja_contactes.csv`, et au demarrage, charger les adresses deja traitees.

Le concept se decompose en deux fonctions :

- une qui lit le journal au depart et renvoie l'ensemble des adresses deja contactees (un `set` pour un test d'appartenance rapide). Si le fichier n'existe pas encore, renvoyez un ensemble vide.
- une qui ajoute une ligne au journal apres chaque brouillon cree. Pensez a ecrire l'en-tete la premiere fois.

Normalisez les adresses (minuscules, sans espaces) avant de comparer, sinon `Sophie@X.com` et `sophie@x.com` seront vus comme differents.

### Etape 6 : assembler la boucle principale

Objectif : tout relier. Lire les cibles, charger le journal, et pour chaque cible non encore contactee, creer le brouillon puis journaliser.

La logique de la boucle :

- ignorer les lignes sans email.
- ignorer les adresses deja dans le journal (incrementer un compteur "ignores").
- sinon, creer le brouillon, journaliser, ajouter l'adresse a l'ensemble en memoire, incrementer "crees".

A la fin, affichez un bilan : combien de brouillons crees, combien ignores. Et rappelez a l'utilisateur d'aller relire dans Gmail.

Glissez une petite pause entre deux appels (`time.sleep(0.5)`) pour rester poli avec l'API et eviter de saturer le quota.

Question cle : si vous relancez le script tout de suite apres, que doit afficher le bilan ? Verifiez que c'est bien ce qui se passe.

## 5. Pieges courants

- `credentials.json` absent : le flux OAuth ne peut pas demarrer. Verifiez que le fichier est bien a cote du script, avec ce nom exact.
- token expire : normalement votre code le rafraichit tout seul. Si le refresh echoue (jeton revoque, scope change), supprimez `token.json` et relancez pour refaire le login.
- scope insuffisant : si vous avez d'abord teste avec un autre scope, le `token.json` existant ne couvre pas `gmail.compose`. Supprimez-le et relancez pour reautoriser avec le bon scope.
- doublons : si vous oubliez le journal ou si vous le lisez mal, chaque relance recree des brouillons. Le symptome est immediat dans Gmail.
- piece jointe introuvable : le `cv_path` pointe vers un fichier qui n'existe pas. Votre code doit le signaler sans planter, et creer le brouillon sans piece jointe.
- quota Gmail : en lancant des centaines de creations sans pause, vous pouvez heurter une limite. La petite pause entre deux appels et le volume raisonnable de l'atelier suffisent a l'eviter.
- ecran de consentement : si vous oubliez d'ajouter votre adresse comme utilisateur test, Google refuse l'autorisation. Erreur frequente au premier lancement.

## 6. Socle et bonus

### Socle (objectif minimal)

- des brouillons Gmail personnalises sont crees, un par cible, avec le CV en piece jointe.
- l'anti-doublon fonctionne : relancer le script ne recree aucun brouillon deja fait.

### Bonus (si vous avez le temps)

- un modele de message adapte par type de poste : un texte different selon que l'offre parle de data engineering, de cloud, ou de plateforme.
- brancher la source de cibles sur la base de l'atelier 2 au lieu du CSV.
- un statut de suivi dans le journal (date d'envoi, reponse recue ou non) pour preparer une relance.

## 7. Critere de reussite

Vous avez reussi quand :

- lancer votre script sur `exemple/cibles.exemple.csv` cree des brouillons personnalises dans votre Gmail (un par cible, avec le CV joint quand le fichier existe).
- relancer le script ne recree aucun doublon, grace au journal `deja_contactes.csv`.

L'exemple `exemple/cibles.exemple.csv` contient 6 cibles fictives en `@example.com`. Il sert a voir les brouillons se creer en demonstration, sans ecrire a de vraies personnes. Copiez-le sous le nom attendu par votre script avant de lancer.

### Securite

Ne commitez jamais :

- `credentials.json` (votre cle d'acces a l'API),
- `token.json` (votre jeton de session),
- votre vrai fichier de cibles (il contient de vraies adresses).

Ajoutez ces noms a votre `.gitignore` des le depart. Seul le fichier d'exemple en `@example.com` a vocation a etre partage.
