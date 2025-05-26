import WebApp from '@twa-dev/sdk';
import { useEffect } from 'react';
import { UserProfile } from './components/UserProfile';
import './App.css';

function App() {
    useEffect(() => {
      // Инициализация WebApp
      WebApp.ready();

      // Расширяем окно на всю высоту
      WebApp.expand();
    }, []);

    return (
      <div className="app">
        <UserProfile />
      </div>
    );
}

export default App;
