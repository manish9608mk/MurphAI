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
import AvailableJobsPage from './pages/AvailableJobsPage'
import JobDetailsPage from './pages/JobDetailsPage'
import JobInterestsPage from './pages/JobInterestsPage'
import WorkerAssignmentsPage from './pages/WorkerAssignmentsPage'
import WorkerWorkPage from './pages/WorkerWorkPage'
import WorkerHistoryPage from './pages/WorkerHistoryPage'
import WorkerPublicProfilePage from './pages/WorkerPublicProfilePage'
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

          <Route
            path="/jobs/available"
            element={<AvailableJobsPage />}
          />

          <Route
            path="/jobs/:jobId"
            element={<JobDetailsPage />}
          />

          <Route
            path="/jobs/:jobId/interests"
            element={<JobInterestsPage />}
          />

          <Route
            path="/assignments"
            element={<WorkerAssignmentsPage />}
          />

          <Route
            path="/works/:workId"
            element={<WorkerWorkPage />}
          />

          <Route
            path="/workers/history"
            element={<WorkerHistoryPage />}
          />

          <Route
            path="/workers/:workerId/profile"
            element={<WorkerPublicProfilePage />}
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
