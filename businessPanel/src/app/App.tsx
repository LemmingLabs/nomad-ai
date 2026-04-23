import { AppProviders } from './providers/AppProviders'
import { AppRouter } from './router'
import { useAuthBootstrap } from '../features/auth/hooks/useAuthBootstrap'

export default function App() {
  useAuthBootstrap()

  return (
    <AppProviders>
      <AppRouter />
    </AppProviders>
  )
}
