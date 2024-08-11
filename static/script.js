var socket;

let lobby = document.getElementById('lobby');
let currentPlayer = document.getElementById('current');
let question = document.getElementById('question');

document.getElementById('connect').onclick = function(event) {
    socket = new WebSocket("ws://3cd40db57c7460eb8f12bd46580a3607.serveo.net/ws");

    socket.onopen = function(e) {
        console.log(e);
    };

    socket.onerror = function(error) {
        console.log(error);
    };

    socket.onmessage = function(event) {
        let data = event.data;
        let obj = JSON.parse(data);
        if (obj.action == "team") {
            let value = obj.value;
            for (let i = 0; i < value.length; i++) {
                let li = document.createElement('li');
                li.innerHTML = value[i];
                lobby.append(li);
            }
        } else if (obj.action == "join") {
            let value = obj.value;
            let li = document.createElement('li');
            li.innerHTML = value;
            lobby.append(li);
        } else if (obj.action == "connect") {
            currentPlayer.innerHTML = `My name: ${obj.value}`;
        } else if (obj.action == "disconnect") {
            let children = lobby.children;
            for (let i = 0; i < children.length; i++) {
                if (children[i].textContent == obj.value) {
                    children[i].remove();
                    break;
                }
            }
        } else if (obj.action == "question") {
            question.innerHTML = `Question: ${obj.value}`;
        } else if (obj.action == "answers") {
            let value = obj.value;
            for (let i = 0; i < value.length; i++) {
                let button = document.createElement('button');
                button.innerHTML = value[i];
                button.type = "button";
                question.after(button);
            }
        }
        console.log(data);
    }
};