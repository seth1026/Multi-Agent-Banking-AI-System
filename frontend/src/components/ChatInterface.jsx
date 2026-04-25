import React, { useState, useRef, useEffect } from 'react';
import { sendMessage } from '../services/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatInterface = ({ agent, onBack }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [sessionId] = useState(`web_session_${Date.now()}`);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // Add welcome message when agent is selected
        if (agent && agent.name) {
            const welcomeMessage = {
                type: 'agent',
                content: `Hello! I'm your ${getAgentDisplayName(agent.name)}. How can I help you today?`,
                timestamp: new Date(),
            };
            setMessages([welcomeMessage]);
        }
    }, [agent]);

    const getAgentDisplayName = (agentName) => {
        const nameMap = {
            'AccountMasterAgent': 'Account Management Assistant',
            'CardMasterAgent': 'Card Services Assistant',
            'TransactionMasterAgent': 'Transaction Assistant',
            'LoansAndInvestmentMasterAgent': 'Loans & Investment Assistant',
            'PayeeRecurringPaymentMasterAgent': 'Payees & Payments Assistant',
            'BankingServicesMasterAgent': 'Banking Services Assistant'
        };
        return nameMap[agentName] || agentName;
    };

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
            const response = await sendMessage(
                agent.endpoint,
                userMessage.content,
                'web_user',
                sessionId
            );

            const agentMessage = {
                type: 'agent',
                content: response.response,
                timestamp: new Date(),
                agentName: response.agent_name,
            };

            setMessages(prev => [...prev, agentMessage]);
        } catch (err) {
            setError('Failed to send message. Please try again.');
            console.error('Error sending message:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const getAgentIcon = (agentName) => {
        const iconMap = {
            'AccountMasterAgent': '🏦',
            'CardMasterAgent': '💳',
            'TransactionMasterAgent': '💸',
            'LoansAndInvestmentMasterAgent': '📈',
            'PayeeRecurringPaymentMasterAgent': '🔄',
            'BankingServicesMasterAgent': '🛠️'
        };
        return iconMap[agentName] || '🤖';
    };

    // Safety check for agent prop
    if (!agent || !agent.name) {
        return (
            <div className="container">
                <div className="error-message">
                    Error: No agent selected. Please go back and select an agent.
                </div>
                <button onClick={onBack} className="back-button">
                    ← Back to Agents
                </button>
            </div>
        );
    }

    return (
        <div>
            <div style={{ marginBottom: '20px', textAlign: 'center' }}>
                <button
                    onClick={onBack}
                    className="back-button"
                >
                    ← Back to Agents
                </button>
            </div>

            <div className="chat-container">
                <div className="chat-header">
                    <h3>
                        {getAgentIcon(agent.name)} {getAgentDisplayName(agent.name)}
                    </h3>
                </div>

                <div className="chat-messages">
                    {messages.map((message, index) => (
                        <div key={index} className={`message ${message.type}`}>
                            <div className="message-avatar">
                                {message.type === 'user' ? '👤' : getAgentIcon(agent.name)}
                            </div>
                            <div className="message-content">
                                {message.type === 'agent' ? (
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            table: ({ node, ...props }) => (
                                                <table style={{ width: '100%', borderCollapse: 'collapse', margin: '16px 0' }} {...props} />
                                            ),
                                            th: ({ node, ...props }) => (
                                                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #2d3748', background: '#2d3748', color: '#ffffff' }} {...props} />
                                            ),
                                            td: ({ node, ...props }) => (
                                                <td style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #2d3748', color: '#e6e6e6' }} {...props} />
                                            ),
                                            code: ({ node, inline, ...props }) => (
                                                inline ?
                                                    <code style={{ background: '#1e2328', padding: '2px 6px', borderRadius: '4px', color: '#ffa726' }} {...props} /> :
                                                    <code style={{ background: '#1e2328', padding: '16px', borderRadius: '8px', display: 'block', color: '#e6e6e6' }} {...props} />
                                            )
                                        }}
                                    >
                                        {message.content}
                                    </ReactMarkdown>
                                ) : (
                                    message.content
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="message agent">
                            <div className="message-avatar">
                                {getAgentIcon(agent.name)}
                            </div>
                            <div className="message-content">
                                <div className="loading">
                                    <span>Thinking</span>
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
                        <div className="error-message">
                            {error}
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-container">
                    <form onSubmit={handleSendMessage} className="chat-input-form">
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder={`Ask your ${getAgentDisplayName(agent.name).toLowerCase()}...`}
                            className="chat-input"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            className="send-button"
                            disabled={isLoading || !inputMessage.trim()}
                        >
                            {isLoading ? '...' : 'Send'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;