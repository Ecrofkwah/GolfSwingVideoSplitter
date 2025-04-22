import { useState } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';

function App() {

  return (
    <>
      <div>
      <BrowserRouter>
      {/*<AppNavbar loginUser={loginUser} setLoginUser={setLoginUser}/>*/}
      <div className='pages'>
        <Routes>
          <Route path="/" element={<Home/>} />
        </Routes>
      </div>
    </BrowserRouter>
      </div>
    </>
  )
}

export default App
