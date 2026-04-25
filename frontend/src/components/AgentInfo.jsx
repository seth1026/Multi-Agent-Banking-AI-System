import React, { useState, useEffect } from 'react';
import { getAvailableAgents } from '../services/api';

const AgentInfo = ({ onClose }) => {
    const [agentsData, setAgentsData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAgents = async () => {
            try {
                const data = await getAvailableAgents();
                setAgentsData(data);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching agents:', err);
                setLoading(false);
            }
        };

        fetchAgents();
    }, []);

    const getAgentIcon = (agentName) => {
        const iconMap = {
            'MainBankingMasterAgent': '🏦',
            'AccountMasterAgent': '🏦',
            'CardMasterAgent': '💳',
            'TransactionMasterAgent': '💸',
            'LoansAndInvestmentMasterAgent': '📈',
            'PayeeRecurringPaymentMasterAgent': '🔄',
            'BankingServicesMasterAgent': '🛠️'
        };
        return iconMap[agentName] || '🤖';
    };

    const getAgentColor = (agentName) => {
        const colorMap = {
            'MainBankingMasterAgent': '#4a90e2',
            'AccountMasterAgent': '#4a90e2',
            'CardMasterAgent': '#28a745',
            'TransactionMasterAgent': '#ffc107',
            'LoansAndInvestmentMasterAgent': '#17a2b8',
            'PayeeRecurringPaymentMasterAgent': '#6f42c1',
            'BankingServicesMasterAgent': '#fd7e14'
        };
        return colorMap[agentName] || '#6c757d';
    };

    if (loading) {
        return (
            <div className="agent-info-panel">
                <div className="panel-header">
                    <h3>Agent Information</h3>
                    <button className="close-button" onClick={onClose}>✕</button>
                </div>
                <div className="panel-content">
                    <div className="loading">
                        <span>Loading agent information...</span>
                        <div className="loading-dots">
                            <div className="loading-dot"></div>
                            <div className="loading-dot"></div>
                            <div className="loading-dot"></div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="agent-info-panel">
            <div className="panel-header">
                <h3>🤖 Agent Information</h3>
                <button className="close-button" onClick={onClose}>✕</button>
            </div>

            <div className="panel-content">
                {agentsData?.main_agent && (
                    <div className="main-agent-section">
                        <h4>🎯 Main Agent</h4>
                        <div className="agent-card main-agent">
                            <div className="agent-header">
                                <span
                                    className="agent-icon"
                                    style={{ backgroundColor: getAgentColor(agentsData.main_agent.name) }}
                                >
                                    {getAgentIcon(agentsData.main_agent.name)}
                                </span>
                                <div className="agent-details">
                                    <h5>Intelligent Banking Router</h5>
                                    <span className="agent-endpoint">{agentsData.main_agent.endpoint}</span>
                                </div>
                            </div>
                            <p className="agent-description">
                                {agentsData.main_agent.description}
                            </p>
                            <div className="agent-features">
                                <span className="feature-badge">🧠 AI Routing</span>
                                <span className="feature-badge">💬 Natural Language</span>
                                <span className="feature-badge">🔄 Context Aware</span>
                            </div>
                        </div>
                    </div>
                )}

                {agentsData?.specialized_agents && (
                    <div className="specialized-agents-section">
                        <h4>🎯 Specialized Agents</h4>
                        <div className="agents-list">
                            {agentsData.specialized_agents.map((agent, index) => (
                                <div key={index} className="agent-card specialized-agent">
                                    <div className="agent-header">
                                        <span
                                            className="agent-icon"
                                            style={{ backgroundColor: getAgentColor(agent.name) }}
                                        >
                                            {getAgentIcon(agent.name)}
                                        </span>
                                        <div className="agent-details">
                                            <h6>{agent.name.replace('MasterAgent', '').replace(/([A-Z])/g, ' $1').trim()}</h6>
                                            <span className="agent-endpoint">{agent.endpoint}</span>
                                        </div>
                                    </div>
                                    <p className="agent-description">
                                        {agent.description}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="how-it-works-section">
                    <h4>🔄 How It Works</h4>
                    <div className="workflow-steps">
                        <div className="workflow-step">
                            <span className="step-number">1</span>
                            <div className="step-content">
                                <h6>You Ask</h6>
                                <p>Type your banking question in natural language</p>
                            </div>
                        </div>
                        <div className="workflow-step">
                            <span className="step-number">2</span>
                            <div className="step-content">
                                <h6>AI Analyzes</h6>
                                <p>Main agent analyzes your query and determines the best specialist</p>
                            </div>
                        </div>
                        <div className="workflow-step">
                            <span className="step-number">3</span>
                            <div className="step-content">
                                <h6>Expert Responds</h6>
                                <p>Specialized agent provides detailed, accurate information</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="tips-section">
                    <h4>💡 Tips</h4>
                    <ul className="tips-list">
                        <li>Ask questions naturally - no need to specify which agent</li>
                        <li>Be specific for better results (e.g., "credit card balance" vs "balance")</li>
                        <li>You can ask follow-up questions in the same conversation</li>
                        <li>The system remembers context from previous messages</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default AgentInfo;