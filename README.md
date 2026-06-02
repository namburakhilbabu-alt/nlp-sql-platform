# DataMind — Enterprise AI Data Assistant (NLP-to-SQL Platform)

> Convert plain English business questions into optimized SQL queries across a large-scale enterprise database — powered by a local LLM, vector search, and graph-based schema reasoning.

---

## What It Does

Ask questions like a business user. Get SQL, results, and explanations instantly.

```
"Show unpaid invoices above 5 lakhs from last quarter"
         ↓
SELECT i.invoice_id, c.customer_name, i.total_amount ...
FROM invoices AS i JOIN customers AS c ON i.customer_id = c.customer_id
WHERE i.invoice_date >= date('now', '-3 months') AND i.total_amount > 500000 ...
         ↓
98 rows · "There are 98 unpaid invoices exceeding ₹5 lakhs. The largest is ₹14.81 lakhs from Customer Corp 9..."
```

---

## Architecture

```
User Question (plain English)
        │
        ▼
┌──────────────────────────────────────────────────────┐
│              Intent Router (Mistral 7B)              │
│         Classifies: DATA query vs CHAT message       │
└────────────┬─────────────────────────────────────────┘
             │ DATA                      │ CHAT
             ▼                           ▼
┌────────────────────┐       ┌─────────────────────┐
│  Semantic Cache    │       │  Conversational Reply│
│  ChromaDB cos≥0.92 │       │  (Mistral directly) │
└───────┬────────────┘       └─────────────────────┘
        │ MISS
        ▼
┌──────────────────────────────────────────────────────┐
│    Schema Retrieval — ChromaDB Vector Search         │
│    sentence-transformers finds top-5 relevant tables │
│    from 15 tables (architecture scales to 800+)      │
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│    Graph-Based Schema Reasoning — NetworkX           │
│    FK relationship graph → auto JOIN discovery       │
│    No hardcoded JOINs anywhere in the codebase       │
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│    Adaptive Prompt Builder                           │
│    Schema + JOIN hints + business glossary +         │
│    conversation history → custom prompt per query    │
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│    SQL Generation — Mistral 7B (Ollama, local)       │
│    Auto-retry up to 3× with correction prompt        │
│    Confidence score decreases per retry              │
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│    SQL Validation & Safety Layer                     │
│    Blocks: DROP / DELETE / INSERT / UPDATE / DDL     │
│    Strips markdown · auto-adds LIMIT · sqlparse check│
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│    Query Execution — SQLAlchemy → SQLite             │
│    15-table enterprise DB · 1000+ seeded rows        │
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│    Business Explanation — Mistral 7B                 │
│    Plain English summary for non-technical users     │
└───────────────────────┬──────────────────────────────┘
                        ▼
              JSON Response + Metrics + Cache Write
```

---

## Features

### Mandatory ✅
| Feature | Implementation |
|---|---|
| REST APIs | FastAPI — 9 endpoints, auto Swagger at `/docs` |
| Schema retrieval system | ChromaDB vector search, sentence-transformers |
| SQL generation | Mistral 7B via Ollama (local LLM) |
| SQL validation layer | Blocks all DDL/DML, verifies SELECT-only |
| Retry handling | 3 attempts with automatic correction prompt |
| Logging | Structured logs — console + `logs/app.log` |
| Error handling | HTTP 422/500 with descriptive messages |
| Modular architecture | 12 independent modules, clean separation |

### Strongly Preferred ✅
| Feature | Implementation |
|---|---|
| Multi-turn conversation | Session-ID based history, last 10 turns |
| Query explanation engine | Mistral generates plain English summaries |
| Business glossary mapping | lakhs, crores, last quarter, overdue — in every prompt |
| Query confidence scoring | Decreases per retry (1.0 → 0.85 → 0.70) |
| Semantic caching | ChromaDB cosine similarity ≥ 0.92 → instant return |

### Bonus ✅
| Feature | Implementation |
|---|---|
| Graph-based schema reasoning | NetworkX directed FK graph |
| Autonomous join discovery | Shortest-path traversal finds JOINs automatically |
| Adaptive prompt optimization | JOIN hints + glossary injected dynamically per query |
| Streaming responses | SSE endpoint — `POST /api/v1/query/stream` |
| Docker deployment | `Dockerfile` + `docker-compose.yml` included |
| Monitoring dashboard | `GET /api/v1/metrics` — live query stats |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · FastAPI · Uvicorn |
| Local LLM | Mistral 7B via Ollama |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Store | ChromaDB — schema index + semantic query cache |
| Schema Graph | NetworkX — FK relationship graph, auto JOIN discovery |
| Database | SQLite via SQLAlchemy ORM |
| Frontend | Vanilla HTML/CSS/JS — no framework |

---

## Database Schema

15 interconnected enterprise tables across 5 business domains:

| Domain | Tables |
|---|---|
| Finance | `invoices`, `invoice_items`, `payments`, `expenses` |
| Sales | `customers`, `sales_orders`, `contracts` |
| Procurement | `vendors`, `purchase_orders`, `purchase_order_items` |
| Inventory | `products`, `inventory_transactions` |
| HR | `employees`, `departments`, `leaves` |

**Sample data:** 1000+ rows seeded with realistic Indian enterprise data (Customer Corp 1–100, Vendor Solutions 1–40, etc.)

### Key Relationships
```
customers ←── invoices ──→ invoice_items ──→ products
                 ↑
             payments

vendors ←── purchase_orders ──→ purchase_order_items ──→ products

departments ←── employees ←── sales_orders ──→ customers
                    ↑
                  leaves

expenses ──→ departments
```

---

## Setup & Run

### Prerequisites
- Python 3.12+
- [Ollama](https://ollama.com) — for the local LLM

### Step-by-Step

```bash
# 1. Clone the repository
git clone <repo-url>
cd nlp-sql-platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Ollama and pull Mistral (one-time, ~4GB download)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral

# 5. Configure environment
cp .env.example .env
# Edit .env if needed (defaults work out of the box)

# 6. Seed the database (creates enterprise.db with 1000+ rows)
python database/seed.py

# 7. Build the schema vector index (one-time)
python database/schema_indexer.py

# 8. Pre-load verified SQL cache for the 5 demo queries
python database/seed_cache.py

# 9. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open in browser:
- **Chat UI**: `http://localhost:8000`
- **Swagger API**: `http://localhost:8000/docs`
- **Flow Explainer**: `http://localhost:8000/app/flow.html`
- **Metrics**: `http://localhost:8000/api/v1/metrics`

### Docker (Alternative)

```bash
docker-compose up --build
# Then pull Mistral inside the Ollama container:
docker exec nlp_sql_ollama ollama pull mistral
```

---

## API Reference

### POST `/api/v1/query` — Ask a Business Question

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show unpaid invoices above 5 lakhs from last quarter",
    "session_id": "my-session"
  }'
```

**Response:**
```json
{
  "question": "Show unpaid invoices above 5 lakhs from last quarter",
  "intent": "data",
  "sql": "SELECT i.invoice_id, c.customer_name, i.total_amount ...",
  "data": [
    {"invoice_id": 97, "customer_name": "Customer Corp 9", "total_amount": 1481066, ...}
  ],
  "row_count": 98,
  "explanation": "There are 98 unpaid invoices exceeding ₹5 lakhs from the last quarter...",
  "relevant_tables": ["invoices", "customers"],
  "from_cache": true,
  "confidence_score": 1.0,
  "execution_time_ms": 449
}
```

### All Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/query` | Ask a natural language question |
| `POST` | `/api/v1/query/stream` | Streaming SSE response (real-time tokens) |
| `GET` | `/api/v1/query/history/{session_id}` | Get conversation history |
| `DELETE` | `/api/v1/query/session/{session_id}` | Clear a session |
| `GET` | `/api/v1/schema/tables` | List all 15 tables |
| `GET` | `/api/v1/schema/table/{table_name}` | Get table details |
| `GET` | `/api/v1/schema/search?q=...` | Semantic table search |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/metrics` | Live monitoring dashboard |

> **Full interactive API docs**: `http://localhost:8000/docs` (Swagger UI)
> **Postman collection**: import `postman_collection.json` from this repository

---

## Sample Questions to Try

```
# Finance
Show unpaid invoices above 5 lakhs from last quarter
Total payments received this month
Expenses above 1 lakh pending approval

# Procurement
Top 10 vendors by payment delays
Pending purchase orders above 10 lakhs
Vendors with rating below 3

# Sales
Customers with highest outstanding balance this month
Sales orders delivered this week
Contracts expiring this month

# Inventory
Products with stock below reorder level
Items received in Mumbai warehouse this week

# HR
Employees in Sales department
Highest paid employees by department
Pending leave applications this month
```

---

## Project Structure

```
nlp-sql-platform/
│
├── app/                          # Main application
│   ├── api/routes/
│   │   ├── query.py              # POST /query · streaming · history
│   │   ├── schema.py             # Schema explorer endpoints
│   │   ├── health.py             # Health check
│   │   └── metrics.py            # Monitoring dashboard
│   │
│   ├── core/
│   │   ├── config.py             # Settings (env vars, Pydantic)
│   │   ├── logging_config.py     # Structured logger setup
│   │   └── metrics_tracker.py    # In-memory query metrics
│   │
│   ├── llm/
│   │   ├── gemini_client.py      # Ollama/Mistral HTTP client + retry
│   │   ├── intent_classifier.py  # DATA vs CHAT intent router
│   │   └── prompt_builder.py     # Adaptive prompt templates
│   │
│   ├── middleware/
│   │   └── logging_middleware.py # Request/response logger
│   │
│   ├── models/
│   │   └── database.py           # SQLAlchemy engine + execute_query()
│   │
│   ├── schema/
│   │   ├── schema_manager.py     # ChromaDB vector search for tables
│   │   └── schema_graph.py       # NetworkX FK graph + JOIN discovery
│   │
│   ├── services/
│   │   ├── query_service.py      # Main 13-step pipeline orchestrator
│   │   ├── cache_service.py      # Semantic cache (ChromaDB)
│   │   └── conversation_service.py # Multi-turn session management
│   │
│   ├── validation/
│   │   └── sql_validator.py      # SQL safety checks
│   │
│   └── main.py                   # FastAPI app entry point
│
├── database/
│   ├── enterprise_schema.py      # 15 table definitions + metadata
│   ├── seed.py                   # Seeds 1000+ rows of sample data
│   ├── schema_indexer.py         # Builds ChromaDB schema index
│   └── seed_cache.py             # Pre-loads verified query cache
│
├── frontend/
│   ├── index.html                # Chat UI (multi-session, vanilla JS)
│   └── flow.html                 # Scroll-animated architecture explainer
│
├── tests/
│   └── test_query.py             # 8 SQL validation tests (all passing)
│
├── .env.example                  # Environment variable template
├── Dockerfile                    # Container build
├── docker-compose.yml            # App + Ollama orchestration
├── postman_collection.json       # Postman API collection (import to test)
└── README.md                     # This file
```

---

## How the Pipeline Works

See the **interactive flow explainer** at `http://localhost:8000/app/flow.html` — a scroll-animated page that traces every file and function call from user question to final answer.

**13 steps in every query:**

1. **FastAPI** receives `POST /api/v1/query`
2. **Logging middleware** assigns request ID, logs start
3. **Intent classifier** — Mistral decides: DATA or CHAT?
4. **Semantic cache** — ChromaDB checks cosine similarity ≥ 0.92
5. **Schema retrieval** — vector search finds top-5 relevant tables
6. **Schema graph** — NetworkX traverses FK graph, discovers JOINs
7. **Adaptive prompt** — schema + JOIN hints + glossary assembled
8. **SQL generation** — Mistral 7B generates SQL (retry on failure)
9. **SQL validator** — safety checks, SELECT-only enforcement
10. **DB execution** — SQLAlchemy runs query on SQLite
11. **Explanation** — Mistral writes plain English business summary
12. **Metrics + cache** — latency recorded, SQL cached for future
13. **JSON response** — structured response to frontend

---

## Running Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

```
tests/test_query.py::test_valid_select           PASSED
tests/test_query.py::test_blocks_drop            PASSED
tests/test_query.py::test_blocks_delete          PASSED
tests/test_query.py::test_blocks_insert          PASSED
tests/test_query.py::test_auto_adds_limit        PASSED
tests/test_query.py::test_strips_markdown        PASSED
tests/test_query.py::test_empty_sql_raises       PASSED
tests/test_query.py::test_non_select_raises      PASSED

8 passed in 0.12s
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `mistral` | Model name (mistral, llama3, etc.) |
| `DATABASE_URL` | `sqlite:///./enterprise.db` | SQLAlchemy connection string |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |
| `LOG_LEVEL` | `INFO` | Logging level |
| `APP_ENV` | `development` | Environment name |
