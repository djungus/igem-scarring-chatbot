const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatWindow = document.getElementById('chat-window');

let mapCounter = 0; // To ensure unique IDs for map containers
let legendShown = false; // To track if the legend has been displayed
const history = []; // Previous turns sent with each message so follow-ups have context

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    userInput.value = '';
    const typingElement = showTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, history })
        });

        const data = await response.json();
        typingElement.remove();

        history.push({ role: 'user', text });
        if (data.status === 'handoff') {
            history.push({ role: 'bot', text: 'HANDOFF_REQUIRED' });
            triggerHandoff();
        } else {
            let reply = data.reply;
            history.push({ role: 'bot', text: reply });
            
            // Check for Map Trigger with Filter (e.g. [SHOW_MAP: Texas | SOAR])
            const mapRegex = /\[SHOW_MAP:\s*(.*?)\s*\|\s*(.*?)\]/i;
            const match = reply.match(mapRegex);
            
            if (match) {
                const region = match[1].trim();
                const filter = match[2].toUpperCase().trim(); // 'ALL' or 'SOAR'
                reply = reply.replace(mapRegex, '').trim(); // Remove tag from text
                appendMessage('bot', reply);
                renderMap(region, filter); // Show map widget
            } else {
                appendMessage('bot', reply);
            }
        }
    } catch (error) {
        typingElement.remove();
        appendMessage('bot', 'Error connecting to the CareBot server. Please ensure the Python backend is running.');
        console.error(error);
    }
});

function appendMessage(sender, text) {
    if (!text) return;
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', `${sender}-message`);
    
    const bubble = document.createElement('div');
    bubble.classList.add('message-bubble');
    
    // Escape HTML first, then parse markdown bold (**text**) and line breaks
    let formattedText = escapeHtml(text).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedText = formattedText.replace(/\n/g, '<br>');
    bubble.innerHTML = formattedText;
    
    msgDiv.appendChild(bubble);
    chatWindow.appendChild(msgDiv);
    scrollToBottom();
}

function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

async function renderMap(region, filter) {
    // Show Legend on first run
    if (!legendShown) {
        const legendDiv = document.createElement('div');
        legendDiv.classList.add('message', 'bot-message');
        legendDiv.innerHTML = `
            <div class="handoff-card" style="padding: 12px; margin-bottom: 8px;">
                <h4 style="margin:0 0 8px 0; font-size:14px;">📍 Map Key</h4>
                <p style="margin:0; font-size:13px; display:flex; align-items:center; gap:8px;">
                    <span style="background-color: #2563eb; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 10px;">➕</span> 
                    <strong>Verified Burn Center</strong> (Medical Care)
                </p>
                <p style="margin:8px 0 0 0; font-size:13px; display:flex; align-items:center; gap:8px;">
                    <span style="background-color: #ea580c; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 10px;">❤️</span> 
                    <strong>Phoenix SOAR Hospital</strong> (Medical Care + Peer Support)
                </p>
            </div>
        `;
        chatWindow.appendChild(legendDiv);
        legendShown = true;
    }

    mapCounter++;
    const mapId = `map-${mapCounter}`;
    
    // Create Map Container in Chat
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'bot-message');
    msgDiv.style.width = '100%';
    
    const mapContainer = document.createElement('div');
    mapContainer.id = mapId;
    mapContainer.classList.add('map-container');
    
    msgDiv.appendChild(mapContainer);
    chatWindow.appendChild(msgDiv);
    scrollToBottom();

    // Initialize Leaflet Map
    const map = L.map(mapId).setView([39.8283, -98.5795], 4);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    // Custom Icons
    const burnCenterIcon = L.divIcon({
        html: `<div style="background-color: #2563eb; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-size: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">➕</div>`,
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    const soarHospitalIcon = L.divIcon({
        html: `<div style="background-color: #ea580c; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-size: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">❤️</div>`,
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    // Fetch Full Dataset and Render
    try {
        // Appending a timestamp query parameter forces the browser to bypass its cache
        const response = await fetch(`/hospitals.json?t=${new Date().getTime()}`);
        const hospitals = await response.json();
        
        let plottedCount = 0;
        hospitals.forEach(hospital => {
            // Apply filtering logic
            if (filter.includes('SOAR') && hospital.type !== 'soar_hospital') {
                return; // Skip non-soar hospitals if user specifically asked for support
            }
            
            plottedCount++;
            const icon = hospital.type === 'soar_hospital' ? soarHospitalIcon : burnCenterIcon;
            L.marker([hospital.lat, hospital.lng], { icon: icon })
             .addTo(map)
             .bindTooltip(`<strong>${escapeHtml(hospital.name)}</strong><br>${hospital.type === 'soar_hospital' ? 'Phoenix SOAR Support' : 'ABA Verified Center'}`);
        });
        console.log(`Plotted ${plottedCount} hospitals based on filter: ${filter}`);
    } catch (e) {
        console.error("Failed to load hospitals.json", e);
    }

    // Auto-Zoom to Region using free Nominatim API
    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(region)}`);
        const data = await res.json();
        if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lon = parseFloat(data[0].lon);
            map.flyTo([lat, lon], 6, { duration: 1.5 });
        }
    } catch (e) {
        console.log("Geocoding failed, leaving map at default view.");
    }
}

function triggerHandoff() {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'bot-message');
    msgDiv.innerHTML = `
        <div class="handoff-card">
            <h3>I want to make sure you get the best support possible.</h3>
            <p>It sounds like you might be experiencing something that requires a human touch or professional guidance. While I am an AI and cannot provide medical advice or personal counseling, there are incredible people waiting to support you.</p>
            <div class="handoff-links">
                <a href="https://resources.phoenix-society.org/contact-us" target="_blank" class="handoff-link">
                    <span>The Phoenix Society Support</span>
                    <span>→</span>
                </a>
                <a href="https://www.crisistextline.org/" target="_blank" class="handoff-link">
                    <span>Crisis Text Line (Text HOME to 741741)</span>
                    <span>→</span>
                </a>
                <a href="https://ameriburn.org/" target="_blank" class="handoff-link">
                    <span>Find a Burn Center near you</span>
                    <span>→</span>
                </a>
            </div>
        </div>
    `;
    chatWindow.appendChild(msgDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'bot-message');
    msgDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    chatWindow.appendChild(msgDiv);
    scrollToBottom();
    return msgDiv;
}

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
