window.onload = () => {
  console.log("window loaded");
  document.getElementById("rides_result").style.display = "none";
  document.getElementById("visit").style.display = "block";
  document.getElementById("contentdiv").style.display = "none";
};

function consultaEnquetes() {
  var titulo = document.getElementById("titulo_consulta").value;
  var username = document.getElementById("username").value;

  consulta = {
    user: username,
    enquete: titulo,
    request: "get info"
  }

  response = fetch("http://10.0.0.109:5000/users?channel=channel&user="+username + "&enquete="+titulo + "&request=get info", {
    method: "GET",
    headers: {}
  })
  .then(function (response) {
    return response.json();
  })
  .then(function (enquetes) {
    var targetContainer = document.getElementById("response");
    response_json =
      "<pre>" + JSON.stringify(enquetes, undefined, 2) + "</pre>";

    targetContainer.innerHTML = response_json;
  })
  .catch((err) => {
    console.error(err);
  });
}

function cadastraEnquete() {
  var titulo = document.getElementById("titulo_cadastra").value;
  var local = document.getElementById("local").value;
  var limite = document.getElementById("limite").value;
  var datas = document.getElementById("datas").value;
  var username = document.getElementById("username").value;

  enquete = {
    enquete: titulo,
    local: local,
    limite: limite,
    votos: datas,
    user: username
  };

  fetch("http://10.0.0.109:5000/users", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(enquete),
  })
    .then((response) => {
      console.log(response);
    })
    .catch((err) => {
      console.error(err);
    });

  clear_all();
}

function clear_all() {
  document.getElementById("titulo_consulta").value = "";
  document.getElementById("titulo_cadastra").value = "";
  document.getElementById("titulo_vota").value = "";
  document.getElementById("local").value = "";
  document.getElementById("limite").value = "";
  document.getElementById("datas").value = "";
  document.getElementById("voto").value = "";
}


function votaEnquete() {
  var enquete = document.getElementById("titulo_vota").value;
  var voto = document.getElementById("voto").value;
  var username = document.getElementById("username").value;

  votos = {
    user: username,
    enquete: enquete,
    voto: voto
  };

  fetch("http://10.0.0.109:5000/users", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(votos),
  })
    .then((response) => {
      console.log(response);
    })
    .catch((err) => {
      console.error(err);
    });

  clear_all();
}

function visit() {
  document.getElementById("visit").style.display = "none";
  document.getElementById("contentdiv").style.display = "block";
  var username = document.getElementById("username").value;
  document.getElementById("loggedas").innerHTML = username;

  fetch("http://10.0.0.109:5000/users?channel=channel&user="+username + "&request=visit", {
    method: "GET",
    headers: {},
  })
    .then((response) => {
      console.log(response);
    })
    .catch((err) => {
      console.error(err);
    });

  var targetContainer = document.getElementById("data");
  var eventSource = new EventSource("http://10.0.0.109:5000/event");

  eventSource.onmessage = function(e) {
    targetContainer.innerHTML = e.data;
  };

  eventSource.onerror = (event, err) => {
    console.error("Error in connect SSE", event, err);
  };


  // eventSource.addEventListener("message", (e) => {
  //   console.log("received event", e);
  //   var targetContainer = document.getElementById("data");
  //   var data_filtered = e.data.replaceAll("---", "<br />");
  //   //var data_filtered = "</pre>" + JSON.parse(e.data) + "</pre>"
  //   targetContainer.innerHTML = data_filtered;
  // });
}


var source = new EventSource("http://10.0.0.109:5000/event");
    source.addEventListener('publish', function(event) {
        console.log(event.data);
        var data = JSON.parse(event.data);
        console.log("The server says " + data.message);

        var targetContainer = document.getElementById("data");
        var data_filtered = event.data.replaceAll("---", "<br />");
        targetContainer.innerHTML = data_filtered;
    }, false);
    source.addEventListener('error', function(event) {
        console.log("Error"+ event)
        alert("Failed to connect to event stream. Is Redis running?");
    }, false);

// 2021-11-24_03:03