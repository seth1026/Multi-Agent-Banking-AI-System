import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team.team import Team
from agno.models.azure import AzureOpenAI
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.storage.sqlite import SqliteStorage

# Import all specialized master agents
from agents.accounts.AccountMasterAgent import account_master_agent, initialize_knowledge_base as init_accounts_kb
from agents.cards.CardsMasterAgent import CardMasterAgent, initialize_shared_knowledge_base as init_cards_kb
from agents.transactions.TransactionMasterAgent import TransactionMasterAgent, initialize_shared_knowledge_base as init_transactions_kb
from agents.loansAndInsurance.LoansInvestmentsMasterAgent import LoansAndInvestmentMasterAgent, initialize_shared_knowledge_base as init_loans_kb
from agents.payeesRecurringPayments.PayeesRecurringPaymentsMasterAgent import PayeeRecurringPaymentMasterAgent, initialize_shared_knowledge_base as init_payees_kb
from agents.miscellaneous.MiscellaneousBankingMasterAgent import BankingServicesMasterAgent, initialize_shared_knowledge_base as init_misc_kb

# Load environment variables
load_dotenv()

# Initialize persistent memory and storage for the main agent
main_memory_db = SqliteMemoryDb(
    table_name="main_agent_memories", 
    db_file="tmp/main_banking_agent.db"
)

main_memory = Memory(
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    db=main_memory_db,
    delete_memories=False,  # Keep memories for better context
    clear_memories=False,   # Don't clear memories on restart
)

main_storage = SqliteStorage(
    table_name="main_agent_sessions", 
    db_file="tmp/main_banking_agent.db"
)

# Create the Main Banking Master Agent Team with routing
MainBankingMasterAgent = Team(
    name="Main Banking Master Agent",
    mode="route",  # Route mode to direct queries to appropriate agents
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    members=[
        account_master_agent,           # Account profiles, balances, deposits
        CardMasterAgent,                # Credit/debit cards, limits, rewards
        TransactionMasterAgent,         # Transaction history, transfers
        LoansAndInvestmentMasterAgent,  # Loans, EMIs, investments, insurance
        PayeeRecurringPaymentMasterAgent, # Payees, recurring payments
        BankingServicesMasterAgent,     # General banking services
    ],
    memory=main_memory,
    storage=main_storage,
    add_history_to_messages=True,
    num_history_runs=5,
    show_tool_calls=True,
    markdown=True,
    instructions=[
        "You are the Main Banking Master Agent that intelligently routes banking queries to specialized agents.",
        "Analyze the user's query and determine which specialized agent can best handle the request:",
        "",
        "Route to Account Master Agent for:",
        "- Account balances, profiles, and holder information",
        "- IFSC codes, branch details, and account status",
        "- Fixed deposits, savings accounts, current accounts",
        "- KYC status and account opening details",
        "- Overdraft facilities and account limits",
        "",
        "Route to Card Master Agent for:",
        "- Credit card and debit card information",
        "- Card limits, available credit, and cash limits",
        "- Card statements, billing cycles, and due dates",
        "- Reward points, programs, and redemptions",
        "- Card controls, international usage, and security settings",
        "",
        "Route to Transaction Master Agent for:",
        "- Transaction history and payment details",
        "- UPI transfers, NEFT, RTGS transactions",
        "- Spending analysis and categorization",
        "- Merchant transactions and e-commerce purchases",
        "- Transaction status and reference numbers",
        "",
        "Route to Loans & Investment Master Agent for:",
        "- Home loans, personal loans, and EMI details",
        "- Loan balances, interest rates, and repayment schedules",
        "- Mutual funds, SIP investments, and portfolio performance",
        "- Insurance policies (life, health, motor)",
        "- Investment valuations and returns",
        "",
        "Route to Payees & Recurring Payments Master Agent for:",
        "- Registered payees and beneficiaries",
        "- Recurring payments, SIP mandates, and subscriptions",
        "- UPI IDs, account details of payees",
        "- Payment schedules and mandate management",
        "- Bill payments and utility connections",
        "",
        "Route to Banking Services Master Agent for:",
        "- Credit scores and bureau information",
        "- Account alerts and notifications",
        "- Transaction limits and daily limits",
        "- Disputes, claims, and customer service issues",
        "- Document downloads and account statements",
        "- General banking queries not covered by other agents",
        "",
        "For complex queries spanning multiple areas, route to the most relevant primary agent.",
        "Always maintain conversation context and remember user preferences.",
        "If the query is unclear, ask clarifying questions to route correctly.",
        "Provide comprehensive responses by leveraging the specialized knowledge of each agent.",
    ],
    show_members_responses=True,  # Show which agent responded
)

# Initialize all knowledge bases
def initialize_all_knowledge_bases():
    """Initialize all knowledge bases for the specialized agents"""
    try:
        print("Initializing all knowledge bases...")
        
        # Initialize each agent's knowledge base
        init_accounts_kb()
        print("✅ Account Master Agent knowledge base initialized")
        
        init_cards_kb()
        print("✅ Card Master Agent knowledge base initialized")
        
        init_transactions_kb()
        print("✅ Transaction Master Agent knowledge base initialized")
        
        init_loans_kb()
        print("✅ Loans & Investment Master Agent knowledge base initialized")
        
        init_payees_kb()
        print("✅ Payees & Recurring Payments Master Agent knowledge base initialized")
        
        init_misc_kb()
        print("✅ Banking Services Master Agent knowledge base initialized")
        
        print("🎉 All knowledge bases initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing knowledge bases: {e}")

# Helper function for interactive chat
def chat_with_main_agent(user_id: str = "main_user"):
    """Interactive chat with the main banking master agent"""
    print("🏦 Welcome to the Main Banking Master Agent!")
    print("I can help you with all your banking needs by routing your queries to specialized agents:")
    print("• 🏦 Account Management - Balances, profiles, deposits")
    print("• 💳 Card Services - Credit/debit cards, limits, rewards")
    print("• 💸 Transaction History - Transfers, payments, spending analysis")
    print("• 📈 Loans & Investments - EMIs, mutual funds, insurance")
    print("• 🔄 Payees & Payments - Recurring payments, beneficiaries")
    print("• 🛠️ Banking Services - Credit scores, alerts, general queries")
    print("\nType 'exit' to quit\n")
    
    while True:
        try:
            user_input = input(f"\n💬 {user_id}: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Thank you for using the Main Banking Master Agent!")
                break
                
            if not user_input:
                continue
                
            # Get response from main agent team
            print(f"\n🤖 Banking Agent Team:")
            MainBankingMasterAgent.print_response(
                user_input,
                user_id=user_id,
                stream=True
            )
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize all knowledge bases
    initialize_all_knowledge_bases()
    
    print("\n" + "="*60)
    print("MAIN BANKING MASTER AGENT - ROUTING DEMO")
    print("="*60)
    
    # Test different types of queries to demonstrate routing
    test_queries = [
        "What is my current account balance?",  # Should route to Account Master Agent
        "Show me my credit card statement",     # Should route to Card Master Agent
        "What are my recent UPI transactions?", # Should route to Transaction Master Agent
        "When is my next EMI due?",            # Should route to Loans & Investment Agent
        "Show me my registered payees",        # Should route to Payees Agent
        "What is my credit score?",            # Should route to Banking Services Agent
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")
        print("-" * 50)
        try:
            MainBankingMasterAgent.print_response(
                query,
                user_id="demo_user",
                stream=True
            )
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)
    
    # Start interactive mode
    print("\nStarting interactive mode...")
    chat_with_main_agent("banking_user")