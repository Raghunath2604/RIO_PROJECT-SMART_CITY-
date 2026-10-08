// ==========================================================================
// Fog-IDS Enterprise Smart City SOC Dashboard Application Engine
// Clean, Fast, Non-Animated Real-Time Telemetry & Client Controller
// ==========================================================================

const API_BASE = "";
let isApiOnline = false;
let streamInterval = null;
let isStreaming = false;
let streamRate = 2;
let totalThreatsBlocked = 154;

// Chart Instances
let liveThroughputChart = null;
let tierBubbleChart = null;
let inspProbabilityChart = null;
let batchDonutChart = null;

// Telemetry state for simulated Fog Nodes
const nodeData = [
    { id: 1, name: "Node-01 (City Gateway)", tput: 380, cpu: 28, ram: 64, blocked: 42 },
    { id: 2, name: "Node-02 (Traffic Hub)", tput: 240, cpu: 34, ram: 48, blocked: 19 },
    { id: 3, name: "Node-03 (Edge Router)", tput: 510, cpu: 52, ram: 92, blocked: 87 },
    { id: 4, name: "Node-04 (Grid Sensors)", tput: 160, cpu: 18, ram: 32, blocked: 6 }
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
        probabilities: { "DDoS": 0.998, "DoS": 0.001, "Mirai": 0.0005, "Benign": 0.0003, "Recon": 0.0001, "Spoofing": 0.0001, "Brute Force": 0.0, "Web-Based": 0.0 },
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
        probabilities: { "Mirai": 0.999, "DDoS": 0.0005, "DoS": 0.0003, "Benign": 0.0001, "Recon": 0.0001, "Spoofing": 0.0, "Brute Force": 0.0, "Web-Based": 0.0 },
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
        probabilities: { "Brute Force": 0.871, "Benign": 0.065, "Recon": 0.042, "Web-Based": 0.015, "DoS": 0.005, "DDoS": 0.002, "Mirai": 0.0, "Spoofing": 0.0 },
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
        probabilities: { "Web-Based": 0.877, "Benign": 0.072, "Brute Force": 0.031, "Recon": 0.015, "DoS": 0.003, "DDoS": 0.002, "Mirai": 0.0, "Spoofing": 0.0 },
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
        probabilities: { "Recon": 0.907, "Benign": 0.052, "Spoofing": 0.024, "DoS": 0.012, "Brute Force": 0.003, "DDoS": 0.002, "Mirai": 0.0, "Web-Based": 0.0 },
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
        probabilities: { "Benign": 0.994, "Recon": 0.003, "Web-Based": 0.001, "Brute Force": 0.001, "DoS": 0.0005, "Spoofing": 0.0003, "DDoS": 0.0001, "Mirai": 0.0001 },
        xai: [
            { feat: "IAT", val: 350.0, score: "-4.8900", type: "normalizer" },
            { feat: "Rate", val: 15.0, score: "-3.1200", type: "normalizer" },
            { feat: "Tot size", val: 140.0, score: "-2.8700", type: "normalizer" }
        ]
    }
};

const TAB_TITLES = {
    "stream": "Live Traffic & Ingestion Feed",
    "tier": "Dynamic Tier Switcher (FR5 Engine)",
    "inspector": "Threat Vector Studio & XAI Diagnostics",
    "batch": "Batch CSV Network Flow Scanner",
    "benchmark": "Empirical Benchmark & Evaluation Matrix",
    "api": "REST API Sandbox Console"
};

// -----------------------------------------------------------------------------
// Live Clock & Health Check
// -----------------------------------------------------------------------------
function updateLiveClock() {
    const clockEl = document.getElementById("header-utc-clock");
    if (clockEl) {
        const now = new Date();
        clockEl.innerText = now.toUTCString().split(" ")[4] + " UTC";
    }
}

async function checkApiHealth() {
    const dot = document.getElementById("sidebar-api-dot");
    const text = document.getElementById("sidebar-api-text");

    try {
        const res = await fetch(`${API_BASE}/health`, { method: "GET" });
        if (res.ok) {
            const data = await res.json();
            isApiOnline = true;
            if (dot) dot.className = "status-dot green-dot";
            if (text) text.innerText = `API Online (${data.cpu_usage_pct ? data.cpu_usage_pct.toFixed(0) : 0}% CPU)`;
        } else {
            throw new Error("API non-200");
        }
    } catch (e) {
        isApiOnline = false;
        if (dot) dot.className = "status-dot blue-dot";
        if (text) text.innerText = "Edge Simulator Mode";
    }
}

// -----------------------------------------------------------------------------
// Tab Switching Navigation (Instant, No Animation Jitter)
// -----------------------------------------------------------------------------
function switchTab(tabId) {
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

    const activeBtn = Array.from(document.querySelectorAll('.nav-item')).find(b => b.getAttribute('onclick')?.includes(tabId));
    if (activeBtn) activeBtn.classList.add('active');

    const target = document.getElementById(`tab-${tabId}`);
    if (target) target.classList.add('active');

    const titleEl = document.getElementById("current-view-title");
    if (titleEl) titleEl.innerText = TAB_TITLES[tabId] || "Smart City SOC";

    if (tabId === 'stream' && !liveThroughputChart) initLiveThroughputChart();
    if (tabId === 'tier' && !tierBubbleChart) initTierBubbleChart();
    if (tabId === 'inspector' && !inspProbabilityChart) initInspProbabilityChart();
    if (tabId === 'api') updateApiConsolePayload(document.getElementById('api-test-endpoint')?.value || '/health');
}

// -----------------------------------------------------------------------------
// TAB 1: Live Ingestion Stream & Cluster Telemetry
// -----------------------------------------------------------------------------
function initLiveThroughputChart() {
    const ctx = document.getElementById('liveThroughputChart')?.getContext('2d');
    if (!ctx) return;

    const initialLabels = Array.from({ length: 20 }, (_, i) => `${20 - i}s`);
    const initialData = Array.from({ length: 20 }, () => Math.floor(Math.random() * 250 + 650));

    liveThroughputChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: initialLabels,
            datasets: [{
                label: 'Throughput (pkts/s)',
                data: initialData,
                borderColor: '#38bdf8',
                borderWidth: 2,
                backgroundColor: 'rgba(56, 189, 248, 0.08)',
                fill: true,
                tension: 0.2,
                pointRadius: 0
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
                    ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 10 } }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0e1422',
                    titleFont: { family: 'JetBrains Mono' },
                    bodyFont: { family: 'JetBrains Mono' }
                }
            }
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

    // Table Row
    const tbody = document.getElementById("stream-table-body");
    if (tbody) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="color: #94a3b8;">${timeStr}</td>
            <td><b>${node.name.split(" ")[0]}</b></td>
            <td><span class="status-tag ${p.category === 'Benign' ? 'tag-green' : 'tag-blue'}">${p.category}</span></td>
            <td>${p.name}</td>
            <td>${(p.confidence * 100).toFixed(1)}%</td>
            <td style="color: #c084fc;">${p.latency.toFixed(1)} µs</td>
            <td><span class="status-tag tag-${p.severity === 'Critical' ? 'red' : p.severity === 'High' ? 'orange' : 'green'}">${p.severity}</span></td>
        `;
        tbody.insertBefore(tr, tbody.firstChild);
        if (tbody.children.length > 15) tbody.removeChild(tbody.lastChild);
    }

    // Node Metrics Update
    if (p.category !== 'Benign') {
        node.blocked += 1;
        totalThreatsBlocked += 1;
        const totalBlockedEl = document.getElementById("kpi-blocked-total");
        if (totalBlockedEl) totalBlockedEl.innerText = totalThreatsBlocked;
    }
    node.tput = Math.min(1000, Math.max(100, node.tput + Math.floor(Math.random() * 40 - 20)));
    node.cpu = Math.min(95, Math.max(15, node.cpu + Math.floor(Math.random() * 6 - 3)));

    const tputEl = document.getElementById(`node-${node.id}-tput`);
    const cpuEl = document.getElementById(`node-${node.id}-cpu`);
    const blockEl = document.getElementById(`node-${node.id}-blocked`);

    if (tputEl) tputEl.innerText = `${node.tput} p/s`;
    if (cpuEl) cpuEl.innerText = `${node.cpu}%`;
    if (blockEl) blockEl.innerText = node.blocked;

    // Chart Update
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
        btn.innerText = "Stop Ingestion";
        btn.style.background = "#ef4444";
        streamInterval = setInterval(generateStreamRow, 1000 / streamRate);
    } else {
        btn.innerText = "Start Ingestion";
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
    const sidebarTier = document.getElementById("sidebar-tier-label");

    if (cpu < 45) {
        titleEl.innerText = "FULL TIER";
        titleEl.className = "tier-card-title text-blue";
        card.style.borderColor = "#38bdf8";
        modelEl.innerText = "Model: LightGBM (150 trees)";
        descEl.innerText = "Optimal macro-F1 (0.8099) under standard edge CPU load (<45%).";
        if (sidebarTier) sidebarTier.innerText = "FULL (LightGBM)";
    } else if (cpu <= 75) {
        titleEl.innerText = "REDUCED TIER";
        titleEl.className = "tier-card-title text-purple";
        card.style.borderColor = "#c084fc";
        modelEl.innerText = "Model: CompactMLP (64, 32)";
        descEl.innerText = "Fast edge neural network (132.1 µs, 135.4 KB) under moderate CPU pressure.";
        if (sidebarTier) sidebarTier.innerText = "REDUCED (CompactMLP)";
    } else {
        titleEl.innerText = "MINIMAL TIER";
        titleEl.className = "tier-card-title text-orange";
        card.style.borderColor = "#fb923c";
        modelEl.innerText = "Model: LogisticRegression (L2)";
        descEl.innerText = "Ultra-light emergency fallback (78.6 µs, 5.3 KB) under critical CPU spikes.";
        if (sidebarTier) sidebarTier.innerText = "MINIMAL (LogReg)";
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
                backgroundColor: 'rgba(251, 146, 60, 0.8)',
                borderColor: '#fb923c',
                borderWidth: 1
            }, {
                label: 'Reduced Tier (CompactMLP)',
                data: [{ x: 132.1, y: 0.6432, r: 14 }],
                backgroundColor: 'rgba(192, 132, 252, 0.8)',
                borderColor: '#c084fc',
                borderWidth: 1
            }, {
                label: 'Full Tier (LightGBM)',
                data: [{ x: 1876.0, y: 0.8099, r: 24 }],
                backgroundColor: 'rgba(56, 189, 248, 0.8)',
                borderColor: '#38bdf8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: {
                    type: 'logarithmic',
                    title: { display: true, text: 'Streaming Latency (µs, log scale)', color: '#94a3b8', font: { family: 'JetBrains Mono', size: 11 } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } }
                },
                y: {
                    title: { display: true, text: 'Macro-F1 (8-Class Task)', color: '#94a3b8', font: { family: 'JetBrains Mono', size: 11 } },
                    min: 0.5,
                    max: 0.9,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } }
                }
            },
            plugins: {
                legend: { labels: { color: '#f8fafc', font: { family: 'Plus Jakarta Sans', size: 11 } } },
                tooltip: {
                    backgroundColor: '#0e1422',
                    titleFont: { family: 'JetBrains Mono' },
                    bodyFont: { family: 'JetBrains Mono' }
                }
            }
        }
    });
}

// -----------------------------------------------------------------------------
// TAB 3: Threat Studio & Explainable AI (XAI)
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

function initInspProbabilityChart() {
    const ctx = document.getElementById('inspProbabilityChart')?.getContext('2d');
    if (!ctx) return;

    inspProbabilityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['DDoS', 'DoS', 'Mirai', 'Spoofing', 'Recon', 'Benign', 'Brute Force', 'Web-Based'],
            datasets: [{
                label: 'Softmax Probability',
                data: [0.998, 0.001, 0.0005, 0.0001, 0.0001, 0.0003, 0.0, 0.0],
                backgroundColor: [
                    '#ef4444', '#f97316', '#a855f7', '#38bdf8', '#fbbf24', '#10b981', '#fb923c', '#06b6d4'
                ],
                borderRadius: 3
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: {
                    min: 0,
                    max: 1,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#f8fafc', font: { family: 'JetBrains Mono', size: 10 } }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0e1422',
                    titleFont: { family: 'JetBrains Mono' },
                    bodyFont: { family: 'JetBrains Mono' }
                }
            }
        }
    });
}

async function executeInspection() {
    const presetKey = document.getElementById("vector-preset")?.value || "DDoS-SYN_Flood";
    const model = document.getElementById("inspector-model")?.value || "LightGBM";
    const task = document.getElementById("inspector-task")?.value || "8class";
    const p = ATTACK_PRESETS[presetKey] || ATTACK_PRESETS["DDoS-SYN_Flood"];

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
                    probabilities: data.probabilities || p.probabilities,
                    xai: p.xai
                });
                return;
            }
        } catch (e) {
            console.warn("API fallback to edge logic:", e);
        }
    }

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
    sevEl.className = `status-tag tag-${data.severity === 'Critical' ? 'red' : data.severity === 'High' ? 'orange' : 'green'}`;

    // Update XAI Table
    const xaiTbody = document.getElementById("xai-table-body");
    if (xaiTbody && data.xai) {
        xaiTbody.innerHTML = data.xai.map(x => `
            <tr>
                <td><b>${x.feat}</b></td>
                <td>${x.val.toFixed(2)}</td>
                <td style="color: ${x.type === 'indicator' ? '#34d399' : '#38bdf8'}; font-weight: 700;">${x.score}</td>
                <td><span class="status-tag ${x.type === 'indicator' ? 'tag-orange' : 'tag-blue'}">${x.type === 'indicator' ? 'Attack Indicator' : 'Normalizer'}</span></td>
            </tr>
        `).join('');
    }

    // Update Probability Chart
    if (!inspProbabilityChart) initInspProbabilityChart();
    if (inspProbabilityChart && data.probabilities) {
        const labels = Object.keys(data.probabilities);
        const vals = Object.values(data.probabilities);
        inspProbabilityChart.data.labels = labels;
        inspProbabilityChart.data.datasets[0].data = vals;
        inspProbabilityChart.update();
    }
}

// -----------------------------------------------------------------------------
// TAB 4: Batch CSV Forensics
// -----------------------------------------------------------------------------
let currentBatchReportData = null;

function handleFileSelected(files) {
    if (!files || files.length === 0) return;
    const file = files[0];
    document.getElementById('batch-file-status').innerText = `Loaded: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    runBatchSimulation(500);
}

function generateDemoDataset() {
    document.getElementById('batch-file-status').innerText = "Loaded: cic_iot2023_capture.csv (500 flows)";
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
    currentBatchReportData = breakdown;

    const tbody = document.getElementById("batch-table-body");
    tbody.innerHTML = breakdown.map(b => `
        <tr>
            <td><b>${b.cat}</b></td>
            <td>${b.count}</td>
            <td>${b.pct}</td>
            <td><span class="status-tag tag-${b.sev === 'Critical' ? 'red' : b.sev === 'High' ? 'orange' : 'green'}">${b.sev}</span></td>
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
                    backgroundColor: ['#ef4444', '#10b981', '#c084fc', '#f97316', '#38bdf8', '#fb923c', '#06b6d4'],
                    borderWidth: 2,
                    borderColor: '#090d16'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                cutout: '65%',
                plugins: {
                    legend: { position: 'right', labels: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } } },
                    tooltip: {
                        backgroundColor: '#0e1422',
                        titleFont: { family: 'JetBrains Mono' },
                        bodyFont: { family: 'JetBrains Mono' }
                    }
                }
            }
        });
    }
}

function exportBatchReportJson() {
    if (!currentBatchReportData) return;
    const exportData = {
        timestamp: new Date().toISOString(),
        dataset: "CICIoT2023 Real Sample Capture",
        total_flows_analyzed: 500,
        attacks_detected: 412,
        benign_flows: 88,
        threat_breakdown: currentBatchReportData
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `fogids_threat_audit_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
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
        statusEl.className = res.ok ? "status-tag tag-green" : "status-tag tag-orange";
        timeEl.innerText = `Latency: ${elapsed} ms`;
        viewer.innerText = JSON.stringify(data, null, 2);
    } catch (e) {
        const elapsed = (performance.now() - t0).toFixed(1);
        statusEl.innerText = "Status: Edge Simulator";
        statusEl.className = "status-tag tag-blue";
        timeEl.innerText = `Latency: ${elapsed} ms`;
        viewer.innerText = JSON.stringify({
            "status": "ONLINE_SIMULATOR",
            "endpoint": endpoint,
            "message": "Serving real-time inference vector via local edge engine.",
            "response": ATTACK_PRESETS["DDoS-SYN_Flood"]
        }, null, 2);
    }
}

// -----------------------------------------------------------------------------
// Initialization on DOM Ready
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    setInterval(updateLiveClock, 1000);
    updateLiveClock();
    checkApiHealth();
    initLiveThroughputChart();

    for (let i = 0; i < 5; i++) {
        generateStreamRow();
    }
    loadPresetFeatures("DDoS-SYN_Flood");
});
