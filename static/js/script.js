/*const button = document.getElementById("send-btn");

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

});*/
const button = document.getElementById("send-btn");

const input = document.getElementById("user-input");

const chatBox = document.getElementById("chat-box");


button.addEventListener("click", async () => {


    const message = input.value;


    if (message.trim() === "")
        return;



    chatBox.innerHTML +=
        `<div>You: ${message}</div>`;


    input.value = "";



    const response = await fetch("/chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            message: message

        })

    });



    const data = await response.json();



    chatBox.innerHTML +=
        `<div>Bot: ${data.reply}</div>`;

});