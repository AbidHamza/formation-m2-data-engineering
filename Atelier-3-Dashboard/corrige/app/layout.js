import "./globals.css";

export const metadata = {
  title: "Dashboard Data Engineer IDF",
  description:
    "Tableau de bord des offres Data Engineer en Île-de-France (corrigé formation M2).",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body className="bg-slate-50 text-slate-800 antialiased">{children}</body>
    </html>
  );
}
