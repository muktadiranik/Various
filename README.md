# Various

A collection of programming exercises, notebooks, and experimental applications
covering Python, JavaScript, algorithms, AI, databases, and real-time web apps.
The folders are independent projects rather than one application with a shared
entry point.

## Repository guide

| Area | Location |
| --- | --- |
| Algorithms and data structures | [Algorithms](Algorithms/), plus root-level graph and tree notebooks |
| AI agents and knowledge chatbot | [LangChain](LangChain/) — [chat storage and testing notes](LangChain/README.md) |
| Machine learning and NLP | [Machine Learning](Machine%20Learning/), [NLP Tutorial](NLP%20Tutorial/), [Hugging Face Chatbot](Hugging%20Face%20Chatbot/) |
| Database and ORM exercises | [SQLAlchemy](SQLAlchemy/), [fastapi sqlalchemy](fastapi%20sqlalchemy/) |
| Real-time chat experiments | [realtime_chat_server](realtime_chat_server/README.md), [rtc_server](rtc_server/), [WebSocket Chat Application](WebSocket%20Chat%20Application/) |
| Discord-style applications | [discord_api](discord_api/), [discord_scalable](discord_scalable/), [discord-backend](discord-backend/), [discord-frontend](discord-frontend/) |
| Inventory applications | [inventory_management](inventory_management/README.md), [inventory_app](inventory_app/) |
| Other application experiments | [ai-knowledge-base](ai-knowledge-base/), [Smart Task Manager API](Smart%20Task%20Manager%20API/) |
| Browser testing | [playwright-conduit](playwright-conduit/) |
| Tutorial exercises | [Mosh Python](Mosh%20Python/), [Mosh Node](Mosh%20Node/), [Derek Banas](Derek%20Banas/), [Derek Banas JavaScript](Derek%20Banas%20JavaScript/), [Gemini JavaScript](Gemini%20JavaScript/) |

## Getting started

Clone the repository and choose the folder you want to explore:

```bash
git clone https://github.com/muktadiranik/Various.git
cd Various
```

### Python projects

Use an isolated virtual environment. For example, on Windows with PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

On macOS or Linux, activate the environment with `source .venv/bin/activate`
instead. Python requirements vary by project; the newer chatbot code uses
Python 3.11+ features, and its regression tests have been run with Python 3.12.

Prefer a project's own `requirements.txt` and setup instructions when present.
The root dependency list covers a broad range of experiments and is unpinned;
installing it may download large machine-learning packages:

```bash
python -m pip install -r requirements.txt
```

The root `Pipfile` is a separate, minimal configuration targeting Python 3.10;
it does not describe every project's dependencies.

Run the chosen Python script directly, or use `python -m notebook` to explore
the `.ipynb` files after installing the required packages. Some scripts expect
local data files, so check their paths and working-directory assumptions first.

### JavaScript projects

Install Node.js and npm, then work inside the relevant folder containing a
`package.json`. Run `npm install` there and consult that project's README and
package scripts for its development or test commands. There is no root-level
JavaScript application to start.

## Configuration

Some applications require PostgreSQL, Redis, or external AI/search credentials.
Check the selected project's documentation and environment-variable references
before starting it. Keep credentials in local environment variables or ignored
`.env` files; do not commit secrets.

## Tests

There is no single test command for all projects. The LangChain chatbot's chat
persistence regression suite can be run from the repository root after
installing its Python dependencies:

```bash
python -B -m pytest LangChain/tests/test_chat_persistence.py -q -p no:cacheprovider
```

These tests use an isolated SQLite database and Redis/agent test doubles; they
do not require live PostgreSQL, Redis, or model-provider credentials. See the
[chatbot README](LangChain/README.md) for persistence behavior and pagination.
