# 🏦 Intelligent Banking Agent System

Hey there! Welcome to the **Banking Master Agent** project.

This isn't just another chatbot; it's a **multi-agent system** designed to handle complex banking queries by routing them to specialized experts. Instead of one giant AI trying to know everything, we have a team of agents working together, orchestrated by a "Main Master Agent."

Think of it like walking into a bank branch: you talk to the receptionist (Main Agent), and they direct you to the loan officer, the teller, or the investment advisor depending on what you need.

## 🧠 The "Brain" Behind It

The core logic is built using **Agno** (formerly Phidata) and **Azure OpenAI**. We use a **Hub & Spoke** architecture:

*   **Main Banking Master Agent**: The router. It listens to your request and decides who can help you best.
*   **Specialized Agents**:
    *   **💰 Accounts**: Balances, deposits, KYC, account details.
    *   **💳 Cards**: Credit/debit limits, rewards, statements.
    *   **💸 Transactions**: History, UPI, NEFT/RTGS transfers.
    *   **📈 Loans & Investments**: EMIs, mutual funds, insurance.
    *   **🔄 Payees**: Managing beneficiaries and recurring payments.
    *   **🛠️ Services**: General queries, credit scores, support.

Each agent has its own "knowledge base" so it doesn't hallucinate answers about things it shouldn't know.

## 🚀 Getting Started

You'll need **Python 3.10+** and **Node.js** installed.

### 1. Backend Setup (The Brains)

First, let's get the agents running.

```bash
# Clone the repo (if you haven't already)
git clone <repo-url>
cd "Banking Agent/Agents"

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Configuration:**
You need to set up your environment variables. Create a `.env` file in the `Agents` folder:

```env
AZURE_OPENAI_API_KEY=your_key_here
ENDPOINT=your_azure_endpoint
DEPLOYMENT=your_deployment_name
API_VERSION=your_api_version
```

**Run the API:**
```bash
python api/api.py
```
The backend will start humming at `http://localhost:8000`. You can check the health at `http://localhost:8000/docs`.

### 2. Frontend Setup (The Face)

Now for the UI. Open a new terminal:

```bash
cd frontend

# Install the node modules
npm install

# Start the React app
npm start
```

The app should pop up at `http://localhost:3000`.

## 🎮 How to Use It

Once both servers are running, just go to `http://localhost:3000`.

You'll see a dashboard with all the specialized agents. You can:
1.  **Chat with the Main Agent**: Just ask "What's my balance and when is my credit card bill due?" It will figure out it needs to talk to both the *Accounts* and *Cards* agents.
2.  **Select a Specific Agent**: If you know exactly what you want (e.g., "I need a loan"), click on the Loans agent to go straight to the source.

## 📂 Project Structure

Here's a quick map of the land:

*   `agents/`: The Python code for all the intelligent agents.
    *   `mainMasterAgent.py`: The big boss that routes everything.
    *   `accounts/`, `cards/`, etc.: The specialized agent logic.
*   `api/`: The FastAPI backend that connects the agents to the world.
*   `frontend/`: The React application for the user interface.
*   `knowledge/`: Documents and data that the agents "read" to learn about banking rules.

## 🛠️ Tech Stack

*   **AI/LLM**: Azure OpenAI (GPT-4o or similar)
*   **Orchestration**: Agno (Phidata)
*   **Backend**: FastAPI, Python
*   **Frontend**: React, Node.js
*   **Database**: SQLite (for agent memory and sessions)


