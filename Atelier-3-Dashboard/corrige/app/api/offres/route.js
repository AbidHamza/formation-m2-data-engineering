import { NextResponse } from "next/server";
import offres from "@/data/offres.sample.json";

// Route API qui renvoie les offres.
// Pour l'instant on lit un fichier JSON local (corrigé pédagogique).
// À remplacer plus tard par une requête Supabase ou l'API France Travail
// récupérée pendant l'atelier 1.
export async function GET() {
  return NextResponse.json(offres);
}
