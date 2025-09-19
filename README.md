# 📱 MewbileTech Customer Call Management System

## Overview

This project is a Python-based telecom management system that simulates how a phone company could track and visualize customer call history, contracts, and billing.

The system:
  - Reads historic call records from a dataset (JSON format).
  - Tracks customers, phone lines, and contracts (Month-to-Month, Term, and Prepaid).
  - Supports billing with free minutes, deposits, and prepaid balances.
  - Provides visualizations of calls on a real map of Toronto using Pygame.
  - Implements filters (by customer, location, call duration) and monthly bill viewing.
  - Includes an optional parallel filtering mode (multi-threading) to demonstrate performance improvements.

This was developed as part of CSC148: Introduction to Computer Science (University of Toronto).
⚠️ Note: Some starter code and specifications were provided by the course instructors. This repository is for educational and portfolio purposes only and should not be reused for academic submission.

## Features
- Customer & Phone Line Management: Each customer has unique phone lines linked to contracts.

- Contract Types:
   - Month-to-Month (MTM): No term, higher rates, no free minutes.
   - Term Contract: Lower rates, free minutes, refundable deposit at completion.
   - Prepaid Contract: Pay in advance, automatic top-ups, balance tracking.

- Billing System: Generates monthly bills, including costs, free minutes, deposits, and balances.

- Call Tracking: Records incoming and outgoing calls, including:
  - Source and destination numbers
  - Date/time and duration
  - Geographic locations (longitude/latitude)
- Visualization: Displays calls on a Toronto map with sprites for start/end points.

Filtering:
  - By customer ID
  - By duration (greater/less than)
  - By location
  - Reset all filters

### Getting Started
Install dependencies:
```
pip install pygame pytest
```

### Running the Application
```
python application.py
```
Opens a Toronto map window.
Displays all customer calls visually.
Use keybinds to filter data:
  - C – filter by customer ID
  - D – filter by duration
  - L – filter by location
  - R – reset filters
  - M – display monthly bill
  - X – quit application
