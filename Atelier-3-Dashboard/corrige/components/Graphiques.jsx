"use client";

import { useMemo } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { offresParJour, topSkills, tjmMoyenParXp } from "@/lib/offres";

const INDIGO = "#4f46e5"; // indigo-600, couleur d'accent du dashboard

// Carte enveloppe pour homogénéiser les trois graphiques.
function CarteGraphique({ titre, children }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-indigo-600">{titre}</h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function Graphiques({ offres }) {
  // Les trois agrégations se recalculent uniquement quand les offres filtrées
  // changent. useMemo évite de recalculer à chaque rendu inutile.
  const donneesJour = useMemo(() => offresParJour(offres), [offres]);
  const donneesSkills = useMemo(() => topSkills(offres, 10), [offres]);
  const donneesTjm = useMemo(() => tjmMoyenParXp(offres), [offres]);

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      {/* 1. Offres publiées par jour */}
      <CarteGraphique titre="Nombre d'offres par jour">
        <AreaChart data={donneesJour} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="gradJour" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={INDIGO} stopOpacity={0.3} />
              <stop offset="100%" stopColor={INDIGO} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#64748b" }}
            tickFormatter={(d) => d.slice(5)} // on n'affiche que MM-DD
          />
          <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#64748b" }} />
          <Tooltip />
          <Area
            type="monotone"
            dataKey="count"
            name="Offres"
            stroke={INDIGO}
            strokeWidth={2}
            fill="url(#gradJour)"
          />
        </AreaChart>
      </CarteGraphique>

      {/* 2. Top 10 des technos demandées (barres horizontales) */}
      <CarteGraphique titre="Top 10 des technos demandées">
        <BarChart
          data={donneesSkills}
          layout="vertical"
          margin={{ top: 5, right: 10, left: 10, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
          <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11, fill: "#64748b" }} />
          <YAxis
            type="category"
            dataKey="skill"
            width={80}
            tick={{ fontSize: 11, fill: "#64748b" }}
          />
          <Tooltip cursor={{ fill: "#f1f5f9" }} />
          <Bar dataKey="count" name="Offres" fill={INDIGO} radius={[0, 4, 4, 0]} />
        </BarChart>
      </CarteGraphique>

      {/* 3. TJM moyen par niveau d'expérience */}
      <CarteGraphique titre="TJM moyen par niveau d'expérience">
        <BarChart data={donneesTjm} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="xp" tick={{ fontSize: 11, fill: "#64748b" }} />
          <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
          <Tooltip cursor={{ fill: "#f1f5f9" }} formatter={(v) => `${v} €`} />
          <Bar dataKey="tjm" name="TJM moyen" fill={INDIGO} radius={[4, 4, 0, 0]} />
        </BarChart>
      </CarteGraphique>
    </div>
  );
}
