import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const csvPath = path.join(process.cwd(), '..', 'data', 'processed', 'simulated_conversations.csv');
    const progressPath = path.join(process.cwd(), '..', 'data', 'processed', 'simulation_progress.json');
    
    let completedCount = 0;
    if (fs.existsSync(progressPath)) {
      const progress = JSON.parse(fs.readFileSync(progressPath, 'utf8'));
      completedCount = progress.completed_qids?.length || 0;
    }

    if (!fs.existsSync(csvPath)) {
      return NextResponse.json({ 
        ok: false, 
        error: 'Data not found',
        stats: { completed: completedCount, totalRows: 0 }
      });
    }

    const content = fs.readFileSync(csvPath, 'utf8');
    const lines = content.split('\n');
    const totalRows = lines.length - 1;
    
    // Extract last 10 turns for the live feed
    const last10 = lines.slice(-11).reverse().map(line => {
      const parts = line.split(',');
      if (parts.length < 6) return null;
      return {
        timestamp: parts[0],
        studentId: parts[1],
        question: parts[2]?.replace(/^"|"$/g, ''),
        response: parts[3]?.replace(/^"|"$/g, ''),
        qid: parts[5],
        turn: parts[6]
      };
    }).filter(Boolean);

    return NextResponse.json({
      ok: true,
      stats: {
        completed: completedCount,
        totalRows: totalRows,
        avgTurns: (totalRows / (completedCount * 5 || 1)).toFixed(1)
      },
      recent: last10
    });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err) }, { status: 500 });
  }
}
