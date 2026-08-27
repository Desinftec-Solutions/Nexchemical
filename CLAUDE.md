# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

NexChemical is a Django 6.1 site (server-rendered pages + a parallel DRF JSON API) for a chemical
products catalogue with a public contact form. All code lives under `nexchemicalBack/`.

## Commands

All commands run from `nexchemicalBack/` with `DJANGO_SETTINGS_MODULE` defaulting per environment
(see Settings below — dev typically needs `DJANGO_SETTINGS_MODULE=config.settings.dev` unless a
local `manage.py` default/`.env` already sets it).

```bash
cd nexchemicalBack

pip install -r requirements.txt

python manage.py check                          # Django system checks (run in CI)
python manage.py makemigrations --check --dry-run  # fails if models changed without a migration (run in CI)
python manage.py test                           # run the full test suite (run in CI)
python manage.py test catalogue                 # run one app's tests
python manage.py test catalogue.tests.ClassName.test_method  # run a single test

python manage.py runserver
python manage.py migrate
python manage.py makemigrations

ruff check .        # lint (line-length 100, rules E/F/W/I, migrations excluded)
black .              # format (line-length 100)
```

There is no dedicated JS/CSS build step — `static/` assets (plain JS/CSS) are served as-is via
whitenoise/collectstatic.

## Settings

Settings are split under `config/settings/`: `base.py` holds shared config and is never used
directly, `dev.py` (SQLite, `DEBUG=True`, permissive CORS) and `prod.py` (Postgres via env vars,
HTTPS/HSTS enforced) both do `from .base import *`. `base.py` inserts `apps/` onto `sys.path` so
each app is installed as e.g. `"catalogue"` rather than `"apps.catalogue"`.

## Architecture

Three apps under `apps/`, each following the same layered pattern:

- `models.py` — the source of truth; slugs auto-generate from `name` in `save()` if left blank.
- `services.py` — **all** query/mutation logic lives here (e.g. `list_active_products`,
  `get_active_product`, `create_contact_message`). Both the Django views and the DRF API views
  call into the same service functions rather than querying models directly — when changing
  business logic (filtering, active/is_read flags, etc.), change it once in `services.py`.
- `views.py` — server-rendered pages (Django templates under `templates/<app>/`).
- `api_urls.py` / `api_views.py` / `serializers.py` — the parallel read-only-ish JSON API, mounted
  under `/api/<app>/` in `config/urls.py`. Catalogue exposes DRF `ReadOnlyModelViewSet`s keyed on
  `slug` (not `pk`); contact exposes a `CreateAPIView` for messages plus plain `APIView`/
  `ListAPIView` for company info / regional offices.

Apps:
- **core** — home/about pages; has no models. `core.views.home` pulls `catalogue.services.list_active_products()[:6]` for featured products, so core depends on catalogue.
- **catalogue** — `Category` → `SubCategory` → `Product` (with `ProductImage` gallery and
  `ChemicalComponent` composition rows as inlines). `Product.category` is a convenience property
  proxying `subcategory.category`. Products are only ever queried through `is_active=True` in
  services.
- **contact** — `CompanyInfo` is an enforced singleton (`clean()` raises if a row already exists)
  driving the footer/homepage hero/contact page; `contact.context_processors.company_info` injects
  it into every template's context via `TEMPLATES.OPTIONS.context_processors` in settings, so it's
  always available as `{{ company_info }}` without views passing it explicitly. `RegionalOffice`
  and `ContactMessage` (the contact form submissions, with an `is_read` flag) round out the app.

Cross-app dependency direction is core → catalogue and core/templates → contact (via the context
processor); catalogue and contact don't depend on each other.

## Data seeding

Three management commands populate catalogue/contact data for local dev — none are run in CI or
deploy:
- `catalogue/management/commands/seed_catalogue.py` — hardcoded demo product list.
- `catalogue/management/commands/import_products.py` — idempotent import from an external JSON
  dump (upserts by a SKU derived from the source `id`); see its `help` text for the expected shape.
- `core/management/commands/seed_demo_data.py` — seeds catalogue *and* contact data together,
  including attaching images from `static/img/products/`.

## CI/CD

`.github/workflows/ci.yml`: on every push/PR, installs `requirements.txt` and runs `check`,
`makemigrations --check --dry-run`, then `test`. On push to `main` only, after tests pass it SSHes
to the deploy host and runs `scripts/deploy.sh`, which installs deps, runs `migrate` and
`collectstatic`, runs `check --deploy`, then reloads (or starts) the gunicorn process tracked by
`gunicorn.pid` — a graceful `SIGHUP` reload if already running, otherwise a fresh daemonized start.
