# Atelier — L'envoi (par email, validation humaine)

> Format : storytelling + atelier pratique. Durée 3h30. Niveau hétérogène.
> Livrable : **un robot qui prépare des candidatures personnalisées (message + CV adapté) en brouillons Gmail**, prêtes à partir d'un clic. Anti-doublon intégré. Zéro envoi sans validation humaine.

> Position dans la chaîne : c'est le bouquet final. Il utilise la base (atelier 2), le matching (atelier 4) et le CV généré (atelier 5). On ne peut pas postuler intelligemment avant d'avoir ces briques.

---

## 🎬 Le pitch (10 min)

> *« Vous avez la base, le matching, le CV adapté. Il reste la dernière marche : envoyer.*
>
> *La tentation, c'est le bot LinkedIn qui postule tout seul à 200 offres pendant la nuit. Allez voir GitHub : il y en a des dizaines. Et ils ont tous le même problème. LinkedIn les détecte, et c'est VOTRE compte qui saute. Trois mois avant de chercher un job, vous grillez votre vitrine pro. Catastrophe.*
>
> *Nous, on fait l'inverse. On envoie par email, là où c'est légitime. Le robot prépare tout, parfaitement personnalisé. Mais c'est vous qui cliquez "Envoyer". Semi-automatique. Toute la puissance, zéro risque. »*

L'idée : montrer que le choix d'ingénieur intelligent n'est pas "le plus automatisé", c'est "le plus automatisé qui ne se retourne pas contre toi". L'humain dans la boucle n'est pas une faiblesse, c'est ce qui rend le système durable.

---

## 🎯 La règle du jeu

- **Socle** : pour une liste de cibles (offre + email de contact + CV adapté), le script crée un brouillon Gmail personnalisé par cible, CV en pièce jointe. On ouvre Gmail : les brouillons sont là, prêts.
- **L'anti-doublon obligatoire** : relancer le script ne recrée pas les brouillons déjà faits. Un journal `deja_contactes.csv` tient la mémoire. C'est l'idempotence de l'atelier 2 qui ressert ici.
- **La règle d'or** : aucun mail ne part sans un clic humain. On ne code pas l'envoi automatique de masse. C'est un choix, pas une limite technique.

---

## 🚫 Pourquoi pas LinkedIn auto (le point à marteler)

| Approche | Résultat |
|----------|----------|
| Bot LinkedIn Easy Apply | Détecté, compte banni. C'est ce que font 90 % des projets GitHub. À ne pas reproduire. |
| Envoi email automatique en masse | Gmail flague, finit en spam, réputation d'expéditeur grillée. |
| **Email semi-auto, personnalisé, validé** | Légitime, délivrable, défendable RGPD. **Notre choix.** |

Le canal email fonctionne parce qu'on cible l'adresse de contact d'une offre précise (intérêt légitime), avec un message adapté, et un volume raisonnable relu à la main. Ce n'est pas du spam, c'est une vraie candidature, juste préparée par un outil.

---

## ⏱️ Le déroulé (3h30)

| Temps | Phase | Ce qui se passe |
|-------|-------|-----------------|
| 0:00 – 0:15 | **Le pitch + la démo du danger** | On montre un repo de bot LinkedIn, on explique le ban. On pose le choix semi-auto. |
| 0:15 – 0:45 | **Setup Gmail API** | Console Google Cloud, activer Gmail API, OAuth client "Desktop", `credentials.json`. |
| 0:45 – 1:30 | **Premier brouillon** | Authentifier, construire un message MIME, créer un brouillon via l'API. Le voir apparaître dans Gmail. |
| 1:30 – 1:45 | **Pause** | — |
| 1:45 – 2:30 | **Personnalisation + pièce jointe** | Brancher le message sur les données de la cible, attacher le CV adapté (atelier 5). |
| 2:30 – 3:05 | **Anti-doublon** | Le journal `deja_contactes.csv`. Relancer le script : rien ne se duplique. |
| 3:05 – 3:30 | **Démo finale** | Une liste de cibles → des brouillons prêts. On en ouvre un, on relit, on envoie pour de vrai. |

---

## 🔧 Le vrai apprentissage

- **OAuth d'un service tiers** (Gmail) : le flow `credentials.json` → `token.json`, le refresh. Compétence réutilisable partout.
- **Construire un email proprement** : MIME, sujet, corps, pièce jointe encodée. Ce qui se passe sous le capot quand on clique "joindre".
- **L'humain dans la boucle comme décision d'architecture** : on sait tout automatiser, on choisit de ne pas le faire au dernier mètre. C'est de la maturité d'ingénieur, pas une lacune.

---

## ✅ Critères de réussite

- **Socle** : brouillons Gmail personnalisés créés pour chaque cible, CV joint, anti-doublon fonctionnel.
- **Bonus** :
  - corps du message généré par le LLM de l'atelier 5 (au lieu du template),
  - relance programmée : un brouillon de relance J+7 si pas de réponse,
  - tableau de bord : nb de candidatures préparées, envoyées, en attente (branche sur l'atelier 6),
  - fallback intelligent : si l'offre n'a pas d'email, basculer sur le formulaire/ATS de la boîte.

---

## 🔌 À préparer avant

- `pip install google-api-python-client google-auth-oauthlib`
- Un projet Google Cloud par étudiant (ou un partagé), Gmail API activée, `credentials.json` téléchargé.
- Le `cibles.csv` (issu de la base + du matching) et les CV adaptés (atelier 5) à portée.

---

## 🪝 Mot de la fin

*« Vous avez construit la chaîne complète : trouver, ranger, matcher, rédiger, envoyer. Une machine qui transforme une recherche d'emploi en pipeline. Et le seul moment où elle vous demande de cliquer, c'est juste avant d'engager votre nom. C'est exactement là qu'un humain doit rester. »*
