import argparse
import csv
import hashlib
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


TZ_VN = timezone(timedelta(hours=7))


def _normalize_for_match(text: str) -> str:
    if text is None:
        return ""
    t = str(text).lower().strip()
    # Minimal Vietnamese normalization without external deps:
    # - Replace "đ" first, then remove common combining marks via unicode decomposition.
    # Python's stdlib can do NFD via unicodedata.
    import unicodedata

    t = t.replace("đ", "d")
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = " ".join(t.split())
    return t


def classify_gps_step(question_text: str) -> str:
    q = _normalize_for_match(question_text)

    # Guide
    guide_keywords = (
        "giai thich",
        "khai niem",
        "cong thuc",
        "la gi",
        "tai sao",
        "dinh nghia",
        "phan biet",
        "tom tat",
    )
    if any(k in q for k in guide_keywords):
        return "G"

    # Practice
    practice_keywords = (
        "huong dan",
        "goi y",
        "buoc",
        "em bi ket",
        "lam the nao",
        "sai o dau",
        "kiem tra buoc",
    )
    if any(k in q for k in practice_keywords):
        return "P"

    # Solve / verify / off-protocol
    solve_keywords = (
        "dap an",
        "ket qua",
        "dung khong",
        "xong chua",
        "kiem tra loi giai",
        "giai giup",
        "ra ket qua",
        "ra dap an",
    )
    if any(k in q for k in solve_keywords):
        return "S"

    return "Unknown"


def salted_sha256_hex(salt: str, student_id: str) -> str:
    h = hashlib.sha256()
    h.update((salt + student_id).encode("utf-8"))
    return h.hexdigest()


def weighted_pick(rng: random.Random, choices: list[tuple[str, int]]) -> str:
    total = sum(w for _, w in choices)
    r = rng.randint(1, total)
    acc = 0
    for v, w in choices:
        acc += w
        if r <= acc:
            return v
    return choices[-1][0]


@dataclass(frozen=True)
class StudentProfile:
    student_id: str
    profile: str  # advanced|typical|struggling|offtrack
    speed: str  # fast|normal|slow
    clazz: str


TOPICS = [
    {
        "topic": "Hoán vị",
        "G": "Giải thích hoán vị là gì?",
        "P": "Hướng dẫn từng bước tính hoán vị n!",
        "S": "Em ra kết quả 120, đúng không?",
    },
    {
        "topic": "Chỉnh hợp",
        "G": "Phân biệt chỉnh hợp và tổ hợp giúp em.",
        "P": "Em bị kẹt ở bước chọn k từ n, gợi ý giúp.",
        "S": "Kiểm tra lời giải của em với A(n,k) được không?",
    },
    {
        "topic": "Tổ hợp",
        "G": "Diễn giải công thức C(n,k) theo cách dễ hiểu.",
        "P": "Hướng dẫn em từng bước giải bài chọn 3 từ 10.",
        "S": "C(5,2)=10 đúng không ạ?",
    },
    {
        "topic": "Xác suất",
        "G": "Xác suất là gì và công thức cơ bản?",
        "P": "Gợi ý cách lập không gian mẫu cho bài này.",
        "S": "Em ra P=0.5, đúng không?",
    },
    {
        "topic": "Xác suất có điều kiện",
        "G": "Giải thích xác suất có điều kiện là gì.",
        "P": "Hướng dẫn em tính P(A|B) theo từng bước.",
        "S": "Kết quả cuối cùng của em hợp lý chưa?",
    },
]


AI_RESPONSES = {
    "G": [
        "Mình giải thích khái niệm và ý nghĩa trước nhé, rồi em thử áp dụng vào ví dụ.",
        "Ta nắm định nghĩa và công thức tổng quát, sau đó xác định n và k trong đề.",
    ],
    "P": [
        "Mình chia thành 3 bước: (1) xác định n,k (2) chọn công thức (3) thay số và tính. Em làm bước (1) trước nhé.",
        "Em thử viết không gian mẫu/đếm số cách trước. Nếu kẹt ở bước nào nói mình biết.",
    ],
    "S": [
        "Mình sẽ kiểm tra logic và tính toán của em. Em ghi rõ lập luận và phép tính giúp mình.",
        "Mình không giải hộ, nhưng có thể đối chiếu kết quả và chỉ ra chỗ sai nếu có.",
    ],
}


def generate_students(rng: random.Random, count: int) -> list[StudentProfile]:
    students: list[StudentProfile] = []
    for i in range(1, count + 1):
        student_id = f"HS{str(i).zfill(4)}"
        profile = weighted_pick(
            rng,
            [
                ("advanced", 10),
                ("typical", 75),
                ("struggling", 10),
                ("offtrack", 5),
            ],
        )
        speed = weighted_pick(rng, [("fast", 30), ("normal", 55), ("slow", 15)])
        clazz = rng.choice(["11A1", "11A2", "11A3"])
        students.append(StudentProfile(student_id=student_id, profile=profile, speed=speed, clazz=clazz))
    return students


def pick_question(rng: random.Random, topic: dict, profile: str, truth_step: str) -> str:
    if profile == "offtrack" and truth_step == "S":
        return rng.choice(
            [
                "Giải giúp em bài này với ạ.",
                "Cho em đáp án cuối cùng luôn được không?",
                "Em cần kết quả nhanh, cho em đáp án.",
            ]
        )
    return topic[truth_step]


def pick_session_count(rng: random.Random, profile: str) -> int:
    if profile == "advanced":
        return rng.randint(2, 5)
    if profile == "typical":
        return rng.randint(3, 8)
    if profile == "struggling":
        return rng.randint(4, 10)
    return rng.randint(1, 4)


def pick_day_offset(rng: random.Random, profile: str, day_count: int) -> int:
    # Make a small group stop early to exercise inactivity checks.
    if profile == "offtrack":
        return rng.randint(0, min(day_count - 1, 2))
    if profile == "struggling":
        return rng.randint(0, min(day_count - 1, 4))
    return rng.randint(0, day_count - 1)


def pick_step_sequence(rng: random.Random, profile: str) -> list[str]:
    if profile == "advanced":
        return weighted_pick(
            rng,
            [
                ("P,S", 50),
                ("S", 30),
                ("G,S", 20),
            ],
        ).split(",")
    if profile == "typical":
        return weighted_pick(
            rng,
            [
                ("G,P,S", 70),
                ("G,P,P,S", 25),
                ("G,P", 5),
            ],
        ).split(",")
    if profile == "struggling":
        return weighted_pick(
            rng,
            [
                ("G,P,P", 55),
                ("G,P,P,S", 20),
                ("G,P", 25),
            ],
        ).split(",")
    return weighted_pick(
        rng,
        [
            ("S", 70),
            ("S,S", 25),
            ("G,S", 5),
        ],
    ).split(",")


def gap_minutes(rng: random.Random, speed: str) -> int:
    if speed == "fast":
        return rng.randint(1, 4)
    if speed == "slow":
        return rng.randint(10, 25)
    return rng.randint(4, 12)


def pick_session_start(rng: random.Random, start: datetime, day_offset: int) -> datetime:
    minute_of_day = rng.randint(8 * 60, 21 * 60)
    return start + timedelta(days=day_offset, minutes=minute_of_day)


def pick_satisfaction_step(rng: random.Random, profile: str, step: str) -> int:
    if profile == "advanced":
        return rng.randint(4, 5)
    if profile == "typical":
        return rng.randint(4, 5) if step == "S" else rng.randint(3, 5)
    if profile == "struggling":
        return rng.randint(3, 5) if step == "S" else rng.randint(2, 4)
    return rng.randint(1, 3)


def pick_difficulty_step(rng: random.Random, profile: str, step: str) -> int:
    if profile == "advanced":
        return rng.randint(1, 3)
    if profile == "typical":
        return rng.randint(2, 4)
    if profile == "struggling":
        return rng.randint(3, 5)
    return rng.randint(4, 5)


def generate_logs(
    rng: random.Random,
    students: list[StudentProfile],
    start: datetime,
    end: datetime,
    total_logs: int,
    salt: str,
) -> list[dict]:
    logs: list[dict] = []
    if not students or total_logs <= 0:
        return logs

    day_count = max(1, int((end - start).total_seconds() // (24 * 3600)) + 1)

    def add_log(student: StudentProfile, topic: dict, ts: datetime, step: str, question_text: str) -> None:
        logs.append(
            {
                "submission_id": str(uuid.uuid4()),
                "student_id": student.student_id,
                "student_id_hash": salted_sha256_hex(salt, student.student_id),
                "timestamp": ts.isoformat(),
                "gps_step": step,
                "question_text": question_text,
                "ai_response": rng.choice(AI_RESPONSES[step]),
                "topic": topic["topic"],
                "satisfaction": pick_satisfaction_step(rng, student.profile, step),
                "difficulty": pick_difficulty_step(rng, student.profile, step),
                "notes": f"profile={student.profile};speed={student.speed};class={student.clazz}",
            }
        )

    for student in students:
        sessions = pick_session_count(rng, student.profile)
        for _ in range(sessions):
            day_offset = pick_day_offset(rng, student.profile, day_count)
            session_start = pick_session_start(rng, start, day_offset)
            topic = rng.choice(TOPICS)
            seq = pick_step_sequence(rng, student.profile)

            ts = session_start
            for i, step in enumerate(seq):
                if i > 0:
                    ts = ts + timedelta(minutes=gap_minutes(rng, student.speed))
                # Ensure keywords for robust labeling (esp. repeated P steps)
                if step == "P" and i > 0:
                    question_text = rng.choice([topic["P"], "Gợi ý bước 2 giúp em với.", "Em bị kẹt ở bước này, hướng dẫn em."])
                else:
                    question_text = pick_question(rng, topic, student.profile, step)
                add_log(student, topic, ts, step, question_text)

    logs.sort(key=lambda r: r["timestamp"])
    if len(logs) > total_logs:
        return logs[:total_logs]

    # Top up if needed (rare when students/sessions are small)
    while len(logs) < total_logs:
        student = rng.choice(students)
        day_offset = pick_day_offset(rng, student.profile, day_count)
        session_start = pick_session_start(rng, start, day_offset)
        topic = rng.choice(TOPICS)
        seq = pick_step_sequence(rng, student.profile)

        ts = session_start
        for i, step in enumerate(seq):
            if len(logs) >= total_logs:
                break
            if i > 0:
                ts = ts + timedelta(minutes=gap_minutes(rng, student.speed))
            question_text = pick_question(rng, topic, student.profile, step)
            add_log(student, topic, ts, step, question_text)

    logs.sort(key=lambda r: r["timestamp"])
    return logs


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate realistic Week 1 mock logs (GPS).")
    parser.add_argument("--students", type=int, default=90)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--logs", type=int, default=900)
    parser.add_argument("--salt", type=str, default="GPS_AI_MATH_2026")
    parser.add_argument("--seed", type=int, default=20260313)
    parser.add_argument("--out", type=Path, default=Path("data/raw/mock_week1_realistic.csv"))
    args = parser.parse_args()

    rng = random.Random(args.seed)
    now = datetime.now(TZ_VN)
    start = now - timedelta(days=max(args.days - 1, 0))
    end = now

    students = generate_students(rng, args.students)
    logs = generate_logs(rng, students, start, end, args.logs, args.salt)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "submission_id",
        "student_id",
        "student_id_hash",
        "timestamp",
        "gps_step",
        "question_text",
        "ai_response",
        "topic",
        "satisfaction",
        "difficulty",
        "notes",
    ]

    with args.out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(logs)

    print(f"Wrote {len(logs)} logs to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
