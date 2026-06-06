const API = {
    root: async () => {
        const response = await fetch('/');
        return response.json();
    },

    startJourney: async ({ origin, initial_budget, initial_time_minutes, traveler_name }) => {
        const response = await fetch('/api/journey/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ origin, initial_budget, initial_time_minutes, traveler_name })
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

    getGraph: async () => {
        const response = await fetch('/api/graph');
        return response.json();
    },

    getGraphVisualization: async (start = '', end = '', criterion = '') => {
        const params = new URLSearchParams();
        if (start) params.append('start', start);
        if (end) params.append('end', end);
        if (criterion) params.append('criterion', criterion);

        const response = await fetch(`/api/graph/visualization?${params.toString()}`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.error || 'Error al obtener la visualización del grafo');
        }
        return response.blob();
    },

    getGraphVisualizationByCost: async (start, end) => {
        const response = await fetch(`/api/graph/dijkstra/cost/visualization?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.error || 'Error al obtener la visualización Dijkstra por costo');
        }
        return response.blob();
    },

    getGraphVisualizationByTime: async (start, end) => {
        const response = await fetch(`/api/graph/dijkstra/time/visualization?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.error || 'Error al obtener la visualización Dijkstra por tiempo');
        }
        return response.blob();
    },

    getDijkstraCost: async (start, end) => {
        const response = await fetch(`/api/graph/dijkstra/cost?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
        return response.json();
    },

    getDijkstraTime: async (start, end) => {
        const response = await fetch(`/api/graph/dijkstra/time?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
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
const toastContainer = document.getElementById('toast-container');
const startButton = document.getElementById('startJourney');
const getStateButton = document.getElementById('getState');
const getLogButton = document.getElementById('getLog');
const getReportButton = document.getElementById('getReport');
const getSuggestionsButton = document.getElementById('getSuggestions');
const resetButton = document.getElementById('resetJourney');
const executeDecisionButton = document.getElementById('executeDecision');
const decisionTypeSelect = document.getElementById('decisionType');
const journeyIdInput = document.getElementById('journeyId');
const destinationInput = document.getElementById('destination');
const jobIdInput = document.getElementById('jobId');
const jobHoursInput = document.getElementById('jobHours');
const activityIdInput = document.getElementById('activityId');
const initialTimeInput = document.getElementById('initialTime');
const statePanel = document.getElementById('statePanel');
const logPanel = document.getElementById('logPanel');
const reportPanel = document.getElementById('reportPanel');
const suggestionsPanel = document.getElementById('suggestionsPanel');
const graphPanel = document.getElementById('graphPanel');
const dijkstraPanel = document.getElementById('dijkstraPanel');
const stateContent = document.getElementById('stateContent');
const logContent = document.getElementById('logContent');
const reportContent = document.getElementById('reportContent');
const suggestionsContent = document.getElementById('suggestionsContent');
const graphContent = document.getElementById('graphContent');
const dijkstraContent = document.getElementById('dijkstraContent');
const graphContainer = document.getElementById('graph-container');
const graphImage = document.getElementById('graphImage');
const graphStartInput = document.getElementById('graphStart');
const graphEndInput = document.getElementById('graphEnd');
const showGraphButton = document.getElementById('showGraph');
const runDijkstraCostButton = document.getElementById('runDijkstraCost');
const runDijkstraTimeButton = document.getElementById('runDijkstraTime');

function showToast(message, type = 'info', duration = 4500) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hide');
    }, duration - 250);

    setTimeout(() => {
        toast.remove();
    }, duration);
}

function showResponse(data, message = 'Operación completada') {
    responseEl.textContent = JSON.stringify(data, null, 2);
    if (data && data.error) {
        showToast(data.error, 'error');
    } else if (data && data.success === false) {
        showToast(message, 'error');
    } else {
        showToast(message, 'success');
    }
}

function showError(error) {
    const message = error?.message || error || 'Error inesperado';
    responseEl.textContent = `Error: ${message}`;
    hideAllDetailPanels();
    showToast(message, 'error');
}

function hideAllDetailPanels() {
    [statePanel, logPanel, reportPanel, suggestionsPanel, graphPanel, dijkstraPanel].forEach(panel => panel.hidden = true);
}

function showPanel(panel) {
    hideAllDetailPanels();
    panel.hidden = false;
}

function renderJsonContent(container, data) {
    container.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}

function formatValue(value) {
    if (value === null || value === undefined) {
        return 'N/A';
    }
    if (Array.isArray(value)) {
        return value.length ? value.join(', ') : 'Ninguno';
    }
    if (typeof value === 'object') {
        return JSON.stringify(value, null, 2);
    }
    return String(value);
}

function renderKeyValueRow(label, value) {
    return `<div class="info-row"><span><strong>${label}:</strong></span><span>${formatValue(value)}</span></div>`;
}

function renderObjectList(items) {
    if (!items || !items.length) {
        return '<div class="object-item">Ninguno</div>';
    }
    return items.map(item => {
        if (typeof item === 'object') {
            const fields = Object.entries(item)
                .map(([key, value]) => `<div><strong>${key.replace(/_/g, ' ')}:</strong> ${formatValue(value)}</div>`)
                .join('');
            return `<div class="object-item">${fields}</div>`;
        }
        return `<div class="object-item">${formatValue(item)}</div>`;
    }).join('');
}

function renderArrayRow(label, items) {
    return `<div class="option-group"><h4>${label}</h4>${renderObjectList(items)}</div>`;
}

function renderStateContent(data) {
    const state = data.current_state || data;
    if (!state) {
        renderJsonContent(stateContent, data);
        return;
    }

    let html = '';
    if (state.current_airport) {
        html += '<div class="option-group"><h4>Aeropuerto actual</h4>';
        html += renderKeyValueRow('Código', state.current_airport.code);
        html += renderKeyValueRow('Nombre', state.current_airport.name);
        html += renderKeyValueRow('Ciudad', state.current_airport.city);
        html += renderKeyValueRow('País', state.current_airport.country);
        html += renderKeyValueRow('Hub', state.current_airport.is_hub ? 'Sí' : 'No');
        html += '</div>';
    }

    if (state.budget) {
        html += '<div class="option-group"><h4>Presupuesto</h4>';
        html += renderKeyValueRow('Actual', state.budget.current);
        html += renderKeyValueRow('Inicial', state.budget.initial);
        html += renderKeyValueRow('Gastado', state.budget.spent);
        html += renderKeyValueRow('Ganado', state.budget.earned);
        html += renderKeyValueRow('Restante (%)', `${state.budget.percentage_remaining}%`);
        html += renderKeyValueRow('Crítico', state.budget.budget_critical ? 'Sí' : 'No');
        html += '</div>';

        if (state.budget.budget_critical) {
            html += '<div class="option-group critical-warning"><h4>Presupuesto crítico</h4>';
            html += '<p>Tu presupuesto está por debajo del 35%. Revisa los trabajos disponibles en este aeropuerto y usa la decisión de trabajo para recuperar dinero.</p>';
            html += '</div>';
        }
    }

    if (state.time) {
        html += '<div class="option-group"><h4>Tiempo</h4>';
        html += renderKeyValueRow('Tiempo inicial (min)', state.time.initial_time_minutes ?? state.time.initial_time_hours * 60);
        html += renderKeyValueRow('Tiempo restante (min)', state.time.remaining_time_minutes ?? state.time.remaining_time_hours * 60);
        html += renderKeyValueRow('Minutos en aeropuerto', state.time.at_current_airport_minutes ?? state.time.at_current_airport_hours * 60);
        html += renderKeyValueRow('Minutos desde alojamiento', state.time.minutes_since_last_accommodation ?? state.time.hours_since_last_accommodation * 60);
        html += renderKeyValueRow('Minutos desde comida', state.time.minutes_since_last_meal ?? state.time.hours_since_last_meal * 60);
        html += renderKeyValueRow('Total viaje (min)', state.time.total_journey_minutes ?? state.time.total_journey_hours * 60);
        html += '</div>';
    }

    if (state.journey_progress) {
        html += '<div class="option-group"><h4>Progreso del viaje</h4>';
        html += renderKeyValueRow('Destinos visitados', state.journey_progress.destinations_count);
        html += renderKeyValueRow('Decisiones tomadas', state.journey_progress.decisions_made);
        html += renderKeyValueRow('Eventos registrados', state.journey_progress.events_recorded);
        html += '</div>';
    }

    if (state.mandatory_requirements) {
        html += renderArrayRow('Costos obligatorios', Array.isArray(state.mandatory_requirements) ? state.mandatory_requirements : [state.mandatory_requirements]);
    }
    if (state.optional_activities) {
        html += renderArrayRow('Actividades disponibles', state.optional_activities);
    }
    if (state.available_jobs) {
        html += renderArrayRow('Trabajos disponibles', state.available_jobs);
    }
    if (state.budget && state.budget.budget_critical && !state.available_jobs?.length) {
        html += '<div class="option-group"><h4>Trabajos disponibles</h4><div class="object-item">No hay trabajos disponibles en este aeropuerto actualmente.</div></div>';
    }
    if (state.next_flights) {
        html += renderArrayRow('Vuelos disponibles', state.next_flights);
    }

    stateContent.innerHTML = html || `<pre>${JSON.stringify(state, null, 2)}</pre>`;
}

function renderLogContent(data) {
    let html = '';
    if (data.traveler) {
        html += renderKeyValueRow('Viajero', data.traveler);
    }
    if (data.summary) {
        html += '<div class="option-group"><h4>Resumen del viaje</h4>';
        Object.entries(data.summary).forEach(([key, value]) => {
            html += renderKeyValueRow(key.replace(/_/g, ' '), value);
        });
        html += '</div>';
    }
    if (data.events) {
        html += renderArrayRow('Eventos', data.events);
    }
    if (data.decisions) {
        html += renderArrayRow('Decisiones', data.decisions);
    }
    if (!html) {
        renderJsonContent(logContent, data);
        return;
    }
    logContent.innerHTML = html;
}

function renderReportContent(data) {
    const report = data.report || data;
    let html = '';
    if (report.budget) {
        html += '<div class="option-group"><h4>Resumen de presupuesto</h4>';
        Object.entries(report.budget).forEach(([key, value]) => {
            html += renderKeyValueRow(key.replace(/_/g, ' '), value);
        });
        html += '</div>';
    }
    if (report.destinations) {
        html += '<div class="option-group"><h4>Destinos</h4>';
        Object.entries(report.destinations).forEach(([key, value]) => {
            html += renderKeyValueRow(key.replace(/_/g, ' '), value);
        });
        html += '</div>';
    }
    if (report.efficiency) {
        html += '<div class="option-group"><h4>Eficiencia</h4>';
        Object.entries(report.efficiency).forEach(([key, value]) => {
            html += renderKeyValueRow(key.replace(/_/g, ' '), value);
        });
        html += '</div>';
    }
    if (report.time) {
        html += '<div class="option-group"><h4>Tiempo</h4>';
        Object.entries(report.time).forEach(([key, value]) => {
            html += renderKeyValueRow(key.replace(/_/g, ' '), value);
        });
        html += '</div>';
    }
    if (report.decisions) {
        html += '<div class="option-group"><h4>Decisiones</h4>';
        Object.entries(report.decisions).forEach(([key, value]) => {
            html += renderKeyValueRow(key.replace(/_/g, ' '), value);
        });
        html += '</div>';
    }
    if (!html) {
        renderJsonContent(reportContent, report);
        return;
    }
    reportContent.innerHTML = html;
}

function renderSuggestionsContent(data) {
    let html = '';
    if (data.current_airport) {
        html += '<div class="option-group"><h4>Posición actual</h4>';
        html += renderKeyValueRow('Aeropuerto', data.current_airport);
        html += renderKeyValueRow('Presupuesto restante', data.current_budget);
        html += '</div>';
    }
    if (Array.isArray(data.suggestions) && data.suggestions.length) {
        html += '<div class="option-group"><h4>Sugerencias principales</h4>';
        html += renderObjectList(data.suggestions);
        html += '</div>';
    }
    if (!html) {
        renderJsonContent(suggestionsContent, data);
        return;
    }
    suggestionsContent.innerHTML = html;
}

function renderGraphContent(data) {
    let html = '';
    if (Array.isArray(data.airports)) {
        html += `<div class="option-group"><h4>Aeropuertos (${data.airports.length})</h4>${renderObjectList(data.airports)}</div>`;
    }
    if (Array.isArray(data.routes)) {
        html += `<div class="option-group"><h4>Rutas (${data.routes.length})</h4>${renderObjectList(data.routes)}</div>`;
    }
    if (!html) {
        renderJsonContent(graphContent, data);
        return;
    }
    graphContent.innerHTML = html;
    if (graphContainer) {
        graphContainer.innerHTML = '';
        if (graphImage) {
            graphContainer.appendChild(graphImage);
        }
    }
}

function populateJobSelect(jobs) {
    if (!jobIdInput) return;

    const select = jobIdInput;
    select.innerHTML = '<option value="">Seleccione un trabajo</option>';

    if (!Array.isArray(jobs) || jobs.length === 0) {
        return;
    }

    jobs.forEach((job) => {
        const option = document.createElement('option');
        option.value = job.id || job.job_id || '';
        option.textContent = `${job.name} — ${job.description || (job.hourly_rate ? `$${job.hourly_rate.toFixed(2)}/h` : 'N/A')} ` +
            `${job.max_hours ? `(máx ${job.max_hours}h)` : ''}`;
        select.appendChild(option);
    });
}

function populateActivitySelect(activities) {
    if (!activityIdInput) return;

    const select = activityIdInput;
    select.innerHTML = '<option value="">Seleccione una actividad</option>';

    if (!Array.isArray(activities) || activities.length === 0) {
        return;
    }

    activities.forEach((activity) => {
        const option = document.createElement('option');
        option.value = activity.id || '';
        option.textContent = `${activity.name} — ${activity.description || `${activity.type} ${activity.duration_min} min $${activity.cost ?? 'N/A'}`}`;
        select.appendChild(option);
    });
}

function renderGraphImage(blob) {
    if (!graphImage) return;
    const objectUrl = URL.createObjectURL(blob);
    graphImage.src = objectUrl;
    graphImage.style.display = 'block';

    if (graphContainer) {
        const placeholder = graphContainer.querySelector('p');
        if (placeholder) {
            placeholder.remove();
        }
        if (!graphContainer.contains(graphImage)) {
            graphContainer.appendChild(graphImage);
        }
    }
}

function clearGraphImage() {
    if (!graphImage) return;
    graphImage.src = '';
    graphImage.style.display = 'none';

    if (graphContainer) {
        graphContainer.innerHTML = '';
        const placeholder = document.createElement('p');
        placeholder.textContent = 'El grafo aparecerá aquí';
        graphContainer.appendChild(placeholder);
        graphContainer.appendChild(graphImage);
    }
}

function renderDijkstraContent(data) {
    if (!data || !data.result) {
        renderJsonContent(dijkstraContent, data);
        return;
    }

    let html = '<div class="option-group"><h4>Camino</h4>';
    html += renderKeyValueRow('Criterio', data.criterion);
    html += renderKeyValueRow('Inicio', data.start);
    html += renderKeyValueRow('Destino', data.end);
    html += renderKeyValueRow('Peso total', data.result.totalWeight);
    html += renderKeyValueRow('Ruta', data.result.path.join(' → ') || 'N/A');
    html += '</div>';

    if (Array.isArray(data.result.segments) && data.result.segments.length) {
        html += '<div class="option-group"><h4>Segmentos</h4>';
        html += renderObjectList(data.result.segments);
        html += '</div>';
    }

    dijkstraContent.innerHTML = html;
}

function updateDecisionFields() {
    const selectedType = decisionTypeSelect.value;
    document.querySelectorAll('.decision-field').forEach(field => {
        field.hidden = field.dataset.type !== selectedType;
    });
}

updateDecisionFields();

decisionTypeSelect.addEventListener('change', updateDecisionFields);

function getJourneyIdOrNotify() {
    const journeyId = journeyIdInput.value.trim();
    if (!journeyId) {
        showResponse({ error: 'Journey ID es requerido.' });
        return null;
    }
    return journeyId;
}

function buildDecisionPayload() {
    const type = decisionTypeSelect.value;
    const payload = { type };

    if (type === 'FLIGHT') {
        const destination = destinationInput.value.trim();
        if (!destination) {
            showResponse({ error: 'Destino es requerido para la decisión de vuelo.' });
            return null;
        }
        payload.destination = destination;
    }

    if (type === 'JOB') {
        const jobId = jobIdInput.value.trim();
        const hours = Number(jobHoursInput.value);
        if (!jobId) {
            showResponse({ error: 'Debe seleccionar un trabajo para continuar.' });
            return null;
        }
        if (!hours || hours <= 0) {
            showResponse({ error: 'Horas válidas son requeridas para el trabajo.' });
            return null;
        }
        payload.job_id = jobId;
        payload.hours = hours;
    }

    if (type === 'ACTIVITY') {
        const activityId = activityIdInput.value.trim();
        if (!activityId) {
            showResponse({ error: 'Debe seleccionar una actividad para continuar.' });
            return null;
        }
        payload.activity_id = activityId;
    }

    return payload;
}

startButton.addEventListener('click', async () => {
    const origin = document.getElementById('origin').value.trim() || 'GRU';
    const initial_budget = Number(document.getElementById('budget').value) || 500;
    const initial_time_minutes = Number(initialTimeInput?.value || 0) || 0;
    const traveler_name = document.getElementById('traveler').value.trim() || 'Anonimo';

    responseEl.textContent = 'Iniciando viaje...';
    hideAllDetailPanels();

    try {
        const data = await API.startJourney({ origin, initial_budget, initial_time_minutes, traveler_name });
        showResponse(data, data.success ? `Viaje iniciado: ${data.journey_id}` : 'No se pudo iniciar el viaje');

        if (data.success && data.journey_id) {
            journeyIdInput.value = data.journey_id;
            renderStateContent(data);
            populateJobSelect(data.current_state?.available_jobs || []);
            populateActivitySelect(data.current_state?.optional_activities || []);
            showPanel(statePanel);
        }
    } catch (error) {
        showError(error);
    }
});

getStateButton.addEventListener('click', async () => {
    const journeyId = getJourneyIdOrNotify();
    if (!journeyId) return;

    responseEl.textContent = 'Obteniendo estado...';

    try {
        const data = await API.getJourneyState(journeyId);
        showResponse(data, 'Estado obtenido');
        renderStateContent(data);
        populateJobSelect(data.current_state?.available_jobs || []);
        populateActivitySelect(data.current_state?.optional_activities || []);
        showPanel(statePanel);
    } catch (error) {
        showError(error);
    }
});

getLogButton.addEventListener('click', async () => {
    const journeyId = getJourneyIdOrNotify();
    if (!journeyId) return;

    responseEl.textContent = 'Obteniendo historial...';

    try {
        const data = await API.getJourneyLog(journeyId);
        showResponse(data, 'Historial obtenido');
        renderLogContent(data);
        showPanel(logPanel);
    } catch (error) {
        showError(error);
    }
});

getReportButton.addEventListener('click', async () => {
    const journeyId = getJourneyIdOrNotify();
    if (!journeyId) return;

    responseEl.textContent = 'Generando reporte...';

    try {
        const data = await API.getJourneyReport(journeyId);
        showResponse(data, 'Reporte generado');
        renderReportContent(data);
        showPanel(reportPanel);
    } catch (error) {
        showError(error);
    }
});

getSuggestionsButton.addEventListener('click', async () => {
    const journeyId = getJourneyIdOrNotify();
    if (!journeyId) return;

    responseEl.textContent = 'Obteniendo sugerencias...';

    try {
        const data = await API.getRouteSuggestions(journeyId, { max_destinations: 5, depth: 20 });
        showResponse(data, 'Sugerencias obtenidas');
        renderSuggestionsContent(data);
        showPanel(suggestionsPanel);
    } catch (error) {
        showError(error);
    }
});

showGraphButton.addEventListener('click', async () => {
    const start = graphStartInput.value.trim() || 'GRU';
    const end = graphEndInput.value.trim() || 'GIG';

    responseEl.textContent = 'Cargando grafo...';
    hideAllDetailPanels();
    clearGraphImage();

    try {
        const [data, blob] = await Promise.all([
            API.getGraph(),
            API.getGraphVisualization()
        ]);
        showResponse(data, 'Grafo cargado');
        renderGraphContent(data);
        renderGraphImage(blob);
        showPanel(graphPanel);
    } catch (error) {
        showError(error);
    }
});

runDijkstraCostButton.addEventListener('click', async () => {
    const start = graphStartInput.value.trim();
    const end = graphEndInput.value.trim();
    if (!start || !end) return showResponse({ error: 'Inicio y destino son requeridos.' });

    responseEl.textContent = 'Calculando Dijkstra por costo...';
    hideAllDetailPanels();
    clearGraphImage();

    try {
        const [data, blob] = await Promise.all([
            API.getDijkstraCost(start, end),
            API.getGraphVisualizationByCost(start, end)
        ]);
        showResponse(data, 'Dijkstra por costo calculado');
        renderDijkstraContent(data);
        renderGraphImage(blob);
        showPanel(dijkstraPanel);
    } catch (error) {
        showError(error);
    }
});

runDijkstraTimeButton.addEventListener('click', async () => {
    const start = graphStartInput.value.trim();
    const end = graphEndInput.value.trim();
    if (!start || !end) return showResponse({ error: 'Inicio y destino son requeridos.' });

    responseEl.textContent = 'Calculando Dijkstra por tiempo...';
    hideAllDetailPanels();
    clearGraphImage();

    try {
        const [data, blob] = await Promise.all([
            API.getDijkstraTime(start, end),
            API.getGraphVisualizationByTime(start, end)
        ]);
        showResponse(data, 'Dijkstra por tiempo calculado');
        renderDijkstraContent(data);
        renderGraphImage(blob);
        showPanel(dijkstraPanel);
    } catch (error) {
        showError(error);
    }
});

resetButton.addEventListener('click', async () => {
    const journeyId = getJourneyIdOrNotify();
    if (!journeyId) return;

    responseEl.textContent = 'Reseteando viaje...';
    hideAllDetailPanels();

    try {
        const data = await API.resetJourney(journeyId);
        showResponse(data, 'Viaje reseteado');
    } catch (error) {
        showError(error);
    }
});

executeDecisionButton.addEventListener('click', async () => {
    const journeyId = getJourneyIdOrNotify();
    if (!journeyId) return;

    const decisionData = buildDecisionPayload();
    if (!decisionData) return;

    responseEl.textContent = 'Ejecutando decisión...';
    hideAllDetailPanels();

    try {
        const data = await API.executeDecision(journeyId, decisionData);
        const typeName = decisionData.type === 'FLIGHT' ? 'vuelo' : decisionData.type.toLowerCase();
        showResponse(data, data.success ? `Decisión de ${typeName} ejecutada` : 'No se pudo ejecutar la decisión');
        if (data.success) {
            renderStateContent({ current_state: data.new_state });
            populateJobSelect(data.new_state?.available_jobs || []);
            populateActivitySelect(data.new_state?.optional_activities || []);
            showPanel(statePanel);
        }
    } catch (error) {
        showError(error);
    }
});