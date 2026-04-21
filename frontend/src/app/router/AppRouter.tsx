import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { HomePage } from '../../pages/home';
import { LoginPage } from '../../pages/auth/login';
import { RegisterPage } from '../../pages/auth/register';
import { TripPage } from '../../pages/trip';
import { NotFoundPage } from '../../pages/not-found';

const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />,
  },
  {
    path: '/trip/:id',
    element: <TripPage />,
  },
  {
    path: '/auth/login',
    element: <LoginPage />,
  },
  {
    path: '/auth/register',
    element: <RegisterPage />,
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
