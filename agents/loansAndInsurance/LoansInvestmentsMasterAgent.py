import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.knowledge.json import JSONKnowledgeBase
from agno.models.azure import AzureOpenAI
from agno.tools.reasoning import ReasoningTools
from agno.embedder.azure_openai import AzureOpenAIEmbedder
from agno.vectordb.chroma import ChromaDb
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.storage.sqlite import SqliteStorage

# Load environment variables from .env file
load_dotenv()

# Initialize single persistent ChromaDB for shared knowledge base
shared_vector_db = ChromaDb(
    collection="banking_data_info",
    path="embeddings/chromadb/loansAndInvestment",
    persistent_client=True,
    embedder=AzureOpenAIEmbedder(
        api_key=os.getenv("EMBEDDING_API_KEY"),
        azure_endpoint=os.getenv("EMBEDDING_ENDPOINT"),
        azure_deployment=os.getenv("EMBEDDING_DEPLOYMENT")
    )
)

# Create single shared JSON knowledge base
shared_knowledge_base = JSONKnowledgeBase(
    path="knowledge/CORE_BANKING_DATA.json",
    vector_db=shared_vector_db,
    num_documents=10,
)

# Initialize persistent memory and storage for loans & investments
loans_memory_db = SqliteMemoryDb(table_name="loans_investment_memories", db_file="tmp/loansInvestment/loans_investment_agent.db")
loans_memory = Memory(db=loans_memory_db)
loans_storage = SqliteStorage(table_name="loans_investment_sessions", db_file="tmp/loansInvestment/loans_investment_agent.db")

# Create Loans Management Agent
loansManagementAgent = Agent(
    name="Loans Management Agent",
    role="Handles loan information, EMI details, payment schedules, and loan status",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Loans Management Agent specialized in providing comprehensive information about loans, EMI details, payment schedules, loan status, and financial planning.",
    instructions=[
        "CRITICAL: ALL loan information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide loan information not found in the knowledge base.",
        "Always search for loan-specific information using loan IDs, loan types, or loan-related terms.",
        "When analyzing loans, provide comprehensive insights including:",
        "  - Loan details (ID, type, lender, sanction amount, principal, outstanding principal)",
        "  - Interest rates and rate types (fixed, floating, APR)",
        "  - Loan terms and tenure (months, origination date, maturity date)",
        "  - EMI details (amount, next EMI date, payment schedule)",
        "  - Payment schedule breakdown (principal, interest, fees, total due)",
        "  - Loan status and current position",
        "  - Collateral information (property details, security)",
        "  - Outstanding balance and remaining tenure",
        "  - Prepayment options and charges",
        "  - Loan account status and any pending actions",
        "Handle all types of loans including:",
        "  - Home loans (property loans, mortgage details)",
        "  - Personal loans (unsecured loans, consumer loans)",
        "  - Business loans and commercial financing",
        "  - Vehicle loans and auto financing",
        "  - Education loans and student financing",
        "Use tables to display loan summaries with columns like: Loan ID, Type, Lender, Sanction Amount, Outstanding Principal, Rate, EMI, Next Due, Status",
        "For payment schedules, show detailed breakdown including: Due Date, Principal Component, Interest Component, Fees, Total Due, Status",
        "Include loan status information (active, closed, overdue, etc.)",
        "Show outstanding principal and remaining tenure calculations",
        "Highlight next EMI due dates and amounts",
        "Provide collateral information and security details",
        "Include prepayment options and any applicable charges",
        "Show loan account status and any pending actions",
        "If specific loan information is not available, explicitly state what data is missing",
        "Always cite the specific loan data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Investments & Insurance Agent
investmentsInsuranceAgent = Agent(
    name="Investments & Insurance Agent",
    role="Handles investment portfolios, mutual funds, insurance policies, and financial planning",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are an Investments & Insurance Agent specialized in providing comprehensive information about investment portfolios, mutual funds, insurance policies, and financial planning.",
    instructions=[
        "CRITICAL: ALL investment and insurance information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide investment/insurance information not found in the knowledge base.",
        "Always search for investment/insurance-specific information using investment IDs, insurance policy numbers, or related terms.",
        "When analyzing investments and insurance, provide comprehensive insights including:",
        "  - Investment portfolio details (mutual funds, fixed deposits, other investments)",
        "  - Mutual fund information (provider, folio, holdings, NAV, units, valuation)",
        "  - Fixed deposit details (principal, interest rates, maturity, auto-renewal)",
        "  - Insurance policies (life, health, motor, policy numbers, coverage)",
        "  - Policy details (sum assured, premium, frequency, start/end dates)",
        "  - Investment performance and valuation",
        "  - SIP transactions and investment history",
        "  - Insurance coverage and benefits",
        "  - Policy status and renewal information",
        "  - Investment account linkages and relationships",
        "Handle all types of investments and insurance including:",
        "  - Mutual funds (equity, debt, hybrid, international)",
        "  - Fixed deposits and term deposits",
        "  - Life insurance (term, whole life, endowment)",
        "  - Health insurance (family floater, individual)",
        "  - Motor insurance (car, bike, commercial)",
        "  - Investment SIPs and systematic investments",
        "Use tables to display investment summaries with columns like: Investment ID, Type, Provider, Current Value, Units/Principal, NAV/Rate, Status",
        "For mutual funds, show detailed holdings including: Fund Name, ISIN, Units, Avg NAV, Current NAV, Valuation",
        "For insurance policies, show: Policy Number, Type, Insurer, Sum Assured, Premium, Frequency, Status",
        "Include investment performance metrics and current valuations",
        "Show SIP transaction history and investment patterns",
        "Highlight insurance coverage details and policy benefits",
        "Provide policy renewal information and premium due dates",
        "Show investment account linkages and relationships",
        "Include tax implications and compliance information",
        "If specific investment/insurance information is not available, explicitly state what data is missing",
        "Always cite the specific investment/insurance data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Master Loans & Investment Agent that routes to appropriate agents
LoansAndInvestmentMasterAgent = Agent(
    name="Loans & Investment Master Agent",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    team=[loansManagementAgent, investmentsInsuranceAgent],
    memory=loans_memory,
    storage=loans_storage,
    enable_user_memories=True,
    add_history_to_messages=True,
    num_history_responses=5,
    description="You are a Master Loans & Investment Agent that intelligently routes loan and investment-related queries to specialized agents based on the type of information requested.",
    instructions=[
        "You are the master coordinator for all loans and investment-related queries. Analyze the user's request and route it to the appropriate specialist agent:",
        "",
        "Route to Loans Management Agent for:",
        "- Loan details, EMI amounts, and outstanding balances",
        "- Home loans, personal loans, business loans, vehicle loans, education loans",
        "- Interest rates, loan terms, and tenure information",
        "- EMI payment schedules and next due dates",
        "- Loan status, collateral information, and security details",
        "- Prepayment options and loan account status",
        "- Payment schedule breakdowns (principal, interest, fees)",
        "- Loan origination dates, maturity dates, and remaining tenure",
        "",
        "Route to Investments & Insurance Agent for:",
        "- Investment portfolios, mutual funds, and fixed deposits",
        "- Mutual fund holdings, NAV, units, and valuations",
        "- SIP transactions and investment performance",
        "- Insurance policies (life, health, motor insurance)",
        "- Policy details, sum assured, premiums, and coverage",
        "- Investment account linkages and relationships",
        "- Policy renewal information and premium due dates",
        "- Tax implications and compliance information",
        "",
        "For queries that involve both loans and investments, coordinate with both agents to provide comprehensive financial information.",
        "Always provide clear, organized responses and remember previous conversations to maintain context.",
        "If a query is unclear, ask clarifying questions to route it to the most appropriate agent.",
        "Maintain conversation history and reference previous interactions when relevant.",
        "Focus on providing holistic financial planning insights when dealing with multiple financial products."
    ],
    show_tool_calls=True,
    markdown=True,
)

# Load shared knowledge base only once
def initialize_shared_knowledge_base():
    """Initialize shared knowledge base with persistent storage check"""
    try:
        if not os.path.exists("embeddings/chromadb"):
            os.makedirs("embeddings/chromadb", exist_ok=True)
        
        print("Loading shared banking knowledge base...")
        shared_knowledge_base.load(recreate=False)  # Don't recreate if exists
        print("Shared knowledge base loaded successfully!")
        
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        print("Recreating knowledge base...")
        shared_knowledge_base.load(recreate=True)

# Initialize shared knowledge base
initialize_shared_knowledge_base()

# Interactive mode
if __name__ == "__main__":
    print("=== Loans & Investment Master Agent Initialized ===")
    print("Shared knowledge base with persistent storage enabled.")
    print("Embeddings won't be regenerated on restart.")
    print()
    print("Starting interactive mode. Type 'exit' to quit.")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            
            if user_input:
                print("\nLoans & Investment Master Agent:")
                LoansAndInvestmentMasterAgent.print_response(
                    user_input, 
                    stream=True, 
                    markdown=True,
                    user_id="demo_user",
                    session_id="loans_investment_session"
                )
                print("\n" + "=" * 50)
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue