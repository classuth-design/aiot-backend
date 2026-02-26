const apiBase = "https://aiot-backend-9r32.onrender.com";

let tempChart;
let humChart;

// -------------------------
// CARGAR DATOS INICIALES
// -------------------------
async function loadData() {
    const response = await fetch(apiBase + "/api/data");
    const data = await response.json();

    const fechas = data.map(d => new Date(d.fecha).toLocaleTimeString()).reverse();
    const temperaturas = data.map(d => d.temperatura).reverse();
    const humedades = data.map(d => d.humedad).reverse();

    createCharts(fechas, temperaturas, humedades);
}

// -------------------------
// CREAR GRÁFICOS
// -------------------------
function createCharts(labels, tempData, humData) {

    const tempCtx = document.getElementById('tempChart').getContext('2d');
    const humCtx = document.getElementById('humChart').getContext('2d');

    tempChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Temperatura (°C)',
                data: tempData,
                borderColor: 'red',
                fill: false
            }]
        }
    });

    humChart = new Chart(humCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Humedad (%)',
                data: humData,
                borderColor: 'blue',
                fill: false
            }]
        }
    });
}

// -------------------------
// ACTUALIZAR CADA 30s
// -------------------------
setInterval(async () => {
    const response = await fetch(apiBase + "/api/data");
    const data = await response.json();

    const fechas = data.map(d => new Date(d.fecha).toLocaleTimeString()).reverse();
    const temperaturas = data.map(d => d.temperatura).reverse();
    const humedades = data.map(d => d.humedad).reverse();

    tempChart.data.labels = fechas;
    tempChart.data.datasets[0].data = temperaturas;
    tempChart.update();

    humChart.data.labels = fechas;
    humChart.data.datasets[0].data = humedades;
    humChart.update();

}, 30000);

// -------------------------
// CONTROL LED
// -------------------------
async function toggleLed(led, state) {

    await fetch(apiBase + "/api/led", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            [led]: state
        })
    });

    alert("Comando enviado");
}

// -------------------------
// IA
// -------------------------
async function getPrediction() {
    const response = await fetch(apiBase + "/api/predict");
    const data = await response.json();

    document.getElementById("predictionResult").innerText =
        "Predicción futura de humedad: " + data.predicted_humidity_10_steps;
}

// -------------------------
loadData();
