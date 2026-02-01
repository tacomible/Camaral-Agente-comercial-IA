const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");


function addMessage(text, type) {

  const msg = document.createElement("div");

  msg.className = `message ${type}`;

  msg.textContent = text;

  chatBox.appendChild(msg);

  chatBox.scrollTop = chatBox.scrollHeight;
}



// -------------------------
// Mostrar formulario lead
// -------------------------

function showLeadForm() {

  if (document.getElementById("lead-form")) return;

  const form = document.createElement("div");

  form.id = "lead-form";
  form.className = "lead-form";

  form.innerHTML = `
    <h3>Déjanos tus datos</h3>

    <input id="lead-name" placeholder="Nombre" />
    <input id="lead-email" placeholder="Email" />
    <input id="lead-whatsapp" placeholder="WhatsApp" />

    <button id="lead-send">Enviar</button>
  `;

  chatBox.appendChild(form);

  chatBox.scrollTop = chatBox.scrollHeight;


  document
    .getElementById("lead-send")
    .addEventListener("click", sendLead);
}



// -------------------------
// Enviar lead
// -------------------------

async function sendLead() {

  const name = document.getElementById("lead-name").value.trim();
  const email = document.getElementById("lead-email").value.trim();
  const whatsapp = document.getElementById("lead-whatsapp").value.trim();

  if (!name || !email || !whatsapp) {

    alert("Completa todos los campos");

    return;
  }


  try {

    const res = await fetch("/lead", {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        name,
        email,
        whatsapp
      })
    });


    const data = await res.json();


    if (data.status === "ok") {

      addMessage(
        "Gracias 🙌 Un asesor se comunicará contigo pronto.",
        "bot"
      );

      document.getElementById("lead-form").remove();

    } else {

      addMessage("Error guardando datos.", "bot");
    }


  } catch (err) {

    console.error(err);

    addMessage("Error enviando datos.", "bot");
  }
}



// -------------------------
// Enviar mensaje
// -------------------------

async function sendMessage() {

  const message = input.value.trim();

  if (!message) return;


  addMessage(message, "user");

  input.value = "";


  try {

    const res = await fetch("/chat", {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        text: message
      })
    });


    const data = await res.json();


    if (data.reply) {

      addMessage(data.reply, "bot");


      // 👉 SI HAY INTENCIÓN COMERCIAL
      if (data.lead === true) {

        showLeadForm();
      }

    } else {

      addMessage("Error procesando el mensaje.", "bot");

      console.error(data);
    }


  } catch (err) {

    console.error(err);

    addMessage("Error de conexión.", "bot");
  }
}



// -------------------------
// Eventos
// -------------------------

sendBtn.addEventListener("click", sendMessage);


input.addEventListener("keydown", (e) => {

  if (e.key === "Enter") {

    sendMessage();
  }
});
