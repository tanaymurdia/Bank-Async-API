# Bank Async API

## Overview

The **Bank Async API** is designed to facilitate secure and efficient banking transactions, such as creating accounts and transferring money, through a RESTful API. It uses FastAPI for asynchronous handling, ensuring high-performance execution.

## Features

- **User Authentication**: Manage user sessions and access control.
- **Create Customers and Accounts**: APIs to create new customers and accounts.
- **Transfer Funds**: Securely transfer funds between accounts.
- **Balance Inquiry**: Check the balance of a specific account.
- **Transaction History**: Access past transactions for an account.
  
## Technologies Used

- **FastAPI** for building the web API
- **SQLAlchemy** for ORM and database interactions
- **PostgreSQL** as the database with **asyncpg** as the driver
- **OAuth2 Password Flow** for user authentication
- **Logging** for system operations and tracing

## Setup and Installation

### Prerequisites

- Docker (for containerization)

### Environment Setup

1. **Configure Environment Variables**

   Create a `.env` file in the root directory and set your environment variables:

   ```env
   POSTGRES_USER=user
   POSTGRES_PASSWORD=password
   POSTGRES_DB=bankdb
   DATABASE_URL=postgresql+asyncpg://user:password@db:5432/bankdb
   SECRET_KEY=x9pL4y5JtOq-lesNbsfZav4UPqvKHJ6o1aPYonhasdA
   LOGGING_LEVEL=INFO
   ```

### Running with Docker

1. Build and Run the Container

   ```bash
   docker-compose up --build
   ```

## API Endpoints

### Authentication

- **POST /token**
  - Description: Obtain an access token using username and password.
  - Request: JSON body containing `username` and `password`.
  - The username should be `user` and the password should be `password`

### Customer Management

- **POST /customers/**
  - Description: Create a new customer.
  - Request: JSON body with `name`.

### Account Management

- **POST /accounts/**
  - Description: Create a new bank account for a customer.
  - Request: JSON body with `customer_id` and `initial_deposit`.
  
- **GET /accounts/{account_id}/balance**
  - Description: Retrieve the balance of an account.
  - Request: Account ID as path parameter.

- **GET /accounts/{account_id}/history**
  - Description: Retrieve the transaction history of an account.
  - Request: Account ID as path parameter.

### Transactions

- **POST /transfer/**
  - Description: Transfer funds between two accounts.
  - Request: JSON body with `from_account_id`, `to_account_id`, and `amount`.

## Future Expansion Ideas

1. **Microservice Architecture**:
   - As the project evolves, consider decomposing into smaller services using an event-driven architecture (e.g., using RabbitMQ or Kafka).

2. **Real-time Notifications**:
   - Implement WebSockets for real-time client notifications about transaction status changes.

3. **Third-party API Integrations**:
   - Expand to include integrations with third-party banking APIs for enhanced financial data access.

4. **Enhanced Analytics**:
   - Integrate a data analytics platform to allow users to gain deeper insights from their transaction histories.
   - Use tools like Apache Spark or Google BigQuery for large-scale data processing.
