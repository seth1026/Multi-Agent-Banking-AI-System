import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getAvailableAgents = async () => {
    try {
        const response = await api.get('/agents');
        return response.data;
    } catch (error) {
        console.error('Error fetching agents:', error);
        throw error;
    }
};

export const sendMessage = async (endpoint, message, userId = 'web_user', sessionId = null) => {
    try {
        const response = await api.post(endpoint, {
            message,
            user_id: userId,
            session_id: sessionId,
        });
        return response.data;
    } catch (error) {
        console.error('Error sending message:', error);
        throw error;
    }
};

export const checkHealth = async () => {
    try {
        const response = await api.get('/health');
        return response.data;
    } catch (error) {
        console.error('Error checking health:', error);
        throw error;
    }
};