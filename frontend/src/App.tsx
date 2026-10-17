import { BrowserRouter } from 'react-router-dom';
import { AppRouter } from '@/app/routes';

export default function App() {
  return (
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  );
}
