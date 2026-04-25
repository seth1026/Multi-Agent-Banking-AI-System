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
    path="embeddings/chromadb/recurrPayees",
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

# Initialize persistent memory and storage for payees & recurring payments
payee_memory_db = SqliteMemoryDb(table_name="payee_recurring_memories", db_file="tmp/recurrPayees/payee_recurring_agent.db")
payee_memory = Memory(db=payee_memory_db)
payee_storage = SqliteStorage(table_name="payee_recurring_sessions", db_file="tmp/recurrPayees/payee_recurring_agent.db")

# Create Payees Management Agent
payeesManagementAgent = Agent(
    name="Payees Management Agent",
    role="Handles payee information, billers, payment relationships, and beneficiary management",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Payees Management Agent specialized in providing comprehensive information about payees, billers, payment relationships, and beneficiary management.",
    instructions=[
        "CRITICAL: ALL payee and biller information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide payee information not found in the knowledge base.",
        "Always search for payee-specific information using payee IDs, names, types, or payment-related terms.",
        "When analyzing payees and billers, provide comprehensive insights including:",
        "  - Payee details (ID, name, type, status)",
        "  - Payment method information (UPI, account details, biller codes)",
        "  - Account relationships and linked accounts",
        "  - Biller information (biller codes, biller types)",
        "  - Payment status and history",
        "  - Beneficiary relationships and nominee details",
        "  - UPI handles and virtual payment addresses",
        "  - Account number masking and security",
        "  - IFSC codes and bank information",
        "  - Payment preferences and settings",
        "Handle all types of payees including:",
        "  - Personal payees (people, friends, family)",
        "  - Biller payees (utilities, services, subscriptions)",
        "  - Business payees (vendors, suppliers)",
        "  - Beneficiaries and nominees",
        "Use tables to display payee summaries with columns like: Payee ID, Name, Type, Status, Payment Method, Account Details, Biller Code",
        "For personal payees, show UPI handles, account numbers, and IFSC codes",
        "For biller payees, show biller codes, service types, and payment methods",
        "Include beneficiary information with relationship details and share percentages",
        "Show payment status and any pending payment actions",
        "Highlight security features like account number masking",
        "Provide payment method preferences and available options",
        "If specific payee information is not available, explicitly state what data is missing",
        "Always cite the specific payee data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Recurring Payments & Subscriptions Agent
recurringPaymentsAgent = Agent(
    name="Recurring Payments Agent",
    role="Handles recurring payments, subscriptions, SIP investments, and mandate management",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Recurring Payments & Subscriptions Agent specialized in providing comprehensive information about recurring payments, subscriptions, SIP investments, payment scheduling, and mandate management.",
    instructions=[
        "CRITICAL: ALL recurring payment and subscription information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide recurring payment information not found in the knowledge base.",
        "Always search for recurring payment-specific information using recurring payment IDs, names, or payment-related terms.",
        "When analyzing recurring payments and subscriptions, provide comprehensive insights including:",
        "  - Recurring payment details (ID, name, amount, currency, frequency)",
        "  - Payment source information (from account, from card)",
        "  - Payment scheduling (day of month, next payment date)",
        "  - Mandate details (type, reference, status)",
        "  - Subscription management and status",
        "  - SIP investment details and fund information",
        "  - Payment frequency and timing",
        "  - Linked accounts and payment methods",
        "  - Payment status and history",
        "  - Cancellation and modification options",
        "Handle all types of recurring payments including:",
        "  - Subscription services (Netflix, streaming, utilities)",
        "  - Investment SIPs (mutual funds, systematic investments)",
        "  - Bill payments (utilities, insurance, loans)",
        "  - Standing instructions and mandates",
        "  - Recurring transfers and payments",
        "Use tables to display recurring payment summaries with columns like: Payment ID, Name, Amount, Frequency, Next Date, Source, Status, Mandate",
        "For subscriptions, show service details, amounts, and next billing dates",
        "For SIP investments, show fund details, investment amounts, and next investment dates",
        "Include mandate information (NACH, card-on-file, standing instructions)",
        "Show payment source details (account IDs, card IDs, linked entities)",
        "Highlight payment frequency (monthly, quarterly, yearly) and timing",
        "Provide payment status and any pending actions",
        "Include cancellation and modification information where available",
        "If specific recurring payment information is not available, explicitly state what data is missing",
        "Always cite the specific recurring payment data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Master Payee & Recurring Payment Agent that routes to appropriate agents
PayeeRecurringPaymentMasterAgent = Agent(
    name="Payee & Recurring Payment Master Agent",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    team=[payeesManagementAgent, recurringPaymentsAgent],
    memory=payee_memory,
    storage=payee_storage,
    enable_user_memories=True,
    add_history_to_messages=True,
    num_history_responses=5,
    description="You are a Master Payee & Recurring Payment Agent that intelligently routes payee and recurring payment-related queries to specialized agents based on the type of information requested.",
    instructions=[
        "You are the master coordinator for all payee and recurring payment-related queries. Analyze the user's request and route it to the appropriate specialist agent:",
        "",
        "Route to Payees Management Agent for:",
        "- Payee details, names, types, and status information",
        "- Personal payees (friends, family, contacts)",
        "- Biller payees (utilities, services, merchants)",
        "- Business payees (vendors, suppliers)",
        "- Beneficiary and nominee information",
        "- UPI handles and virtual payment addresses",
        "- Account details, IFSC codes, and bank information",
        "- Payment method preferences and options",
        "- Biller codes and service types",
        "",
        "Route to Recurring Payments Agent for:",
        "- Recurring payment schedules and frequencies",
        "- Subscription services and billing cycles",
        "- SIP investments and systematic investment plans",
        "- Mandate details (NACH, standing instructions)",
        "- Payment scheduling and next payment dates",
        "- Recurring payment sources (accounts, cards)",
        "- Payment status and history for recurring transactions",
        "- Cancellation and modification of recurring payments",
        "",
        "For queries that involve both payees and their recurring payments, coordinate with both agents to provide comprehensive information.",
        "Always provide clear, organized responses and remember previous conversations to maintain context.",
        "If a query is unclear, ask clarifying questions to route it to the most appropriate agent.",
        "Maintain conversation history and reference previous interactions when relevant.",
        "Focus on providing complete payment management insights when dealing with both payee setup and recurring payment scheduling."
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
    print("=== Payee & Recurring Payment Master Agent Initialized ===")
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
                print("\nPayee & Recurring Payment Master Agent:")
                PayeeRecurringPaymentMasterAgent.print_response(
                    user_input, 
                    stream=True, 
                    markdown=True,
                    user_id="demo_user",
                    session_id="payee_recurring_session"
                )
                print("\n" + "=" * 50)
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue