const button = document.getElementById("send-btn");

const input = document.getElementById("user-input");

const chatBox = document.getElementById("chat-box");


button.addEventListener("click", () => {

    const message = input.value;


    if (message.trim() === "")
        return;


    const userMessage = document.createElement("div");

    userMessage.innerHTML = "You: " + message;


    chatBox.appendChild(userMessage);


    input.value = "";

});