import subprocess
import datetime
import time
import os

LOG_FILE = "research_pipeline.log"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_message + "\n")
        f.flush()

def run_step(name, command):
    log(f"🚀 BẮT ĐẦU: {name}")
    log(f"Lệnh chạy: {command}")
    
    # Thiết lập môi trường không buffer cho các script con
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    start_time = time.time()
    try:
        # Chạy lệnh và ghi log trực tiếp
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            bufsize=1 # Line buffered
        )
        
        for line in process.stdout:
            # Ghi log chi tiết vào file log để user theo dõi
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"  > {line}")
                f.flush()
            # print(f"  > {line}", end="", flush=True)
            
        process.wait()
        elapsed = time.time() - start_time
        
        if process.returncode == 0:
            log(f"✅ HOÀN THÀNH: {name} (Thời gian: {elapsed:.2f}s)")
            return True
        else:
            log(f"❌ THẤT BẠI: {name} (Mã lỗi: {process.returncode})")
            return False
            
    except Exception as e:
        log(f"💥 LỖI HỆ THỐNG khi chạy {name}: {e}")
        return False

def main():
    # Đảm bảo PYTHONPATH được thiết lập đúng
    os.environ["PYTHONPATH"] = os.getcwd()
    
    # Xóa log cũ nếu có
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    log("="*60)
    log("HỆ THỐNG ĐIỀU PHỐI NGHIÊN CỨU EMNLP 2026 - GPS-AIEDU")
    log("="*60)
    
    steps = [
        ("Simulation 1: GPS Multi-Agent (N=100)", "python3 scripts/run_massive_simulation.py"),
        ("Simulation 2: Single-Agent Baseline (N=100)", "python3 scripts/run_baseline_simulation.py"),
        ("Simulation 3: Cross-Model Validation (N=50)", "python3 scripts/run_cross_model_simulation.py"),
        ("Data Cleaning: Linguistic & Format Normalization", "python3 scripts/clean_data_pipeline.py"),
        ("Analytics 1: Failure Analysis (Filtering & Categorizing)", "python3 scripts/find_failures.py"),
        ("Analytics 2: Inter-Rater Reliability (Cohen's Kappa)", "python3 scripts/calculate_irr.py"),
        ("Final Report: Data Aggregation & Chart Rendering", "python3 scripts/generate_evaluation_report.py")
    ]
    
    total_start = time.time()
    
    for i, (name, cmd) in enumerate(steps):
        log(f"\n--- BƯỚC {i+1}/{len(steps)} ---")
        success = run_step(name, cmd)
        if not success:
            log("🛑 Dừng pipeline do có bước bị lỗi. Hãy kiểm tra log để biết thêm chi tiết.")
            break
            
    total_elapsed = time.time() - total_start
    log("\n" + "="*60)
    log(f"TOÀN BỘ PIPELINE ĐÃ HOÀN TẤT TRONG {total_elapsed/60:.2f} PHÚT.")
    log(f"Toàn bộ log chi tiết được lưu tại: {LOG_FILE}")
    log("="*60)

if __name__ == "__main__":
    main()
