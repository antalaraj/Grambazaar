# Grambazaar –  Marketplace with AI Branding, Demand Analysis & Learning Support

Grambazaar is a full-stack Django-based digital marketplace designed to empower rural Self Help Groups (SHGs) by enabling them to sell products online, build trust, learn digital skills, and gain demand insights using AI-driven and data-driven tools. This project was built as part of a social innovation hackathon and demonstrates how technology can bridge the gap between rural producers and digital consumers.

---

## Overview

Grambazaar provides a public multi-vendor marketplace with live products, SHG registration, login and a dedicated dashboard, a custom admin dashboard separate from Django admin, DigiLearner micro-courses for digital upskilling, a smart rule-based demand forecasting system, a mock AI branding assistant called InstaBrand, a trust badge system (Bronze/Silver/Gold), and wallet & ledger tracking for SHGs.

---

## Setup & Run

Requirements: Python 3.10 or higher.

Steps:
- Create virtual environment: `python -m venv venv`
- Activate: `venv\Scripts\activate`
- Install: `pip install django==5.2`
- Migrate DB: `python manage.py migrate`
- Load demo data: `python seed_demo.py`
- Run server: `python manage.py runserver`

Application runs on: http://127.0.0.1:8000/

---

## Demo Access

SHG demo users:
- shg1 / password123  
- shg2 / password123  
- shg3 / password123  
- shg4 / password123  

Any user without an SHG profile is treated as a platform admin.

---

## Key URLs

Public:
- `/` – Home  
- `/marketplace/` – Product listing  
- `/product/<slug>/` – Product detail  
- `/product/<slug>/order/` – Demo checkout  

SHG:
- `/signup/` – Register  
- `/login/` – Login  
- `/shg/dashboard/` – Dashboard  
- `/shg/submit-product/` – Submit product  
- `/shg/wallet/` – Wallet & ledger  

Admin:
- `/admin/dashboard/` – Platform metrics  
- `/admin/pending-products/` – Approvals  
- `/admin/orders/` – Order management  
- `/admin/forecast/` – Demand insights  

---

## InstaBrand (Mock AI)

Endpoint: `/instabrand/`

Simulates AI-based branding and returns:
- Product title  
- Description  
- Hashtags  
- Poster image URL  

---

## Smart Demand Forecast

Implemented in: `market/views.py::generate_forecast`

Rule-based logic:
- Low inventory → suggest increase production  
- Food category → seasonal demand  

Forecast results are visible in admin dashboard.

---

## Project Structure

Core components:
- `market/` – Django app (models, views, forms)  
- `market/templates/` – UI  
- `market/static/` – CSS & JS  
- `seed_demo.py` – Demo data generator  
- `manage.py` – Django entry point  

---

## Technology Stack

- Backend: Django (Python)  
- Frontend: HTML, CSS, JavaScript  
- Database: SQLite  
- AI Logic: Rule-based forecasting + mock NLP branding  
- Architecture: MVC  

---

## Future Scope

- Payment gateway integration  
- Logistics & delivery APIs  
- Real ML-based forecasting models  
- Mobile application  
- Multilingual voice interface  
- Government & NGO SHG integrations  

---

## 👨‍💻 Author
Raj Antala  
🎓 PGDM Student in AI and Data Science  
🏫 Adani Institute of Digital Technology Management (AIDTM)  
📍 Gandhinagar, India  
📧 antalaraj214@gmail.com  
🔗 www.linkedin.com/in/antalaraj
