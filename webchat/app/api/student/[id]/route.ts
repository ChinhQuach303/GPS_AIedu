import { NextResponse } from "next/server";
import db from "@/lib/db";

export async function GET(
  req: Request,
  { params }: { params: { id: string } }
) {
  const { id } = params;
  try {
    const student = db.prepare("SELECT * FROM students WHERE id = ?").get(id) as any;
    if (!student) {
      return NextResponse.json({ ok: false, error: "Student not found" }, { status: 404 });
    }
    
    // Đồng thời lấy lịch sử chat cũ nếu có
    const history = db.prepare("SELECT role, content, message_id as messageId FROM messages WHERE student_id = ? ORDER BY timestamp ASC").all(id);

    return NextResponse.json({ 
      ok: true, 
      student: {
        studentId: student.id,
        className: student.class,
        profile: student.profile,
        group: student.research_group
      },
      history
    });
  } catch (error) {
    return NextResponse.json({ ok: false, error: String(error) }, { status: 500 });
  }
}
