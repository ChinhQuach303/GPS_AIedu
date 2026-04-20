import { NextResponse } from "next/server";
import db from "@/lib/db";

export async function GET() {
  const profiles = ["giỏi", "khá", "trung bình", "yếu"];
  const insert = db.prepare("INSERT OR REPLACE INTO students (id, class, profile, research_group) VALUES (?, ?, ?, ?)");

  try {
    const transactions = db.transaction(() => {
      for (let i = 1; i <= 60; i++) {
        const id = `HS${String(i).padStart(2, '0')}`;
        const group = i <= 30 ? "Experimental" : "Control";
        const profile = profiles[i % profiles.length];
        const className = i <= 30 ? "11A1" : "11A2";
        insert.run(id, className, profile, group);
      }
    });
    
    transactions();

    return NextResponse.json({ ok: true, message: "Seeded 60 students successfully." });
  } catch (error) {
    return NextResponse.json({ ok: false, error: String(error) }, { status: 500 });
  }
}
