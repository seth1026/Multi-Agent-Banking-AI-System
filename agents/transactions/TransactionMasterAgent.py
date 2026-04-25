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
    collection="transactions_data_info",
    path="embeddings/chromadb/transactions",
    persistent_client=True,
    embedder=AzureOpenAIEmbedder(
        api_key=os.getenv("EMBEDDING_API_KEY"),
        azure_endpoint=os.getenv("EMBEDDING_ENDPOINT"),
        azure_deployment=os.getenv("EMBEDDING_DEPLOYMENT")
    )
)

# Create single shared JSON knowledge base
shared_knowledge_base = JSONKnowledgeBase(
    path="knowledge/TRANSACTIONS_DATA.json",
    vector_db=shared_vector_db,
    num_documents=10,
)

# Initialize persistent memory and storage for transactions
transaction_memory_db = SqliteMemoryDb(table_name="transaction_memories", db_file="tmp/transactions/transaction_agent.db")
transaction_memory = Memory(db=transaction_memory_db)
transaction_storage = SqliteStorage(table_name="transaction_sessions", db_file="tmp/transactions/transaction_agent.db")

# Create Card & Digital Payments Agent
cardDigitalPaymentsAgent = Agent(
    name="Card & Digital Payments Agent",
    role="Handles credit card transactions, digital payments, e-commerce activities, and international transactions",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Card & Digital Payments Agent specialized in providing detailed analysis of credit card transactions, digital payments, e-commerce activities, and international transactions.",
    instructions=[
        "CRITICAL: ALL card and digital payment information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide card transaction information not found in the knowledge base.",
        "Always search for card-specific information using card IDs, transaction IDs, or digital payment methods.",
        "When analyzing card and digital payments, provide comprehensive insights including:",
        "  - Credit card transaction analysis (spending, refunds, authorization codes)",
        "  - E-commerce tracking and online shopping patterns",
        "  - Merchant categories and MCC codes analysis",
        "  - Digital payment methods (UPI, IMPS, card transactions)",
        "  - International transactions and cross-border payments",
        "  - Currency conversions, exchange rates, and international fees",
        "  - Refund management and related transaction tracking",
        "  - Card security and transaction status monitoring",
        "  - Merchant location analysis and transaction geography",
        "Use tables to display card transaction summaries with columns like: Transaction ID, Date, Amount, Merchant, Category, Method, Status, Auth Code",
        "For e-commerce analysis, group by merchant categories and show spending patterns",
        "Include detailed merchant information (name, location, city, country, MCC codes)",
        "For international transactions, show original amounts, currencies, exchange rates, and fees",
        "Highlight card refunds and their relationship to original transactions",
        "Analyze digital payment method preferences and usage patterns",
        "Provide insights on card security and transaction authorization",
        "If specific card or digital payment information is not available, explicitly state what data is missing",
        "Always cite the specific transaction data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Financial Analytics & Reporting Agent
financialAnalyticsAgent = Agent(
    name="Financial Analytics Agent",
    role="Handles financial reporting, trend analysis, business intelligence, and predictive insights",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Financial Analytics & Reporting Agent specialized in providing comprehensive financial reporting, trend analysis, business intelligence, and predictive insights from transaction data.",
    instructions=[
        "CRITICAL: ALL financial and transaction information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide financial information not found in the knowledge base.",
        "Always search for financial data using transaction IDs, dates, categories, or account information.",
        "When providing financial analytics and reporting, deliver comprehensive insights including:",
        "  - Periodic financial reports (daily, weekly, monthly, yearly summaries)",
        "  - Trend analysis and spending patterns over time",
        "  - Investment tracking (SIP, mutual funds, recurring payments)",
        "  - Business intelligence and merchant performance analysis",
        "  - Location-based spending analysis and geographic patterns",
        "  - Compliance and audit-ready transaction categorization",
        "  - Cash flow forecasting and budget recommendations",
        "  - Financial health indicators and risk assessment",
        "  - Cross-account transaction analysis and portfolio overview",
        "Use professional financial reporting format with clear sections:",
        "  - Executive Summary",
        "  - Key Financial Metrics",
        "  - Detailed Analysis",
        "  - Trends and Patterns",
        "  - Recommendations and Insights",
        "Present data in tables with proper financial formatting (currency symbols, decimal places)",
        "For trend analysis, show period-over-period comparisons and growth rates",
        "Include visual indicators for positive/negative trends and significant changes",
        "Provide actionable insights and recommendations based on the data",
        "For investment analysis, track SIP transactions, fund performance, and portfolio allocation",
        "Always include data sources, calculation methods, and last updated timestamps",
        "If specific financial information is not available, explicitly state what data is missing",
        "Always cite the specific transaction data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Transaction Analysis Agent
transactionAnalysisAgent = Agent(
    name="Transaction Analysis Agent",
    role="Handles transaction analysis, spending patterns, financial insights, and business intelligence",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Transaction Analysis Agent specialized in providing comprehensive transaction analysis, spending patterns, financial insights, and business intelligence from transaction data.",
    instructions=[
        "CRITICAL: ALL transaction information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide transaction information not found in the knowledge base.",
        "Always search for transaction-specific information using transaction IDs, account IDs, card IDs, or transaction categories.",
        "When analyzing transactions, provide comprehensive insights including:",
        "  - Category-wise spending breakdown (Shopping, Food & Drink, Transfers, etc.)",
        "  - Income vs expenses analysis",
        "  - Payment method distribution (UPI, NEFT, RTGS, card transactions)",
        "  - Merchant analysis and transaction patterns",
        "  - Cash flow analysis and balance trends",
        "  - Cross-currency transactions and exchange rates",
        "  - Recurring transactions and standing instructions",
        "  - Transaction status and timing analysis",
        "Use tables to display transaction summaries with columns like: Transaction ID, Date, Amount, Category, Method, Status, Balance After",
        "For spending analysis, group by categories and show totals, percentages, and trends",
        "Include merchant information when available (name, location, MCC codes)",
        "For international transactions, show original amounts, exchange rates, and fees",
        "Always provide actionable insights and patterns from the transaction data",
        "If specific transaction information is not available, explicitly state what data is missing",
        "Always cite the specific transaction data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Master Transaction Agent that routes to appropriate agents
TransactionMasterAgent = Agent(
    name="Transaction Master Agent",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    team=[cardDigitalPaymentsAgent, financialAnalyticsAgent, transactionAnalysisAgent],
    memory=transaction_memory,
    storage=transaction_storage,
    enable_user_memories=True,
    add_history_to_messages=True,
    num_history_responses=5,
    description="You are a Master Transaction Agent that intelligently routes transaction-related queries to specialized agents based on the type of analysis or information requested.",
    instructions=[
        "You are the master coordinator for all transaction-related queries. Analyze the user's request and route it to the appropriate specialist agent:",
        "",
        "Route to Card & Digital Payments Agent for:",
        "- Credit card transaction analysis and spending",
        "- Digital payment methods (UPI, IMPS, card transactions)",
        "- E-commerce and online shopping analysis",
        "- International transactions and currency conversions",
        "- Merchant categories and MCC code analysis",
        "- Card refunds and authorization tracking",
        "- Cross-border payments and exchange rates",
        "- Card security and transaction status monitoring",
        "",
        "Route to Financial Analytics Agent for:",
        "- Periodic financial reports (monthly, yearly summaries)",
        "- Trend analysis and spending patterns over time",
        "- Investment tracking and SIP analysis",
        "- Business intelligence and performance analysis",
        "- Cash flow forecasting and budget recommendations",
        "- Financial health indicators and risk assessment",
        "- Compliance and audit-ready reporting",
        "- Professional financial reporting with executive summaries",
        "",
        "Route to Transaction Analysis Agent for:",
        "- Category-wise spending breakdown and analysis",
        "- Income vs expenses analysis",
        "- Payment method distribution analysis",
        "- Merchant analysis and transaction patterns",
        "- Cash flow analysis and balance trends",
        "- Recurring transaction identification",
        "- General transaction insights and patterns",
        "",
        "For complex queries that span multiple areas, coordinate with multiple agents to provide comprehensive analysis.",
        "Always provide clear, organized responses and remember previous conversations to maintain context.",
        "If a query is unclear, ask clarifying questions to route it to the most appropriate agent.",
        "Maintain conversation history and reference previous interactions when relevant.",
        "Focus on providing actionable financial insights when dealing with transaction data analysis."
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
        
        print("Loading shared transaction knowledge base...")
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
    print("=== Transaction Master Agent Initialized ===")
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
                print("\nTransaction Master Agent:")
                TransactionMasterAgent.print_response(
                    user_input, 
                    stream=True, 
                    markdown=True,
                    user_id="demo_user",
                    session_id="transaction_session"
                )
                print("\n" + "=" * 50)
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue