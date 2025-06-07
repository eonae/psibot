import WebApp from '@twa-dev/sdk';
import { useEffect } from 'react';
import { FileUpload } from './components/FileUpload';
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
        {/* <UserProfile /> */}
        <FileUpload />
      </div>
    );
}

export default App;
