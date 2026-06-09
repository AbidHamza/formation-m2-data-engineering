// Panneau de filtres. Composant "contrôlé" : il ne stocke rien lui-même,
// il reçoit l'état `filtres` et une fonction `setFiltres` depuis le parent
// (app/page.js). Toute modification remonte donc immédiatement au parent,
// qui réapplique le filtrage sur le tableau ET les graphiques.

const OPTIONS_REMOTE = ["Remote", "Partiel", "Présentiel"];

const OPTIONS_XP = [
  { valeur: "junior", label: "Junior" },
  { valeur: "intermediate", label: "Intermediate" },
  { valeur: "senior", label: "Senior" },
  { valeur: "expert", label: "Expert" },
];

export default function Filtres({ filtres, setFiltres }) {
  // Coche/décoche une valeur dans un filtre de type liste (remote ou xp).
  function toggleListe(champ, valeur) {
    const actuelle = filtres[champ];
    const nouvelle = actuelle.includes(valeur)
      ? actuelle.filter((v) => v !== valeur)
      : [...actuelle, valeur];
    setFiltres({ ...filtres, [champ]: nouvelle });
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-indigo-600">
        Filtres
      </h2>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* Télétravail */}
        <fieldset>
          <legend className="mb-2 text-sm font-medium text-slate-700">
            Télétravail
          </legend>
          <div className="space-y-1.5">
            {OPTIONS_REMOTE.map((option) => (
              <label
                key={option}
                className="flex cursor-pointer items-center gap-2 text-sm text-slate-600"
              >
                <input
                  type="checkbox"
                  checked={filtres.remote.includes(option)}
                  onChange={() => toggleListe("remote", option)}
                  className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                {option}
              </label>
            ))}
          </div>
        </fieldset>

        {/* TJM minimum */}
        <div>
          <label
            htmlFor="tjmMin"
            className="mb-2 block text-sm font-medium text-slate-700"
          >
            TJM minimum (€)
          </label>
          <input
            id="tjmMin"
            type="number"
            min="0"
            step="50"
            placeholder="ex : 500"
            value={filtres.tjmMin}
            onChange={(e) =>
              setFiltres({ ...filtres, tjmMin: e.target.value })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        {/* Expérience */}
        <fieldset>
          <legend className="mb-2 text-sm font-medium text-slate-700">
            Expérience
          </legend>
          <div className="space-y-1.5">
            {OPTIONS_XP.map((option) => (
              <label
                key={option.valeur}
                className="flex cursor-pointer items-center gap-2 text-sm text-slate-600"
              >
                <input
                  type="checkbox"
                  checked={filtres.xp.includes(option.valeur)}
                  onChange={() => toggleListe("xp", option.valeur)}
                  className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                {option.label}
              </label>
            ))}
          </div>
        </fieldset>

        {/* Localisation */}
        <div>
          <label
            htmlFor="ville"
            className="mb-2 block text-sm font-medium text-slate-700"
          >
            Localisation
          </label>
          <input
            id="ville"
            type="text"
            placeholder="Entrer une ville..."
            value={filtres.ville}
            onChange={(e) => setFiltres({ ...filtres, ville: e.target.value })}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>
    </div>
  );
}
