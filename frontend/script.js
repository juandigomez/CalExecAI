const ws = new WebSocket("ws://localhost:8001/ws/chat");
const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const spinner = document.getElementById("spinner");

ws.onopen = () => {
  console.log("✅ WebSocket connected");
};

ws.onmessage = (event) => {
  spinner.style.display = "none";  // Hide spinner when bot replies
  appendMessage("Assistant", event.data, "bot");
};

ws.onerror = (err) => {
  spinner.style.display = "none";  // Hide spinner on error too
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
  ws.send(text);
  userInput.value = "";

  spinner.style.display = "block"; // Show spinner after sending message
}

function appendMessage(sender, text, className) {
  const msg = document.createElement("div");
  msg.className = `message ${className}`;
  msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
