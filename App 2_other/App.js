import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios'
import 'react-table/react-table.css'

const App = () => {
  
  const client = 'client2'

  const [message, setMessage] = useState('')
  const [choice, setChoice] = useState(0)
  const [eventSource, setEventsource] = useState(undefined)

  useEffect(() => {    
    console.log('set event source')
    setEventsource(new EventSource("http://localhost:5000/event?channel=" + client))
  }, [])

  useEffect(() => {
    console.log(eventSource)
    if (eventSource != undefined)
      subscribeToEvents()    
  }, [eventSource]);

  const subscribeToEvents = () => {
    console.log('subscribes')
    eventSource.addEventListener("subscribeCaronasNovas", e => {
      console.log('subscribeCaronasNovas')
      console.log(e)
      setMessage(e.data)
    });
    
    eventSource.addEventListener("subscribeInteressadosNovos", e => {
      console.log('subscribeInteressadosNovos')
      console.log(e)
      setMessage(e.data)
    });

    eventSource.onerror = function(err) {
      console.log("EventSource failed: ");
      console.log(err);
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("message :", data);
    }
  }
  
  const getRequest = async (path) => {
    return axios.get("http://localhost:5000/" + path, {
      headers: {'Access-Control-Allow-Origin': '*'}
      })
  }
  
  const postRequest = async (path, data) => {
    console.log(data)
    return axios.post("http://localhost:5000/" + path, data, {
      headers: {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}
      })
  }


  const post = async (path, data) => {
    return await axios({
        method: 'post',
        headers: {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
        url: 'http://localhost:5000/' + path,
        data: data
      });
  }

  const requestConsultarCarona = async (origem, destino, data) => {
    const message = { origem: origem, destino: destino, data: data}
    const request = postRequest('consultarcarona', message)
    console.log('request consultar carona ')
    request.then(result => {
      console.log(result)
        console.log(result.data)
        const dados = result.data
        setMessage(dados)
      },
        error => {
          console.log(error)
        setMessage(error)
      }
    )
    .catch(error => {
      console.log(error)
        setMessage(error)
    })
    console.log('after request consultar carona')
  }

  const requestCadastrarCarona = async (nome, contato, origem, destino, data, num_passageiros) => {
    const message = { channel: client, nome: nome, contato: contato, origem: origem, destino: destino, data: data, num_passageiros: num_passageiros}
    const request = postRequest('cadastrarcarona', message)
    console.log('request cadastrar carona ')
    request.then(result => {
      console.log(result)
        console.log(result.data)
        const dados = result.data
        setMessage(dados)
      },
        error => {
          console.log(error)
        setMessage(error)
      }
    )
    .catch(error => {
      console.log(error)
        setMessage(error)
    })
    console.log('after request cadastrar carona')
  }
  
  const requestCadastrarInteresse = (nome, contato, origem, destino, data) => {
    const message = { channel: client, nome: nome, contato: contato, origem: origem, destino: destino, data: data}
    const request = postRequest('cadastrarinteresse', message)
    console.log('request cadastrar interesse ')
    request.then(result => {
      console.log(result)
        console.log(result.data)
        const dados = result.data
        setMessage(dados)
      },
        error => {
          console.log(error)
        setMessage(error)
      }
    )
    .catch(error => {
      console.log(error)
        setMessage(error)
    })
  }
  
  const requestCancelarCarona = (id) => {
    const message = { id: id }
    const request = postRequest('cancelarcarona', message)
    console.log('request cancelar carona ')
    request.then(result => {
      console.log(result)
        console.log(result.data)
        const dados = result.data
        setMessage(dados)
      },
        error => {
          console.log(error)
        setMessage(error)
      }
    )
    .catch(error => {
      console.log(error)
        setMessage(error)
    })
  }
  
  const requestCancelarInteresse = (id) => {
    const message = { id: id }
    const request = postRequest('cancelarinteresse', message)
    console.log('request cancelar interesse ')
    request.then(result => {
      console.log(result)
        console.log(result.data)
        const dados = result.data
        setMessage(dados)
      },
        error => {
          console.log(error)
        setMessage(error)
      }
    )
    .catch(error => {
      console.log(error)
        setMessage(error)
    })
  }


  const ConsultarCarona = () => {
    var origem = ''
    var destino = ''
    var data = ''
    return (
      <div>
        <a>origem: </a>
        <input onChange={(e) => origem = e.target.value}/>
        <br/>
        <a>destino: </a>
        <input onChange={(e) => destino = e.target.value}/>
        <br/>
        <a>data: </a>
        <input onChange={(e) => data = e.target.value}/>
        <br/>
        <br/>
        <button onClick={() => requestConsultarCarona(origem, destino, data)} >enviar</button>
      </div>
    )
  }
  
  const CadastrarCarona = () => {
    var nome = ''
    var contato = ''
    var origem = ''
    var destino = ''
    var data = ''
    var num_passageiros
    return (
      <div>
        <a>nome: </a>
        <input onChange={(e) => nome = e.target.value}/>
        <br/>
        <a>contato: </a>
        <input onChange={(e) => contato = e.target.value}/>
        <br/>
        <a>origem: </a>
        <input onChange={(e) => origem = e.target.value}/>
        <br/>
        <a>destino: </a>
        <input onChange={(e) => destino = e.target.value}/>
        <br/>
        <a>data: </a>
        <input onChange={(e) => data = e.target.value}/>
        <br/>
        <a>número de passageiros: </a>
        <input onChange={(e) => num_passageiros = e.target.value}/>
        <br/>
        <br/>
        <button onClick={() => requestCadastrarCarona(nome, contato, origem, destino, data, num_passageiros)} >enviar</button>
      </div>
    )
  }
  
  const CadastrarInteresse = () => {
    var nome = ''
    var contato = ''
    var origem = ''
    var destino = ''
    var data = ''
    return (
      <div>
        <a>nome: </a>
        <input onChange={(e) => nome = e.target.value}/>
        <br/>
        <a>contato: </a>
        <input onChange={(e) => contato = e.target.value}/>
        <br/>
        <a>origem: </a>
        <input onChange={(e) => origem = e.target.value}/>
        <br/>
        <a>destino: </a>
        <input onChange={(e) => destino = e.target.value}/>
        <br/>
        <a>data: </a>
        <input onChange={(e) => data = e.target.value}/>
        <br/>
        <br/>
        <button onClick={() => requestCadastrarInteresse(nome, contato, origem, destino, data)} >enviar</button>
      </div>
    )
  }
  
  const CancelarCarona = () => {
    var id = ''
    return (
      <div>
        <a>id: </a>
        <input onChange={(e) => id = e.target.value}/>
        <br/>
        <button onClick={() => requestCancelarCarona(id)} >enviar</button>
      </div>
    )
  }    
  
  const CancelarInteresse = () => {
    var id = ''
    return (
      <div>
        <a>id: </a>
        <input onChange={(e) => id = e.target.value}/>
        <br/>
        <button onClick={() => requestCancelarInteresse(id)} >enviar</button>
      </div>
    )
  }


  return (
    <div className="App">
    <header className="App-header">
      <p>Selecione uma ação: </p>
      <div>
        <button onClick={() => setChoice(1)}>1 - consultar carona</button>
        <br/>
        <button onClick={() => setChoice(2)}>2 - cadastrar carona</button>
        <br/>
        <button onClick={() => setChoice(3)}>3 - cadastrar interesse</button>
        <br/>
        <button onClick={() => setChoice(4)}>4 - cancelar carona</button>
        <br/>
        <button onClick={() => setChoice(5)}>5 - cancelar interesse</button>
        <br/>
        <p>{message}</p>
        {choice == 1 ? <ConsultarCarona /> : console.log()}
        {choice == 2 ? <CadastrarCarona /> : console.log()}
        {choice == 3 ? <CadastrarInteresse /> : console.log()}
        {choice == 4 ? <CancelarCarona /> : console.log()}
        {choice == 5 ? <CancelarInteresse /> : console.log()}
      </div>
    </header>
  </div>
  )
}
export default App;
