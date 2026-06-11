# UniPay BNPL API

**Buy Now Pay Later** — Azerbaijan bazarı üçün hazırlanmış, production-style FastAPI backend sistemi.

---

## Layihə Haqqında

UniPay BNPL, kiçik və orta bizneslərin müştərilərinə taksitli ödəniş imkanı təqdim etməsinə imkan verən bir API sistemidir. Merchant müştəriyə mal satır, UniPay ödənişi öz üzərinə götürür, müştəri isə borcunu aylıq hissələrlə qaytarır.

```
Müştəri alış edir → UniPay merchantə 100% ödəyir → Müştəri aylıq taksit ödəyir
```

Kredit riski tamamilə UniPay-in üzərindədir — merchant heç bir risk daşımır.

---

## Texnologiyalar

| Texnologiya | Versiya | Məqsəd |
|---|---|---|
| Python | 3.14 | Əsas dil |
| FastAPI | 0.115+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic v2 | 2.11+ | Validation / Serialization |
| SQLite | — | Development DB |
| PostgreSQL | 16 | Production DB |
| pytest | 8.3+ | Test framework |
| Docker | — | Konteynerləşdirmə |

---

## Qovluq Strukturu

```
unipay_bnpl/
├── app/
│   ├── main.py               # FastAPI app factory
│   ├── config.py             # Mühit dəyişənləri (pydantic-settings)
│   ├── database.py           # SQLAlchemy engine + session
│   │
│   ├── core/
│   │   ├── enums.py          # Bütün status enum-ları
│   │   └── exceptions.py     # Custom exception-lar
│   │
│   ├── models/               # SQLAlchemy ORM modelləri
│   │   ├── base.py           # BaseModel (id, timestamps)
│   │   ├── customer.py       # Müştəri
│   │   ├── merchant.py       # Merchant (satıcı)
│   │   ├── loan.py           # LoanApplication + Loan
│   │   ├── installment.py    # Taksit hissələri
│   │   └── payment.py        # Ödəniş tranzaksiyaları
│   │
│   ├── schemas/              # Pydantic request/response schema-ları
│   │   ├── customer.py
│   │   ├── merchant.py
│   │   ├── application.py
│   │   ├── loan.py
│   │   ├── installment.py
│   │   └── payment.py
│   │
│   ├── services/             # Business logic (bütün qərarlar burada)
│   │   ├── customer_service.py
│   │   ├── merchant_service.py
│   │   ├── application_service.py
│   │   ├── loan_service.py
│   │   └── payment_service.py
│   │
│   └── api/
│       ├── deps.py           # Dependency Injection (DB session)
│       └── v1/
│           ├── customers.py
│           ├── merchants.py
│           ├── applications.py
│           ├── loans.py
│           ├── payments.py
│           └── admin.py
│
├── tests/
│   ├── conftest.py           # Fixtures (db, client, helper-lər)
│   ├── smoke/
│   │   └── test_health.py    # Sistem ayaq üstədir?
│   └── functional/
│       ├── test_customers.py
│       ├── test_merchants.py
│       ├── test_applications.py
│       ├── test_loans.py
│       └── test_payments.py
│
├── pytest.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Arxitektura

Layihə **4 qatlı (layered) arxitektura** üzərində qurulub:

```
HTTP Request
    ↓
API Layer (api/v1/)       — Yalnız route: request al, service çağır, response qaytar
    ↓
Service Layer (services/) — Bütün business logic burada cəmlənib
    ↓
Model Layer (models/)     — SQLAlchemy ORM, database strukturu
    ↓
PostgreSQL / SQLite
```

### Arxitektura Prinsipləri

**OOP + SOLID** — Hər service bir class, hər metod bir məsuliyyət daşıyır.

**Clean Code** — Kiçik, oxunaqlı metodlar; aydın adlandırma; sehrli ədədlər yoxdur.

**KISS** — ABC (Abstract Base Class) yoxdur, lazımsız abstraksiya yoxdur.

**Constructor qaydası** — `__init__`-ə yalnız `db: Session` ötürülür, business data deyil.

**Thin API layer** — Route-lar business logic bilmir, yalnız HTTP-ni idarə edir.

**Dependency Injection** — DB session FastAPI-nin `Depends()` mexanizmi ilə inject edilir.

---

## BNPL Business Axını

### Status Flow-ları

**LoanApplication:**
```
PENDING → APPROVED → (Loan yaranır)
        → REJECTED
        → CANCELLED
```

**Installment:**
```
SCHEDULED → DUE → PAID
                 → OVERDUE   (due date keçib, ödənilməyib)
                 → BAD_DEBT  (30+ gün overdue)
                 → COLLECTION (debt sale sonrası)
                 → WRITTEN_OFF
```

**Payment:**
```
PENDING → SUCCESS
        → FAILED
        → REFUNDED
```

### Tam BNPL Axını

```
1. Merchant qeydiyyatdan keçir
2. Müştəri qeydiyyatdan keçir
3. KYC doğrulanır → credit_score əlavə edilir
4. Müştəri BNPL müraciəti edir (məbləğ + müddət)
5. Admin müraciəti yoxlayır:
   - Credit score < 500 → REJECTED
   - Aktiv loan varsa  → REJECTED
   - KYC verified deyil → REJECTED
   - Hər şey qaydasındadır → APPROVED
6. Loan yaranır, amortization cədvəli generasiya olunur
7. Müştəri hər ay taksit ödəyir
8. Cron job (admin endpoint):
   - Vaxtı keçmiş → OVERDUE
   - 30+ gün → BAD_DEBT
```

---

## API Endpoint-ləri

### Customers
| Metod | Endpoint | Təsvir |
|---|---|---|
| POST | `/api/v1/customers` | Yeni müştəri qeydiyyatı |
| GET | `/api/v1/customers/{id}` | Müştəri məlumatları |
| PATCH | `/api/v1/customers/{id}/kyc` | KYC statusunu yenilə |

### Merchants
| Metod | Endpoint | Təsvir |
|---|---|---|
| POST | `/api/v1/merchants` | Yeni merchant qeydiyyatı |
| GET | `/api/v1/merchants/{id}` | Merchant məlumatları |
| PATCH | `/api/v1/merchants/{id}/status` | Aktivləşdir / deaktiv et |

### Loan Applications
| Metod | Endpoint | Təsvir |
|---|---|---|
| POST | `/api/v1/applications` | BNPL müraciəti yarat |
| GET | `/api/v1/applications/{id}` | Müraciət detalları |
| PATCH | `/api/v1/applications/{id}/decision` | Approve / Reject |

### Loans
| Metod | Endpoint | Təsvir |
|---|---|---|
| GET | `/api/v1/loans/{id}` | Loan detalları |
| GET | `/api/v1/loans/{id}/schedule` | Taksit ödəniş cədvəli |
| GET | `/api/v1/customers/{id}/loans` | Müştərinin bütün loan-ları |

### Payments
| Metod | Endpoint | Təsvir |
|---|---|---|
| GET | `/api/v1/installments/{id}` | Taksit detalları |
| POST | `/api/v1/installments/{id}/pay` | Taksit ödə |
| GET | `/api/v1/installments/{id}/payments` | Ödəniş tarixi |

### Admin (Cron)
| Metod | Endpoint | Təsvir |
|---|---|---|
| POST | `/api/v1/admin/overdue/process` | Vaxtı keçmişləri OVERDUE et |
| POST | `/api/v1/admin/bad-debt/process` | 30+ günlükləri BAD_DEBT et |

---

## Database Sxemi

```
customers (1) ──────────── (many) loan_applications
                                        │
                                        │ (1-1)
                                        ▼
merchants (1) ──────────── (many) loans
                                        │
                                        │ (1-many)
                                        ▼
                                  installments
                                        │
                                        │ (1-many)
                                        ▼
                                    payments
```

---

## Quraşdırma və İşə Salma

### Tələblər
- Python 3.12+
- pip
- (Production üçün) PostgreSQL 16+

### Development (SQLite ilə)

```bash
# 1. Layihəni klon et
git clone <repo-url>
cd unipay_bnpl

# 2. Virtual mühit yarat
python -m venv venv
source venv/bin/activate

# 3. Asılılıqları qur
pip install -r requirements.txt

# 4. Mühit dəyişənlərini hazırla
cp .env.example .env
# .env faylını aç, DATABASE_URL-i tənzimlə

# 5. Serveri işə sal
uvicorn app.main:app --reload
```

API hazırdır: `http://localhost:8000`

### Production (Docker ilə)

```bash
cp .env.example .env
# .env-i tənzimlə

docker compose up --build -d
```

---

## Mühit Dəyişənləri

`.env.example` əsasında `.env` faylı yarat:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/unipay_bnpl
DEBUG=false
MIN_CREDIT_SCORE=500
```

| Dəyişən | Default | Təsvir |
|---|---|---|
| `DATABASE_URL` | — | DB bağlantı URL-i |
| `DEBUG` | `false` | SQL log-larını göstər |
| `MIN_CREDIT_SCORE` | `500` | Loan təsdiq üçün minimum kredit skoru |

---

## Testlər

```bash
# pytest.ini lazımdır (artıq mövcuddur)

# Yalnız smoke testlər (sistem ayaq üstədir?)
pytest tests/smoke/ -v

# Yalnız functional testlər
pytest tests/functional/ -v

# Bütün testlər
pytest tests/ -v

# Coverage ilə
pytest tests/ -v --cov=app --cov-report=term-missing

# HTML hesabat
pytest tests/ -v --html=test_report.html --self-contained-html
```

### Test Nəticələri

```
Smoke Tests:      10/10  ✅
Functional Tests: 53/53  ✅
──────────────────────────
TOTAL:            63/63  ✅  (0 failed)
```

### Test Əhatəsi

| Test faylı | Test sayı | Əhatə |
|---|---|---|
| `smoke/test_health.py` | 10 | Server, docs, basic endpoints |
| `functional/test_customers.py` | 11 | CRUD, KYC, duplicate, validation |
| `functional/test_merchants.py` | 9 | CRUD, status, application bloklama |
| `functional/test_applications.py` | 13 | Apply, approve, reject, edge cases |
| `functional/test_loans.py` | 10 | Schedule, məbləğlər, tarixlər |
| `functional/test_payments.py` | 10 | Ödəniş, overdue, bad debt |

### Test Strategiyası

Hər test izolə olunub — öncəki testin datası növbətiyə keçmir. Bu `conftest.py`-dakı rollback mexanizmi ilə təmin edilir:

```
engine (SQLite in-memory)
    └── connection
            └── transaction  ← hər test sonrası rollback
                    └── session → client
```

---


## İnkişaf Yol Xəritəsi

- [ ] JWT Authentication (müştəri / admin rolları)
- [ ] Alembic migrations
- [ ] Credit bureau inteqrasiyası (AzərCredit)
- [ ] Payment provider webhook-ları
- [ ] Debt sale batch prosessing
- [ ] Background tasks (Celery / APScheduler)
- [ ] Rate limiting
- [ ] Structured logging

---

## Lisenziya

Bu layihə təhsil məqsədilə hazırlanmışdır.
