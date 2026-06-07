const API = {
    root: async () => {
        const response = await fetch('/');
        return response.json();
    },

    startJourney: async ({ origin, final_destination, initial_budget, initial_time_minutes, traveler_name }) => {
        const response = await fetch('/api/journey/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ origin, final_destination, initial_budget, initial_time_minutes, traveler_name })
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

    getGraphPath: async (start, end, criterion = 'cost') => {
        const params = new URLSearchParams();
        params.append('start', start);
        params.append('end', end);
        params.append('criterion', criterion);

        const response = await fetch(`/api/graph/path?${params.toString()}`);
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
const finalDestinationInput = document.getElementById('finalDestination');
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
const routeCriterionSelect = document.getElementById('routeCriterion');
const calculateRoutePlanButton = document.getElementById('calculateRoutePlan');
const routePlannerPanel = document.getElementById('routePlannerPanel');
const routePlannerContent = document.getElementById('routePlannerContent');
const showGraphButton = document.getElementById('showGraph');
const toggleGraphSummaryButton = document.getElementById('toggleGraphSummary');
const graphSummaryContainer = document.getElementById('graphSummaryContainer');
const runDijkstraCostButton = document.getElementById('runDijkstraCost');
const runDijkstraTimeButton = document.getElementById('runDijkstraTime');
const journeySuggestionsPanel = document.getElementById('suggestionsPanel');
const journeySuggestionsContent = document.getElementById('suggestionsContent');
const floatingStatus = document.getElementById('floatingStatus');
const floatingAirport = document.getElementById('floatingAirport');
const floatingBudget = document.getElementById('floatingBudget');
const floatingTime = document.getElementById('floatingTime');

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
    [statePanel, logPanel, reportPanel, suggestionsPanel, graphPanel, dijkstraPanel, routePlannerPanel, journeySuggestionsPanel].forEach(panel => panel.hidden = true);
}

function showPanel(panel) {
    hideAllDetailPanels();
    panel.hidden = false;
}

function showPanels(panels) {
    hideAllDetailPanels();
    panels.forEach(panel => {
        if (panel) {
            panel.hidden = false;
        }
    });
}

function setGraphSummaryVisibility(visible) {
    if (!graphSummaryContainer || !toggleGraphSummaryButton) return;
    graphSummaryContainer.hidden = !visible;
    toggleGraphSummaryButton.textContent = visible ? 'Ocultar resumen del grafo' : 'Mostrar resumen del grafo';
}

function toggleGraphSummary() {
    if (!graphSummaryContainer) return;
    setGraphSummaryVisibility(graphSummaryContainer.hidden);
}

function renderJsonContent(container, data) {
    container.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}

function formatValue(value) {
    if (value === null || value === undefined) {
        return 'N/A';
    }
    if (Array.isArray(value)) {
        if (!value.length) {
            return 'Ninguno';
        }
        return value
            .map(item => {
                if (item === null || item === undefined) {
                    return 'N/A';
                }
                if (typeof item === 'object') {
                    return formatObjectSummary(item);
                }
                return String(item);
            })
            .join(', ');
    }
    if (typeof value === 'object') {
        return formatObjectSummary(value);
    }
    return String(value);
}

function formatObjectSummary(obj) {
    if (!obj || typeof obj !== 'object') {
        return String(obj);
    }

    if ('type' in obj && 'name' in obj) {
        return `${obj.type} - ${obj.name}`;
    }
    if ('type' in obj && 'id' in obj) {
        return `${obj.type} (${obj.id})`;
    }
    if ('name' in obj) {
        return `${obj.name}`;
    }
    if ('id' in obj) {
        return `${obj.id}`;
    }
    if ('destination' in obj && 'origin' in obj) {
        return `${obj.origin} → ${obj.destination}`;
    }
    return JSON.stringify(obj, null, 2);
}

function renderKeyValueRow(label, value) {
    return `<div class="info-row"><span><strong>${label}:</strong></span><span>${formatValue(value)}</span></div>`;
}

function renderObjectList(items) {
    if (!items || !items.length) {
        return '<div class="object-item">Ninguno</div>';
    }
    return items.map(item => {
        if (typeof item === 'object' && item !== null) {
            const fields = Object.entries(item)
                .map(([key, value]) => `<div><strong>${key.replace(/_/g, ' ')}:</strong> ${formatValue(value)}</div>`)
                .join('');
            return `<div class="object-item">${fields}</div>`;
        }
        return `<div class="object-item">${formatValue(item)}</div>`;
    }).join('');
}

function renderTableRow(label, items) {
    if (!items || !items.length) {
        return `<div class="option-group"><h4>${label}</h4><div class="object-item">Ninguno</div></div>`;
    }

    const rows = Array.isArray(items) ? items : [items];
    const objectRows = rows.filter(item => typeof item === 'object' && item !== null);

    if (!objectRows.length) {
        return renderArrayRow(label, rows);
    }

    const headers = Array.from(new Set(objectRows.flatMap(item => Object.keys(item))));
    const headerCells = headers.map(header => `<th>${header.replace(/_/g, ' ')}</th>`).join('');

    const bodyRows = rows.map(item => {
        if (typeof item !== 'object' || item === null) {
            return `<tr><td colspan="${headers.length}">${formatValue(item)}</td></tr>`;
        }

        const cells = headers.map(key => `<td>${formatValue(item[key])}</td>`).join('');
        return `<tr>${cells}</tr>`;
    }).join('');

    return `
        <div class="option-group">
            <h4>${label}</h4>
            <div class="table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>${headerCells}</tr>
                    </thead>
                    <tbody>
                        ${bodyRows}
                    </tbody>
                </table>
            </div>
        </div>
    `;
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
        if (Array.isArray(state.journey_progress.destinations_visited)) {
            html += renderKeyValueRow('Ruta actual', state.journey_progress.destinations_visited.join(' → '));
        }
        html += '</div>';
    }

    if (state.final_destination) {
        html += '<div class="option-group"><h4>Destino final</h4>';
        html += renderKeyValueRow('Final', state.final_destination);
        html += '</div>';
    }

    if (state.mandatory_requirements) {
        html += renderTableRow('Costos obligatorios', Array.isArray(state.mandatory_requirements) ? state.mandatory_requirements : [state.mandatory_requirements]);
    }
    if (state.optional_activities) {
        html += renderTableRow('Actividades disponibles', state.optional_activities);
    }
    if (state.available_jobs) {
        html += renderTableRow('Trabajos disponibles', state.available_jobs);
    }
    if (state.budget && state.budget.budget_critical && !state.available_jobs?.length) {
        html += '<div class="option-group"><h4>Trabajos disponibles</h4><div class="object-item">No hay trabajos disponibles en este aeropuerto actualmente.</div></div>';
    }
    if (state.next_flights) {
        html += renderTableRow('Vuelos disponibles', state.next_flights);
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

function renderJourneyFlightSuggestions(state) {
    updateFloatingStatus(state);
    if (!state || !Array.isArray(state.next_flights)) {
        journeySuggestionsContent.innerHTML = '<div class="object-item">No hay sugerencias de vuelos disponibles.</div>';
        return;
    }

    let html = `<div class="option-group"><h4>Aeropuerto actual</h4>`;
    html += renderKeyValueRow('Aeropuerto', state.current_airport?.code || state.current_airport || 'N/A');
    html += renderKeyValueRow('Presupuesto restante', state.budget?.current ?? 'N/A');
    if (state.final_destination) {
        html += renderKeyValueRow('Destino final', state.final_destination);
    }
    if (Array.isArray(state.journey_progress?.destinations_visited)) {
        html += renderKeyValueRow('Ruta actual', state.journey_progress.destinations_visited.join(' → '));
    }
    html += '</div>';

    html += '<div class="option-group"><h4>Vuelos conectados disponibles</h4>';
    state.next_flights.forEach((flight, index) => {
        html += '<div class="object-item">';
        html += `<div><strong>${flight.destination}</strong> — ${flight.destination_name}</div>`;
        html += `<div>${flight.city}, ${flight.country}</div>`;
        html += `<div>Distancia: ${flight.distance_km} km</div>`;
        html += `<div>Estadía mínima: ${flight.minimum_stay_hours} h</div>`;
        html += `<div>Subsidizado: ${flight.is_subsidized ? 'Sí' : 'No'}</div>`;

        if (Array.isArray(flight.aircraft_options) && flight.aircraft_options.length) {
            html += '<div class="table-wrapper"><table class="data-table"><thead><tr>' +
                '<th>Aeronave</th><th>Costo</th><th>Tiempo (hrs)</th><th>Seleccionar</th>' +
                '</tr></thead><tbody>';

            flight.aircraft_options.forEach((option) => {
                html += '<tr>' +
                    `<td>${formatValue({ type: option.type, id: option.id })}</td>` +
                    `<td>${option.cost}</td>` +
                    `<td>${option.time_hours}</td>` +
                    `<td><button class="flight-select-button" data-destination="${flight.destination}" data-aircraft-id="${option.id}">Seleccionar</button></td>` +
                    '</tr>';
            });

            html += '</tbody></table></div>';
        } else {
            html += '<div>No hay aeronaves disponibles para este destino.</div>';
        }

        html += '</div>';
    });
    html += '</div>';

    journeySuggestionsContent.innerHTML = html;
    document.querySelectorAll('.flight-select-button').forEach(button => {
        button.addEventListener('click', async () => {
            const journeyId = journeyIdInput.value.trim();
            const destination = button.dataset.destination;
            const aircraftId = button.dataset.aircraftId;
            if (!journeyId) {
                showResponse({ error: 'Se requiere el Journey ID para seleccionar un vuelo.' });
                return;
            }
            await selectFlightOption(journeyId, destination, aircraftId);
        });
    });
}

async function selectFlightOption(journeyId, destination, aircraftId) {
    responseEl.textContent = `Seleccionando vuelo a ${destination}...`;
    hideAllDetailPanels();

    try {
        const decisionData = {
            type: 'FLIGHT',
            destination,
            aircraft_id: aircraftId
        };
        const data = await API.executeDecision(journeyId, decisionData);
        showResponse(data, data.success ? `Vuelo seleccionado a ${destination}` : 'No se pudo seleccionar el vuelo');

        if (data.success) {
            renderStateContent(data.new_state);
            renderJourneyFlightSuggestions(data.new_state);
            populateJobSelect(data.new_state?.available_jobs || []);
            populateActivitySelect(data.new_state?.optional_activities || []);
            showPanels([statePanel, journeySuggestionsPanel]);
        }
    } catch (error) {
        showError(error);
    }
}

function updateFloatingStatus(state) {
    if (!floatingStatus || !state) {
        return;
    }

    const airportName = state.current_airport?.name || state.current_airport?.code || 'N/A';
    const destinationName = state.final_destination || 'N/A';
    const budgetValue = state.budget?.current != null ? `$${state.budget.current}` : 'N/A';
    const timeRemaining = state.time?.remaining_time_minutes != null
        ? `${state.time.remaining_time_minutes} min`
        : state.time?.remaining_time_hours != null
            ? `${state.time.remaining_time_hours} h`
            : 'N/A';

    floatingAirport.textContent = airportName;
    document.getElementById('floatingDestination').textContent = destinationName;
    floatingBudget.textContent = budgetValue;
    floatingTime.textContent = timeRemaining;

    floatingStatus.hidden = false;
}

function resetFloatingStatus() {
    if (!floatingStatus) {
        return;
    }

    floatingAirport.textContent = 'N/A';
    floatingBudget.textContent = 'N/A';
    floatingTime.textContent = 'N/A';
    floatingStatus.hidden = true;
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
    if (toggleGraphSummaryButton) {
        toggleGraphSummaryButton.hidden = false;
    }
    setGraphSummaryVisibility(false);
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
        html += renderTableRow('Segmentos', data.result.segments);
        html += '</div>';
    }

    dijkstraContent.innerHTML = html;
}

function renderAirportsPathTable(airports) {
    if (!Array.isArray(airports) || airports.length === 0) {
        return '<div class="object-item">No hay aeropuertos en la ruta.</div>';
    }

    const headers = [
        'iata', 'name', 'city', 'country', 'is_hub',
        'accommodation_cost', 'alimentation_cost', 'activities', 'jobs'
    ];

    const headerCells = headers.map(header => `<th>${header.replace(/_/g, ' ')}</th>`).join('');

    const rowsHtml = airports.map((airport) => {
        const rowCells = headers.map(key => {
            const value = airport[key];
            if (key === 'activities') {
                return `<td>${Array.isArray(value) ? value.length : 0}</td>`;
            }
            if (key === 'jobs') {
                return `<td>${Array.isArray(value) ? value.length : 0}</td>`;
            }
            return `<td>${formatValue(value)}</td>`;
        }).join('');

        return `
            <tr class="clickable-row" data-iata="${airport.iata}">
                ${rowCells}
            </tr>
        `;
    }).join('');

    return `
        <div class="option-group">
            <h4>Aeropuertos en la ruta</h4>
            <div class="table-wrapper">
                <table class="data-table route-table">
                    <thead>
                        <tr>${headerCells}</tr>
                    </thead>
                    <tbody>${rowsHtml}</tbody>
                </table>
            </div>
            <p class="hint-text">Haz clic en un aeropuerto para copiarlo al campo de destino y elegirlo como siguiente vértice.</p>
        </div>
    `;
}

function renderRoutePlannerContent(data) {
    if (!data || !data.success) {
        renderJsonContent(routePlannerContent, data);
        return;
    }

    let html = '<div class="option-group"><h4>Resumen de la ruta</h4>';
    html += renderKeyValueRow('Origen', data.start);
    html += renderKeyValueRow('Destino', data.end);
    html += renderKeyValueRow('Criterio', data.criterion);
    html += renderKeyValueRow('Ruta', data.route.path.join(' → ') || 'N/A');
    html += renderKeyValueRow('Número de saltos', data.route.segments?.length || 0);
    html += renderKeyValueRow('Costo total', data.route.totalWeight ?? 'N/A');
    html += '</div>';

    if (Array.isArray(data.route.segments) && data.route.segments.length) {
        html += '<div class="option-group"><h4>Segmentos</h4>';
        html += renderTableRow('Segmentos', data.route.segments);
        html += '</div>';
    }

    html += renderAirportsPathTable(data.airports);
    routePlannerContent.innerHTML = html;

    document.querySelectorAll('.clickable-row').forEach((row) => {
        row.addEventListener('click', () => {
            const selectedIata = row.dataset.iata;
            if (selectedIata && graphEndInput) {
                graphEndInput.value = selectedIata;
                showToast(`Destino seleccionado: ${selectedIata}`, 'info');
            }
        });
    });
}

function updateDecisionFields() {
    const selectedType = decisionTypeSelect.value;
    document.querySelectorAll('.decision-field').forEach(field => {
        field.hidden = field.dataset.type !== selectedType;
    });
}

updateDecisionFields();

decisionTypeSelect.addEventListener('change', updateDecisionFields);
if (toggleGraphSummaryButton) {
    toggleGraphSummaryButton.addEventListener('click', toggleGraphSummary);
}

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
    const final_destination = finalDestinationInput?.value.trim() || 'GIG';
    const initial_budget = Number(document.getElementById('budget').value) || 500;
    const initial_time_minutes = Number(initialTimeInput?.value || 0) || 0;
    const traveler_name = document.getElementById('traveler').value.trim() || 'Anonimo';

    responseEl.textContent = 'Iniciando viaje...';
    hideAllDetailPanels();

    try {
        const data = await API.startJourney({ origin, final_destination, initial_budget, initial_time_minutes, traveler_name });
        showResponse(data, data.success ? `Viaje iniciado: ${data.journey_id}` : 'No se pudo iniciar el viaje');

        if (data.success && data.journey_id) {
            journeyIdInput.value = data.journey_id;
            renderStateContent(data.current_state);
            renderJourneyFlightSuggestions(data.current_state);
            populateJobSelect(data.current_state?.available_jobs || []);
            populateActivitySelect(data.current_state?.optional_activities || []);
            showPanels([statePanel, journeySuggestionsPanel]);
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
        renderStateContent(data.current_state);
        renderJourneyFlightSuggestions(data.current_state);
        populateJobSelect(data.current_state?.available_jobs || []);
        populateActivitySelect(data.current_state?.optional_activities || []);
        showPanels([statePanel, journeySuggestionsPanel]);
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

calculateRoutePlanButton.addEventListener('click', async () => {
    const start = graphStartInput.value.trim();
    const end = graphEndInput.value.trim();
    const criterion = routeCriterionSelect.value;

    if (!start || !end) return showResponse({ error: 'Origen y destino son requeridos para planificar la ruta.' });

    responseEl.textContent = 'Calculando ruta recomendada...';
    hideAllDetailPanels();

    try {
        const data = await API.getGraphPath(start, end, criterion);
        showResponse(data, 'Ruta recomendada calculada');
        renderRoutePlannerContent(data);
        showPanel(routePlannerPanel);
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
        resetFloatingStatus();
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