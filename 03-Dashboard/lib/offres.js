// Fonctions utilitaires pures pour filtrer, trier et agréger les offres.
// "Pures" = elles ne modifient rien, elles prennent des données et en renvoient
// de nouvelles. C'est plus simple à tester et à réutiliser dans les composants.

// Filtre la liste d'offres selon les critères saisis dans le panneau de filtres.
// `filtres` ressemble à :
// {
//   recherche: "python spark",        // mots-clés (titre + skills)
//   remote: ["Remote", "Partiel"],    // types de télétravail cochés
//   tjmMin: 500,                       // TJM minimum (number) ou null
//   xp: ["senior"],                    // niveaux d'expérience cochés
//   ville: "paris"                     // texte libre sur la ville
// }
export function filtrerOffres(offres, filtres) {
  const recherche = (filtres.recherche || "").trim().toLowerCase();
  const ville = (filtres.ville || "").trim().toLowerCase();

  return offres.filter((offre) => {
    // 1. Recherche par mots-clés : chaque mot doit apparaître dans le titre
    //    ou dans l'un des skills de l'offre.
    if (recherche) {
      const mots = recherche.split(/\s+/);
      const texte = (
        offre.titre +
        " " +
        offre.skills.join(" ") +
        " " +
        offre.entreprise
      ).toLowerCase();
      const tousLesMotsPresents = mots.every((mot) => texte.includes(mot));
      if (!tousLesMotsPresents) return false;
    }

    // 2. Télétravail : si des cases sont cochées, l'offre doit en faire partie.
    if (filtres.remote && filtres.remote.length > 0) {
      if (!filtres.remote.includes(offre.remote)) return false;
    }

    // 3. TJM minimum : on compare au TJM max de l'offre (la borne haute).
    //    Les offres sans TJM (null) sont exclues dès qu'un minimum est demandé.
    if (filtres.tjmMin) {
      if (offre.tjmMax == null) return false;
      if (offre.tjmMax < filtres.tjmMin) return false;
    }

    // 4. Expérience : même logique que le télétravail.
    if (filtres.xp && filtres.xp.length > 0) {
      if (!filtres.xp.includes(offre.xp)) return false;
    }

    // 5. Ville : recherche partielle insensible à la casse.
    if (ville) {
      if (!offre.ville.toLowerCase().includes(ville)) return false;
    }

    return true;
  });
}

// Trie les offres sur une colonne donnée, dans l'ordre asc ou desc.
// On renvoie une copie pour ne pas modifier le tableau d'origine.
export function trierOffres(offres, colonne, direction) {
  const copie = [...offres];

  copie.sort((a, b) => {
    let valeurA = a[colonne];
    let valeurB = b[colonne];

    // Cas particulier du TJM : on trie sur le TJM max, null en dernier.
    if (colonne === "tjm") {
      valeurA = a.tjmMax ?? -1;
      valeurB = b.tjmMax ?? -1;
    }

    // Les skills sont un tableau : on trie sur le nombre de skills.
    if (colonne === "skills") {
      valeurA = a.skills.length;
      valeurB = b.skills.length;
    }

    if (valeurA < valeurB) return direction === "asc" ? -1 : 1;
    if (valeurA > valeurB) return direction === "asc" ? 1 : -1;
    return 0;
  });

  return copie;
}

// Agrégation 1 : nombre d'offres publiées par jour.
// Renvoie un tableau trié par date : [{ date: "2026-06-01", count: 3 }, ...]
export function offresParJour(offres) {
  const compteur = {};
  for (const offre of offres) {
    compteur[offre.datePublication] = (compteur[offre.datePublication] || 0) + 1;
  }
  return Object.entries(compteur)
    .map(([date, count]) => ({ date, count }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

// Agrégation 2 : top N des skills les plus demandés.
// Renvoie [{ skill: "Python", count: 12 }, ...] limité à `limite` éléments.
export function topSkills(offres, limite = 10) {
  const compteur = {};
  for (const offre of offres) {
    for (const skill of offre.skills) {
      compteur[skill] = (compteur[skill] || 0) + 1;
    }
  }
  return Object.entries(compteur)
    .map(([skill, count]) => ({ skill, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limite);
}

// Agrégation 3 : TJM moyen par niveau d'expérience.
// On moyenne le centre de la fourchette [(tjmMin + tjmMax) / 2] des offres
// qui ont un TJM renseigné. Renvoie les 4 niveaux dans l'ordre logique.
export function tjmMoyenParXp(offres) {
  const niveaux = ["junior", "intermediate", "senior", "expert"];
  const labels = {
    junior: "Junior",
    intermediate: "Intermediate",
    senior: "Senior",
    expert: "Expert",
  };

  return niveaux.map((niveau) => {
    const offresNiveau = offres.filter(
      (o) => o.xp === niveau && o.tjmMin != null && o.tjmMax != null
    );
    let moyenne = 0;
    if (offresNiveau.length > 0) {
      const somme = offresNiveau.reduce(
        (acc, o) => acc + (o.tjmMin + o.tjmMax) / 2,
        0
      );
      moyenne = Math.round(somme / offresNiveau.length);
    }
    return { xp: labels[niveau], tjm: moyenne };
  });
}

// Formate l'affichage du TJM dans le tableau.
export function formaterTjm(offre) {
  if (offre.tjmMin == null || offre.tjmMax == null) return "Non précisé";
  return `${offre.tjmMin} - ${offre.tjmMax} €`;
}
