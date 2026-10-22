# Enterprise Operations & Procurement Suite (EOPS)

**An Odoo 19 modular solution for enterprise operations, procurement, inventory, and finance.**

## Overview

Enterprise Operations & Procurement Suite (EOPS) is a modular Odoo 19 project designed to organize enterprise procurement processes and connect related business operations through dedicated Odoo addons.

The project is structured into five modules, providing a foundation for managing core operations, purchase requests, procurement activities, inventory processes, and financial workflows.

## Modules

| Module | Description |
|---|---|
| `eops_core` | Core functionality shared across the EOPS suite. |
| `eops_purchase_request` | Manages purchase requests as part of the procurement workflow. |
| `eops_procurement` | Supports procurement operations and tender-related processes. |
| `eops_inventory` | Connects procurement activities with inventory operations. |
| `eops_finance` | Supports the financial processes associated with procurement. |

## Key Objectives

- Organize enterprise procurement workflows.
- Separate business functionality into reusable Odoo addons.
- Connect purchase requests, procurement, inventory, and finance processes.
- Apply Odoo's modular architecture and ORM framework.
- Provide a maintainable foundation for future enhancements.

## Technology Stack

- **ERP Framework:** Odoo 19
- **Programming Language:** Python
- **Database:** PostgreSQL
- **Data and UI:** XML
- **Version Control:** Git and GitHub

## Project Structure

```text
enterprise-operations-procurement-suite/
├── eops_core/
├── eops_purchase_request/
├── eops_procurement/
├── eops_inventory/
└── eops_finance/
```

Each addon contains its own module structure and implementation files.

## Installation

### Prerequisites

- Odoo 19
- PostgreSQL
- Git

### Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/IbrahemIsbieh/Enterprise-Operations-Procurement-Suite
   ```

2. Copy the five addon directories into a directory included in your Odoo `addons_path`, or configure the repository path directly in your Odoo configuration.

3. Restart the Odoo server.

4. Log in to Odoo and enable Developer Mode.

5. Open **Apps**, update the Apps List, and install the required EOPS modules according to their dependencies.


## Testing

The project workflows have been tested in the development environment. For a new installation, verify module dependencies and configuration before running the suite.

## Project Goals

This project is part of a practical Odoo 19 development portfolio, demonstrating modular addon development and the integration of enterprise procurement-related workflows.

## Author

**Ibrahem Issa**

## License

See the individual module manifests and repository files for the applicable license information.
