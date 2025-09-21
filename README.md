# Banking App

A simple command line banking organiser that lets you store banking institutions, their cards and track credit scores in one place. The data is stored in a JSON file so you keep control of your information while consolidating it in a single dashboard.

## Features

- Maintain a catalogue of banking institutions along with contact details and notes.
- Store information about debit, credit or charge cards issued by each institution.
- Track credit scores from multiple providers and keep notes about changes.
- Generate a summary that highlights utilisation and overall credit score trends.

## Installation

This project uses the standard Python tooling that ships with Python 3.10+. No external dependencies are required for the core application.

To work on the project locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

The CLI can be executed with `python -m banking_app`. By default the application stores data in `~/.banking_app/data.json`. The `--storage` flag can be used to override the location.

Initialise the data store:

```bash
python -m banking_app init
```

Add an institution and a card:

```bash
python -m banking_app add-institution "Example Bank" --website https://example.com
python -m banking_app add-card "Rewards Plus" --institution "Example Bank" \
  --card-type credit --credit-limit 5000 --balance 1200 --rewards "2% cashback"
```

Update a credit score and view the summary dashboard:

```bash
python -m banking_app update-credit-score Experian 720
python -m banking_app summary
```

All commands support `--help` for additional options.

## Running Tests

Use `pytest` to run the automated test suite:

```bash
pytest
```
