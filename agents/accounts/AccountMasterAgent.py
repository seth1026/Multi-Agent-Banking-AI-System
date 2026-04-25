import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.knowledge.json import JSONKnowledgeBase
from agno.models.azure import AzureOpenAI
from agno.tools.reasoning import ReasoningTools
from agno.embedder.azure_openai import AzureOpenAIEmbedder
from agno.vectordb.chroma import ChromaDb
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage

# Load environment variables
load_dotenv()

# Initialize persistent ChromaDB for knowledge base
def create_persistent_vector_db(collection_name: str):
    return ChromaDb(
        collection=collection_name,
        path="embeddings/chromadb/accounts",  # Persistent storage path
        persistent_client=True,
        embedder=AzureOpenAIEmbedder(
            api_key=os.getenv("EMBEDDING_API_KEY"),
            azure_endpoint=os.getenv("EMBEDDING_ENDPOINT"),
            azure_deployment=os.getenv("EMBEDDING_DEPLOYMENT")
        )
    )

# Create shared knowledge base with persistent storage
knowledge_base = JSONKnowledgeBase(
    path="knowledge/CORE_BANKING_DATA.json",
    vector_db=create_persistent_vector_db("banking_knowledge"),
    num_documents=10,
)

# Initialize persistent memory and storage
memory_db = SqliteMemoryDb(
    table_name="user_memories", 
    db_file="tmp/accounts/banking_agent_memory.db"
)

memory = Memory(
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    db=memory_db,
    delete_memories=True,
    clear_memories=True,
)

storage = SqliteStorage(
    table_name="agent_sessions", 
    db_file="tmp/accounts/banking_agent_sessions.db"
)

# Create specialized agents
def create_account_profile_agent():
    return Agent(
        name="AccountProfileSummaryAgent",
        model=AzureOpenAI(
            azure_deployment=os.getenv("DEPLOYMENT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("ENDPOINT"),
            api_version=os.getenv("API_VERSION")
        ),
        tools=[ReasoningTools(add_instructions=True)],
        knowledge=knowledge_base,
        search_knowledge=True,
        description="Specialized in providing comprehensive account information, holder details, and KYC status across all deposit accounts.",
        instructions=[
            "Search the knowledge base for account-specific information using account numbers, holder names, or account types.",
            "Provide detailed account profiles including IFSC codes, branch details, opening dates, and account status.",
            "Always include holder information and KYC status in account summaries.",
            "Use tables to display multiple accounts for easy comparison.",
            "If information is not available in the knowledge base, explicitly state this."
        ],
        show_tool_calls=True,
        markdown=True,
    )

def create_balance_overdraft_agent():
    return Agent(
        name="BalanceOverdraftAgent",
        model=AzureOpenAI(
            azure_deployment=os.getenv("DEPLOYMENT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("ENDPOINT"),
            api_version=os.getenv("API_VERSION")
        ),
        tools=[ReasoningTools(add_instructions=True)],
        knowledge=knowledge_base,
        search_knowledge=True,
        description="Specialized in providing monetary state information, account balances, overdraft details, and account-level limits.",
        instructions=[
            "Search for balance-specific information using account numbers, balance types, or overdraft terms.",
            "Always include timestamps when reporting balances.",
            "Distinguish between available balance and current balance.",
            "For overdraft queries, provide overdraft limits, available overdraft, and terms.",
            "Flag low-balance risks by comparing against minimum balance requirements.",
            "Include overdraft utilization calculations when available."
        ],
        show_tool_calls=True,
        markdown=True,
    )

def create_fd_interest_agent():
    return Agent(
        name="FDInterestAgent",
        model=AzureOpenAI(
            azure_deployment=os.getenv("DEPLOYMENT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("ENDPOINT"),
            api_version=os.getenv("API_VERSION")
        ),
        tools=[ReasoningTools(add_instructions=True)],
        knowledge=knowledge_base,
        search_knowledge=True,
        description="Specialized in providing comprehensive information about term deposits, maturity timelines, interest calculations, and investment account linkages.",
        instructions=[
            "Search for FD-specific information using account numbers, maturity dates, interest rates, or term deposit keywords.",
            "Include principal amount, interest rate, tenure, maturity date, and current status.",
            "Calculate remaining tenure and maturity proceeds.",
            "Report auto-renewal status and payout frequency.",
            "Flag FDs nearing maturity within 30 days.",
            "Include nominee details and tax implications when available."
        ],
        show_tool_calls=True,
        markdown=True,
    )

# Create the Account Master Agent
account_master_agent = Agent(
    name="AccountMasterAgent",
    model=AzureOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_version=os.getenv("API_VERSION")
    ),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=knowledge_base,
    search_knowledge=True,
    memory=memory,
    storage=storage,
    enable_agentic_memory=True,  # Enable user memory management
    add_history_to_messages=True,  # Add chat history to context
    num_history_runs=5,  # Include last 5 conversation turns
    read_chat_history=True,  # Allow reading full chat history
    description="Master banking agent that intelligently routes user requests to specialized banking agents and provides comprehensive banking assistance.",
    instructions=[
        "You are the main interface for banking operations. Analyze user requests and determine the most appropriate response strategy.",
        "For account profile, holder details, KYC status, IFSC codes, or branch information - use AccountProfileSummaryAgent approach.",
        "For balance inquiries, overdraft information, account limits, or monetary state - use BalanceOverdraftAgent approach.",
        "For fixed deposit details, maturity information, interest calculations, or investment accounts - use FDInterestAgent approach.",
        "For complex queries spanning multiple areas, combine approaches from relevant specialized agents.",
        "Always search the knowledge base first before responding.",
        "Maintain context from previous conversations using memory and chat history.",
        "Provide personalized responses based on user's banking history and preferences.",
        "If you cannot find specific information, clearly state what data is missing.",
        "Use tables and structured formats for better readability when presenting multiple accounts or complex data.",
        "Remember user preferences and frequently accessed accounts for future interactions."
    ],
    show_tool_calls=True,
    markdown=True,
)

# Initialize the knowledge base (run once or when data changes)
def initialize_knowledge_base():
    """Initialize the knowledge base with persistent storage"""
    try:
        # Check if embeddings already exist
        if not knowledge_base.vector_db.exists():
            print("Creating new embeddings...")
            knowledge_base.load(recreate=True)
            print("Knowledge base initialized successfully!")
        else:
            print("Using existing embeddings...")
            knowledge_base.load(recreate=False)
    except Exception as e:
        print(f"Error initializing knowledge base: {e}")
        # Fallback to recreate if there's an issue
        knowledge_base.load(recreate=True)

# Helper function to get user context
def get_user_context(user_id: str) -> str:
    """Get user context from memory for personalization"""
    try:
        user_memories = memory.get_user_memories(user_id=user_id)
        if user_memories:
            context = "User Context:\n"
            for mem in user_memories[-3:]:  # Last 3 memories
                context += f"- {mem.memory}\n"
            return context
    except:
        pass
    return ""

# Main interaction function
def chat_with_master_agent(user_id: str = "default_user"):
    """Interactive chat with the master agent"""
    print("🏦 Welcome to Banking Master Agent!")
    print("I can help you with:")
    print("• Account profiles and holder information")
    print("• Balance inquiries and overdraft details") 
    print("• Fixed deposit information and calculations")
    print("• General banking queries")
    print("\nType 'exit' to quit\n")
    
    while True:
        try:
            user_input = input(f"\n💬 {user_id}: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Thank you for using Banking Master Agent!")
                break
                
            if not user_input:
                continue
                
            # Get response from master agent with user context
            response = account_master_agent.run(
                message=user_input,
                user_id=user_id,
                stream=False
            )
            
            print(f"\n🤖 Banking Agent: {response.content}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Initialize knowledge base with persistent storage
    initialize_knowledge_base()
    
    # Start interactive chat directly
    chat_with_master_agent("banking_user")