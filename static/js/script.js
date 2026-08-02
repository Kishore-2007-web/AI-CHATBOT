const button = document.getElementById("send-btn");

const input = document.getElementById("user-input");

const chatBox = document.getElementById("chat-box");



function addMessage(message, type) {

    const div = document.createElement("div");

    div.className = "message " + type;

    div.innerHTML = marked.parse(message);

    chatBox.appendChild(div);


    chatBox.scrollTop = chatBox.scrollHeight;

}



async function sendMessage() {


    const message = input.value.trim();


    if (message === "")
        return;


    addMessage(message, "user");


    input.value = "";


    const loading = document.createElement("div");

    loading.className = "message bot";

    loading.textContent = "Kisa is thinking...";


    chatBox.appendChild(loading);



    try {


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


        loading.remove();



        addMessage(
            data.reply,
            "bot"
        );



    }

    catch (error) {


        loading.remove();


        addMessage(
            "Something went wrong. Please try again.",
            "bot"
        );


    }

}



button.addEventListener(
    "click",
    sendMessage
);



input.addEventListener(
    "keypress",
    function (event) {

        if (event.key === "Enter") {

            sendMessage();

        }

    }
);