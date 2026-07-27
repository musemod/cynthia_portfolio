# Production Engineering - Portfolio Site

An in-progress portfolio site built for the MLH / Meta Production Engineering Fellowship.

**Stack**
- **Backend:** Flask, Python, Peewee ORM, MySQL
- **Frontend:** Jinja, JavaScript
- **DevOps & Scripting:** Docker, Nginx, Bash

> **Note:** Basic templates adapted from [Amandaleeanne/MLH_Portfolio_Website_WK1](https://github.com/Amandaleeanne/MLH_Portfolio_Website_WK1), built in collaboration with 2 wonderful teammates!

---

## Project Structure

```
MyPortfolio/
├── .env
├── example.env
├── .gitignore
├── .claudeignore
├── prettier.ignore
├── CLAUDE.md
├── README.md
├── requirements.txt
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── scripts/
│   ├── curl-test.sh
│   ├── redeploy-site.sh
│   └── run-test.sh
├── tests/
│   ├── test_app.py
│   └── test_db.py
├── user_conf.d/
│   └── myportfolio.conf
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── models.py
│   └── portfolio_data.py
├── static/
│   ├── img/
│   │   ├── icons/
│   ├── vendor/
│   │   ├── js-sha256/
│   │   │   └── sha256.min.js
│   │   └── leaflet/
│   │       ├── leaflet.js
│   │       ├── leaflet.css
│   │       └── images/
│   └── styles/
│       └── main.css
└── templates/
    ├── base.html
    ├── hobbies.html
    ├── index.html
    ├── travel.html
    ├── timeline.html
    ├── macros/
    │   └── list_section.html
    └── partials/
        └── lightbox.html
```

> Not shown: `python3-virtualenv/` (local venv, gitignored) and `__pycache__/` directories (generated, gitignored).

---

## Installation (Linux)

The application itself runs entirely inside Docker — you do **not** need a local Python environment to run the site. A local virtual environment is only needed if you want to run unit tests or use local dev tooling (IDE autocomplete, linting, etc.) outside of Docker.

### Preconditions

Make sure you have Docker Engine installed. If you also plan to run tests locally (see [Testing](#testing)), you'll additionally need `python3.12` and `pip`.

### (Optional) Set up a local virtual environment for testing/tooling

```bash
$ python3.12 -m venv python3-virtualenv
$ source python3-virtualenv/bin/activate
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application (Linux)

### Configure environment variables

Create a `.env` file using the `example.env` template — copy the template and fill in the variables inside.

| Variable | Description |
|---|---|
| `URL` | Base URL the app runs at (e.g. `localhost:5000`) |
| `MYSQL_HOST` | Hostname of the MySQL service (typically the Docker service name, e.g. `mysql`) |
| `MYSQL_USER` | MySQL user the app connects as |
| `MYSQL_PASSWORD` | Password for `MYSQL_USER` |
| `MYSQL_DATABASE` | Name of the database the app uses |
| `MYSQL_PORT` | Port MySQL is exposed on |
| `MYSQL_ROOT_PASSWORD` | Root password for the MySQL container itself (used by the `mysql` service on first init) |
| `TEST_BASE_URL` | Base URL used by `scripts/curl-test.sh` when hitting endpoints (e.g. `http://localhost:5000/api/timeline_post`) |
| `EMAIL` | Email used by the production Nginx service for Let's Encrypt/Certbot registration |
| `TESTING` | `false` for normal operation. `scripts/run-test.sh` overrides this to `true` at invocation time (in-memory SQLite instead of MySQL) — you don't need to toggle this manually in `.env` |

### Choose a deployment mode

**1. Local machine (development environment)**

Build the Docker image and start the containers:

```bash
$ docker compose up -d
```

You should see output similar to:

```
❯ docker compose up -d
[+] up 3/3
 ✔ Network myportfolio_default Created                                                                                                        0.1s
 ✔ Container mysql             Started                                                                                                        0.5s
 ✔ Container myportfolio       Started                                                                                                        0.8s
```

The site will be available at `localhost:5000` or `127.0.0.1:5000`.

> **Note:** The portfolio site only runs while the Docker containers are up.

**2. Virtual private server (production environment)**

Build the Docker image and start the containers using `docker-compose.prod.yml`:

```bash
$ docker compose -f docker-compose.prod.yml up -d
```

This requires a domain already set up for the site, along with the appropriate configuration — see `user_conf.d/myportfolio.conf` for the `server_name` used to verify the SSL certificate.

The site will run on the domain you've already set up (e.g. `https://cynthiawong.duckdns.org/`).

### Manually stopping containers

```bash
$ docker compose down
```

---

## Testing

**Unit tests**

Run everything in the `tests/` folder via:

```bash
$ scripts/run-test.sh
```

This script automatically sets `TESTING=true`, which switches the app to an in-memory SQLite database instead of the real MySQL database. This runs locally against your virtual environment — Docker containers do **not** need to be running for this.

**Endpoint tests**

Run:

```bash
$ scripts/curl-test.sh
```

This requires the real MySQL service to be running inside Docker (see [Running the Application](#running-the-application-linux) for dev vs. VPS commands), and `.env` should have `TESTING=false`.

---

## Redeploying on VPS (production) after changes

Run `scripts/redeploy-site.sh` to redeploy the site after making changes. This will pull the latest changes from GitHub, spin down any currently-running Docker containers, then rebuild the image and start fresh containers.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

Pull requests are still required for review and feedback on all changes. Please make sure to update tests as appropriate.