┌─────────────────────────────────────────────────────────────┐
│                    CUSTOMER REQUEST                          │
│              (from quote_requests_sample.csv)                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR AGENT                          │
│         (Analyzes request and routes to agents)              │
└──┬──────────┬──────────┬──────────┬──────────┬──────────────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐
│INVENTORY│ │QUOTING │ │ORDERING│ │FINANCIAL│ │  DATABASE  │
│ AGENT  │ │ AGENT  │ │ AGENT  │ │ AGENT  │ │ (munder_   │
│        │ │        │ │        │ │        │ │  difflin.  │
│Tools:  │ │Tools:  │ │Tools:  │ │Tools:  │ │  db)       │
│• check_│ │• search│ │• process│ │• check_│ │            │
│  item_ │ │  _hist-│ │  _sales│ │  cash_ │ │Tables:     │
│  stock │ │  orical│ │  _trans│ │  balanc│ │• inventory │
│• check_│ │  _quote│ │  action│ │  e     │ │• transacti-│
│  all_  │ │  s     │ │• process│ │• approve│ │  ons       │
│  invent│ │• calcul│ │  _stock│ │  _purch│ │• quote_    │
│  ory   │ │  ate_  │ │  _order│ │  ase   │ │  requests  │
│• get_  │ │  quote │ │  _trans│ │• get_  │ │• quotes    │
│  availa│ │  _price│ │  action│ │  financ│ │            │
│  ble_  │ │• get_  │ │• check_│ │  ial_  │ │            │
│  items │ │  item_ │ │  deliv-│ │  report│ │            │
│• find_ │ │  prices│ │  ery_  │ │• calcul│ │            │
│  simil-│ │        │ │  timel-│ │  ate_  │ │            │
│  ar_   │ │        │ │  ine   │ │  financ│ │            │
│  items │ │        │ │• check_│ │  ial_  │ │            │
│• get_  │ │        │ │  restoc│ │  health│ │            │
│  item_ │ │        │ │  k_    │ │        │ │            │
│  price │ │        │ │  needed│ │        │ │            │
│• find_ │ │        │ │• get_  │ │        │ │            │
│  items │ │        │ │  item_ │ │        │ │            │
│  _by_  │ │        │ │  unit_ │ │        │ │            │
│  catego│ │        │ │  price │ │        │ │            │
│  ry    │ │        │ │        │ │        │ │            │
└────┬───┘ └───┬────┘ └───┬────┘ └───┬────┘ └──────┬─────┘
     │         │          │          │             │
     └─────────┴──────────┴──────────┴─────────────┘
                        │
                        ▼
         ┌──────────────────────────────────┐
         │      CUSTOMER RESPONSE           │
         │  (Quote or Order Confirmation)   │
         └──────────────────────────────────┘


## Typical Request Flows:
### Quote Request Flow:
Customer Request → Orchestrator Agent
  → Inventory Agent (find items, check stock availability)
  → Quoting Agent (search historical quotes, calculate price with discounts)
  → Customer Response (detailed quote with breakdown)

### Order/Purchase Flow:
Customer Request → Orchestrator Agent
  → Inventory Agent (check stock availability)
  → Quoting Agent (calculate final price)
  → Financial Agent (check cash balance - internal)
  → Ordering Agent (process sales transaction)
  → Inventory Agent (check if restock needed)
  → [IF RESTOCK NEEDED]:
      → Ordering Agent (check delivery timeline)
      → Financial Agent (approve restock purchase)
      → Ordering Agent (create stock order transaction)
  → Customer Response (order confirmation with delivery date)

### Inventory Inquiry Flow:
Customer Request → Orchestrator Agent
  → Inventory Agent (find items, check stock, get prices)
  → Customer Response (availability and pricing info)

### Financial Report Flow (Internal):
Request → Orchestrator Agent
  → Financial Agent (generate report, calculate health metrics)
  → Response (financial summary)

## System Architecture Notes:
- **5 Agents Total**: 1 Orchestrator + 4 Worker Agents (Inventory, Quoting, Ordering, Financial)
- **Orchestrator Pattern**: Central coordinator delegates to specialized agents
- **Database**: All agents interact with shared SQLite database (munder_difflin.db)
- **Processing**: Sequential processing of requests from quote_requests_sample.csv
- **State Tracking**: Database maintains inventory levels, transactions, and cash balance
- **Financial Controls**: 20% safety margin maintained on all purchases
