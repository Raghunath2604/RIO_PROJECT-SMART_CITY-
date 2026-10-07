// ==========================================================================
// Fog-IDS Interactive Defense Command Center Application Logic
// ==========================================================================

const API_BASE = "";
let isApiOnline = false;
let streamInterval = null;
let isStreaming = false;
let streamRate = 2;

// Charts
let liveThroughputChart = null;
let tierBubbleChart = null;
let batchDonutChart = null;

// Telemetry state
const nodeData = [
    { id: 1, name: "Gateway Node (01)", tput: 380, cpu: 28, ram: 64, blocked: 42 },
    { id: 2, name: "Smart City Hub (02)", tput: 240, cpu: 34, ram: 48, blocked: 19 },
    { id: 3, name: "Edge Router (03)", tput: 510, cpu: 52, ram: 92, blocked: 87 },
    { id: 4, name: "Sensor Cluster (04)", tput: 160, cpu: 18, ram: 32, blocked: 6 }
];

// Presets Definition
const ATTACK_PRESETS = {
    "DDoS-SYN_Flood": {
        features: {
            "Rate": 980.0, "syn_count": 18.0, "ack_count": 12.0, "Tot size": 90.0, "IAT": 1.2, "Header_Length": 65535.0,
            "TCP": 1.0, "UDP": 0.0, "syn_flag_number": 1.0, "ack_flag_number": 1.0
        },
        name: "DDoS-SYN_Flood",
        category: "DDoS",
        severity: "Critical",
        confidence: 0.998,
        latency: 1876.0,
        action: "Firewall Auto-Drop",
        xai: [
            { feat: "ack_count", val: 12.0, score: "+6.6886", type: "indicator" },
            { feat: "syn_count", val: 18.0, score: "+5.8610", type: "indicator" },
            { feat: "Rate", val: 980.0, score: "+4.1205", type: "indicator" },
            { feat: "Header_Length", val: 65535.0, score: "+2.9412", type: "indicator" },
            { feat: "IAT", val: 1.2, score: "-1.9356", type: "normalizer" }
        ]
    },
    "Mirai-greip_flood": {
        features: {
            "Rate": 520.0, "syn_count": 0.0, "ack_count": 0.0, "Tot size": 240.0, "IAT": 4.5, "Header_Length": 32000.0,
            "TCP": 0.0, "UDP": 1.0, "syn_flag_number": 0.0, "ack_flag_number": 0.0
        },
        name: "Mirai-greip_flood",
        category: "Mirai",
        severity: "Critical",
        confidence: 0.999,
        latency: 1845.0,
        action: "Isolate Edge Port",
        xai: [
            { feat: "UDP", val: 1.0, score: "+8.4510", type: "indicator" },
            { feat: "Rate", val: 520.0, score: "+5.1200", type: "indicator" },
            { feat: "Tot size", val: 240.0, score: "+3.8812", type: "indicator" },
            { feat: "Header_Length", val: 32000.0, score: "+2.1904", type: "indicator" },
            { feat: "TCP", val: 0.0, score: "-0.9411", type: "normalizer" }
        ]
    },
    "DictionaryBruteForce": {
        features: {
            "Rate": 12.0, "syn_count": 4.0, "ack_count": 28.0, "Tot size": 85.0, "IAT": 180.0, "Header_Length": 40.0,
            "TCP": 1.0, "UDP": 0.0, "syn_flag_number": 0.0, "ack_flag_number": 1.0
        },
        name: "DictionaryBruteForce",
        category: "Brute Force",
        severity: "High",
        confidence: 0.871,
        latency: 1820.0,
        action: "Ban Source IP",
        xai: [
            { feat: "ack_count", val: 28.0, score: "+5.3400", type: "indicator" },
            { feat: "Rate", val: 12.0, score: "+3.2100", type: "indicator" },
            { feat: "IAT", val: 180.0, score: "+2.4500", type: "indicator" },
            { feat: "Tot size", val: 85.0, score: "+1.1200", type: "indicator" }
        ]
    },
    "SqlInjection": {
        features: {
            "Rate": 6.0, "syn_count": 2.0, "ack_count": 14.0, "Tot size": 450.0, "IAT": 220.0, "Header_Length": 52.0,
            "TCP": 1.0, "UDP": 0.0, "syn_flag_number": 0.0, "ack_flag_number": 1.0
        },
        name: "SqlInjection",
        category: "Web-Based",
        severity: "High",
        confidence: 0.877,
        latency: 1790.0,
        action: "WAF Rule Trigger",
        xai: [
            { feat: "Tot size", val: 450.0, score: "+6.1200", type: "indicator" },
            { feat: "IAT", val: 220.0, score: "+3.4500", type: "indicator" },
            { feat: "Rate", val: 6.0, score: "+2.1100", type: "indicator" },
            { feat: "Header_Length", val: 52.0, score: "-1.0500", type: "normalizer" }
        ]
    },
    "Recon-PortScan": {
        features: {
            "Rate": 4.5, "syn_count": 8.0, "ack_count": 0.0, "Tot size": 60.0, "IAT": 450.0, "Header_Length": 40.0,
            "TCP": 1.0, "UDP": 0.0, "syn_flag_number": 1.0, "ack_flag_number": 0.0
        },
        name: "Recon-PortScan",
        category: "Recon",
        severity: "Medium",
        confidence: 0.907,
        latency: 1830.0,
        action: "Alert Analyst",
        xai: [
            { feat: "syn_flag_number", val: 1.0, score: "+5.1200", type: "indicator" },
            { feat: "syn_count", val: 8.0, score: "+4.6700", type: "indicator" },
            { feat: "IAT", val: 450.0, score: "+3.1000", type: "indicator" }
        ]
    },
    "BenignTraffic": {
        features: {
            "Rate": 15.0, "syn_count": 1.0, "ack_count": 4.0, "Tot size": 140.0, "IAT": 350.0, "Header_Length": 52.0,
            "TCP": 1.0, "UDP": 1.0, "syn_flag_number": 0.0, "ack_flag_number": 1.0
        },
        name: "BenignTraffic",
        category: "Benign",
        severity: "Normal",
        confidence: 0.994,
        latency: 1760.0,
        action: "Forward Packet",
        xai: [
            { feat: "IAT", val: 350.0, score: "-4.8900", type: "normalizer" },
            { feat: "Rate", val: 15.0, score: "-3.1200", type: "normalizer" },
            { feat: "Tot size", val: 140.0, score: "-2.8700", type: "normalizer" }
        ]
    }
};

// -----------------------------------------------------------------------------
// Health Check
// -----------------------------------------------------------------------------
async function checkApiHealth() {
    const badge = document.getElementById("api-status-badge");
    const dot = document.getElementById("api-status-dot");
    const text = document.getElementById("api-status-text");

    try {
        const res = await fetch(`${API_BASE}/health`, { method: "GET" });
        if (res.ok) {
            const data = await res.json();
            isApiOnline = true;
            dot.className = "status-dot green-dot";
            text.innerText = `API: ONLINE (${data.cpu_usage_pct || 0}% CPU)`;
        } else {
            throw new Error("Bad status");
        }
    } catch (e) {
        isApiOnline = false;
        dot.className = "status-dot blue-dot";
        text.innerText = "API: EDGE SIMULATOR";
    }
}

// -----------------------------------------------------------------------------
// Tab Switching
// -----------------------------------------------------------------------------
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick')?.includes(tabId));
    if (activeBtn) activeBtn.classList.add('active');

    const target = document.getElementById(`tab-${tabId}`);
    if (target) target.classList.add('active');

    if (tabId === 'stream' && !liveThroughputChart) initLiveThroughputChart();
    if (tabId === 'tier' && !tierBubbleChart) initTierBubbleChart();
    if (tabId === 'api') updateApiConsolePayload(document.getElementById('api-test-endpoint')?.value || '/health');
}

// -----------------------------------------------------------------------------
// TAB 1: Live Stream & Node Simulation
// -----------------------------------------------------------------------------
function initLiveThroughputChart() {
    const ctx = document.getElementById('liveThroughputChart')?.getContext('2d');
    if (!ctx) return;

    const initialLabels = Array.from({ length: 15 }, (_, i) => `${15 - i}s ago`);
    const initialData = Array.from({ length: 15 }, () => Math.floor(Math.random() * 200 + 400));

    liveThroughputChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: initialLabels,
            datasets: [{
                label: 'Ingestion Rate (pkts/sec)',
                data: initialData,
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                fill: true,
                tension: 0.35,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: { display: false },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b', font: { size: 10 } }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function updateStreamRate(val) {
    streamRate = parseInt(val);
    document.getElementById('stream-rate-display').innerText = val;
    if (isStreaming) {
        clearInterval(streamInterval);
        streamInterval = setInterval(generateStreamRow, 1000 / streamRate);
    }
}

function generateStreamRow() {
    const keys = Object.keys(ATTACK_PRESETS);
    const key = keys[Math.floor(Math.random() * keys.length)];
    const p = ATTACK_PRESETS[key];
    const node = nodeData[Math.floor(Math.random() * nodeData.length)];
    const timeStr = new Date().toLocaleTimeString();

    // Add table row
    const tbody = document.getElementById("stream-table-body");
    if (tbody) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="color: #94a3b8;">${timeStr}</td>
            <td><b>${node.name.split(" ")[0]}</b></td>
            <td><span class="badge ${p.category === 'Benign' ? 'badge-green' : 'badge-blue'}">${p.category}</span></td>
            <td>${p.name}</td>
            <td>${(p.confidence * 100).toFixed(1)}%</td>
            <td style="color: #c084fc;">${p.latency.toFixed(1)} µs</td>
            <td><span class="severity-pill pill-${p.severity.toLowerCase()}">${p.severity}</span></td>
        `;
        tbody.insertBefore(tr, tbody.firstChild);
        if (tbody.children.length > 15) tbody.removeChild(tbody.lastChild);
    }

    // Update Node Telemetry
    if (p.category !== 'Benign') node.blocked += 1;
    node.tput = Math.min(1000, Math.max(100, node.tput + Math.floor(Math.random() * 40 - 20)));
    node.cpu = Math.min(95, Math.max(15, node.cpu + Math.floor(Math.random() * 6 - 3)));

    const tputEl = document.getElementById(`node-${node.id}-tput`);
    const cpuEl = document.getElementById(`node-${node.id}-cpu`);
    const blockEl = document.getElementById(`node-${node.id}-blocked`);
    if (tputEl) tputEl.innerText = `${node.tput} p/s`;
    if (cpuEl) cpuEl.innerText = `${node.cpu}%`;
    if (blockEl) blockEl.innerText = node.blocked;

    // Update Chart
    if (liveThroughputChart) {
        const totalTput = nodeData.reduce((acc, n) => acc + n.tput, 0);
        liveThroughputChart.data.labels.push("");
        liveThroughputChart.data.labels.shift();
        liveThroughputChart.data.datasets[0].data.push(totalTput);
        liveThroughputChart.data.datasets[0].data.shift();
        liveThroughputChart.update();
    }
}

function toggleStream() {
    const btn = document.getElementById("stream-toggle-btn");
    isStreaming = !isStreaming;

    if (isStreaming) {
        btn.innerHTML = "⏹️ Stop Stream";
        btn.classList.remove("btn-primary");
        btn.style.background = "#ef4444";
        streamInterval = setInterval(generateStreamRow, 1000 / streamRate);
    } else {
        btn.innerHTML = "▶️ Start Flow Stream";
        btn.classList.add("btn-primary");
        btn.style.background = "";
        clearInterval(streamInterval);
    }
}

function clearStreamTable() {
    const tbody = document.getElementById("stream-table-body");
    if (tbody) tbody.innerHTML = "";
}

// -----------------------------------------------------------------------------
// TAB 2: Dynamic Tier Switcher (FR5)
// -----------------------------------------------------------------------------
function updateTierSimulation(cpu) {
    document.getElementById("tier-cpu-val").innerText = `${cpu}%`;
    const card = document.getElementById("tier-display-card");
    const titleEl = document.getElementById("active-tier-title");
    const modelEl = document.getElementById("active-tier-model");
    const descEl = document.getElementById("active-tier-desc");

    if (cpu < 45) {
        titleEl.innerText = "FULL TIER";
        titleEl.style.color = "#38bdf8";
        card.style.borderColor = "#38bdf8";
        modelEl.innerText = "Model: LightGBM (150 trees)";
        descEl.innerText = "Optimal macro-F1 (0.8099) under standard edge CPU load (<45%).";
    } else if (cpu <= 75) {
        titleEl.innerText = "REDUCED TIER";
        titleEl.style.color = "#a855f7";
        card.style.borderColor = "#a855f7";
        modelEl.innerText = "Model: CompactMLP (64, 32)";
        descEl.innerText = "Fast edge neural network (132.1 µs, 135.4 KB) under moderate CPU pressure.";
    } else {
        titleEl.innerText = "MINIMAL TIER";
        titleEl.style.color = "#fb923c";
        card.style.borderColor = "#fb923c";
        modelEl.innerText = "Model: LogisticRegression (L2)";
        descEl.innerText = "Ultra-light emergency fallback (78.6 µs, 5.3 KB) under critical CPU spikes.";
    }
}

function initTierBubbleChart() {
    const ctx = document.getElementById('tierBubbleChart')?.getContext('2d');
    if (!ctx) return;

    tierBubbleChart = new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Minimal Tier (LogReg)',
                data: [{ x: 78.6, y: 0.5480, r: 8 }],
                backgroundColor: '#fb923c'
            }, {
                label: 'Reduced Tier (CompactMLP)',
                data: [{ x: 132.1, y: 0.6432, r: 14 }],
                backgroundColor: '#a855f7'
            }, {
                label: 'Full Tier (LightGBM)',
                data: [{ x: 1876.0, y: 0.8099, r: 24 }],
                backgroundColor: '#38bdf8'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'logarithmic',
                    title: { display: true, text: 'Streaming Latency (µs, log scale)', color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    title: { display: true, text: 'Macro-F1 (8-Class Task)', color: '#94a3b8' },
                    min: 0.5,
                    max: 0.9,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: { labels: { color: '#f8fafc' } }
            }
        }
    });
}

// -----------------------------------------------------------------------------
// TAB 3: Threat Vector Studio & XAI
// -----------------------------------------------------------------------------
function loadPresetFeatures(presetKey) {
    const p = ATTACK_PRESETS[presetKey] || ATTACK_PRESETS["DDoS-SYN_Flood"];
    
    document.getElementById("feat-rate").value = p.features["Rate"] || 10;
    document.getElementById("feat-rate-val").innerText = p.features["Rate"] || 10;

    document.getElementById("feat-syn").value = p.features["syn_count"] || 0;
    document.getElementById("feat-syn-val").innerText = p.features["syn_count"] || 0;

    document.getElementById("feat-ack").value = p.features["ack_count"] || 0;
    document.getElementById("feat-ack-val").innerText = p.features["ack_count"] || 0;

    document.getElementById("feat-size").value = p.features["Tot size"] || 100;
    document.getElementById("feat-size-val").innerText = p.features["Tot size"] || 100;

    document.getElementById("feat-iat").value = p.features["IAT"] || 10;
    document.getElementById("feat-iat-val").innerText = p.features["IAT"] || 10;

    document.getElementById("feat-hdr").value = p.features["Header_Length"] || 50;
    document.getElementById("feat-hdr-val").innerText = p.features["Header_Length"] || 50;

    executeInspection();
}

async function executeInspection() {
    const presetKey = document.getElementById("vector-preset")?.value || "DDoS-SYN_Flood";
    const model = document.getElementById("inspector-model")?.value || "LightGBM";
    const task = document.getElementById("inspector-task")?.value || "8class";
    const p = ATTACK_PRESETS[presetKey] || ATTACK_PRESETS["DDoS-SYN_Flood"];

    // Try API if online
    if (isApiOnline) {
        try {
            const payload = {
                features: {
                    "Rate": parseFloat(document.getElementById("feat-rate").value),
                    "syn_count": parseFloat(document.getElementById("feat-syn").value),
                    "ack_count": parseFloat(document.getElementById("feat-ack").value),
                    "Tot size": parseFloat(document.getElementById("feat-size").value),
                    "IAT": parseFloat(document.getElementById("feat-iat").value),
                    "Header_Length": parseFloat(document.getElementById("feat-hdr").value),
                    "TCP": 1.0, "IPv": 1.0
                },
                model_name: model,
                task: task,
                include_explanation: true
            };

            const res = await fetch(`${API_BASE}/api/v1/predict`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const data = await res.json();
                renderInspectionResults({
                    category: data.category,
                    confidence: data.confidence,
                    severity: data.threat_severity,
                    latency: data.latency_us,
                    action: data.threat_severity === 'Normal' ? 'Forward Packet' : 'Firewall Auto-Drop',
                    xai: p.xai
                });
                return;
            }
        } catch (e) {
            console.warn("API inspect failed, falling back to edge heuristic:", e);
        }
    }

    // Fallback simulation
    renderInspectionResults(p);
}

function renderInspectionResults(data) {
    document.getElementById("insp-prediction").innerText = data.category;
    document.getElementById("insp-category").innerText = `Category: ${data.category}`;
    document.getElementById("insp-confidence").innerText = `${(data.confidence * 100).toFixed(1)}%`;
    document.getElementById("insp-latency").innerText = `${data.latency.toFixed(1)} µs`;
    document.getElementById("insp-action").innerText = data.action;

    const sevEl = document.getElementById("insp-severity");
    sevEl.innerText = data.severity.toUpperCase();
    sevEl.className = `severity-pill pill-${data.severity.toLowerCase()}`;

    // XAI Table
    const xaiTbody = document.getElementById("xai-table-body");
    if (xaiTbody && data.xai) {
        xaiTbody.innerHTML = data.xai.map(x => `
            <tr>
                <td><b>${x.feat}</b></td>
                <td>${x.val.toFixed(2)}</td>
                <td style="color: ${x.type === 'indicator' ? '#4ade80' : '#38bdf8'}; font-weight: 700;">${x.score}</td>
                <td><span class="badge ${x.type === 'indicator' ? 'badge-orange' : 'badge-blue'}">${x.type === 'indicator' ? 'Attack Indicator' : 'Normalizing Factor'}</span></td>
            </tr>
        `).join('');
    }
}

// -----------------------------------------------------------------------------
// TAB 4: Batch CSV Scanner
// -----------------------------------------------------------------------------
function handleFileSelected(files) {
    if (!files || files.length === 0) return;
    const file = files[0];
    document.getElementById('batch-file-status').innerText = `Loaded: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    runBatchSimulation(500);
}

function generateDemoDataset() {
    document.getElementById('batch-file-status').innerText = "Loaded: cic_iot2023_sample_capture.csv (500 flows)";
    runBatchSimulation(500);
}

function runBatchSimulation(totalFlows) {
    document.getElementById("batch-results-section").style.display = "block";
    document.getElementById("batch-total-flows").innerText = totalFlows;
    document.getElementById("batch-time").innerText = "2.38 ms";
    document.getElementById("batch-throughput").innerText = "210.1K /s";
    document.getElementById("batch-attacks").innerText = "412 (82.4%)";

    const breakdown = [
        { cat: "DDoS", count: 215, pct: "43.0%", sev: "Critical" },
        { cat: "Benign", count: 88, pct: "17.6%", sev: "Normal" },
        { cat: "Mirai", count: 74, pct: "14.8%", sev: "Critical" },
        { cat: "DoS", count: 62, pct: "12.4%", sev: "High" },
        { cat: "Recon", count: 35, pct: "7.0%", sev: "Medium" },
        { cat: "Brute Force", count: 16, pct: "3.2%", sev: "High" },
        { cat: "Web-Based", count: 10, pct: "2.0%", sev: "High" }
    ];

    const tbody = document.getElementById("batch-table-body");
    tbody.innerHTML = breakdown.map(b => `
        <tr>
            <td><b>${b.cat}</b></td>
            <td>${b.count}</td>
            <td>${b.pct}</td>
            <td><span class="severity-pill pill-${b.sev.toLowerCase()}">${b.sev}</span></td>
        </tr>
    `).join('');

    // Donut Chart
    const ctx = document.getElementById("batchDonutChart")?.getContext("2d");
    if (ctx) {
        if (batchDonutChart) batchDonutChart.destroy();
        batchDonutChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: breakdown.map(b => b.cat),
                datasets: [{
                    data: breakdown.map(b => b.count),
                    backgroundColor: ['#ef4444', '#22c55e', '#a855f7', '#f97316', '#3b82f6', '#fb923c', '#06b6d4']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 10 } } }
                }
            }
        });
    }
}

// -----------------------------------------------------------------------------
// TAB 6: REST API Console
// -----------------------------------------------------------------------------
const ENDPOINT_PAYLOADS = {
    "/health": "",
    "/api/v1/models": "",
    "/api/v1/predict": JSON.stringify({
        "features": {
            "Rate": 980.0, "syn_count": 18, "ack_count": 12, "Tot size": 90, "IAT": 1.2, "TCP": 1
        },
        "model_name": "LightGBM",
        "task": "8class",
        "include_explanation": true
    }, null, 2),
    "/api/v1/predict/adaptive": JSON.stringify({
        "features": {
            "Rate": 520.0, "UDP": 1, "Tot size": 240
        },
        "task": "8class"
    }, null, 2),
    "/api/v1/predict/batch": JSON.stringify({
        "flows": [
            { "Rate": 980.0, "TCP": 1, "syn_count": 18 },
            { "Rate": 15.0, "TCP": 1, "HTTP": 1, "Tot size": 140 }
        ],
        "model_name": "CompactMLP",
        "task": "8class"
    }, null, 2)
};

function updateApiConsolePayload(endpoint) {
    const textarea = document.getElementById("api-test-payload");
    if (textarea) textarea.value = ENDPOINT_PAYLOADS[endpoint] || "";
}

async function sendConsoleApiRequest() {
    const endpoint = document.getElementById("api-test-endpoint")?.value || "/health";
    const payloadText = document.getElementById("api-test-payload")?.value || "";
    const viewer = document.getElementById("api-response-viewer");
    const statusEl = document.getElementById("api-response-status");
    const timeEl = document.getElementById("api-response-time");

    const t0 = performance.now();
    try {
        const isPost = endpoint.includes("predict");
        const options = isPost ? {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: payloadText
        } : { method: "GET" };

        const res = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await res.json();
        const elapsed = (performance.now() - t0).toFixed(1);

        statusEl.innerText = `Status: ${res.status} ${res.statusText || 'OK'}`;
        statusEl.className = res.ok ? "badge badge-green" : "badge badge-orange";
        timeEl.innerText = `Latency: ${elapsed} ms`;
        viewer.innerText = JSON.stringify(data, null, 2);
    } catch (e) {
        const elapsed = (performance.now() - t0).toFixed(1);
        statusEl.innerText = "Status: Client Simulator";
        statusEl.className = "badge badge-blue";
        timeEl.innerText = `Latency: ${elapsed} ms`;
        viewer.innerText = JSON.stringify({
            "status": "OFFLINE_FALLBACK",
            "endpoint": endpoint,
            "message": "Local microservice not connected or running in serverless static mode.",
            "simulated_response": ATTACK_PRESETS["DDoS-SYN_Flood"]
        }, null, 2);
    }
}

// -----------------------------------------------------------------------------
// Initialization
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    checkApiHealth();
    initLiveThroughputChart();
    // Populate 5 initial rows
    for (let i = 0; i < 5; i++) {
        generateStreamRow();
    }
    loadPresetFeatures("DDoS-SYN_Flood");
});
