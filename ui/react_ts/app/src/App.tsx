import React from 'react'
import dotenv from 'dotenv'


function App() {
  console.log('test 1')
  console.log(process.env)
  console.log(process.env.DEBUG)
  return (
    <div className="App">
      <header className="App-header">
        "hello world"
      </header>
    </div>
  );
}

export default App;
