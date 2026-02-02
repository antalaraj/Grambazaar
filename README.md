# Grambazaar –  Marketplace with AI Branding, Demand Analysis & Learning Support

Grambazaar is a full-stack Django-based digital marketplace designed to empower rural Self Help Groups (SHGs) by enabling them to sell products online, build trust, learn digital skills, and gain demand insights using AI-driven and data-driven tools. This project was built as part of a social innovation hackathon and demonstrates how technology can bridge the gap between rural producers and digital consumers.

Grambazaar provides a public multi-vendor marketplace with live products, SHG registration, login and dedicated dashboard, a custom admin dashboard separate from Django admin, DigiLearner micro-courses for digital upskilling, smart rule-based demand forecasting, a mock AI branding assistant called InstaBrand, trust badge system (Bronze/Silver/Gold), and wallet & ledger tracking for SHGs.

Setup requires Python 3.10 or higher. Create a virtual environment using `python -m venv venv`, activate it using `venv\Scripts\activate`, install dependencies using `pip install django==5.2`, apply migrations using `python manage.py migrate`, load demo data using `python seed_demo.py`, and start the server using `python manage.py runserver`. The application runs on http://127.0.0.1:8000/

Demo SHG accounts are `shg1`, `shg2`, `shg3`, `shg4` with password `password123`. Any user without an SHG profile is treated as a platform admin.

Important URLs include public routes `/`, `/marketplace/`, `/product/<slug>/`, buyer checkout `/product/<slug>/order/`, SHG routes `/signup/`, `/login/`, `/shg/dashboard/`, `/shg/submit-product/`, `/shg/wallet/`, and admin routes `/admin/dashboard/`, `/admin/pending-products/`, `/admin/orders/`, `/admin/forecast/`.

The InstaBrand mock AI endpoint `/instabrand/` simulates branding output and returns sample JSON containing title, description, hashtags, and poster URL.

The smart demand forecast is implemented in `market/views.py::generate_forecast` and uses rule-based logic where low inventory triggers production suggestions and food category products are marked as seasonal demand.

Core project structure includes the `market/` app with models, views, forms, templates and static assets, along with `seed_demo.py` and `manage.py`.

Technology stack includes Django for backend, HTML/CSS/JavaScript for frontend, SQLite for database, rule-based AI logic for forecasting and branding, and modular MVC architecture.

Future scope includes payment gateway integration, logistics APIs, real machine learning forecasting models, mobile application, multilingual voice support, and large-scale SHG integrations with government and NGOs.

Author: Raj Antala, AI & Data Science Student, Adani Institute of Digital Technology Management.
