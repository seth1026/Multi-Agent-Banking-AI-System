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
    path="embeddings/chromadb/miscellaneous",
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

# Initialize persistent memory and storage for banking services
banking_memory_db = SqliteMemoryDb(table_name="banking_services_memories", db_file="tmp/miscellaneous/banking_services_agent.db")
banking_memory = Memory(db=banking_memory_db)
banking_storage = SqliteStorage(table_name="banking_services_sessions", db_file="tmp/miscellaneous/banking_services_agent.db")

# Create Banking Services & Support Agent
bankingServicesSupportAgent = Agent(
    name="Banking Services & Support Agent",
    role="Handles rewards programs, banking documents, consents, disputes, alerts, and travel notices",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Banking Services & Support Agent specialized in providing comprehensive information about rewards programs, banking documents, consents, disputes, alerts, travel notices, and other banking services.",
    instructions=[
        "CRITICAL: ALL banking services and support information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide banking services information not found in the knowledge base.",
        "Always search for banking services-specific information using relevant terms or data categories.",
        "When analyzing banking services and support, provide comprehensive insights including:",
        "  - Rewards programs (program names, points balance, currency, accruals, redemptions)",
        "  - Rewards ledger (transaction history, points earned, points redeemed, reasons)",
        "  - Banking documents (statements, reports, document types, periods, URIs)",
        "  - Account aggregator consents (providers, purposes, scopes, status, expiry)",
        "  - Disputes and complaints (transaction disputes, reasons, status, resolution)",
        "  - Banking alerts (low balance, security, transaction, status updates)",
        "  - Travel notices (countries, dates, status, card associations)",
        "  - Banking limits and controls (UPI limits, transaction limits, daily limits)",
        "  - Service status and availability",
        "  - Support and customer service information",
        "Handle all types of banking services and support including:",
        "  - Rewards and loyalty programs",
        "  - Banking documents and statements",
        "  - Consents and authorizations",
        "  - Disputes and complaints",
        "  - Alerts and notifications",
        "  - Travel and international services",
        "  - Banking limits and controls",
        "  - Customer support services",
        "Use tables to display banking services summaries with columns like: Service Type, Details, Status, Dates, Information",
        "For rewards programs, show program details, points balance, and transaction history",
        "For documents, show document types, periods, and access information",
        "Include consent information with providers, purposes, and expiry dates",
        "Show dispute details including reasons, status, and resolution information",
        "Highlight alert information and notification details",
        "Provide travel notice information and international usage details",
        "Show banking limits and control information",
        "Include service status and availability information",
        "Provide customer support and service information",
        "If specific banking services information is not available, explicitly state what data is missing",
        "Always cite the specific data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Financial Profile & Compliance Agent
financialProfileComplianceAgent = Agent(
    name="Financial Profile & Compliance Agent",
    role="Handles credit profiles, tax information, compliance, regulatory data, and financial health indicators",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=shared_knowledge_base,
    search_knowledge=True,
    description="You are a Financial Profile & Compliance Agent specialized in providing comprehensive information about credit profiles, tax information, compliance, regulatory data, and financial health indicators.",
    instructions=[
        "CRITICAL: ALL financial profile and compliance information is available in the knowledge base. You MUST search the knowledge base before responding to any query.",
        "NEVER make assumptions or provide financial profile information not found in the knowledge base.",
        "Always search for financial profile-specific information using relevant terms or data categories.",
        "When analyzing financial profiles and compliance, provide comprehensive insights including:",
        "  - Credit profile information (bureau scores, risk grades, credit history)",
        "  - Credit bureau details (CIBIL, Experian, scores, risk assessment)",
        "  - Credit enquiries and applications (dates, types, institutions, amounts, results)",
        "  - Tradelines and credit accounts (types, open dates, institutions, limits, balances)",
        "  - Tax information (Form 26AS, assessment year, PAN details)",
        "  - Tax deduction details (TDS salary, TDS other, TCS, advance tax)",
        "  - Self-assessment tax and tax payments",
        "  - Statement of Financial Transactions (SFT) details",
        "  - Gross total income estimates and tax paid totals",
        "  - Compliance and regulatory information",
        "  - Financial health indicators and risk assessment",
        "Handle all types of financial profile and compliance data including:",
        "  - Credit bureau reports and scores",
        "  - Tax returns and Form 26AS",
        "  - Credit enquiries and applications",
        "  - Tradelines and credit accounts",
        "  - Tax deductions and payments",
        "  - Income estimates and compliance",
        "Use tables to display financial profile summaries with columns like: Category, Details, Values, Status, Dates",
        "For credit profiles, show bureau scores, risk grades, and credit history details",
        "For tax information, show assessment year, PAN, and detailed breakdown of tax components",
        "Include credit enquiry information with dates, types, and results",
        "Show tradeline details including account types, institutions, and balances",
        "Highlight tax deduction and payment information",
        "Provide income estimates and tax compliance status",
        "Include risk assessment and financial health indicators",
        "Show compliance status and regulatory requirements",
        "If specific financial profile information is not available, explicitly state what data is missing",
        "Always cite the specific data you found in your response"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create Master Banking Services Agent that routes to appropriate agents
BankingServicesMasterAgent = Agent(
    name="Banking Services Master Agent",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    team=[bankingServicesSupportAgent, financialProfileComplianceAgent],
    memory=banking_memory,
    storage=banking_storage,
    enable_user_memories=True,
    add_history_to_messages=True,
    num_history_responses=5,
    description="You are a Master Banking Services Agent that intelligently routes banking services and compliance-related queries to specialized agents based on the type of information requested.",
    instructions=[
        "You are the master coordinator for all banking services and compliance-related queries. Analyze the user's request and route it to the appropriate specialist agent:",
        "",
        "Route to Banking Services & Support Agent for:",
        "- Rewards programs, points balance, and loyalty programs",
        "- Rewards ledger and transaction history",
        "- Banking documents, statements, and reports",
        "- Account aggregator consents and authorizations",
        "- Disputes, complaints, and resolution status",
        "- Banking alerts and notifications",
        "- Travel notices and international services",
        "- Banking limits and transaction controls",
        "- Customer support and service information",
        "- Service status and availability",
        "",
        "Route to Financial Profile & Compliance Agent for:",
        "- Credit profiles, bureau scores, and risk grades",
        "- Credit bureau reports (CIBIL, Experian)",
        "- Credit enquiries and applications history",
        "- Tradelines and credit account details",
        "- Tax information and Form 26AS",
        "- Tax deductions (TDS, TCS, advance tax)",
        "- Income estimates and tax compliance",
        "- Financial health indicators and risk assessment",
        "- Regulatory compliance and requirements",
        "",
        "For queries that involve both banking services and compliance aspects, coordinate with both agents to provide comprehensive information.",
        "Always provide clear, organized responses and remember previous conversations to maintain context.",
        "If a query is unclear, ask clarifying questions to route it to the most appropriate agent.",
        "Maintain conversation history and reference previous interactions when relevant.",
        "Focus on providing complete banking service and compliance insights when dealing with customer queries."
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
    print("=== Banking Services Master Agent Initialized ===")
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
                print("\nBanking Services Master Agent:")
                BankingServicesMasterAgent.print_response(
                    user_input, 
                    stream=True, 
                    markdown=True,
                    user_id="demo_user",
                    session_id="banking_services_session"
                )
                print("\n" + "=" * 50)
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue