import {useState, useEffect} from 'react'
function App() {
  const [message,setMessage] = useState('WAIT')
    useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then(response => response.json())
      .then(data => setMessage(data.message))
      .catch(error => setMessage('Error fetching message'))
  },[])
  return (
    <div style={{padding:'20px', fontFamily: 'Arial',textAlign: 'center'}}>
      <h1>backend status:{message}</h1>
    </div>
  )
}
export default App