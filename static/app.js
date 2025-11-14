// static/app.js
// Cliente WebSocket que conecta con el endpoint /ws.
// Comentarios explican cada bloque.

const protocol = window.location.protocol === "https:" ? "wss" : "ws";
// Usamos window.location.host para que funcione tanto local como en Render (dominio real)
const ws = new WebSocket(`${protocol}://${window.location.host}/ws`);

// Elementos del DOM
const form = document.getElementById("chat-form");
const chatBox = document.getElementById("chat-box");
const usernameInput = document.getElementById("username");
const messageInput = document.getElementById("message");

// Mensaje de carga mientras llegan los mensajes anteriores
const loading = document.createElement("p");
loading.textContent = "Cargando mensajes anteriores...";
chatBox.appendChild(loading);

// Evento cuando la conexión WebSocket se abre correctamente
ws.onopen = () => {
  loading.textContent = "Conectado. Puedes chatear.";
};

// Evento cuando llega un mensaje (tanto historial como nuevos)
ws.onmessage = (event) => {
  const msg = document.createElement("p");
  msg.textContent = event.data; // el backend envía "usuario: texto"
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight; // auto-scroll al final
};

// Manejo de submit del formulario
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const user = usernameInput.value.trim();
  const text = messageInput.value.trim();
  if (!text || !user) return; // validación básica
  // Enviamos en el formato "usuario: texto" (el backend lo parsea y guarda)
  ws.send(`${user}: ${text}`);
  messageInput.value = ""; // limpiamos el input
});
