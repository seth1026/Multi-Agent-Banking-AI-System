# Banking Master Agents Frontend

A React-based frontend for interacting with Banking Master Agents through a clean, intuitive interface.

## Features

- **Agent Selection**: Choose from 6 specialized banking agents
- **Real-time Chat**: Interactive chat interface with each agent
- **Markdown Support**: Rich text responses from agents
- **Responsive Design**: Works on desktop and mobile devices
- **Session Management**: Maintains conversation context
- **Error Handling**: Graceful error handling and user feedback

## Available Agents

1. **🏦 Account Management** - Account profiles, balances, and deposit information
2. **💳 Card Services** - Credit/debit cards, limits, rewards, and controls
3. **💸 Transaction History** - Transaction history, transfers, and payment queries
4. **📈 Loans & Investments** - Loans, EMIs, investments, and insurance queries
5. **🔄 Payees & Recurring Payments** - Payees, beneficiaries, and recurring payments
6. **🛠️ General Banking Services** - General banking queries and miscellaneous services

## Quick Start

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## Configuration

The frontend automatically connects to the API server at `http://localhost:8000`. 

To change the API URL, set the `REACT_APP_API_URL` environment variable:

```bash
REACT_APP_API_URL=http://your-api-server:8000 npm start
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── AgentSelector.js    # Agent selection grid
│   │   └── ChatInterface.js    # Chat interface component
│   ├── services/
│   │   └── api.js             # API service functions
│   ├── App.js                 # Main application component
│   ├── index.js              # React entry point
│   └── index.css             # Global styles
├── package.json
└── README.md
```

## Usage

1. **Select an Agent**: Click on any agent card to start a conversation
2. **Chat**: Type your banking questions in the chat input
3. **View Responses**: Agent responses support markdown formatting for tables and lists
4. **Switch Agents**: Use the "Back to Agents" button to select a different agent
5. **Session Persistence**: Each chat session maintains context throughout the conversation

## API Integration

The frontend communicates with the Banking Master Agents API through:

- `GET /agents` - Fetch available agents
- `POST /{agent}/chat` - Send messages to specific agents
- `GET /health` - Check API health status

## Styling

The application uses a modern, gradient-based design with:
- Responsive grid layout for agent selection
- Clean chat interface with message bubbles
- Smooth animations and hover effects
- Mobile-friendly responsive design

## Development

To contribute to the frontend:

1. Follow React best practices
2. Use functional components with hooks
3. Maintain responsive design principles
4. Test on multiple screen sizes
5. Handle loading and error states gracefully

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.