import './App.css'

import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import CreateJobPage from './pages/CreateJobPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}

        <Route
          path="/"
          element={<LandingPage />}
        />

        <Route
          path="/login"
          element={<LoginPage />}
        />

        <Route
          path="/register"
          element={<RegisterPage />}
        />

        {/* Protected routes */}

        <Route element={<ProtectedRoute />}>
          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/jobs/new"
            element={<CreateJobPage />}
          />
        </Route>

        {/* Unknown routes */}

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App