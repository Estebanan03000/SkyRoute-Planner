const API = {
    root: async () => {
        const response = await fetch('/');
        return response.json();
    },

    startJourney: async ({ origin, initial_budget, traveler_name }) => {
        const response = await fetch('/api/journey/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ origin, initial_budget, traveler_name })
        });
        return response.json();
    },

    getJourneyState: async (journeyId) => {
        const response = await fetch(`/api/journey/${journeyId}/state`);
        return response.json();
    },

    executeDecision: async (journeyId, decisionData) => {
        const response = await fetch(`/api/journey/${journeyId}/decide`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(decisionData)
        });
        return response.json();
    },

    getJourneyLog: async (journeyId) => {
        const response = await fetch(`/api/journey/${journeyId}/log`);
        return response.json();
    },

    getJourneyReport: async (journeyId) => {
        const response = await fetch(`/api/journey/${journeyId}/report`);
        return response.json();
    },

    getRouteSuggestions: async (journeyId, { max_destinations = 10, depth = 50 } = {}) => {
        const response = await fetch(`/api/journey/${journeyId}/suggestions?max_destinations=${max_destinations}&depth=${depth}`);
        return response.json();
    },

    resetJourney: async (journeyId) => {
        const response = await fetch(`/api/journey/${journeyId}/reset`, {
            method: 'POST'
        });
        return response.json();
    }
};

const responseEl = document.getElementById('response');
const startButton = document.getElementById('startJourney');
const getStateButton = document.getElementById('getState');
const getLogButton = document.getElementById('getLog');
const getReportButton = document.getElementById('getReport');
const getSuggestionsButton = document.getElementById('getSuggestions');
const resetButton = document.getElementById('resetJourney');
const executeDecisionButton = document.getElementById('executeDecision');

const journeyIdInput = document.getElementById('journeyId');
const destinationInput = document.getElementById('destination');

function showResponse(data) {
    responseEl.textContent = JSON.stringify(data, null, 2);
}

function showError(error) {
    responseEl.textContent = `Error: ${error.message}`;
}

startButton.addEventListener('click', async () => {
    const origin = document.getElementById('origin').value.trim() || 'GRU';
    const initial_budget = Number(document.getElementById('budget').value) || 500;
    const traveler_name = document.getElementById('traveler').value.trim() || 'Anonimo';

    responseEl.textContent = 'Iniciando viaje...';

    try {
        const data = await API.startJourney({ origin, initial_budget, traveler_name });
        showResponse(data);

        if (data.success && data.journey_id) {
            journeyIdInput.value = data.journey_id;
        }
    } catch (error) {
        showError(error);
    }
});

getStateButton.addEventListener('click', async () => {
    const journeyId = journeyIdInput.value.trim();
    if (!journeyId) return showResponse({ error: 'Journey ID es requerido.' });

    responseEl.textContent = 'Obteniendo estado...';

    try {
        const data = await API.getJourneyState(journeyId);
        showResponse(data);
    } catch (error) {
        showError(error);
    }
});

getLogButton.addEventListener('click', async () => {
    const journeyId = journeyIdInput.value.trim();
    if (!journeyId) return showResponse({ error: 'Journey ID es requerido.' });

    responseEl.textContent = 'Obteniendo historial...';

    try {
        const data = await API.getJourneyLog(journeyId);
        showResponse(data);
    } catch (error) {
        showError(error);
    }
});

getReportButton.addEventListener('click', async () => {
    const journeyId = journeyIdInput.value.trim();
    if (!journeyId) return showResponse({ error: 'Journey ID es requerido.' });

    responseEl.textContent = 'Generando reporte...';

    try {
        const data = await API.getJourneyReport(journeyId);
        showResponse(data);
    } catch (error) {
        showError(error);
    }
});

getSuggestionsButton.addEventListener('click', async () => {
    const journeyId = journeyIdInput.value.trim();
    if (!journeyId) return showResponse({ error: 'Journey ID es requerido.' });

    responseEl.textContent = 'Obteniendo sugerencias...';

    try {
        const data = await API.getRouteSuggestions(journeyId, { max_destinations: 5, depth: 20 });
        showResponse(data);
    } catch (error) {
        showError(error);
    }
});

resetButton.addEventListener('click', async () => {
    const journeyId = journeyIdInput.value.trim();
    if (!journeyId) return showResponse({ error: 'Journey ID es requerido.' });

    responseEl.textContent = 'Reseteando viaje...';

    try {
        const data = await API.resetJourney(journeyId);
        showResponse(data);
    } catch (error) {
        showError(error);
    }
});

executeDecisionButton.addEventListener('click', async () => {
    const journeyId = journeyIdInput.value.trim();
    const destination = destinationInput.value.trim();
    if (!journeyId) return showResponse({ error: 'Journey ID es requerido.' });
    if (!destination) return showResponse({ error: 'Destino es requerido.' });

    responseEl.textContent = 'Ejecutando decisión de vuelo...';

    try {
        const data = await API.executeDecision(journeyId, {
            type: 'FLIGHT',
            destination
        });
        showResponse(data);
    } catch (error) {
        showError(error);
    }
});