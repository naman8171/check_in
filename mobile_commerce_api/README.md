# Mobile Commerce API Builder for Odoo 19 Enterprise

## Enterprise Architecture

This add-on provides an Odoo-native backend for Android and iOS mobile commerce applications. It is organized around a versioned REST API layer (`/mobile/api/v1`), mobile app configuration per company and website, API key authentication, JWT customer sessions, mobile merchandising content, device registration, Firebase-ready notifications, telemetry, and customer commerce features.

### Main Components

| Layer | Responsibility |
| --- | --- |
| Mobile App Configuration | App name, branding, splash, colors, Firebase values, JWT settings, feature flags, maintenance mode, company, website, languages, currency. |
| Security Layer | Odoo backend groups, multi-company record rules, generated API keys, JWT signing and validation, request logging. |
| Customer Layer | Registration, login, logout, forgot password, profile, addresses, wishlist, product comparison, reviews, orders. |
| Catalog Layer | Product list/detail/search/filter, category tree, product variants, related products, reviews, product media URLs. |
| Cart & Checkout | Cart creation and synchronization using `sale.order`, line updates, removal, checkout confirmation. |
| Engagement Layer | Device registry, FCM token storage, promotional/order/scheduled notifications, notification status counters. |
| Home Page CMS | Banners, sliders, and configurable product/category sections for featured products, new arrivals, best sellers, and hot deals. |
| Observability | Full API request logging with endpoint, method, user, API key, status, duration, payload snippets, and errors. |

## Folder Structure

```text
mobile_commerce_api/
├── __manifest__.py
├── README.md
├── controllers/
│   ├── __init__.py
│   └── main.py
├── data/
│   ├── ir_cron.xml
│   └── sequence.xml
├── models/
│   ├── __init__.py
│   ├── mobile_api_key.py
│   ├── mobile_api_log.py
│   ├── mobile_app_config.py
│   ├── mobile_content.py
│   ├── mobile_customer.py
│   ├── mobile_device.py
│   └── mobile_notification.py
├── security/
│   ├── ir.model.access.csv
│   └── mobile_commerce_security.xml
└── views/
    ├── menus.xml
    ├── mobile_api_key_views.xml
    ├── mobile_api_log_views.xml
    ├── mobile_app_config_views.xml
    ├── mobile_banner_views.xml
    ├── mobile_catalog_views.xml
    ├── mobile_dashboard_views.xml
    ├── mobile_device_views.xml
    └── mobile_notification_views.xml
```

## Database Models and Relationships

| Model | Purpose | Key Relations |
| --- | --- | --- |
| `mobile.app.config` | One mobile app profile per website/company. | `website_id`, `company_id`, `currency_id`, one2many API keys/devices/banners/sliders/notifications. |
| `mobile.api.key` | Hashed API key credentials per app/platform. | many2one `mobile.app.config`, related company/website. |
| `mobile.device` | Android/iOS device and FCM token registry. | many2one app config, partner, user, currency. |
| `mobile.notification` | Promotional, order status, scheduled, and system notifications. | many2one app config, many2many partners/devices. |
| `mobile.banner` | Home/category/promotion/splash banners. | many2one app config, product template, public category. |
| `mobile.slider` | Home page carousel slides. | many2one app config, product template, public category. |
| `mobile.home.section` | Featured categories/products, arrivals, sellers, deals. | many2one app config, many2many products/categories. |
| `mobile.api.log` | API audit and performance telemetry. | app config, API key, user, partner, company, website. |
| `mobile.wishlist` | Customer wishlist entries. | partner, product template, website, company. |
| `mobile.product.comparison` | Customer comparison list entries. | partner, product template, website, company. |
| `mobile.product.review` | Mobile product review moderation. | partner, product template, website, company. |

## Security Design

- Backend groups: Mobile Commerce User, Manager, and Administrator.
- Multi-company record rules restrict configuration, keys, devices, notifications, banners, and logs to allowed companies.
- API clients must send `X-Mobile-Api-Key` for every endpoint.
- Customer endpoints require `Authorization: Bearer <jwt>`.
- API keys are stored only as SHA-256 hashes; generated clear text is shown once and can be cleared.
- API requests are logged with endpoint, method, user, API key, duration, status, payload, and error snippets.
- App-level maintenance mode blocks API access with a service-unavailable response.
- Rate limiting is modeled through `api_rate_limit`; production deployments should enforce it at Odoo middleware, reverse proxy, or Redis-backed gateway level.

## API Endpoints

All endpoints are versioned under `/mobile/api/v1`.

| Endpoint | Method | Auth | Description |
| --- | --- | --- | --- |
| `/config` | GET | API key | Branding, Firebase public values, feature flags, website/currency/languages. |
| `/auth/register` | POST | API key | Create portal customer and return JWT. |
| `/auth/login` | POST | API key | Authenticate customer and return JWT. |
| `/auth/logout` | POST | API key + JWT | Logout current session. |
| `/auth/forgot-password` | POST | API key | Send password reset email if account exists. |
| `/customer/profile` | GET/PUT | API key + JWT | Read or update customer profile. |
| `/customer/addresses` | GET/POST | API key + JWT | List or create customer addresses. |
| `/products` | GET | API key | Product listing, search, category filter, pagination. |
| `/products/<id>` | GET | API key | Product details, images, variants, reviews, related products. |
| `/categories` | GET | API key | Nested public category tree. |
| `/home` | GET | API key | Home banners, sliders, configured sections. |
| `/cart` | GET/POST/PUT/DELETE | API key + JWT | Synchronize cart, add/update/remove lines. |
| `/checkout/confirm` | POST | API key + JWT | Confirm draft order. |
| `/orders` | GET | API key + JWT | Customer order history. |
| `/orders/<id>` | GET | API key + JWT | Order status, invoice download URLs, delivery tracking. |
| `/wishlist` | GET/POST/DELETE | API key + JWT | Manage wishlist. |
| `/devices/register` | POST | API key | Register or update mobile device and FCM token. |

## API Examples

### Login Request

```http
POST /mobile/api/v1/auth/login
X-Mobile-Api-Key: mca_xxxxxxxxx
Content-Type: application/json

{
  "login": "customer@example.com",
  "password": "secret"
}
```

### Login Response

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_at": 1790610000,
  "customer": {
    "id": 42,
    "name": "Customer",
    "email": "customer@example.com",
    "phone": null,
    "mobile": null
  }
}
```

### Product Listing Request

```http
GET /mobile/api/v1/products?search=shirt&category_id=8&limit=20&offset=0
X-Mobile-Api-Key: mca_xxxxxxxxx
```

### Add to Cart Request

```http
POST /mobile/api/v1/cart
X-Mobile-Api-Key: mca_xxxxxxxxx
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "product_id": 123,
  "quantity": 2
}
```

### Device Registration Request

```http
POST /mobile/api/v1/devices/register
X-Mobile-Api-Key: mca_xxxxxxxxx
Content-Type: application/json

{
  "platform": "android",
  "device_uuid": "device-uuid",
  "fcm_token": "firebase-token",
  "app_version": "1.0.0",
  "os_version": "15",
  "language": "en_US"
}
```

## Implementation Roadmap

1. Install the add-on and create one `mobile.app.config` per website/company.
2. Generate Android and iOS API keys; clear the one-time generated value after copying to secure mobile build secrets.
3. Configure Firebase project ID, sender ID, server key, and service account JSON.
4. Configure banners, sliders, and home sections for mobile merchandising.
5. Connect the mobile app using `/config`, `/auth/login`, `/products`, `/categories`, `/home`, `/cart`, and `/orders`.
6. Add production-grade rate limiting in Nginx/HAProxy/Odoo middleware or Redis-backed API gateway.
7. Extend payment/shipping APIs to map exact carrier and acquirer choices required by the storefront.
8. Integrate FCM HTTP v1 dispatch in `mobile.notification.action_send_now` using the stored service account credentials.
9. Add automated API tests for each endpoint and mobile CI contract tests.
10. Harden JWT secret rotation, refresh tokens, device trust policies, and suspicious activity alerts.

## Deployment Guide

1. Copy `mobile_commerce_api` into the Odoo 19 Enterprise addons path.
2. Restart Odoo and update the apps list.
3. Install **Mobile Commerce API Builder**.
4. Assign backend users to Mobile Commerce User/Manager/Administrator groups.
5. Create a mobile app configuration under **Mobile Commerce → Configuration → Mobile App Settings**.
6. Generate API keys under **Mobile Commerce → Configuration → API Keys**.
7. Configure your reverse proxy for HTTPS only, request size limits, and optional per-key/IP rate limiting.
8. Configure Firebase credentials and validate device registration from Android/iOS builds.
9. Monitor **Mobile Commerce → Technical → API Logs** after mobile app integration.
10. Use Odoo backups and regular key rotation for production operations.
