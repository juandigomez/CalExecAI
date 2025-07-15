const ws = new WebSocket("ws://localhost:8001/ws/chat");
const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const spinner = document.getElementById("spinner");
const typingIndicator = document.getElementById("typing-indicator");

// Load sounds
//const sendSound = new Audio("/static/send.mp3");
//const receiveSound = new Audio("/static/receive.mp3");

ws.onopen = () => {
  console.log("✅ WebSocket connected");
};

ws.onmessage = (event) => {
  removeInlineSpinner();
  typingIndicator.style.display = "none";
  //receiveSound.play();
  appendMessage("Assistant", event.data, "bot");
};

ws.onerror = (err) => {
  removeInlineSpinner();
  typingIndicator.style.display = "none";
  appendMessage("System", "⚠️ WebSocket error", "bot");
  console.error("WebSocket error:", err);
};

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  appendMessage("You", text, "user");
  //sendSound.play();
  ws.send(text);
  userInput.value = "";

  addInlineSpinner();
  typingIndicator.style.display = "block";
}

function appendMessage(sender, text, className) {
  const msg = document.createElement("div");
  msg.className = `message ${className}`;
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  msg.innerHTML = `<strong>${sender}:</strong><br>${text}<span class="timestamp">${time}</span>`;
  chatWindow.appendChild(msg);

  // GCal-style event card
  if (sender === "Assistant") {
    const eventCard = extractEventCard(text);
    if (eventCard) {
      chatWindow.appendChild(eventCard);
    }
  }

  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addInlineSpinner() {
  removeInlineSpinner();

  const spinnerBubble = document.createElement("div");
  spinnerBubble.className = "message bot inline-spinner";
  spinnerBubble.id = "inline-spinner";
  spinnerBubble.innerHTML = `
    <span class="spinner-dot"></span>
    <span class="spinner-dot"></span>
    <span class="spinner-dot"></span>
  `;
  chatWindow.appendChild(spinnerBubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeInlineSpinner() {
  const old = document.getElementById("inline-spinner");
  if (old) old.remove();
}


function extractEventCard(text) {
  const eventRegex = /(schedule|add|set).*?(\bmeeting\b|\bevent\b).*?\b(on|for)\b (.+?)\b(at|@)\b (.+?)(\.|$)/i;
  const match = text.match(eventRegex);

  if (match) {
    const title = match[2].charAt(0).toUpperCase() + match[2].slice(1);
    const date = match[4];
    const time = match[6];

    const card = document.createElement("div");
    card.style.marginTop = "10px";
    card.style.padding = "12px 16px";
    card.style.border = "1px solid #e5e7eb";
    card.style.borderRadius = "10px";
    card.style.backgroundColor = "#fef9f5";
    card.style.fontSize = "13px";
    card.style.boxShadow = "0 2px 6px rgba(0, 0, 0, 0.05)";
    card.innerHTML = `
      <strong>📅 ${title}</strong><br>
      <span>🗓️ ${date}<br>🕒 ${time}</span>
    `;
    return card;
  }
  return null;
}

const prefersDark = localStorage.getItem("theme") === "dark";
if (prefersDark) {
  document.body.classList.replace("light-mode", "dark-mode");
  document.body.setAttribute("data-theme", "dark");
}

document.getElementById("theme-toggle").addEventListener("click", () => {
  const isDark = document.body.classList.contains("dark-mode");
  if (isDark) {
    document.body.classList.replace("dark-mode", "light-mode");
    document.body.setAttribute("data-theme", "light");
    localStorage.setItem("theme", "light");
  } else {
    document.body.classList.replace("light-mode", "dark-mode");
    document.body.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
  }
});