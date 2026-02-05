# Grambazaar –  Marketplace with AI Branding, Demand Analysis & Learning Support 🛒

## 📋 Table of Contents
- [🌟 Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [⚙️ Tech Stack](#%EF%B8%8F-tech-stack)
- [📂 Project Structure](#-project-structure)
- [🛠️ Setup & Installation](#%EF%B8%8F-setup--installation)
- [🤝 Contributing](#-contributing)
- [👥 Author](#-team)

## 🌟 Features

### 🛍️ For Buyers
- 🏷️ Browse and search products by categories
- 👤 Create accounts and manage profiles
- 🛒 Place and track orders
- ⭐ Leave product reviews and ratings
- 🔒 Secure checkout process

### 👥 For SHGs (Self Help Groups)
- 🏢 Create and manage SHG profiles
- 📦 List and manage products with images
- 📊 Track inventory and sales
- 📚 Access digital learning resources (DigiCourses)
- 💰 View financial transactions and wallet balance
- 📈 Receive smart inventory and demand forecasts

#### 🤖 AI-Powered Tools
- **BrandSetu AI**: AI-powered product marketing and branding assistance
- **DigiSarathi AI**: Intelligent digital assistant for business guidance
- **Smart Recommendations**: Personalized product suggestions
- **Automated Insights**: Data-driven business intelligence

### 👨‍💼 For Administrators
- 👥 Manage SHG registrations
- ✅ Approve/reject products
- 📦 Process and manage orders
- 📊 Generate demand forecasts
- 🎓 Manage digital learning content
- 📱 Monitor platform analytics

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Virtual environment (recommended)

### One-Command Setup
```bash
# Clone and setup (Linux/macOS)
git clone https://github.com/yourusername/grambazaar.git && cd grambazaar && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py createsuperuser
```

## ⚙️ Tech Stack

### Backend
- **Framework**: [Django 5.2](https://www.djangoproject.com/)
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Django AllAuth
- **API**: Django REST Framework

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- [Bootstrap 5](https://getbootstrap.com/) - Responsive design
- [jQuery](https://jquery.com/) - DOM manipulation
- [Chart.js](https://www.chartjs.org/) - Data visualization

### AI/ML Stack
- **BrandSetu**: PyTorch, Transformers
- **DigiSarathi**: NLP, RASA
- **Forecasting**: scikit-learn, Prophet
- **Recommendations**: Surprise, LightFM

## 📂 Project Structure

```plaintext
GramBazaar/
├── .github/               # GitHub workflows and configurations
│   └── workflows/         # CI/CD pipelines
│
├── .vscode/               # VS Code workspace settings
│   └── settings.json      # Editor configurations
│
├── GramBazaar/            # Main project configuration
│   ├── __init__.py
│   ├── settings/          # Split settings for different environments
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py           # Main URL configuration
│   ├── asgi.py           # ASGI config
│   └── wsgi.py           # WSGI config
│
├── market/                # Main application
│   ├── migrations/        # Database migrations
│   ├── static/            # Static assets
│   │   ├── css/          # Stylesheets
│   │   ├── js/           # JavaScript files
│   │   └── images/       # Static images
│   │
│   ├── templates/         # HTML templates
│   │   └── market/       # Namespaced templates
│   │       ├── base.html # Base template
│   │       ├── includes/ # Reusable template parts
│   │       ├── shg/      # SHG-specific templates
│   │       └── admin/    # Admin templates
│   │
│   ├── management/        # Custom management commands
│   │   └── commands/
│   │
│   ├── templatetags/     # Custom template tags
│   │   └── __init__.py
│   │
│   ├── admin.py          # Admin site configuration
│   ├── apps.py           # App config
│   ├── forms.py          # Form definitions
│   ├── models.py         # Database models
│   ├── urls.py          # App URL routing
│   ├── utils.py         # Utility functions
│   └── views.py         # View functions
│
├── content/              # Content management app
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   └── views.py
│
├── media/                # User-uploaded files (not in version control)
│   ├── products/         # Product images
│   └── profiles/         # Profile pictures
│
├── static/               # Global static files
│   ├── css/             # Global styles
│   ├── js/              # Global scripts
│   └── vendor/          # Third-party libraries
│
├── tests/               # Test files
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test data
│
├── venv/                # Virtual environment (not in version control)
│
├── .env                 # Environment variables
├── .gitignore           # Git ignore rules
├── db.sqlite3           # Development database (not in version control)
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## 🛠️ Setup & Installation

### Development
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/grambazaar.git
cd grambazaar

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔄 Open a Pull Request

### Development Guidelines
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Write tests for new features
- Update documentation
- Keep commit messages clear and descriptive

## 🐛 Troubleshooting

### Common Issues
1. **Database connection failed**
   - Check your database settings in `.env`
   - Ensure the database server is running

2. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Migration errors**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```


## 👥 Author

<div align="center">
  <img src="https://avatars.githubusercontent.com/antalaraj?s=160" width="140" alt="Raj Antala" />

  <h3>Raj Antala</h3>

  <p>
    PGDM in AI & Data Science<br>
    Adani Institute of Digital Technology Management
  </p>

  <p>
    <a href="mailto:antalaraj214@gmail.com">📧 Email</a> |
    <a href="https://www.linkedin.com/in/antalaraj">💼 LinkedIn</a> |
    <a href="https://github.com/antalaraj">💻 GitHub</a>
  </p>
</div>

## 🙏 Acknowledgments

- Django Community for the amazing web framework
- All open-source libraries and tools used in this project
- Our mentors and advisors for their guidance

---

<div align="center">
  <h3>Made with ❤️ for rural empowerment</h3>
  <p>Support the project by giving it a ⭐ on GitHub!</p>
</div>


