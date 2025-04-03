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
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update profile
- `POST /api/auth/promote/<user_id>/` - Promote user to admin (admin only)

### Services
- `GET /api/services/` - List all services
- `POST /api/services/` - Create new service (admin only)
- `GET /api/services/<id>/` - Get service details
- `PUT /api/services/<id>/` - Update service (admin only)
- `DELETE /api/services/<id>/` - Delete service (admin only)
- `GET /api/services/?ordering=average_rating` - Sort services by rating
- `GET /api/services/?name=<name>` - Filter services by name
- `GET /api/services/?price=<price>` - Filter services by price

### Cart
- `GET /api/carts/` - View user's cart
- `POST /api/cart/add/` - Add service to cart
- `DELETE /api/cart/remove/<id>/` - Remove service from cart

### Orders
- `GET /api/orders/` - View order history
- `POST /api/orders/` - Place order from cart
- `GET /api/orders/<id>/` - Get order details

### Reviews
- `GET /api/reviews/` - List all reviews
- `POST /api/reviews/` - Create review for service
- `GET /api/reviews/?service_id=<id>` - Get reviews for specific service
- `PUT /api/reviews/<id>/` - Update review
- `DELETE /api/reviews/<id>/` - Delete review
