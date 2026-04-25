import React, { useState, useRef, useEffect } from 'react';
import { sendMessage } from '../services/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MainChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [sessionId] = useState(`main_session_${Date.now()}`);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // Add welcome message when component mounts
        const welcomeMessage = {
            type: 'agent',
            content: `# Welcome to Banking Master Agent! 🏦

I'm your intelligent banking assistant that can help you with all your banking needs. I automatically route your questions to the most appropriate specialist:

**What I can help you with:**
- 🏦 **Account Management** - Balances, profiles, deposits
- 💳 **Card Services** - Credit/debit cards, limits, rewards  
- 💸 **Transactions** - History, transfers, payments
- 📈 **Loans & Investments** - EMIs, mutual funds, insurance
- 🔄 **Payees & Payments** - Recurring payments, beneficiaries
- 🛠️ **General Banking** - Credit scores, alerts, services

**Just ask me anything!** For example:
- "What's my account balance?"
- "Show me my credit card statement"
- "When is my next EMI due?"
- "What are my recent transactions?"

How can I assist you today?`,
            timestamp: new Date(),
            agentName: 'MainBankingMasterAgent'
        };
        setMessages([welcomeMessage]);
    }, []);

    const handleSendMessage = async (e) => {
        e.preventDefault();

        if (!inputMessage.trim() || isLoading) return;

        const userMessage = {
            type: 'user',
            content: inputMessage.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);
        setError(null);

        try {
            // Send to main agent endpoint which handles routing
            const response = await sendMessage(
                '/chat', // Main agent endpoint
                userMessage.content,
                'web_user',
                sessionId
            );

            const agentMessage = {
                type: 'agent',
                content: response.response,
                timestamp: new Date(),
                agentName: response.agent_name,
                routedTo: getRoutedAgentInfo(response.agent_name)
            };

            setMessages(prev => [...prev, agentMessage]);
        } catch (err) {
            setError('Failed to send message. Please try again.');
            console.error('Error sending message:', err);

            // Add error message to chat
            const errorMessage = {
                type: 'error',
                content: 'Sorry, I encountered an error processing your request. Please try again.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const getRoutedAgentInfo = (agentName) => {
        const agentInfo = {
            'AccountMasterAgent': { icon: '🏦', name: 'Account Specialist', color: '#4a90e2' },
            'CardMasterAgent': { icon: '💳', name: 'Card Specialist', color: '#28a745' },
            'TransactionMasterAgent': { icon: '💸', name: 'Transaction Specialist', color: '#ffc107' },
            'LoansAndInvestmentMasterAgent': { icon: '📈', name: 'Loans & Investment Specialist', color: '#17a2b8' },
            'PayeeRecurringPaymentMasterAgent': { icon: '🔄', name: 'Payments Specialist', color: '#6f42c1' },
            'BankingServicesMasterAgent': { icon: '🛠️', name: 'Banking Services Specialist', color: '#fd7e14' },
            'MainBankingMasterAgent': { icon: '🏦', name: 'Main Banking Agent', color: '#4a90e2' }
        };
        return agentInfo[agentName] || { icon: '🤖', name: 'Banking Assistant', color: '#6c757d' };
    };

    const handleQuickAction = (action) => {
        setInputMessage(action);
    };

    const quickActions = [
        "What's my account balance?",
        "Show me my credit card details",
        "Recent transactions",
        "When is my next EMI due?",
        "Show my registered payees",
        "What's my credit score?"
    ];

    return (
        <div className="main-chat-container">
            <div className="chat-messages">
                {messages.map((message, index) => (
                    <div key={index} className={`message ${message.type}`}>
                        <div className="message-header">
                            <div className="message-avatar">
                                {message.type === 'user' ? (
                                    <span className="user-avatar">👤</span>
                                ) : message.type === 'error' ? (
                                    <span className="error-avatar">⚠️</span>
                                ) : (
                                    <span className="agent-avatar">
                                        {message.routedTo?.icon || '🏦'}
                                    </span>
                                )}
                            </div>
                            <div className="message-info">
                                <span className="message-sender">
                                    {message.type === 'user' ? 'You' :
                                        message.type === 'error' ? 'System' :
                                            message.routedTo?.name || 'Banking Agent'}
                                </span>
                                <span className="message-time">
                                    {message.timestamp.toLocaleTimeString([], {
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })}
                                </span>
                            </div>
                        </div>
                        <div className="message-content">
                            {message.type === 'agent' ? (
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    components={{
                                        table: ({ node, ...props }) => (
                                            <table className="markdown-table" {...props} />
                                        ),
                                        th: ({ node, ...props }) => (
                                            <th className="markdown-th" {...props} />
                                        ),
                                        td: ({ node, ...props }) => (
                                            <td className="markdown-td" {...props} />
                                        ),
                                        code: ({ node, inline, ...props }) => (
                                            inline ?
                                                <code className="markdown-code-inline" {...props} /> :
                                                <code className="markdown-code-block" {...props} />
                                        ),
                                        h1: ({ node, ...props }) => <h1 className="markdown-h1" {...props} />,
                                        h2: ({ node, ...props }) => <h2 className="markdown-h2" {...props} />,
                                        h3: ({ node, ...props }) => <h3 className="markdown-h3" {...props} />,
                                        ul: ({ node, ...props }) => <ul className="markdown-ul" {...props} />,
                                        ol: ({ node, ...props }) => <ol className="markdown-ol" {...props} />,
                                        li: ({ node, ...props }) => <li className="markdown-li" {...props} />,
                                        p: ({ node, ...props }) => <p className="markdown-p" {...props} />,
                                        strong: ({ node, ...props }) => <strong className="markdown-strong" {...props} />,
                                        em: ({ node, ...props }) => <em className="markdown-em" {...props} />
                                    }}
                                >
                                    {message.content}
                                </ReactMarkdown>
                            ) : (
                                <p>{message.content}</p>
                            )}
                        </div>
                        {message.routedTo && message.agentName !== 'MainBankingMasterAgent' && (
                            <div className="routing-info">
                                <span
                                    className="routing-badge"
                                    style={{ backgroundColor: message.routedTo.color }}
                                >
                                    {message.routedTo.icon} Routed to {message.routedTo.name}
                                </span>
                            </div>
                        )}
                    </div>
                ))}

                {isLoading && (
                    <div className="message agent">
                        <div className="message-header">
                            <div className="message-avatar">
                                <span className="agent-avatar">🏦</span>
                            </div>
                            <div className="message-info">
                                <span className="message-sender">Banking Agent</span>
                                <span className="message-time">Processing...</span>
                            </div>
                        </div>
                        <div className="message-content">
                            <div className="loading">
                                <span>Analyzing your request and routing to the best specialist...</span>
                                <div className="loading-dots">
                                    <div className="loading-dot"></div>
                                    <div className="loading-dot"></div>
                                    <div className="loading-dot"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="error-banner">
                        <span>⚠️ {error}</span>
                        <button onClick={() => setError(null)}>✕</button>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {messages.length === 1 && (
                <div className="quick-actions">
                    <h4>Quick Actions:</h4>
                    <div className="quick-actions-grid">
                        {quickActions.map((action, index) => (
                            <button
                                key={index}
                                className="quick-action-button"
                                onClick={() => handleQuickAction(action)}
                                disabled={isLoading}
                            >
                                {action}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            <div className="chat-input-container">
                <form onSubmit={handleSendMessage} className="chat-input-form">
                    <div className="input-wrapper">
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder="Ask me anything about your banking needs..."
                            className="chat-input"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            className="send-button"
                            disabled={isLoading || !inputMessage.trim()}
                        >
                            {isLoading ? (
                                <span className="loading-spinner">⏳</span>
                            ) : (
                                <span>Send 📤</span>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default MainChatInterface;