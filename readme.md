# Django E-commerce API  
A scalable and modular e-commerce RESTful API built with Django and Django REST Framework. This project includes user authentication, product management, shopping cart functionality, and more. It is intended as a learning exercise and portfolio project (not production-ready).

## Features  
- **User Authentication:** Register new users and log in with secure token-based authentication (JWT).  
- **Product Management (CRUD):** Create, retrieve, update, and delete products via API endpoints. Products support multiple images, auto-generated URL slugs, and soft-delete (inactive) status.  
- **Product Catalog:** Organize products with categories and tags. Support for custom product attributes (e.g. color, size) is included for future expansion.  
- **Inventory and Discounts:** Each product has a stock level (inventory) field. An abstract discount model is defined to allow future implementation of promotional discounts or price adjustments.  
- **Product Interactions:** Users can comment on products, and the system tracks product likes and view counts. All these interactions are exposed through the API.  
- **Shopping Cart:** Authenticated users have a shopping cart. The API provides endpoints to view the cart, add items, update quantities, and remove items. A custom permission ensures users can only modify their own cart.  
- **Admin Interface:** Django’s admin site is configured for all models (products, categories, tags, carts, etc.) with custom admin classes to make data management easy during development.  
- **Pagination and Filtering:** The product list endpoint includes pagination (default page size 10) and supports search/filter by title, category, or tags. A custom permission (IsAdminOrReadOnly) allows only admins to modify products.  
- **Testing:** The project includes a suite of unit tests using **pytest** to verify core functionality (accounts, products, carts, etc.). 

## Stack  
- **Python 3** – Programming language  
- **Django 5** – Web framework  
- **Django REST Framework** – API framework for building RESTful endpoints  
- **SQLite3** – Default development database (can be changed to other SQL databases)  
- **Pytest** – Testing framework for running automated tests

## Setup  
1. **Clone the repository:**  
   ```bash
   git clone https://github.com/Mohammad913Ab/E-commerce-API.git
   cd E-commerce-API
   ```  
2. **Create a virtual environment and activate it:**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # On Windows use: .venv\Scripts\activate
   ```  
3. **Install dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```
4. **Run database migrations:**  
   ```bash
   python manage.py migrate
   ```  
5. **(Optional) Create a superuser for the admin site:**  
   ```bash
   python manage.py createsuperuser
   ```  
6. **Start the development server:**  
   ```bash
   python manage.py runserver
   ```  
   The API will be available at `http://localhost:8000/`. You can use the browsable API or tools like Postman to interact with the endpoints.  

## About / Notes  
This project is for educational purposes and to showcase API development skills. It is **not** intended for production use. The code follows a modular structure so features like Swagger documentation or additional integrations can be added later. Contributions are welcome, and feel free to modify or extend this API for your own learning.
