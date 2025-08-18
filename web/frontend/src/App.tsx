import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Population from './pages/Population';
import BrainDetail from './pages/BrainDetail';
import Evolution from './pages/Evolution';
import Tasks from './pages/Tasks';
import { WebSocketProvider } from './components/WebSocketProvider';

function App() {
  return (
    <WebSocketProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="population" element={<Population />} />
          <Route path="brain/:id" element={<BrainDetail />} />
          <Route path="evolution" element={<Evolution />} />
          <Route path="tasks" element={<Tasks />} />
        </Route>
      </Routes>
    </WebSocketProvider>
  );
}

export default App;
