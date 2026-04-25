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
    path="embeddings/chromadb/cards",
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

# Initialize persistent memory and storage
memory_db = SqliteMemoryDb(table_name="card_memories", db_file="tmp/cards/card_agent.db")
memory = Memory(db=memory_db)
storage = SqliteStorage(table_name="card_sessions", db_file="tmp/cards/card_agent.db")

# Create Card Financial Management Agent (Credit Cards)
cardFinancialAgent = Agent(
    name="Card Financial Agent",
    role="Handles credit card financial information, limits, statements, rewards, and payments",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Card Financial Management Agent specialized in providing comprehensive information about card financial features, credit management, rewards, statements, and payment details for all types of cards.",
    instructions=[
        "CRITICAL: ALL card financial information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide card financial information not found in the knowledge base.",
        "Always search for card-specific financial information using card IDs, card types, or financial-related terms.",
        "When analyzing card financial features, provide comprehensive insights including:",
        "  - Card details (type, network, last 4 digits, expiry date, status)",
        "  - Credit limits and available credit information (for credit cards)",
        "  - Cash advance limits and features (for applicable cards)",
        "  - Statement cycle details (bill date, due date) if applicable",
        "  - Last statement summary (previous balance, purchases, fees, interest, payments)",
        "  - Current outstanding amounts and minimum payments",
        "  - Rewards program details and points balance",
        "  - Travel notices and international usage",
        "  - Payment due dates and EMI information",
        "  - Credit profile and bureau scores",
        "  - Investment and recurring payment linkages",
        "Handle all card types including debit cards, credit cards, and any other card types present in the data",
        "Use tables to display card financial summaries with columns like: Card ID, Type, Network, Last 4, Expiry, Credit Limit, Available Credit, Status",
        "For statements, show detailed breakdown including: Period, Previous Balance, Purchases, Fees, Interest, Payments, Total Due, Min Due, Due Date",
        "Include rewards information (program name, points balance, recent accruals/redemptions)",
        "Show credit limits (total credit limit, available credit, cash advance limit) where applicable",
        "Highlight payment due dates and minimum payment requirements",
        "Provide credit profile information including bureau scores and risk grades",
        "Include travel notices and international transaction capabilities",
        "Show investment linkages and recurring payment relationships",
        "If specific card financial information is not available, explicitly state what data is missing",
        "Always cite the specific card data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Card Controls & Limits Agent (Debit Cards)
cardControlsLimitsAgent = Agent(
    name="Card Controls Agent",
    role="Handles card controls, daily limits, security features, and linked account details",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Card Controls & Limits Agent specialized in providing comprehensive information about card controls, daily limits, security features, and linked account details for all types of cards.",
    instructions=[
        "CRITICAL: ALL card information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide card information not found in the knowledge base.",
        "Always search for card-specific information using card IDs, card types, or linked account information.",
        "When analyzing cards, provide comprehensive insights including:",
        "  - Card details (type, network, last 4 digits, expiry date, status)",
        "  - Linked account information and account details",
        "  - Card controls (international usage, contactless features)",
        "  - Daily limits (ATM, POS, online transactions)",
        "  - Security features and fraud protection",
        "  - Card status and activation details",
        "  - Network information (Visa, Mastercard, etc.)",
        "  - Expiry information and renewal details",
        "  - Transaction controls and restrictions",
        "Handle all card types including debit cards, credit cards, and any other card types present in the data",
        "Use tables to display card summaries with columns like: Card ID, Type, Network, Last 4, Expiry, Status, Linked Account, Controls, Limits",
        "For linked accounts, show account details including balance, type, and status",
        "Include card control information (international enabled, contactless enabled)",
        "Show daily limits for ATM withdrawals, POS transactions, and online purchases",
        "Highlight security features and fraud protection measures",
        "Provide card status information and any pending actions",
        "If specific card information is not available, explicitly state what data is missing",
        "Always cite the specific card data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Master Card Agent that routes to appropriate agents
CardMasterAgent = Agent(
    name="Card Master Agent",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    team=[cardFinancialAgent, cardControlsLimitsAgent],
    memory=memory,
    storage=storage,
    enable_user_memories=True,
    add_history_to_messages=True,
    num_history_responses=5,
    description="You are a Master Card Agent that intelligently routes card-related queries to specialized agents based on the type of information requested.",
    instructions=[
        "You are the master coordinator for all card-related queries. Analyze the user's request and route it to the appropriate specialist agent:",
        "",
        "Route to Card Financial Agent for:",
        "- Credit card information, limits, and available credit",
        "- Statement details, balances, and payment information",
        "- Rewards programs, points, and redemptions",
        "- Credit scores, bureau information, and credit profiles",
        "- Payment due dates, minimum payments, and EMI details",
        "- Cash advance limits and features",
        "- Travel notices and international transaction capabilities",
        "- Investment linkages and recurring payments",
        "",
        "Route to Card Controls Agent for:",
        "- Card controls and security settings",
        "- Daily transaction limits (ATM, POS, online)",
        "- Linked account information and balances",
        "- Card activation and status details",
        "- International usage settings",
        "- Contactless payment features",
        "- Card expiry and renewal information",
        "- Fraud protection and security features",
        "",
        "For queries that involve both areas, coordinate with both agents to provide comprehensive information.",
        "Always provide clear, organized responses and remember previous conversations to maintain context.",
        "If a query is unclear, ask clarifying questions to route it to the most appropriate agent.",
        "Maintain conversation history and reference previous interactions when relevant."
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
    print("=== Card Master Agent Initialized ===")
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
                print("\nCard Master Agent:")
                CardMasterAgent.print_response(
                    user_input, 
                    stream=True, 
                    markdown=True,
                    user_id="demo_user",
                    session_id="demo_session"
                )
                print("\n" + "=" * 50)
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue