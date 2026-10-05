# Greenhill Food Co-op Ordering System

A simple web application for managing weekly grocery orders for Greenhill Food Co-op.

## Project Overview

Greenhill Food Co-op is a volunteer-run community food co-operative. This system allows members to enter their own weekly orders, gives the coordinator a view of all orders and product totals, and provides a printable packing sheet for the Thursday packing shift.

## Features

- Member management and contact details
- Product catalogue with unit and weight based pricing
- Weekly round management (open/closed/packed states)
- Order placement and tracking for members
- Coordinator dashboard for viewing all orders

## Technology Stack

- Python 3.11+
- Flask 3.0+
- SQLite 3.x
- SQLAlchemy 2.x
- pytest 8.x

## Prerequisites

- Python 3.11 or later
- Git

## Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/L13-fan/greenhill-food-coop-ordering-system.git
cd greenhill-food-coop-ordering-system
```

2. Create and activate a virtual environment:

Windows:

```bush
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
```

5. Initialise the database:

```bash
python init_db.py
```

6. Run the application:

```bash
flask run
The application will be available at http://127.0.0.1:5000/.
```

## Running Tests

```bash
pytest
```

To run with coverage:

```bash
pytest --cov=app
```

## Definition of Done
This project follows the fixed Definition of Done provided in the Greenhill Food Co-op case study. A user story is not done until all criteria in the DoD are met, including code review, automated tests, and a clean checkout run.

## Documentation
  - Project Charter: https://scu-it.atlassian.net/wiki/x/5wBAPg
  
  - Requirements Analysis and Assumptions: https://scu-it.atlassian.net/wiki/x/hIBCPg
  
  - Domain Model and Wireframes: https://scu-it.atlassian.net/wiki/x/joBCPg
  
  - Test Plan: https://scu-it.atlassian.net/wiki/x/l4BCPg
  
  - Technology Stack Selection: https://scu-it.atlassian.net/wiki/x/ZgBEPg
