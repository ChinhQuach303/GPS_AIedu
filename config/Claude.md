# Claude.md — Hướng dẫn cho AI Assistant (Dự án HanoiWaterDemand)

Chào mừng bạn đến với dự án **Hanoi Water Demand Forecast System**. Đây là hệ thống dự báo nhu cầu nước vận hành cho Hà Nội, sử dụng Machine Learning và LLM Tool Calling.

## 1. Kiến trúc Hệ thống (Medallion Architecture)

Hệ thống sử dụng PostgreSQL với mô hình Medallion:
- **Bronze**: Dữ liệu thô từ các nguồn (scraped weather, raw demand).
- **Silver**: Dữ liệu đã làm sạch, chuẩn hóa (`silver.stg_water_demand`, `silver.stg_weather`).
- **Gold**: Dữ liệu phục vụ báo cáo và dự báo (`gold.fct_predictions`, `gold.dim_dma`).

## 2. Công nghệ Core

- **Backend**: FastAPI (Python 3.10+).
- **Database**: PostgreSQL + SQLAlchemy + `psycopg2` (cho bulk COPY tasks).
- **Forecasting**: Scikit-learn (Hybrid Model: Gradient Boosting + Safety Layer).
- **LLM Layer**: OpenAI/Claude API thông qua `llm_provider`.
- **Orchestration**: `ToolOrchestrator` điều phối vòng lặp gọi Tool (SQL, Forecast, Plot).
- **Routing (v6.5)**: `IntentRouter` phân loại query trước khi vào LLM để tối ưu latency (Direct API vs LLM).

## 3. Quy định Cấu trúc Code

- **src/domain**: Chứa logic nghiệp vụ lõi (Interfaces, Forecasting Models).
- **src/infrastructure**: Chứa repo, database connection, external adapters.
- **src/application**: Chứa các services điều phối (ShortTermService, FeatureService).
- **src/api**: Chứa FastAPI server, routers, schemas, dependencies.
- **tests**: Chia rõ `unit`, `integration`, và `eval` (LLM evaluation).

## 4. Hướng dẫn Phát triển cho AI

### 4.1. SQL Guardrails
Khi viết hoặc sửa code liên quan đến SQL execution:
- Luôn sử dụng `SQLGuardrail` để validate query (chỉ cho phép `SELECT`).
- Luôn giới hạn `LIMIT 500` và `statement_timeout`.
- Không bao giờ để LLM sinh query xóa hoặc sửa dữ liệu.

### 4.2. Tool Calling
- **Tool Definition**: Định nghĩa trong `src/api/server/tools/definitions.py`.
- **Tool Implementation**: Nằm trong `src/api/server/tools/executors/`.
- **Forecasting Horizon**: Hệ thống hỗ trợ linh hoạt dựa trên tham số `months` (1-12). Tuy hiện tại mô hình long-term tối ưu cho 3 tháng (Next Quarter), cấu trúc code đã cho phép mở rộng khi có model mới.
- **Priority**: Query có intent rõ ràng (VD: "Dự báo DMA X") phải được route qua Direct API thay vì LLM.

### 4.3. Formatting & Returns
- API response phải tuân thủ `APIResponse` schema.
- Dữ liệu trả về cho Chat phải kèm `audit_id`.
- Sử dụng Markdown Table cho dữ liệu danh sách trong response của LLM.

## 5. Các file quan trọng cần lưu ý
- `src/api/server/app.py`: Entry point của API.
- `src/api/server/routers/chat.py`: Logic routing và chat chính.
- `src/api/server/routing/intent_router.py`: Quyết định route query.
- `implementation_plan.md`: Kế hoạch triển khai các phase.
- `review.md`: Review tổng thể project.

---
**Version hiện tại**: 6.5.0-dev
**Reviewer**: Antigravity Agent
