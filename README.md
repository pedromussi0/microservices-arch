ecommerce_api/
├── alembic/
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── logger.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── products.py
│   │   │       ├── categories.py
│   │   │       ├── orders.py
│   │   │       ├── cart.py
│   │   │       └── payments.py
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── endpoints/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── order.py
│   │   ├── cart.py
│   │   └── payment.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── order.py
│   │   ├── cart.py
│   │   └── payment.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── order.py
│   │   ├── cart.py
│   │   └── payment.py
│   └── services/
│       ├── __init__.py
│       ├── stripe_service.py
│       ├── email_service.py
│       ├── inventory_service.py
│       └── search_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── factories/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_products.py
│   │   └── test_orders.py
│   └── unit/
│       ├── __init__.py
│       ├── test_services/
│       └── test_crud/
├── build/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── test.sh
│   └── lint.sh
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements/
    ├── base.txt
    ├── dev.txt
    └── prod.txt