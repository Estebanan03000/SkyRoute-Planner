const API = {
    root: async () => {
        const response = await fetch('/');
        return response.json();
    },

    startJourney: async ({
    origin,
    initial_budget,
    traveler_name
}) => {

    const response = await fetch(
        '/api/journey/start',
        {
            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({
                origin,
                initial_budget,
                traveler_name
            })
        }
    );

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

    uploadGraph: async (file) => {

        const formData = new FormData();

        formData.append(
            'file',
            file
        );

        const response = await fetch(
            '/api/load-graph',
            {
                method: 'POST',
                body: formData
            }
        );

        return response.json();
    },

    interruptRoute: async (
    journeyId,
    origin,
    destination
) => {

    const response =
        await fetch(
            `/api/journey/${journeyId}/interrupt-route`,
            {
                method: 'POST',

                headers: {
                    'Content-Type':
                        'application/json'
                },

                body: JSON.stringify({

                    origin,
                    destination

                })
            }
        );

    return response.json();
},

calculateDijkstra: async (
    origin,
    destination,
    criterion
) => {

    const response =
        await fetch(
            '/api/dijkstra',
            {
                method: 'POST',

                headers: {
                    'Content-Type':
                        'application/json'
                },

                body: JSON.stringify({

                    origin,
                    destination,
                    criterion

                })
            }
        );

    return response.json();
},

};

const startButton = document.getElementById('startJourney');
const getStateButton = document.getElementById('getState');
const executeDecisionButton = document.getElementById('executeDecision');

const journeyIdInput = document.getElementById('journeyId');
const destinationInput = document.getElementById('destination');

const originNode = document.getElementById('originNode');
const destinationNode = document.getElementById('destinationNode');
const routeArrow = document.getElementById('routeArrow');
const routeStatus = document.getElementById('routeStatus');

const loadGraphButton = document.getElementById('loadGraph');
const graphFileInput = document.getElementById('graphFile');

const currentAirportValue = document.getElementById('currentAirportValue');
const budgetValue = document.getElementById('budgetValue');
const timeValue = document.getElementById('timeValue');
const destinationsValue = document.getElementById('destinationsValue');
const cityValue = document.getElementById('cityValue');
const countryValue = document.getElementById('countryValue');
const mealRequiredValue = document.getElementById('mealRequiredValue');
const accommodationRequiredValue = document.getElementById('accommodationRequiredValue');
const routeValue = document.getElementById('routeValue');

const timelineContainer = document.getElementById('journeyTimeline');
const reportContainer = document.getElementById('reportContainer');

const availableFlights = document.getElementById('availableFlights');
const availableActivities = document.getElementById('availableActivities');
const availableJobs = document.getElementById('availableJobs');

const journeyTimeline = document.getElementById('journeyTimeline');

const interruptOrigin =
    document.getElementById(
        'interruptOrigin'
    );

const interruptDestination =
    document.getElementById(
        'interruptDestination'
    );

const interruptRouteButton =
    document.getElementById(
        'interruptRouteButton'
    );

const dijkstraOrigin =
    document.getElementById(
        'dijkstraOrigin'
    );

const dijkstraDestination =
    document.getElementById(
        'dijkstraDestination'
    );

const dijkstraCriterion =
    document.getElementById(
        'dijkstraCriterion'
    );

const calculateRouteButton =
    document.getElementById(
        'calculateRouteButton'
    );

const dijkstraResult =
    document.getElementById(
        'dijkstraResult'
    );

function showResponse(data) {

    console.log(
        'RESPONSE:',
        data
    );

}

function showError(error) {

    console.error(
        'ERROR:',
        error
    );

    alert(
        error?.message ||
        'Ha ocurrido un error'
    );

}

function updateTravelerState(state) {

    currentAirportValue.textContent =
        state.current_airport || '-';

    budgetValue.textContent =
        `$${state.current_budget || 0}`;

    timeValue.textContent =
        `${state.total_journey_time || 0} h`;

    destinationsValue.textContent =
        state.destinations_visited?.length || 0;

}

function renderAvailableOptions(state) {

    availableFlights.innerHTML = '';
    availableActivities.innerHTML = '';
    availableJobs.innerHTML = '';

    // ==================
    // Flights
    // ==================

    state.next_flights.forEach(flight => {

        const div =
            document.createElement('div');

        div.className = 'option-item';

        div.innerHTML = `
            <strong>
                ${flight.destination}
            </strong>

            <small>
                ${flight.distance_km} km
            </small>
        `;

        availableFlights.appendChild(div);

    });

    // ==================
    // Activities
    // ==================

    state.optional_activities.forEach(activity => {

        const div =
            document.createElement('div');

        div.className = 'option-item';

        div.innerHTML = `
            <strong>
                ${activity.name}
            </strong>

            <small>
                Costo: $${activity.cost}
            </small>
        `;

        availableActivities.appendChild(div);

    });

    // ==================
    // Jobs
    // ==================

    state.available_jobs.forEach(job => {

        const div =
            document.createElement('div');

        div.className = 'option-item';

        div.innerHTML = `
            <strong>
                ${job.name}
            </strong>

            <small>
                Pago: $${job.hourly_rate}/h
            </small>
        `;

        availableJobs.appendChild(div);

    });
}

async function loadJourneyLog(journeyId) {

    try {

        const data =
            await API.getJourneyLog(
                journeyId
            );

        if (!data.success) {
            return;
        }

        journeyTimeline.innerHTML = '';

        const events =
            data.events || [];

        if (events.length === 0) {

            journeyTimeline.innerHTML =
                '<p>No hay eventos registrados.</p>';

            return;
        }

        events.forEach(event => {

            let title = event.type;

            switch(event.type) {

                case 'JOURNEY_START':
                    title = '🚀 Inicio del Viaje';
                    break;

                case 'FLIGHT':
                    title = '✈ Vuelo';
                    break;

                case 'ACTIVITY':
                    title = '🎯 Actividad';
                    break;

                case 'JOB':
                    title = '💼 Trabajo';
                    break;

                case 'MEAL':
                    title = '🍔 Comida';
                    break;

                case 'ACCOMMODATION':
                    title = '🏨 Alojamiento';
                    break;

                case 'ROUTE_INTERRUPTION':
                    title = '🚨 Interrupción de Ruta';
                    break;
            }

            const div =
                document.createElement('div');

            div.className =
                'timeline-item';

            div.innerHTML = `
                <div class="timeline-title">
                    ${title}
                </div>

                <div class="timeline-description">
                    ${event.description}
                </div>

                <div class="timeline-date">
                    ${event.timestamp}
                </div>
            `;

            journeyTimeline.appendChild(div);

        });

    }

    catch(error) {

        console.error(error);

    }
}

async function loadJourneyReport(
    journeyId
) {

    try {

        const data =
            await API.getJourneyReport(
                journeyId
            );

        if (!data.success) {
            return;
        }

        const report =
            data.report;

        reportContainer.innerHTML = `

        <div class="report-section">

            <h3>
                📊 Resumen General
            </h3>

            <p>
                Total de Eventos:
                ${report.journey_overview.total_events}
            </p>

            <p>
                Total de Decisiones:
                ${report.journey_overview.total_decisions}
            </p>

            <p>
                Estados Registrados:
                ${report.journey_overview.total_states}
            </p>

        </div>

        <div class="report-section">

            <h3>
                💰 Rendimiento Financiero
            </h3>

            <p>
                Presupuesto Inicial:
                $${report.budget.initial_budget}
            </p>

            <p>
                Presupuesto Final:
                $${report.budget.final_budget}
            </p>

            <p>
                Total Gastado:
                $${report.budget.total_spent}
            </p>

            <p>
                Total Ganado:
                $${report.budget.total_earned}
            </p>

            <p>
                Presupuesto Restante:
                ${report.budget.budget_remaining_percentage}%
            </p>

        </div>

        <div class="report-section">

            <h3>
                📈 Rendimiento del Viaje
            </h3>

            <p>
                Calificación:
                ${report.efficiency.performance_rating}
            </p>

            <p>
                Destinos Visitados:
                ${report.efficiency.destinations_visited}
            </p>

            <p>
                Gasto Total:
                $${report.efficiency.total_spending}
            </p>

            <p>
                Ganancias Totales:
                $${report.efficiency.total_earnings}
            </p>

        </div>

        <div class="report-section">

            <h3>
                🧠 Estadísticas de Decisiones
            </h3>

            <p>
                Vuelos:
                ${report.decisions.flight_decisions}
            </p>

            <p>
                Actividades:
                ${report.decisions.activity_decisions}
            </p>

            <p>
                Trabajos:
                ${report.decisions.work_decisions}
            </p>

            <p>
                Decisiones Obligatorias:
                ${report.decisions.mandatory_decisions}
            </p>

        </div>

        <div class="report-section">

            <h3>
                ⏱ Distribución del Tiempo
            </h3>

            <p>
                Horas Totales:
                ${report.time.total_hours}
            </p>

            <p>
                Horas de Vuelo:
                ${report.time.flights.hours}
            </p>

            <p>
                Horas en Actividades:
                ${report.time.activities.hours}
            </p>

            <p>
                Horas Trabajadas:
                ${report.time.jobs.hours}
            </p>

            <p>
                Horas en Comidas:
                ${report.time.meals.hours}
            </p>

            <p>
                Horas en Hospedaje:
                ${report.time.accommodation.hours}
            </p>

        </div>

        `;

    }

    catch(error) {

        console.error(error);

    }
}

function renderTimeline(events) {

    timelineContainer.innerHTML = '';

    events.forEach(event => {

        const div =
            document.createElement('div');

        div.className = 'timeline-item';

        div.innerHTML = `
            <strong>${event.event_type}</strong>
            <br>
            ${event.description}
        `;

        timelineContainer.appendChild(div);
    });
}

async function refreshGraph() {

    const graphData =
        await API.getGraph();

    const container =
        document.getElementById(
            'graph-container'
        );

    const data = {

        nodes:
            new vis.DataSet(
                graphData.nodes
            ),

        edges:
            new vis.DataSet(
                graphData.edges
            )
    };

    const options = {

        physics: {
            enabled: true
        },

        edges: {
            arrows: 'to'
        },

        interaction: {
            hover: true
        }
    };

    new vis.Network(
        container,
        data,
        options
    );
}

startButton.addEventListener('click', async () => {

    const origin =
        document.getElementById('origin')
            .value.trim()
            .toUpperCase() || 'GRU';

    const initial_budget =
        Number(
            document.getElementById('budget').value
        ) || 500;

    const traveler_name =
        document.getElementById('traveler')
            .value.trim() || 'Anonimo';

    try {

        const data = await API.startJourney({

            origin,

            initial_budget,

            traveler_name

        });

showResponse(data);

        if (
            data.success &&
            data.journey_id
        ) {

            journeyIdInput.value =
                data.journey_id;

        }

    }

    catch (error) {

        showError(error);

    }

});

getStateButton.addEventListener(
    'click',
    async () => {

        const journeyId =
            journeyIdInput.value.trim();

        if (!journeyId) {
            return;
        }

        try {

            const data =
                await API.getJourneyState(
                    journeyId
                );

            if (!data.success) {
                return;
            }

            const state = data.current_state;

            currentAirportValue.textContent =
                state.current_airport.code;

            budgetValue.textContent =
                `$${state.budget.current}`;

            timeValue.textContent =
                `${state.time.total_journey_hours} h`;

            destinationsValue.textContent =
                state.journey_progress.destinations_count;

            routeValue.textContent =
                state.journey_progress.destinations_visited.join(' → ');

            cityValue.textContent =
                state.current_airport.city;

            countryValue.textContent =
                state.current_airport.country;

            mealRequiredValue.textContent =
                state.mandatory_requirements.meal_required
                    ? 'Sí'
                    : 'No';

            accommodationRequiredValue.textContent =
                state.mandatory_requirements.accommodation_required
                    ? 'Sí'
                    : 'No';

            renderAvailableOptions(state);
            loadJourneyLog(journeyId);
            loadJourneyReport(journeyId);

        }

        catch(error) {

            console.error(error);

        }
    }
);


executeDecisionButton.addEventListener('click', async () => {
    const journeyId = journeyIdInput.value.trim();
    const destination = destinationInput.value.trim().toUpperCase();

    if (!journeyId) {
        return showResponse({ error: 'Journey ID es requerido.' });
    }

    if (!destination) {
        return showResponse({ error: 'Destino es requerido.' });
    }

    try {
        const data = await API.executeDecision(journeyId, {
            type: 'FLIGHT',
            destination
        });

        showResponse(data);

        if (data.success) {
            getStateButton.click();
        }

    } catch (error) {
        showError(error);
    }
});

loadGraphButton.addEventListener(
    'click',
    async () => {

        try {

            const selectedFile =
                graphFileInput.files[0];

            if (!selectedFile) {

                return showResponse({
                    error:
                    'Seleccione un archivo JSON'
                });

            }

            const uploadResult =
                await API.uploadGraph(
                    selectedFile
                );

            if (!uploadResult.success) {

                return showResponse(
                    uploadResult
                );

            }

            await refreshGraph();

            showResponse({
                success: true,
                message:
                    'Grafo cargado correctamente'
            });

        }

        catch (error) {

            showError(error);

        }
    }
);

interruptRouteButton.addEventListener(
    'click',
    async () => {
        
        try {

            const journeyId =
                journeyIdInput.value;

            const origin =
                interruptOrigin.value
                    .trim()
                    .toUpperCase();

            const destination =
                interruptDestination.value
                    .trim()
                    .toUpperCase();

            if (
                !journeyId ||
                !origin ||
                !destination
            ) {
                return;
            }

            const result =
                await API.interruptRoute(
                    journeyId,
                    origin,
                    destination
                );

            alert(
                'Ruta interrumpida correctamente'
            );

            await loadJourneyLog(
                journeyId
            );

            await loadJourneyReport(
                journeyId
            );

            await refreshGraph();

        }

        catch(error) {

            console.error(error);

        }
    }
);

calculateRouteButton.addEventListener(
    'click',
    async () => {

        try {

            const origin =
                dijkstraOrigin.value
                    .trim()
                    .toUpperCase();

            const destination =
                dijkstraDestination.value
                    .trim()
                    .toUpperCase();

            const criterion =
                dijkstraCriterion.value;

            if (
                !origin ||
                !destination
            ) {
                return;
            }

            const result =
                await API.calculateDijkstra(
                    origin,
                    destination,
                    criterion
                );

            const route =
                result.result;

            const segmentsHtml =
                route.segments
                    .map(segment => `
                        <li>

                            ${segment.origin}
                            →
                            ${segment.destination}

                            |

                            ✈ ${segment.aircraft}

                            |

                            💰 ${segment.cost}

                            |

                            📏 ${segment.distanceKm} km

                        </li>
                    `)
                    .join('');

            dijkstraResult.innerHTML = `

                <h3>
                    Ruta Encontrada
                </h3>

                <p>

                    <strong>
                        Camino:
                    </strong>

                    ${route.path.join(' → ')}

                </p>

                <p>

                    <strong>
                        Peso Total:
                    </strong>

                    ${route.totalWeight}

                </p>

                <ul>

                    ${segmentsHtml}

                </ul>

            `;

        }

        catch(error) {

            console.error(error);

        }
    }
);