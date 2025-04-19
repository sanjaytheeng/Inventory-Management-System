# Real Estate Inventory Management System

A Django-based inventory management system designed for real estate companies to track and manage their inventory items (e.g., lockboxes) and their assignments to agents.

## Features

- **Inventory Management**

  - Add, edit, and delete inventory items
  - Track total, available, and in-use quantities
  - Categorize items for better organization
  - Real-time quantity updates

- **Assignment Management**

  - Create and manage item assignments to agents
  - Free-text agent name input with auto-complete suggestions
  - Track assignment history and status
  - Return/reassign items with automatic quantity updates

- **Agent Management**

  - Maintain agent records
  - Track agent assignments and history
  - Auto-suggest existing agents during assignment

- **User Authentication**
  - Secure login and registration
  - Role-based access control
  - Activity logging and audit trail

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd real-estate-inventory
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. Run the development server:

```bash
python manage.py runserver
```

## Project Structure

```
real_estate_inventory/
├── core/                    # Main application
│   ├── models.py           # Data models
│   ├── views.py            # Business logic
│   ├── forms.py            # Form definitions
│   ├── urls.py             # URL routing
│   └── templates/          # Template files
├── authentication/         # Authentication app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── templates/              # Base templates
│   ├── base.html
│   └── includes/
├── static/                 # Static files
│   ├── css/
│   ├── js/
│   └── img/
└── requirements.txt
```

## Usage

1. Log in to the system using your credentials
2. Navigate to the Inventory section to add new items
3. Use the Assignments section to assign items to agents
4. Track item status and history in the dashboard
5. Manage agents and their assignments in the Agents section

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
