import db from "./lib/db.js";

const profiles = ["giỏi", "khá", "trung bình", "yếu"];

function seed() {
    const insert = db.prepare("INSERT OR REPLACE INTO students (id, class, profile, research_group) VALUES (?, ?, ?, ?)");
    
    console.log("Seeding 60 students...");
    
    for (let i = 1; i <= 60; i++) {
        const id = `HS${String(i).padStart(2, '0')}`;
        // Phân bổ mẫu: 30 Experimental, 30 Control
        const group = i <= 30 ? "Experimental" : "Control";
        // Phân bổ profile ngẫu nhiên hoặc theo quy luật
        const profile = profiles[i % profiles.length];
        const className = i <= 30 ? "11A1" : "11A2";
        
        insert.run(id, className, profile, group);
    }
    
    console.log("Done seeding.");
}

seed();
