const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const ws = new WebSocket(`${protocol}://${window.location.host}/ws`);

const form = document.getElementById("chat-form");
const chatBox = document.getElementById("chat-box");
const usernameInput = document.getElementById("username");
const messageInput = document.getElementById("message");

// Mostrar mensaje de carga
const loading = document.createElement("p");
loading.textContent = "Cargando mensajes anteriores...";
chatBox.appendChild(loading);

ws.onopen = () => {
  loading.textContent = " Conectado. Puedes chatear.";
};

ws.onmessage = (event) => {
  const msg = document.createElement("p");
  msg.textContent = event.data;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
};

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const user = usernameInput.value.trim();
  const text = messageInput.value.trim();
  if (!text || !user) return;
  ws.send(`${user}: ${text}`);
  messageInput.value = "";
});
