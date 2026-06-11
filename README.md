# UniPay BNPL API

**Buy Now Pay Later** — Azerbaijan bazarı üçün hazırlanmış production-style FastAPI backend sistemi.

Müştəri mal alır, UniPay merchantə 100% ödəyir, müştəri borcu aylıq taksitlə qaytarır. Bütün kredit riski UniPay-in üzərindədir.

---

## Texnologiyalar

| Texnologiya | Versiya | Məqsəd |
|---|---|---|
| Python | 3.12+ | Əsas dil |
| FastAPI | 0.115+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic v2 | 2.11+ | Validation / Serialization |
| pydantic-settings | 2.7+ | Mühit dəyişənləri |
| python-dateutil | 2.9+ | Tarix hesablamaları |
| SQLite | — | Development DB |
| PostgreSQL | 16 | Production DB |
| pytest | 8.3+ | Test framework |

---

## Qovluq Strukturu

```
unipay_bnpl/
├── main.py                        # Giriş nöqtəsi — python main.py
├── app/
│   ├── main.py                    # FastAPI app factory (create_app)
│   ├── config.py                  # Mühit dəyişənləri (pydantic-settings)
│   ├── database.py                # SQLAlchemy engine + session
│   │
│   ├── core/
│   │   ├── enums.py               # Bütün status enum-ları
│   │   └── exceptions.py          # Custom exception-lar
│   │
│   ├── models/                    # SQLAlchemy ORM modelləri (DB cədvəlləri)
│   │   ├── base.py                # BaseModel — id, timestamps
│   │   ├── customer.py            # Müştəri
│   │   ├── merchant.py            # Merchant (satıcı)
│   │   ├── loan.py                # LoanApplication + Loan
│   │   ├── installment.py         # Aylıq taksit hissələri
│   │   └── payment.py             # Ödəniş tranzaksiyaları
│   │
│   ├── schemas/                   # Pydantic request/response schema-ları
│   │   ├── base.py                # ORMBase — from_attributes
│   │   ├── customer.py
│   │   ├── merchant.py
│   │   ├── application.py
│   │   ├── loan.py
│   │   ├── installment.py
│   │   └── payment.py
│   │
│   ├── utils/                     # Paylaşılan validator və hesablama funksiyaları
│   │   ├── customer_validators.py # KYC, dublikat yoxlamaları
│   │   ├── merchant_validators.py # Aktiv merchant yoxlaması
│   │   ├── loan_validators.py     # Aktiv loan, pending status yoxlamaları
│   │   ├── credit_checker.py      # Kredit skoru yoxlaması
│   │   ├── installment_calculator.py # Amortization hesablaması
│   │   └── payment_validators.py  # Ödənilə bilən installment yoxlaması
│   │
│   ├── services/                  # Business logic — bütün qərarlar buradadır
│   │   ├── customer_service.py
│   │   ├── merchant_service.py
│   │   ├── application_service.py
│   │   ├── loan_service.py
│   │   ├── payment_service.py
│   │   └── admin_service.py
│   │
│   └── api/
│       ├── __init__.py            # Exception handler-lar
│       ├── deps.py                # DB session dependency injection
│       └── v1/
│           ├── __init__.py        # Router registry — /api/v1
│           ├── customers.py
│           ├── merchants.py
│           ├── applications.py
│           ├── loans.py
│           ├── payments.py
│           └── admin.py
│
├── tests/
│   ├── conftest.py                # Fixtures — db, client, helper-lər
│   ├── smoke/
│   │   └── test_health.py         # Sistem ayaq üstədir?
│   └── functional/
│       ├── test_customers.py
│       ├── test_merchants.py
│       ├── test_applications.py
│       ├── test_loans.py
│       └── test_payments.py
│
├── pytest.ini
├── requirements.txt
└── .env.example
```

---

## Arxitektura

Layihə **4 qatlı arxitektura** üzərindədir. Hər qatın bir işi var, başqasının işinə qarışmır.

```
HTTP Request
    ↓
API Layer       — request al, service çağır, response qaytar
    ↓
Utils Layer     — paylaşılan validasiya və hesablama funksiyaları
    ↓
Service Layer   — bütün business logic, qərarlar buradadır
    ↓
Model Layer     — SQLAlchemy ORM, DB strukturu
    ↓
SQLite / PostgreSQL
```

### Tətbiq olunan prinsiplər

**OOP** — Hər service class-dır. `__init__`-ə yalnız `db: Session` ötürülür — state management üçün. Business data constructor-a girmir.

**Single Responsibility** — Hər metod bir iş görür. `_build_loan` yalnız Loan obyekti qurur. `_mark_paid` yalnız statusları dəyişir. `_json_error` yalnız JSONResponse qurur.

**KISS** — ABC yoxdur, mürəkkəb abstraksiya yoxdur. Utils-də class yoxdur — sadəcə funksiyalar. Oxuyanda hər şeyin nə etdiyi aydındır.

**DRY** — `BaseModel`-də `id`, `created_at`, `updated_at` bir dəfə yazılıb. `ORMBase`-də `model_config` bir dəfə yazılıb. Paylaşılan validasiya məntiqi utils-dədir.

**Clean Code** — Adlar özü izah edir. `get_verified_customer`, `assert_no_active_loan`, `assert_installment_is_payable` — şərh olmadan başa düşülür.

---

## BNPL Business Axını

```
1. Merchant qeydiyyatdan keçir
2. Müştəri qeydiyyatdan keçir
3. KYC doğrulanır → credit_score əlavə edilir
4. Müştəri BNPL müraciəti edir (məbləğ + müddət)
5. Sistem yoxlayır:
   ├── KYC verified deyil     → 422
   ├── Merchant deaktivdir    → 422
   ├── Aktiv loan var         → 422
   └── Credit score < 500     → 422 (approve zamanı)
6. Admin qərar verir: APPROVED / REJECTED
7. APPROVED → Loan yaranır, amortization cədvəli generasiya olunur
8. Müştəri hər ay taksit ödəyir
9. Cron job (gündəlik):
   ├── Vaxtı keçmiş → OVERDUE
   └── 30+ gün overdue → BAD_DEBT
```

### Status Flow-ları

```
LoanApplication:  PENDING → APPROVED | REJECTED | CANCELLED
Loan:             ACTIVE → CLOSED | DEFAULTED
Installment:      SCHEDULED → DUE → PAID
                                  → OVERDUE → BAD_DEBT → COLLECTION → WRITTEN_OFF
Payment:          PENDING → SUCCESS | FAILED | REFUNDED
```

---

## API Endpoint-ləri

### Customers
| Metod | Endpoint | Təsvir | Status |
|---|---|---|---|
| POST | `/api/v1/customers` | Yeni müştəri qeydiyyatı | 201 |
| GET | `/api/v1/customers/{id}` | Müştəri məlumatları | 200 |
| PATCH | `/api/v1/customers/{id}/kyc` | KYC və kredit skoru yenilə | 200 |

### Merchants
| Metod | Endpoint | Təsvir | Status |
|---|---|---|---|
| POST | `/api/v1/merchants` | Yeni merchant qeydiyyatı | 201 |
| GET | `/api/v1/merchants/{id}` | Merchant məlumatları | 200 |
| PATCH | `/api/v1/merchants/{id}/status` | Aktivləşdir / deaktiv et | 200 |

### Loan Applications
| Metod | Endpoint | Təsvir | Status |
|---|---|---|---|
| POST | `/api/v1/applications` | BNPL müraciəti yarat | 201 |
| GET | `/api/v1/applications/{id}` | Müraciət detalları | 200 |
| PATCH | `/api/v1/applications/{id}/decision` | Approve / Reject | 200 |

### Loans
| Metod | Endpoint | Təsvir | Status |
|---|---|---|---|
| GET | `/api/v1/loans/{id}` | Loan detalları | 200 |
| GET | `/api/v1/loans/{id}/schedule` | Taksit ödəniş cədvəli | 200 |
| GET | `/api/v1/customers/{id}/loans` | Müştərinin bütün loan-ları | 200 |

### Payments
| Metod | Endpoint | Təsvir | Status |
|---|---|---|---|
| GET | `/api/v1/installments/{id}` | Taksit detalları | 200 |
| POST | `/api/v1/installments/{id}/pay` | Taksit ödə | 201 |
| GET | `/api/v1/installments/{id}/payments` | Ödəniş tarixi | 200 |

### Admin
| Metod | Endpoint | Təsvir | Status |
|---|---|---|---|
| POST | `/api/v1/admin/overdue/process` | Vaxtı keçmişləri OVERDUE et | 200 |
| POST | `/api/v1/admin/bad-debt/process` | 30+ günlükləri BAD_DEBT et | 200 |

---

## Qurulum və İşə Salma

### Tələblər
- Python 3.12+
- pip
- Virtual environment

### Development (SQLite ilə)

```bash
# 1. Layihəni klon et
git clone <repo-url>
cd unipay_bnpl

# 2. Virtual mühit yarat və aktivləşdir
python -m venv venv
source venv/bin/activate          # Linux/macOS
venv\Scripts\activate             # Windows

# 3. Asılılıqları qur
pip install -r requirements.txt

# 4. Mühit dəyişənlərini hazırla
cp .env.example .env

# 5. Serveri işə sal
python main.py
# və ya
uvicorn app.main:app --reload
```

### CLI parametrləri

```bash
python main.py                              # default: 127.0.0.1:8000
python main.py --port 8080                  # port dəyiş
python main.py --host 0.0.0.0 --port 8000  # bütün interfeyslər
python main.py --no-reload                  # auto-reload söndür
```

### Swagger UI

Server işə düşdükdən sonra:
```
http://localhost:8000/docs   # Swagger UI
http://localhost:8000/redoc  # ReDoc
```

---

## Mühit Dəyişənləri

`.env.example` əsasında `.env` faylı yarat:

```env
DATABASE_URL=sqlite:///./unipay_bnpl.db
DEBUG=false
MIN_CREDIT_SCORE=500
```

| Dəyişən | Default | Məcburi | Təsvir |
|---|---|---|---|
| `DATABASE_URL` | — | ✅ | DB bağlantı URL-i |
| `DEBUG` | `false` | — | SQL log-larını göstər |
| `MIN_CREDIT_SCORE` | `500` | — | Loan təsdiq üçün minimum kredit skoru |

---

## Testlər

```bash
# Bütün testlər
pytest tests/ -v

# Yalnız smoke
pytest tests/smoke/ -v

# Yalnız functional
pytest tests/functional/ -v

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
TOTAL:            63/63  ✅
```

### Test Strategiyası

Hər test izolə olunub — öncəki testin datası növbətiyə keçmir. `conftest.py`-da hər test üçün ayrı transaction açılır, test bitəndə rollback edilir.

```
SQLite in-memory
    └── connection
            └── transaction  ← test sonrası rollback
                    └── session → TestClient
```

**Fixture-lar:**
- `verified_customer` — KYC=VERIFIED, credit_score=650 hazır customer
- `active_merchant` — aktiv merchant
- `approved_loan` — tam flow: apply → approve → loan hazır

---

## Əsas Dizayn Qərarları

**Niyə utils qovluğu?**
Paylaşılan validasiya məntiqi service-lərin içindən çıxarılıb. `get_verified_customer`, `assert_no_active_loan` kimi funksiyalar istənilən service-dən çağırıla bilər, ayrıca test edilə bilər.

**Niyə `flush()` və `commit()` ayrıdır?**
`flush()` datanı DB-yə göndərir amma transaction-ı bağlamır. `loan.id` yaranır ki növbəti əməliyyatda istifadə olunsun. Bütün əməliyyatlar uğurlu olduqda `commit()` çağırılır — atomiklik təmin olunur.

**Niyə ABC yoxdur?**
Service-lər konkret class-lardır. Interfeys tələb edən ssenari yoxdur. ABC əlavə etmək KISS-i pozar, kodu mürəkkəbləşdirər.

**Niyə `__init__`-ə yalnız `db` ötürülür?**
Constructor state management üçündür. Business data metodlara parametr kimi verilir. Bu test yazılmasını asanlaşdırır — service-i istənilən `db` ilə yaratmaq olur.

**Niyə `PAYABLE_STATUSES` set-dir?**
`in` operatoru `set`-də O(1), `list`-də O(n)-dir. Kiçik fərq amma doğru alışqanlıqdır.

---

## Qısa Kod Axını

```
POST /api/v1/applications
    ↓
deps.py          → DB session açılır
    ↓
applications.py  → ApplicationService(db).create(data)
    ↓
utils/           → get_verified_customer()
                 → get_active_merchant()
                 → assert_no_active_loan()
    ↓
service          → _build_application() → db.commit()
    ↓
schemas          → ApplicationResponse serialize olunur
    ↓
HTTP 201         → session bağlanır
```
