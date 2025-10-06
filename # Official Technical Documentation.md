# Official Technical Documentation: Local E-Voting System (Django)

**Document Version:** 1.0
**Project Name:** ProjectZephyr
**Technology Stack:** Django 5.1.1, Python 3.10, SQLite3
**Purpose:** To provide a secure, self-contained electronic voting platform for local, controlled elections.

---

## I. Project Overview and Architectural Design

### A. System Philosophy and Design Goals

The system operates on the principle of **integrity through isolation**. By being locally hosted, it minimizes external dependencies and external security vectors common to cloud-based systems. The design prioritizes:

1.  **Verifiable Data Integrity:** All votes are recorded directly into the local database, ensuring direct control over the tallying process.
2.  **Ease of Local Deployment:** The reliance on SQLite allows for rapid setup on a single server machine within the polling location.
3.  **Clear Separation of Concerns:** The Model-View-Template (MVT) architecture ensures that business logic (`voteApp`) is entirely separate from informational presentation (`landingPage`).

### B. Application Structure and Component Roles

The project (`votingapp`) is divided into distinct Django applications, each handling a core functional area:

| Application | Core Responsibility | Key Directories |
| :--- | :--- | :--- |
| **`voteApp`** | **Core Election Engine.** Handles the creation of ballots, the casting of votes, and the display of results. | `models.py`, `views.py`, `urls.py` |
| **`landingPage`** | **User Entry Point.** Serves the root page, instructional content, and handles any pre-voting access controls (if implemented). | `views.py`, `urls.py` |
| **`votingapp`** | **Global Configuration.** Contains the root URL router, global settings, and WSGI/ASGI handlers. | `settings.py`, `urls.py` |
| **`templates`** | **Presentation Layer.** Contains reusable HTML structure (`base.html`, `partials/`) and application-specific templates (`polls/`). | `pages/`, `partials/`, `polls/` |

---

## II. Deployment and System Configuration

### A. Initial Setup and Execution Guide

All administrative and setup commands must be executed from the project's root directory.

| Step | Command | Rationale |
| :--- | :--- | :--- |
| **1. Install Dependencies** | `pip install -r requirements.txt` | Ensures the necessary Django version and any libraries are present in the Python environment. |
| **2. Initialize Database** | `python manage.py migrate` | Creates the `db.sqlite3` file and establishes all required database tables, including user authentication and the core `Question`/`Choice` tables. |
| **3. Create Administrator** | `python manage.py createsuperuser` | Establishes the initial privileged user required to access the Django Admin interface and configure elections. |
| **4. Start Local Server** | `python manage.py runserver` | Initiates the Django development server for immediate local access. |
| **5. Start on Specific IP** | `python manage.py runserver 192.168.1.5:8000` | **Recommended for Polling Stations.** Binds the server to a specific local network IP, allowing client voting machines to connect. |

### B. Security and Environment Settings (`votingapp/settings.py`)

The following points address mandatory configuration changes for live operation, migrating from the default development settings.

| Setting | Current Value | Live Operation Requirement and Rationale |
| :--- | :--- | :--- |
| **`DEBUG`** | `True` | **MUST BE SET TO `False`**. Leaving debug enabled exposes system internals and configuration data to the public, creating a severe security vulnerability. |
| **`SECRET_KEY`** | Hardcoded Dev Key | **CRITICAL ACTION REQUIRED.** The key must be generated uniquely for the production environment and loaded from an external, secure source (e.g., environment variable, secrets manager) to prevent repository exposure. |
| **`ALLOWED_HOSTS`** | `[]` (Empty) | When `DEBUG` is `False`, this list **must contain all hostnames or IP addresses** from which the application will be accessed (e.g., `['127.0.0.1', 'localhost', '192.168.1.5']`). |
| **Database Engine** | `sqlite3` | **Recommendation:** For high-stakes, concurrent voting, migrate to a client-server RDBMS (e.g., PostgreSQL) to ensure database locking integrity and performance under heavy load. |

---

## III. User Guide for Administration

All election management is conducted through the secure Django Administration panel, accessible at `/admin/`.

### A. Election Management Workflow

1.  **Login:** Access the Admin portal using the superuser credentials created during setup.
2.  **Create a New Question:** Navigate to the **`voteApp`** section and select **Questions**.
    * **`question_text`**: Enter the title of the election (e.g., "Vote for Treasurer").
    * **`pub_date`**: Set the precise date and time the election should be considered live.
3.  **Add Candidates (Choices):** After saving the Question, use the inline editor at the bottom of the Question detail page to add choices.
    * **`choice_text`**: Enter the candidate's name or the option's text.
    * **`image`**: Upload the candidate's image; it will be stored in `media/candidate_images/`.
    * **`votes`**: **Do not manually edit.** This field must remain 0 before the election starts.
4.  **Verification:** Navigate to the front-end poll list (`/polls/`) to ensure the new question is displayed correctly with all choices and images.

### B. Retrieving Results

Results are live and updated instantly as votes are cast.

1.  **Front-end:** Results are viewable by any user at the question's results URL (`/polls/<id>/results/`).
2.  **Admin Review:** For official verification, review the data directly in the Admin portal under **Questions** or **Choices**. The `votes` column on the `Choice` list displays the canonical tally.

---

## IV. Application Logic Reference

### A. Data Model Integrity (`voteApp/models.py`)

| Model | Purpose | Critical Field/Method Detail | Relationship |
| :--- | :--- | :--- | :--- |
| **`Question`** | The ballot structure. | **`was_published_recently()`**: A Boolean utility method crucial for displaying time-sensitive statuses in the Admin interface. | Parent of `Choice`. |
| **`Choice`** | The candidate/option entity. | **`votes`**: An `IntegerField` that serves as the non-relational, atomic vote counter. Must be initialized to 0. | Foreign Key (`question`) linked to `Question` via `CASCADE`. |

### B. Critical Voting View (`voteApp/views.py`)

The **`vote`** function handles the most sensitive operation: vote processing.

| Component | Detail | Functional Outcome |
| :--- | :--- | :--- |
| **Input Validation** | Uses a `try/except` block on `request.POST['choice']` | Ensures a choice was actually selected by the voter. Failure returns the user to the detail page with an error message, preventing invalid data submission. |
| **Atomic Update** | `selected_choice.votes += 1` followed by `selected_choice.save()` | **Note:** While simple, in a highly concurrent environment (many votes at once), this standard increment may be susceptible to race conditions. For live deployment, consider using `F()` expressions or database-level transactions for strict atomic voting. |
| **Post-Vote Action** | `HttpResponseRedirect(reverse('polls:results', args=(question_id,)))` | Immediately redirects the voter away from the `vote` endpoint to prevent browser back/forward buttons from casting duplicate votes (a common pattern in Django polls). |

---

## V. Maintenance and Troubleshooting

### A. Diagnostic and Maintenance Commands

| Task | Command | Purpose |
| :--- | :--- | :--- |
| **Test Database Integrity** | `python manage.py check --database` | Runs core Django checks to verify database settings and connection integrity. |
| **Clear Sessions/Cache** | (Requires manual intervention or a third-party app) | Useful for resolving persistent, strange behavior potentially caused by stale user sessions or server-side cache data. |
| **Enter Interactive Shell**| `python manage.py shell` | Allows direct inspection and manipulation of election data models for debugging specific records. |

### B. Debugging Guide: Common Failure Modes

| Failure Symptom | Most Likely Cause | Resolution Steps |
| :--- | :--- | :--- |
| **403 Forbidden Error** | Missing `{% csrf_token %}` in a form, or `ALLOWED_HOSTS` issue when `DEBUG=False`. | 1. Ensure `{% csrf_token %}` is the first tag inside all `<form method="POST">` tags. 2. Verify the host IP is listed in `settings.ALLOWED_HOSTS`. |
| **Vote Double-Counting** | Voter using browser history or multiple tabs. | The redirect in the `vote` view mitigates this, but true prevention requires session-based voter authentication to track if a specific user has already cast a vote for the question. |

| **Static Assets Missing** | Filesystem paths or URLs are misconfigured for production. | 1. Run `python manage.py collectstatic`. 2. Ensure your production web server (Nginx/Apache) is configured to serve `STATIC_ROOT` and `MEDIA_ROOT` files directly, bypassing Django. |
