# Banking Master Agents API

This API provides endpoints for all banking master agents, allowing you to interact with specialized banking agents through HTTP requests.

## Available Agents

- **AccountMasterAgent** (`/accounts/chat`) - Account profiles, balances, deposits
- **CardMasterAgent** (`/cards/chat`) - Credit/debit cards, limits, rewards
- **TransactionMasterAgent** (`/transactions/chat`) - Transaction history, transfers
- **LoansInvestmentsMasterAgent** (`/loans/chat`) - Loans, EMIs, investments
- **PayeesRecurringPaymentsMasterAgent** (`/payees/chat`) - Payees, recurring payments
- **MiscellaneousBankingMasterAgent** (`/miscellaneous/chat`) - General banking queries

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure your `.env` file is configured with Azure OpenAI credentials

3. Run the API server:
```bash
python api.py
```

4. Access the API at `http://localhost:8000`

## API Endpoints

### General Chat (Auto-routing)
```
POST /chat
```
Automatically routes your query to the most appropriate agent.

### Specific Agent Endpoints
```
POST /accounts/chat
POST /cards/chat
POST /transactions/chat
POST /loans/chat
POST /payees/chat
POST /miscellaneous/chat
```

### Request Format
```json
{
  "message": "Show me my account balance",
  "user_id": "user123",
  "session_id": "optional_session_id"
}
```

### Response Format
```json
{
  "response": "Agent response here...",
  "agent_name": "AccountMasterAgent",
  "user_id": "user123",
  "session_id": "user123_accounts_session"
}
```

### Other Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /agents` - List all available agents

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## Example Usage

```bash
# Using curl
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is my account balance?", "user_id": "user123"}'

# Using Python requests
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Show me my credit card details",
        "user_id": "user123"
    }
)
print(response.json())
```