"use client";

import { useState, useMemo } from "react";
import { trierOffres, formaterTjm } from "@/lib/offres";

// Définition des colonnes du tableau.
// `cle` sert à la fois pour l'affichage et pour le tri.
// `triable: false` = on n'autorise pas le tri sur cette colonne.
const COLONNES = [
  { cle: "datePublication", label: "Publication", triable: true },
  { cle: "titre", label: "Titre", triable: true },
  { cle: "tjm", label: "TJM", triable: true },
  { cle: "remote", label: "Remote", triable: true },
  { cle: "duree", label: "Durée", triable: true },
  { cle: "xp", label: "Xp", triable: true },
  { cle: "skills", label: "Skills", triable: false },
  { cle: "entreprise", label: "Entreprise", triable: true },
  { cle: "ville", label: "Ville", triable: true },
  { cle: "action", label: "", triable: false },
];

const OPTIONS_LIGNES = [10, 15, 20, 25];

export default function TableauOffres({ offres }) {
  // État du tri : sur quelle colonne et dans quel sens.
  const [tri, setTri] = useState({ colonne: "datePublication", direction: "desc" });
  // État de la pagination.
  const [lignesParPage, setLignesParPage] = useState(10);
  const [page, setPage] = useState(0); // page courante, indexée à partir de 0

  // On trie les offres à chaque changement de tri ou de données.
  // useMemo évite de retrier inutilement à chaque rendu.
  const offresTriees = useMemo(
    () => trierOffres(offres, tri.colonne, tri.direction),
    [offres, tri]
  );

  const total = offresTriees.length;
  const nbPages = Math.max(1, Math.ceil(total / lignesParPage));
  // On borne la page courante (utile si un filtre réduit le nombre de résultats).
  const pageSure = Math.min(page, nbPages - 1);
  const debut = pageSure * lignesParPage;
  const offresPage = offresTriees.slice(debut, debut + lignesParPage);

  // Clic sur un en-tête : on bascule le sens si c'est la même colonne,
  // sinon on trie la nouvelle colonne en ascendant.
  function trierPar(colonne) {
    setPage(0);
    setTri((ancien) => {
      if (ancien.colonne === colonne) {
        return {
          colonne,
          direction: ancien.direction === "asc" ? "desc" : "asc",
        };
      }
      return { colonne, direction: "asc" };
    });
  }

  // Indicateur ▲ / ▼ affiché à côté du titre de la colonne triée.
  function indicateur(colonne) {
    if (tri.colonne !== colonne) return "";
    return tri.direction === "asc" ? " ▲" : " ▼";
  }

  // Bornes affichées dans "1-10 of N".
  const borneBas = total === 0 ? 0 : debut + 1;
  const borneHaut = Math.min(debut + lignesParPage, total);

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-6 py-4">
        <h2 className="text-base font-semibold text-indigo-600">
          Offres ({total})
        </h2>
      </div>

      {/* Le conteneur scrolle horizontalement sur petit écran. */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              {COLONNES.map((col) => (
                <th
                  key={col.cle}
                  scope="col"
                  className={`px-4 py-3 font-medium text-slate-600 ${
                    col.triable ? "cursor-pointer select-none hover:text-indigo-600" : ""
                  }`}
                  onClick={col.triable ? () => trierPar(col.cle) : undefined}
                >
                  {col.label}
                  <span className="text-indigo-600">{indicateur(col.cle)}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {offresPage.map((offre) => (
              <tr
                key={offre.id}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
              >
                <td className="whitespace-nowrap px-4 py-3 text-slate-500">
                  {offre.datePublication}
                </td>
                <td className="px-4 py-3 font-medium text-slate-800">
                  {offre.titre}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                  {formaterTjm(offre)}
                </td>
                <td className="px-4 py-3 text-slate-600">{offre.remote}</td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                  {offre.duree}
                </td>
                <td className="px-4 py-3 capitalize text-slate-600">{offre.xp}</td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {offre.skills.map((skill) => (
                      <span
                        key={skill}
                        className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                  {offre.entreprise}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                  {offre.ville}
                </td>
                <td className="px-4 py-3">
                  {/* Lien d'action. Ici sans destination réelle (corrigé) ;
                      à brancher plus tard sur une page de détail. */}
                  <a
                    href="#"
                    className="font-medium text-indigo-600 hover:text-indigo-800 hover:underline"
                  >
                    Voir
                  </a>
                </td>
              </tr>
            ))}

            {offresPage.length === 0 && (
              <tr>
                <td
                  colSpan={COLONNES.length}
                  className="px-4 py-10 text-center text-slate-400"
                >
                  Aucune offre ne correspond aux filtres.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Barre de pagination */}
      <div className="flex flex-col items-center justify-between gap-3 border-t border-slate-200 px-6 py-4 sm:flex-row">
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <label htmlFor="lignesParPage">Lignes par page</label>
          <select
            id="lignesParPage"
            value={lignesParPage}
            onChange={(e) => {
              setLignesParPage(Number(e.target.value));
              setPage(0);
            }}
            className="rounded-lg border border-slate-300 px-2 py-1 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {OPTIONS_LIGNES.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-4 text-sm text-slate-600">
          <span>
            {borneBas}-{borneHaut} of {total}
          </span>
          <div className="flex gap-1">
            <BoutonPagination
              label="«"
              titre="Première page"
              disabled={pageSure === 0}
              onClick={() => setPage(0)}
            />
            <BoutonPagination
              label="‹"
              titre="Page précédente"
              disabled={pageSure === 0}
              onClick={() => setPage(pageSure - 1)}
            />
            <BoutonPagination
              label="›"
              titre="Page suivante"
              disabled={pageSure >= nbPages - 1}
              onClick={() => setPage(pageSure + 1)}
            />
            <BoutonPagination
              label="»"
              titre="Dernière page"
              disabled={pageSure >= nbPages - 1}
              onClick={() => setPage(nbPages - 1)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// Petit bouton réutilisable pour la pagination.
function BoutonPagination({ label, titre, disabled, onClick }) {
  return (
    <button
      type="button"
      title={titre}
      aria-label={titre}
      disabled={disabled}
      onClick={onClick}
      className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
    >
      {label}
    </button>
  );
}
