# Note de cadrage RGPD — Plateforme d'automatisation de candidatures

> À distribuer aux étudiants dès l'atelier 1. Sert de cadre légal et de support pédagogique. Le respect de cette note compte dans l'évaluation finale (15 %).

## Pourquoi ça compte

Le projet manipule des données personnelles (recruteurs, et le CV de l'étudiant). En France, ça relève du **RGPD** et de la loi Informatique et Libertés. Faire les choses proprement, c'est à la fois une obligation légale et une compétence professionnelle recherchée.

## Les 3 types de données du projet

| Donnée | Nature | Risque | Règle |
|--------|--------|--------|-------|
| Offres d'emploi | Données d'entreprise (publiques, via API officielle) | Faible | Libre exploitation |
| Recruteurs / DRH | **Données personnelles** | Élevé | Minimisation stricte, voir ci-dessous |
| CV de l'étudiant | **Données personnelles** (les siennes) | Moyen | Ne pas diffuser hors plateforme |

## Règles d'or (non négociables)

1. **Pas de scraping LinkedIn massif.** On utilise l'**API France Travail** pour les offres. Le scraping massif viole les conditions d'utilisation de LinkedIn et le principe de minimisation. C'est aussi un risque de bannissement des comptes étudiants.

2. **Pas de base de données de recruteurs revendable.** On ne constitue pas un fichier de centaines de DRH stocké « au cas où ». L'enrichissement d'un contact se fait **à la demande, sur une offre précise** que l'étudiant cible réellement.

3. **Validation humaine avant tout envoi.** Aucune candidature ne part automatiquement. La plateforme **prépare** (CV adapté + brouillon), un humain **valide et envoie**. C'est conforme et ça évite les envois aberrants.

4. **Minimisation.** On ne collecte que ce qui sert la candidature : nom, fonction, entreprise, contact professionnel lié à l'offre. Pas de données privées, pas de profil exhaustif.

5. **Durée de conservation limitée.** Les contacts liés à une offre non poursuivie sont supprimés après X semaines. À définir et à documenter.

## Les principes RGPD appliqués au projet (à enseigner)

- **Base légale** : pour contacter un recruteur dans le cadre d'une candidature, la base est l'**intérêt légitime** (article 6.1.f). À justifier : démarche de recherche d'emploi ciblée, contact professionnel, dans son contexte attendu.
- **Finalité** : candidater à des offres de Data Engineer. Toute autre utilisation (prospection commerciale, revente) est interdite.
- **Minimisation** : seules les données utiles à la finalité.
- **Transparence** : le recruteur contacté peut savoir d'où vient la démarche.
- **Droits** : droit d'accès, de rectification, d'opposition, d'effacement. La plateforme doit permettre de supprimer un contact sur demande.
- **Sécurité** : clés API et données dans des variables d'environnement, jamais en dur dans le code, jamais commitées sur Git.

## Checklist sécurité technique (atelier par atelier)

- [ ] Clés API (France Travail, Claude, Supabase, Gmail) dans `.env`, jamais dans le code
- [ ] `.env` dans le `.gitignore`
- [ ] Accès Supabase protégé (Row Level Security activé)
- [ ] Pas de données personnelles dans les logs
- [ ] CV stockés de façon restreinte (chaque étudiant accède au sien)
- [ ] Suppression possible d'un contact / d'une candidature

## Exercice pédagogique associé (atelier 1)

Faire rédiger par chaque groupe, en 15 minutes, le **registre de traitement** du projet :

| Champ | À remplir |
|-------|-----------|
| Finalité | … |
| Données collectées | … |
| Base légale | … |
| Durée de conservation | … |
| Mesures de sécurité | … |

C'est un livrable court, concret, et c'est exactement ce qu'un DPO attend en entreprise.

## Le piège à éviter (à expliquer clairement)

L'envoi **totalement** automatique de CV dès qu'une offre sort, sans validation, sur LinkedIn :
- viole les ToS de LinkedIn (risque de ban),
- juridiquement gris côté RGPD (envois non maîtrisés),
- contre-productif (candidatures génériques mal ciblées = mauvaise image).

La version **semi-automatique** (préparation auto + validation humaine) a la **même valeur pédagogique** (toute la chaîne data + LLM est construite) sans aucun de ces risques. C'est le choix retenu pour la formation.
