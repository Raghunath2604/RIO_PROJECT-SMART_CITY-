// ==========================================================================
// Fog-IDS Interactive Client-Side Engine & REST Integration
// ==========================================================================

const API_BASE = "";

// State
let streamInterval = null;
let isStreaming = false;
let tierChart = null;

// Tab Switcher
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    const target = document.getElementById(`tab-${tabId}`);
    if (target) target.classList.add('active');

    if (tabId === 'tier' && !tierChart) {
        initTierChart();
    }
}

// Preset Attack Definitions
const ATTACK_PRESETS = {
    "DDoS-SYN_Flood": {
        features: {
            "TCP": 1.0, "syn_flag_number": 1.0, "ack_flag_number": 1.0, "syn_count": 18.0,
            "ack_count": 12.0, "Rate": 980.0, "Srate": 980.0, "Tot size": 90.0, "IAT": 1.2
        },
        name: "DDoS-SYN_Flood",
        category: "DDoS",
        severity: "Critical",
        confidence: 0.998,
        latency: 1876.0
    },
    "Mirai-greip_flood": {
        features: {
            "UDP": 1.0, "TCP": 0.0, "Rate": 520.0, "Srate": 520.0, "Header_Length": 32000.0, "Tot size": 240.0
        },
        name: "Mirai-greip_flood",
        category: "Mirai",
        severity: "Critical",
        confidence: 0.999,
        latency: 1845.0
    },
    "DictionaryBruteForce": {
        features: {
            "TCP": 1.0, "SSH": 1.0, "Telnet": 1.0, "Rate": 12.0, "Srate": 12.0, "psh_flag_number": 1.0
        },
        name: "DictionaryBruteForce",
        category: "Brute Force",
        severity: "High",
        confidence: 0.871,
        latency: 1820.0
    },
    "SqlInjection": {
        features: {
            "HTTP": 1.0, "HTTPS": 1.0, "TCP": 1.0, "Rate": 6.0, "Tot size": 450.0, "IAT": 220.0
        },
        name: "SqlInjection",
        category: "Web-Based",
        severity: "High",
        confidence: 0.877,
        latency: 1790.0
    },
    "Recon-PortScan": {
        features: {
            "TCP": 1.0, "syn_flag_number": 1.0, "rst_flag_number": 1.0, "Rate": 4.5, "Tot size": 60.0
        },
        name: "Recon-PortScan",
        category: "Recon",
        severity: "Medium",
        confidence: 0.907,
        latency: 1830.0
    },
    "BenignTraffic": {
        features: {
            "TCP": 1.0, "UDP": 1.0, "HTTP": 1.0, "HTTPS": 1.0, "DNS": 1.0, "Rate": 15.0, "Tot size": 140.0
        },
        name: "BenignTraffic",
        category: "Benign",
        severity: "Normal",
        confidence: 0.994,
        latency: 1760.0
    }
};

// Stream Replay Engine
const NODES = ["Node-01 (Gateway)", "Node-02 (Smart Hub)", "Node-03 (Edge Router)", "Node-04 (Sensor Hub)"];

function addStreamRow(presetKey) {
    const p = ATTACK_PRESETS[presetKey] || ATTACK_PRESETS["DDoS-SYN_Flood"];
    const tbody = document.getElementById("stream-table-body");
    const node = NODES[Math.floor(Math.random() * NODES.length)];
    const timeStr = new Date().toLocaleTimeString();

    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td style="color: #94a3b8;">${timeStr}</td>
        <td><b>${node}</b></td>
        <td><span class="badge ${p.category === 'Benign' ? 'badge-green' : 'badge-blue'}">${p.category}</span></td>
        <td>${p.name}</td>
        <td>${(p.confidence * 100).toFixed(1)}%</td>
        <td style="color: #c084fc;">${p.latency.toFixed(1)} µs</td>
        <td><span class="severity-pill pill-${p.severity.toLowerCase()}">${p.severity}</span></td>
    `;

    tbody.insertBefore(tr, tbody.firstChild);
    if (tbody.children.length > 15) {
        tbody.removeChild(tbody.lastChild);
    }
}

function toggleStream() {
    const btn = document.getElementById("stream-toggle-btn");
    isStreaming = !isStreaming;

    if (isStreaming) {
        btn.innerHTML = "⏹️ Stop Stream";
        btn.classList.remove("btn-primary");
        btn.style.background = "#ef4444";
        
        const keys = Object.keys(ATTACK_PRESETS);
        streamInterval = setInterval(() => {
            const randomKey = keys[Math.floor(Math.random() * keys.length)];
            addStreamRow(randomKey);
        }, 1200);
    } else {
        btn.innerHTML = "▶️ Start Flow Stream";
        btn.classList.add("btn-primary");
        btn.style.background = "";
        clearInterval(streamInterval);
    }
}

// FR5 Tier Switcher Logic
function updateTierSimulation(cpu) {
    document.getElementById("cpu-slider-val").innerText = `${cpu}%`;
    const card = document.getElementById("tier-card");
    const nameEl = document.getElementById("active-tier-name");
    const modelEl = document.getElementById("active-tier-model");
    const descEl = document.getElementById("active-tier-desc");

    if (cpu < 45) {
        nameEl.innerText = "FULL TIER";
        nameEl.style.color = "#38bdf8";
        card.style.borderColor = "#38bdf8";
        modelEl.innerText = "Model: LightGBM (150 trees)";
        descEl.innerText = "Optimal macro-F1 (0.8099) under standard edge CPU load (<45%).";
    } else if (cpu <= 75) {
        nameEl.innerText = "REDUCED TIER";
        nameEl.style.color = "#a855f7";
        card.style.borderColor = "#a855f7";
        modelEl.innerText = "Model: CompactMLP (64, 32)";
        descEl.innerText = "Fast edge neural network (132 µs, 135 KB) under moderate CPU pressure.";
    } else {
        nameEl.innerText = "MINIMAL TIER";
        nameEl.style.color = "#fb923c";
        card.style.borderColor = "#fb923c";
        modelEl.innerText = "Model: LogisticRegression (L2)";
        descEl.innerText = "Ultra-light emergency fallback (78 µs, 5.3 KB) under critical CPU spikes.";
    }
}

function initTierChart() {
    const ctx = document.getElementById('tierChart').getContext('2d');
    tierChart = new Chart(ctx, {
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

// Inspector Logic
function runInspection() {
    const presetKey = document.getElementById("preset-select").value;
    const model = document.getElementById("model-select").value;
    const task = document.getElementById("task-select").value;
    const p = ATTACK_PRESETS[presetKey] || ATTACK_PRESETS["DDoS-SYN_Flood"];

    document.getElementById("insp-prediction").innerText = p.category;
    document.getElementById("insp-category").innerText = `Category: ${p.category}`;
    document.getElementById("insp-confidence").innerText = `${(p.confidence * 100).toFixed(1)}%`;
    document.getElementById("insp-latency").innerText = `${p.latency.toFixed(1)} µs`;

    const sevEl = document.getElementById("insp-severity");
    sevEl.innerText = p.severity.toUpperCase();
    sevEl.className = `severity-pill pill-${p.severity.toLowerCase()}`;

    // Update XAI table
    const xaiTbody = document.getElementById("xai-table-body");
    xaiTbody.innerHTML = `
        <tr><td>ack_count</td><td>12.00</td><td style="color:#4ade80;">+6.6886</td><td><span class="badge badge-orange">Attack Indicator</span></td></tr>
        <tr><td>syn_count</td><td>18.00</td><td style="color:#4ade80;">+5.8610</td><td><span class="badge badge-orange">Attack Indicator</span></td></tr>
        <tr><td>Variance</td><td>10.00</td><td style="color:#4ade80;">+3.0733</td><td><span class="badge badge-orange">Attack Indicator</span></td></tr>
        <tr><td>fin_count</td><td>10.00</td><td style="color:#4ade80;">+2.4568</td><td><span class="badge badge-orange">Attack Indicator</span></td></tr>
        <tr><td>IAT</td><td>1.20</td><td style="color:#38bdf8;">-1.9356</td><td><span class="badge badge-blue">Normalizing Factor</span></td></tr>
    `;
}

// Initialize on Load
document.addEventListener("DOMContentLoaded", () => {
    // Populate initial stream rows
    for (let i = 0; i < 5; i++) {
        const keys = Object.keys(ATTACK_PRESETS);
        addStreamRow(keys[i % keys.length]);
    }
    runInspection();
});
