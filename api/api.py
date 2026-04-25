import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv

# Add the parent directory to the path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all master agents
from agents.accounts.AccountMasterAgent import account_master_agent, initialize_knowledge_base as init_accounts_kb
from agents.cards.CardsMasterAgent import CardMasterAgent, initialize_shared_knowledge_base as init_cards_kb
from agents.transactions.TransactionMasterAgent import TransactionMasterAgent, initialize_shared_knowledge_base as init_transactions_kb
from agents.loansAndInsurance.LoansInvestmentsMasterAgent import LoansAndInvestmentMasterAgent, initialize_shared_knowledge_base as init_loans_kb
from agents.payeesRecurringPayments.PayeesRecurringPaymentsMasterAgent import PayeeRecurringPaymentMasterAgent, initialize_shared_knowledge_base as init_payees_kb
from agents.miscellaneous.MiscellaneousBankingMasterAgent import BankingServicesMasterAgent, initialize_shared_knowledge_base as init_misc_kb
from agents.mainMasterAgent import MainBankingMasterAgent, initialize_all_knowledge_bases as init_main_kb

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Banking Master Agents API",
    description="API endpoints for all banking master agents",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "api_user"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_name: str
    user_id: str
    session_id: Optional[str] = None

# Initialize all knowledge bases on startup
@app.on_event("startup")
async def startup_event():
    """Initialize all knowledge bases when the API starts"""
    try:
        print("Initializing all knowledge bases...")
        # Initialize main agent (which initializes all sub-agents)
        init_main_kb()
        print("All knowledge bases initialized successfully!")
    except Exception as e:
        print(f"Error initializing knowledge bases: {e}")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Banking Master Agents API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "All agents are ready"}

# Main Banking Master Agent endpoint (with intelligent routing)
@app.post("/chat", response_model=ChatResponse)
async def chat_with_main_agent(request: ChatRequest):
    """Chat with the Main Banking Master Agent - intelligently routes to appropriate specialized agents"""
    try:
        session_id = request.session_id or f"{request.user_id}_main_session"
        
        response = MainBankingMasterAgent.run(
            message=request.message,
            user_id=request.user_id,
            stream=False
        )
        
        return ChatResponse(
            response=response.content,
            agent_name="MainBankingMasterAgent",
            user_id=request.user_id,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Account Master Agent endpoints
@app.post("/accounts/chat", response_model=ChatResponse)
async def chat_with_accounts_agent(request: ChatRequest):
    """Chat with the Account Master Agent for account-related queries"""
    try:
        session_id = request.session_id or f"{request.user_id}_accounts_session"
        
        response = account_master_agent.run(
            message=request.message,
            user_id=request.user_id,
            stream=False
        )
        
        return ChatResponse(
            response=response.content,
            agent_name="AccountMasterAgent",
            user_id=request.user_id,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Cards Master Agent endpoints
@app.post("/cards/chat", response_model=ChatResponse)
async def chat_with_cards_agent(request: ChatRequest):
    """Chat with the Cards Master Agent for card-related queries"""
    try:
        session_id = request.session_id or f"{request.user_id}_cards_session"
        
        response = CardMasterAgent.run(
            message=request.message,
            user_id=request.user_id,
            stream=False
        )
        
        return ChatResponse(
            response=response.content,
            agent_name="CardMasterAgent",
            user_id=request.user_id,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Transaction Master Agent endpoints
@app.post("/transactions/chat", response_model=ChatResponse)
async def chat_with_transactions_agent(request: ChatRequest):
    """Chat with the Transaction Master Agent for transaction-related queries"""
    try:
        session_id = request.session_id or f"{request.user_id}_transactions_session"
        
        response = TransactionMasterAgent.run(
            message=request.message,
            user_id=request.user_id,
            stream=False
        )
        
        return ChatResponse(
            response=response.content,
            agent_name="TransactionMasterAgent",
            user_id=request.user_id,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Loans & Investments Master Agent endpoints
@app.post("/loans/chat", response_model=ChatResponse)
async def chat_with_loans_agent(request: ChatRequest):
    """Chat with the Loans & Investments Master Agent for loans and investment queries"""
    try:
        session_id = request.session_id or f"{request.user_id}_loans_session"
        
        response = LoansAndInvestmentMasterAgent.run(
            message=request.message,
            user_id=request.user_id,
            stream=False
        )
        
        return ChatResponse(
            response=response.content,
            agent_name="LoansAndInvestmentMasterAgent",
            user_id=request.user_id,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Payees & Recurring Payments Master Agent endpoints
@app.post("/payees/chat", response_model=ChatResponse)
async def chat_with_payees_agent(request: ChatRequest):
    """Chat with the Payees & Recurring Payments Master Agent"""
    try:
        session_id = request.session_id or f"{request.user_id}_payees_session"
        
        response = PayeeRecurringPaymentMasterAgent.run(
            message=request.message,
            user_id=request.user_id,
            stream=False
        )
        
        return ChatResponse(
            response=response.content,
            agent_name="PayeeRecurringPaymentMasterAgent",
            user_id=request.user_id,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Miscellaneous Banking Master Agent endpoints
@app.post("/miscellaneous/chat", response_model=ChatResponse)
async def chat_with_miscellaneous_agent(request: ChatRequest):
    """Chat with the Miscellaneous Banking Master Agent for general banking queries"""
    try:
        session_id = request.session_id or f"{request.user_id}_misc_session"
        
        response = BankingServicesMasterAgent.run(
            message=request.message,
            user_id=request.user_id,
            stream=False
        )
        
        return ChatResponse(
            response=response.content,
            agent_name="BankingServicesMasterAgent",
            user_id=request.user_id,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


# Get available agents
@app.get("/agents")
async def get_available_agents():
    """Get list of available agents and their descriptions"""
    return {
        "main_agent": {
            "name": "MainBankingMasterAgent",
            "endpoint": "/chat",
            "description": "Intelligent routing agent that automatically directs queries to the most appropriate specialized banking agent"
        },
        "specialized_agents": [
            {
                "name": "AccountMasterAgent",
                "endpoint": "/accounts/chat",
                "description": "Handles account profiles, balances, and deposit information"
            },
            {
                "name": "CardMasterAgent", 
                "endpoint": "/cards/chat",
                "description": "Manages credit/debit cards, limits, rewards, and controls"
            },
            {
                "name": "TransactionMasterAgent",
                "endpoint": "/transactions/chat", 
                "description": "Processes transaction history, transfers, and payment queries"
            },
            {
                "name": "LoansAndInvestmentMasterAgent",
                "endpoint": "/loans/chat",
                "description": "Handles loans, EMIs, investments, and insurance queries"
            },
            {
                "name": "PayeeRecurringPaymentMasterAgent",
                "endpoint": "/payees/chat",
                "description": "Manages payees, beneficiaries, and recurring payments"
            },
            {
                "name": "BankingServicesMasterAgent",
                "endpoint": "/miscellaneous/chat",
                "description": "Handles general banking queries and miscellaneous services"
            }
        ]
    }

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )