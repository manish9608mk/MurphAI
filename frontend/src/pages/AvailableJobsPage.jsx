import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  BriefcaseBusiness,
  Clock3,
  MapPin,
  Menu,
  Search,
  ShieldCheck,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import {
  getAvailableJobs,
  getCurrentUser,
  logoutUser,
} from '../services/api'


function AvailableJobsPage() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    async function loadAvailableJobs() {
      try {
        const [userData, jobsData] = await Promise.all([
          getCurrentUser(),
          getAvailableJobs(),
        ])

        setUser(userData)
        setJobs(Array.isArray(jobsData) ? jobsData : [])
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load available jobs.',
        )
      } finally {
        setLoading(false)
      }
    }

    loadAvailableJobs()
  }, [])

  function handleLogout() {
    logoutUser()
    navigate('/login')
  }

  function closeSidebar() {
    setSidebarOpen(false)
  }

  if (loading) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />

            <h2>Finding available work...</h2>

            <p>
              Looking for open jobs in the MurphAI marketplace.
            </p>
          </div>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-error-screen">
          <div className="dashboard-error-card">
            <div className="dashboard-error-icon">
              <ShieldCheck size={24} />
            </div>

            <h1>We couldn't load available jobs</h1>

            <p>{error}</p>

            <button
              type="button"
              className="dashboard-primary-button"
              onClick={() => navigate('/dashboard')}
            >
              <ArrowLeft size={17} />
              Back to dashboard
            </button>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="dashboard-shell">
      {sidebarOpen && (
        <button
          type="button"
          className="dashboard-sidebar-overlay"
          aria-label="Close navigation"
          onClick={closeSidebar}
        />
      )}

      <aside
        className={`dashboard-sidebar ${
          sidebarOpen
            ? 'dashboard-sidebar-open'
            : ''
        }`}
      >
        <div className="dashboard-brand">
          <div className="dashboard-brand-mark">
            M
          </div>

          <div>
            <strong>MurphAI</strong>
            <span>Work. Trust. Growth.</span>
          </div>

          <button
            type="button"
            className="dashboard-mobile-close"
            onClick={closeSidebar}
            aria-label="Close navigation"
          >
            <ArrowLeft size={19} />
          </button>
        </div>

        <nav className="dashboard-nav">
          <button
            type="button"
            className="dashboard-nav-item"
            onClick={() => navigate('/dashboard')}
          >
            <BriefcaseBusiness size={19} />
            <span>Dashboard</span>
          </button>

          <button
            type="button"
            className="dashboard-nav-item dashboard-nav-item-active"
            onClick={() => navigate('/jobs/available')}
          >
            <Search size={19} />
            <span>Browse Jobs</span>
          </button>

          <button
            type="button"
            className="dashboard-nav-item"
            onClick={() => navigate('/dashboard')}
          >
            <BriefcaseBusiness size={19} />
            <span>My Jobs</span>
          </button>

          <button
            type="button"
            className="dashboard-nav-item"
          >
            <Clock3 size={19} />
            <span>Notifications</span>
          </button>

          <button
            type="button"
            className="dashboard-nav-item"
          >
            <ShieldCheck size={19} />
            <span>Profile</span>
          </button>
        </nav>

        <div className="dashboard-sidebar-bottom">
          <div className="dashboard-help-card">
            <div className="dashboard-help-icon">
              ✦
            </div>

            <strong>Need help?</strong>

            <p>
              MurphAI is here to help you get work done.
            </p>

            <button type="button">
              Chat with MurphAI
            </button>
          </div>

          <button
            type="button"
            className="dashboard-logout-sidebar"
            onClick={handleLogout}
          >
            Sign out
          </button>
        </div>
      </aside>

      <section className="dashboard-main">
        <header className="dashboard-topbar">
          <button
            type="button"
            className="dashboard-menu-button"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={21} />
          </button>

          <div className="dashboard-search">
            <Search size={18} />

            <input
              type="text"
              placeholder="Search available jobs..."
              aria-label="Search available jobs"
            />
          </div>

          <div className="dashboard-topbar-actions">
            <div className="dashboard-user-menu">
              <div className="dashboard-avatar">
                {user?.name
                  ?.charAt(0)
                  ?.toUpperCase()}
              </div>

              <div className="dashboard-user-copy">
                <strong>
                  Hello, {user?.name?.split(' ')[0]}
                </strong>

                <span>Marketplace</span>
              </div>
            </div>
          </div>
        </header>

        <div className="dashboard-content">
          <section className="marketplace-header">
            <button
              type="button"
              className="create-job-back"
              onClick={() => navigate('/dashboard')}
            >
              <ArrowLeft size={17} />
              Back to dashboard
            </button>

            <span className="dashboard-eyebrow">
              MURPHAI MARKETPLACE
            </span>

            <h1>Find work that fits you.</h1>

            <p>
              Explore open jobs posted by customers and
              discover work you can confidently take on.
            </p>
          </section>

          <section className="marketplace-toolbar">
            <div>
              <span className="dashboard-panel-kicker">
                AVAILABLE NOW
              </span>

              <h2>
                {jobs.length === 1
                  ? '1 open job'
                  : `${jobs.length} open jobs`}
              </h2>
            </div>

            <div className="marketplace-toolbar-note">
              <ShieldCheck size={16} />
              <span>
                Open jobs from other customers
              </span>
            </div>
          </section>

          {jobs.length === 0 ? (
            <section className="dashboard-panel marketplace-empty">
              <div className="dashboard-empty-icon">
                <BriefcaseBusiness size={23} />
              </div>

              <h3>No open jobs right now</h3>

              <p>
                New opportunities will appear here when
                customers post work.
              </p>

              <button
                type="button"
                className="dashboard-secondary-button"
                onClick={() => navigate('/dashboard')}
              >
                <ArrowLeft size={17} />
                Back to dashboard
              </button>
            </section>
          ) : (
            <section className="marketplace-job-grid">
              {jobs.map((job) => (
                <article
                  className="marketplace-job-card"
                  key={job.id}
                >
                  <div className="marketplace-job-card-top">
                    <div className="marketplace-job-icon">
                      <BriefcaseBusiness size={20} />
                    </div>

                    <span className="dashboard-status dashboard-status-open">
                      Open
                    </span>
                  </div>

                  <div className="marketplace-job-card-body">
                    <h3>{job.title}</h3>

                    <p className="marketplace-job-description">
                      {job.description}
                    </p>

                    <div className="marketplace-job-meta">
                      <span>
                        <MapPin size={15} />
                        {job.location}
                      </span>

                      <span>
                        <Clock3 size={15} />
                        {job.created_at
                          ? formatDate(job.created_at)
                          : 'Recently posted'}
                      </span>
                    </div>
                  </div>

                  <div className="marketplace-job-card-footer">
                    <div>
                      <span>Budget</span>

                      <strong>
                        ₹
                        {Number(
                          job.budget,
                        ).toLocaleString('en-IN')}
                      </strong>
                    </div>

                    <button
                      type="button"
                      className="dashboard-secondary-button"
                      onClick={() =>
                        navigate(`/jobs/${job.id}`)
                      }
                    >
                      View job
                    </button>
                  </div>
                </article>
              ))}
            </section>
          )}
        </div>
      </section>
    </main>
  )
}


function formatDate(value) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Recently posted'
  }

  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}


export default AvailableJobsPage
