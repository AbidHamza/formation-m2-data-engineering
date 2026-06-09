"use client";

import { useState, useEffect, useMemo } from "react";
import Filtres from "@/components/Filtres";
import Compteur from "@/components/Compteur";
import TableauOffres from "@/components/TableauOffres";
import Graphiques from "@/components/Graphiques";
import { filtrerOffres } from "@/lib/offres";

// État initial des filtres. Tout est vide / décoché au démarrage.
const FILTRES_INITIAUX = {
  recherche: "",
  remote: [],
  tjmMin: "",
  xp: [],
  ville: "",
};

export default function Page() {
  const [offres, setOffres] = useState([]);
  const [chargement, setChargement] = useState(true);
  const [filtres, setFiltres] = useState(FILTRES_INITIAUX);

  // Au montage, on récupère les offres depuis la route API.
  useEffect(() => {
    fetch("/api/offres")
      .then((res) => res.json())
      .then((data) => setOffres(data))
      .catch(() => setOffres([]))
      .finally(() => setChargement(false));
  }, []);

  // Filtrage live : recalculé dès qu'un filtre ou les données changent.
  // tjmMin arrive en texte depuis l'input, on le convertit en nombre ici.
  const offresFiltrees = useMemo(() => {
    return filtrerOffres(offres, {
      ...filtres,
      tjmMin: filtres.tjmMin ? Number(filtres.tjmMin) : null,
    });
  }, [offres, filtres]);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* En-tête : titre + barre de recherche */}
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">
          Dashboard Data Engineer IDF
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Offres freelance Data en Île-de-France
        </p>

        <div className="mt-4">
          <input
            type="text"
            placeholder="Python, Spark, Airflow..."
            value={filtres.recherche}
            onChange={(e) =>
              setFiltres({ ...filtres, recherche: e.target.value })
            }
            className="w-full max-w-xl rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            aria-label="Recherche par mots-clés"
          />
        </div>
      </header>

      {/* Compteur */}
      <div className="mb-4">
        <Compteur total={offresFiltrees.length} />
      </div>

      {/* Panneau de filtres */}
      <div className="mb-6">
        <Filtres filtres={filtres} setFiltres={setFiltres} />
      </div>

      {chargement ? (
        <p className="py-20 text-center text-slate-400">Chargement des offres...</p>
      ) : (
        <div className="space-y-6">
          {/* Graphiques réactifs aux filtres */}
          <Graphiques offres={offresFiltrees} />

          {/* Tableau des offres */}
          <TableauOffres offres={offresFiltrees} />

          {/* Emplacement carte (bonus de l'atelier) */}
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
            <p className="text-sm font-medium text-slate-500">Carte (bonus)</p>
            <p className="mt-1 text-xs text-slate-400">
              À implémenter avec react-leaflet en dynamic import (ssr: false)
              pendant l&apos;atelier.
            </p>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-10 border-t border-slate-200 pt-6 text-center text-xs text-slate-400">
        Corrigé formation M2 Data Engineering
      </footer>
    </main>
  );
}
