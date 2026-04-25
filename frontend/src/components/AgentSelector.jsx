import React from 'react';

const AgentSelector = ({ agents, onAgentSelect }) => {
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

    const getAgentDisplayName = (agentName) => {
        const nameMap = {
            'AccountMasterAgent': 'Account Management',
            'CardMasterAgent': 'Card Services',
            'TransactionMasterAgent': 'Transaction History',
            'LoansAndInvestmentMasterAgent': 'Loans & Investments',
            'PayeeRecurringPaymentMasterAgent': 'Payees & Recurring Payments',
            'BankingServicesMasterAgent': 'General Banking Services'
        };
        return nameMap[agentName] || agentName;
    };

    // Handle case where agents is undefined or not an array
    if (!agents || !Array.isArray(agents)) {
        return (
            <div className="agents-container">
                <div className="loading">
                    <span>Loading agents...</span>
                    <div className="loading-dots">
                        <div className="loading-dot"></div>
                        <div className="loading-dot"></div>
                        <div className="loading-dot"></div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="agents-container">
            <div className="agents-grid">
                {agents.map((agent, index) => (
                    <div
                        key={agent?.name || index}
                        className="agent-card"
                        onClick={() => agent && onAgentSelect(agent)}
                    >
                        <span className="agent-icon">
                            {getAgentIcon(agent?.name)}
                        </span>
                        <h3>{getAgentDisplayName(agent?.name)}</h3>
                        <p>{agent?.description || 'No description available'}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default AgentSelector;