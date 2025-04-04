# Household Service Platform API

Household Service Platform is a RESTful API built using Django REST Framework (DRF). It provides endpoints for managing users, services, orders, reviews, and more. The project includes JWT authentication and API documentation with Swagger.

## Features
- User authentication (registration, login, profile management)
- Service management (create, update, delete, list, and filter services)
- Cart and order functionality (add/remove items, place orders, view order history)
- Reviews management (add, update, delete, and filter reviews)
- JWT authentication using Djoser
- API documentation using Swagger (drf_yasg)

## Technologies Used
- **Django** - Backend framework
- **Django REST Framework (DRF)** - API development
- **Djoser** - Authentication
- **Simple JWT** - JWT authentication
- **drf-yasg** - API documentation (Swagger)
- **PostgreSQL** (or SQLite) - Database

## Setup

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

4. Create superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

5. Run development server:
   ```bash
   python manage.py runserver
   ```


## API Documentation
Swagger documentation is available at:
```
http://127.0.0.1:8000/swagger/
```

ReDoc documentation is available at:
```
http://127.0.0.1:8000/redoc/
```

## API Endpoints

### Authentication
- `POST /users/register/` - Register new user
- `POST /users/login/` - Login and get JWT token
- `GET /users/profile/` - Get user profile
- `PUT /users/profile/update/` - Update profile
- `POST /users/<user_id>/promote` - Promote user to admin (admin only)

### Services
- `GET /services/` - List all services
- `POST /services/` - Create new service (admin only)
- `GET /services/<id>/` - Get service details
- `PUT /services/<id>/` - Update service (admin only)
- `DELETE /services/<id>/` - Delete service (admin only)
- `GET /services/?ordering=rating` - Sort services by rating
- `GET /services/?name=<name>` - Filter services by name
- `GET /services/?price=<price>` - Filter services by price

### Cart
- `GET /carts/` - View user's cart
- `POST /cart/add/` - Add service to cart
- `DELETE /cart/remove/<id>/` - Remove service from cart

### Orders
- `GET /orders/` - View order history
- `POST /orders/` - Place order from cart
- `GET /orders/<id>/` - Get order details

### Reviews
- `GET /reviews/` - List all reviews
- `POST /reviews/` - Create review for service
- `GET /reviews/?service_id=<id>` - Get reviews for specific service
- `PUT /reviews/<id>/` - Update review
- `DELETE /reviews/<id>/` - Delete review

## Environment Variables
Create a `.env` file in the root directory and add the following:
```ini
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=your_database_url
ALLOWED_HOSTS=*
EMIL_HOST=your_email_host


## License
This project is licensed under the MIT License.

---
### Author
Tamim Islam (https://https://github.com/thewiseguy-tamim)
