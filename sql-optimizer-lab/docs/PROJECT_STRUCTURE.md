# Project structure

```text
sql-optimizer-lab/
├── backend/
│   ├── app/
│   │   ├── api/routes.py
│   │   ├── core/config.py
│   │   ├── db/connector.py
│   │   ├── db/schema.py
│   │   ├── engine/executor.py
│   │   ├── engine/learning.py
│   │   ├── engine/llm.py
│   │   ├── engine/optimizer.py
│   │   ├── engine/plans.py
│   │   ├── engine/rewrites.py
│   │   ├── engine/safety.py
│   │   ├── models/schemas.py
│   │   ├── main.py
│   │   └── seed_demo.py
│   ├── tests/test_safety.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── app/page.tsx
│   ├── app/layout.tsx
│   ├── app/globals.css
│   ├── components/ConnectionPanel.tsx
│   ├── components/QueryEditor.tsx
│   ├── components/Charts.tsx
│   ├── components/Dashboard.tsx
│   ├── lib/api.ts
│   ├── package.json
│   ├── .env.local.example
│   └── Dockerfile
├── docs/API.md
├── docs/DESIGN.md
├── docs/SETUP.md
├── docs/PROJECT_STRUCTURE.md
├── data/                  # generated demo.db
├── docker-compose.yml
├── .gitignore
└── README.md
```
