import Database from "better-sqlite3";
import { join } from "path";

const dbPath = join(process.cwd(), "gps_aiedu.sqlite");
const db = new Database(dbPath);

// Khởi tạo cấu trúc bảng
db.exec(`
  CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    class TEXT,
    profile TEXT,
    research_group TEXT -- 'Experimental' | 'Control'
  );

  CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    student_id TEXT,
    role TEXT, -- 'user' | 'assistant'
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    gps_step TEXT, -- 'G' | 'P' | 'S'
    message_id TEXT -- UUID from client/server
  );

  CREATE TABLE IF NOT EXISTS ratings (
    message_id TEXT PRIMARY KEY,
    satisfaction INTEGER,
    difficulty INTEGER
  );
`);

export default db;
