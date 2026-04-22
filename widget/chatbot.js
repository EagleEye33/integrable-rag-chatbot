(function () {
  function createChatbotWidget(config) {
    var settings = Object.assign(
      {
        apiBaseUrl: "http://localhost:8000",
        apiPrefix: "/api",
        organizationName: "Support Assistant",
      },
      config || {}
    );

    var style = document.createElement("link");
    style.rel = "stylesheet";
    style.href = settings.cssUrl || "/widget/chatbot.css";
    document.head.appendChild(style);

    var toggle = document.createElement("button");
    toggle.className = "chatbot-toggle";
    toggle.textContent = "AI";
    document.body.appendChild(toggle);

    var panel = document.createElement("div");
    panel.className = "chatbot-panel";
    panel.innerHTML =
      '<div class="chatbot-header">' +
      settings.organizationName +
      '</div><div class="chatbot-messages"></div><div class="chatbot-input-wrap"><input placeholder="Ask a question..." /><button>Send</button></div>';
    document.body.appendChild(panel);

    var messagesEl = panel.querySelector(".chatbot-messages");
    var inputEl = panel.querySelector("input");
    var sendBtn = panel.querySelector("button");

    function addMessage(text, role, sources) {
      var item = document.createElement("div");
      item.className = "chatbot-msg " + role;
      item.textContent = text;
      if (role === "bot" && sources && sources.length) {
        var refs = document.createElement("div");
        refs.className = "chatbot-sources";
        refs.textContent =
          "Sources: " + sources.map(function (s) { return s.source; }).join(", ");
        item.appendChild(refs);
      }
      messagesEl.appendChild(item);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    async function askQuestion(question) {
      var endpoint = settings.apiBaseUrl + settings.apiPrefix + "/chat";
      var response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question }),
      });
      if (!response.ok) {
        throw new Error("Request failed");
      }
      return response.json();
    }

    async function sendMessage() {
      var question = inputEl.value.trim();
      if (!question) return;

      addMessage(question, "user");
      inputEl.value = "";
      sendBtn.disabled = true;

      try {
        var payload = await askQuestion(question);
        addMessage(payload.answer, "bot", payload.sources || []);
      } catch (err) {
        addMessage("Sorry, the assistant is currently unavailable.", "bot");
      } finally {
        sendBtn.disabled = false;
      }
    }

    sendBtn.addEventListener("click", sendMessage);
    inputEl.addEventListener("keydown", function (event) {
      if (event.key === "Enter") sendMessage();
    });
    toggle.addEventListener("click", function () {
      panel.classList.toggle("open");
    });

    addMessage(
      "Hi! Ask me anything about " + settings.organizationName + ".",
      "bot"
    );
  }

  window.WebsiteChatbot = { init: createChatbotWidget };
})();
