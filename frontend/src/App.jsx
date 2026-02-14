import { useState, useEffect } from 'react'
import './App.css'

function App() {
    const [message, setMessage] = useState('Loading message from Django...')

    useEffect(() => {
        fetch('/api/hello/')
            .then(response => response.json())
            .then(data => setMessage(data.message))
            .catch(error => {
                console.error('Error fetching data:', error)
                setMessage('Error connecting to Django backend. Make sure it is running!')
            })
    }, [])

    return (
        <div className="App">
            <header className="App-header">
                <h1>Django + React Scaffold</h1>
                <div className="card">
                    <p>
                        Backend says: <strong>{message}</strong>
                    </p>
                </div>
                <p className="read-the-docs">
                    Edit <code>src/App.jsx</code> and save to test HMR
                </p>
            </header>
        </div>
    )
}

export default App
