const ws = new WebSocket("ws://localhost:8001/");
const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const spinner = document.getElementById("spinner");
const typingIndicator = document.getElementById("typing-indicator");
const isExtension = typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.id;
let pendingEventLink = null;

// Load sounds
const receiveSound = isExtension
  ? new Audio(chrome.runtime.getURL("resources/sounds/receive.mp3"))
  : new Audio("/static/resources/sounds/receive.mp3");

const sendSound = isExtension
  ? new Audio(chrome.runtime.getURL("resources/sounds/send.mp3"))
  : new Audio("/static/resources/sounds/send.mp3");

ws.onopen = () => {
  logToServer("WebSocket connected", "info");
};

ws.onmessage = (event) => {
  try {
    const message = JSON.parse(event.data);

    if (
      message.type === "tool_response" &&
      message.content &&
      message.content.tool_responses
    ) {
      const response = message.content.tool_responses[0].content;

      const match = response.match(/^\('(.+?)',\s*None\)$/s);
      if (match) {
        const jsonString = match[1]
          .replace(/\\n/g, "")
          .replace(/\\"/g, '"')
          .replace(/\\\\/g, "\\");

        const eventData = JSON.parse(jsonString);

        if (eventData.htmlLink) {
          pendingEventLink = eventData.htmlLink;
        }
      }
    }

    if (
      message.type === "text" &&
      message.content &&
      message.content.sender === "AssistantAgent" &&
      message.content.content
    ) {
      removeInlineSpinner();
      typingIndicator.style.display = "none";
      receiveSound.play();

      let botMessage = message.content.content;

      // Inject link if available
      if (pendingEventLink) {
        botMessage += `<br><br><a href="${pendingEventLink}" target="_blank" class="calendar-link">📅 View Calendar Event</a>`;
        pendingEventLink = null;
      }

      appendMessage("Bevie", botMessage, "bot");
    }

  } catch (error) {
    logToServer("Failed to parse WebSocket message: " + error, "error");
  }
};

ws.onerror = (err) => {
  removeInlineSpinner();
  typingIndicator.style.display = "none";
  appendMessage("System", "⚠️ WebSocket error", "bot");
  logToServer("WebSocket error: " + err, "error");
};

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;
  logToServer("User sent: " + text, "info");

  appendMessage("You", text, "user");
  sendSound.play();
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

function logToServer(message, level = "info") {
  fetch("http://localhost:8000/log", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({ message, level })
  }).catch(err => console.error("Failed to log to server:", err));
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

window.addEventListener("beforeunload", () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    // Choose closure code depending on your situation
    const isNavigation = performance.getEntriesByType("navigation")[0]?.type === "navigate";
    
    const code = isNavigation ? 1001 : 1000; // Use 1001 if navigating away, 1000 otherwise
    const reason = code === 1001 ? "Client navigating away" : "Client closed connection";

    ws.close(code, reason);
  }
});