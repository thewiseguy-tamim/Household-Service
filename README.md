# Household Service Platform API

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
