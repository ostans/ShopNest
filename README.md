# ShopNest 🛍️

![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![Django 6.1](https://img.shields.io/badge/Django-6.1-092E20?logo=django&logoColor=white)
![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

ShopNest is a Django marketplace where customers browse products from independent stores, place orders, and track delivery. Sellers manage stores, listings, fulfillment, and wallet withdrawals through the web app and Django admin.

## ✨ Features

- Product catalog with categories, search, product images, and homepage hero campaigns
- Customer registration, login, saved delivery addresses, cart, checkout, and order history
- Seller registration, store and listing management, order fulfillment, and wallet withdrawals
- Admin workflows for orders, suborders, payments, and withdrawal requests
- PostgreSQL-backed persistence and uploaded media storage

## 🧰 Stack

- Python 3.14
- Django 6.1
- PostgreSQL
- Pillow for image handling
- django-unfold for the admin interface

## 📋 Requirements

For local development, install Python 3.14 and PostgreSQL. For the containerized setup, install Docker Engine and the Docker Compose plugin.

## 💻 Local Development

1. Create and activate a virtual environment:

   ```sh
   python3.14 -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell, activate it with:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies and create your local environment file:

   ```sh
   python -m pip install -r requirements.txt
   cp .env.example .env
   ```

3. Create a PostgreSQL role and database. `createdb` prompts for the role password when required:

   ```sh
   createuser --pwprompt shopnest
   createdb --owner=shopnest shopnest
   ```

4. Edit `.env` for your local PostgreSQL instance. Set `DB_HOST=127.0.0.1` and `DB_PORT=5432`, and use the same database name, username, and password you created above. Replace the sample `SECRET_KEY` as well.

5. Apply migrations, create an admin account, and run Django:

   ```sh
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

Open <http://127.0.0.1:8000/>. The Django admin is available at <http://127.0.0.1:8000/admin/>.

## 🐳 Docker Compose

The Compose configuration starts Django and PostgreSQL. The example environment values are configured for Compose, where Django reaches the database at `db:5432`.

1. Create the environment file and replace the sample secret and database password:

   ```sh
   cp .env.example .env
   ```

2. Build and start the services:

   ```sh
   docker compose up --build
   ```

The web container waits for PostgreSQL, applies migrations, and starts Django on <http://localhost:8000/>. PostgreSQL is also published on host port `5433` for optional access from local tools.

Create an admin account in another terminal:

```sh
docker compose exec web python manage.py createsuperuser
```

Useful commands:

```sh
# Run tests in the container
docker compose exec web python manage.py test

# Stop the services while preserving database and media volumes
docker compose down

# Stop the services and permanently remove database and media volumes
docker compose down -v
```

The named `postgres_data` and `media_data` volumes survive normal container restarts. Removing the volumes permanently deletes their contents.

## 🔐 Environment Variables

| Variable        | Purpose                           | Compose example                           |
| --------------- | --------------------------------- | ----------------------------------------- |
| `SECRET_KEY`    | Django signing and security key   | Set a private random value                |
| `DEBUG`         | Enables Django debug mode         | `True` for local development              |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames | `localhost,127.0.0.1`                     |
| `DB_NAME`       | PostgreSQL database name          | `shopnest`                                |
| `DB_USER`       | PostgreSQL username               | `shopnest`                                |
| `DB_PASSWORD`   | PostgreSQL password               | Set a private value                       |
| `DB_HOST`       | PostgreSQL hostname               | `db` in Compose; `127.0.0.1` locally      |
| `DB_PORT`       | PostgreSQL port                   | `5432` in Compose; usually `5432` locally |

The `.env` file is ignored by Git. Do not commit production credentials or secrets.

## 🧪 Tests

Run the Django test suite from the project root:

```sh
python manage.py test
```

Run a specific app's tests with:

```sh
python manage.py test orders
```

## 🗂️ Project Layout

- `accounts/`: users, seller and customer profiles, and delivery addresses
- `products/`: categories, products, images, and homepage heroes
- `stores/`: stores, listings, seller order views, and fulfillment
- `cart/`: customer cart and cart items
- `orders/`: checkout, orders, suborders, and payment confirmation
- `payments/`: wallets, transactions, payments, and withdrawal requests
- `core/`: shared models, access mixins, and context processors
- `config/settings/`: shared, development, and production settings
- `templates/`: Django templates
- `static/`: source static assets
- `media/`: uploaded product, store, and hero images

## 🚀 Deployment Note

The included Docker Compose setup is intended for local development. It runs Django's development server with the development settings and `DEBUG=True`; do not expose it as a production deployment. A production setup should use a production WSGI/ASGI server, secure environment-specific settings, HTTPS, and a dedicated static/media serving strategy.
