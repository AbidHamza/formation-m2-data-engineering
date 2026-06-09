// Petite ligne qui affiche le nombre total d'offres correspondant aux filtres.
export default function Compteur({ total }) {
  return (
    <p className="text-sm text-slate-600">
      Nombre total d&apos;offres :{" "}
      <span className="font-semibold text-indigo-600">{total}</span>
    </p>
  );
}
