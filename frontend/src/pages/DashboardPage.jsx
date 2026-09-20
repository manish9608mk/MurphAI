import { useEffect, useMemo, useState } from 'react'
import {
  ArrowRight,
  Bell,
  BriefcaseBusiness,
  CheckCircle2,
  ChevronDown,
  Clock3,
  FolderKanban,
  LayoutDashboard,
  LogOut,
  Menu,
  Plus,
  Search,
  Settings,
  ShieldCheck,
  UserRound,
  X,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import {
  getCurrentUser,
  getMyJobs,
  logoutUser,
} from '../services/api'

function DashboardPage() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [userData, jobsData] = await Promise.all([
          getCurrentUser(),
          getMyJobs(),
        ])

        setUser(userData)
        setJobs(Array.isArray(jobsData) ? jobsData : [])
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load your dashboard',
        )
      } finally {
        setLoading(false)
      }
    }

    loadDashboard()
  }, [])

  function handleLogout() {
    logoutUser()
    navigate('/login')
  }

  function closeSidebar() {
    setSidebarOpen(false)
  }

  const stats = useMemo(() => {
    const open = jobs.filter(
      (job) => job.status === 'open',
    ).length

    const assigned = jobs.filter(
      (job) => job.status === 'assigned',
    ).length

    const inProgress = jobs.filter(
      (job) => job.status === 'in_progress',
    ).length

    const completed = jobs.filter(
      (job) => job.status === 'completed',
    ).length

    return {
      total: jobs.length,
      active: open + assigned + inProgress,
      inProgress,
      completed,
    }
  }, [jobs])

  const recentJobs = jobs.slice(0, 5)

  if (loading) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />

            <h2>Loading your workspace...</h2>

            <p>
              Getting your profile and jobs ready.
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

            <h1>We couldn't load your workspace</h1>

            <p>{error}</p>

            <button
              type="button"
              className="dashboard-primary-button"
              onClick={handleLogout}
            >
              <LogOut size={17} />
              Return to login
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
            <X size={20} />
          </button>
        </div>

        <nav className="dashboard-nav">
          <button
            type="button"
            className="dashboard-nav-item dashboard-nav-item-active"
            onClick={() => navigate('/dashboard')}
          >
            <LayoutDashboard size={19} />
            <span>Dashboard</span>
          </button>

          <button
            type="button"
            className="dashboard-nav-item"
            onClick={() => navigate('/jobs/available')}
          >
            <Search size={19} />
            <span>Browse Jobs</span>
          </button>

          <button
            type="button"
            className="dashboard-nav-item"
            onClick={() => navigate('/workers/discover')}
          >
            <UserRound size={19} />
            <span>Browse Workers</span>
          </button>

          <button
            type="button"
            className="dashboard-nav-item"
            onClick={() =>
              navigate('/jobs/mine')
            }
          >
            <FolderKanban size={19} />
            <span>My Jobs</span>

            {jobs.length > 0 && (
              <span className="dashboard-nav-count">
                {jobs.length}
              </span>
            )}
          </button>

          <button
            type="button"
            className="dashboard-nav-item"
          >
            <Bell size={19} />
            <span>Notifications</span>
          </button>

          <button
            type="button"
            className="dashboard-nav-item"
            onClick={() => navigate('/workers/profile')}
          >
            <UserRound size={19} />
            <span>Profile</span>
          </button>

          <button
            type="button"
            className="dashboard-nav-item"
          >
            <Settings size={19} />
            <span>Settings</span>
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
              <ArrowRight size={16} />
            </button>
          </div>

          <button
            type="button"
            className="dashboard-logout-sidebar"
            onClick={handleLogout}
          >
            <LogOut size={17} />
            Logout
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
              placeholder="Search for jobs, skills, or workers..."
              aria-label="Search"
            />
          </div>

          <div className="dashboard-topbar-actions">
            <button
              type="button"
              className="dashboard-icon-button"
              aria-label="Notifications"
              title="Notifications"
            >
              <Bell size={19} />
              <span className="dashboard-notification-dot" />
            </button>

            <div className="dashboard-user-menu">
              <div className="dashboard-avatar">
                {user.name
                  ?.charAt(0)
                  ?.toUpperCase()}
              </div>

              <div className="dashboard-user-copy">
                <strong>
                  Hello, {user.name?.split(' ')[0]}
                </strong>

                <span>Customer</span>
              </div>

              <ChevronDown size={17} />
            </div>
          </div>
        </header>

        <div className="dashboard-content">
          <section className="dashboard-hero">
            <div className="dashboard-hero-copy">
              <span className="dashboard-eyebrow">
                MURPHAI WORKSPACE
              </span>

              <h1>
                Get work done.
                <br />
                Build trust that lasts.
              </h1>

              <p>
                Post work, find skilled people, and
                build a verified professional history
                with MurphAI.
              </p>

              <div className="dashboard-hero-actions">
                <button
                  type="button"
                  className="dashboard-primary-button"
                  onClick={() =>
                    navigate('/jobs/new')
                  }
                >
                  <Plus size={18} />
                  Post a Job
                </button>

                <button
                  type="button"
                  className="dashboard-secondary-button"
                  onClick={() =>
                    navigate('/workers/discover')
                  }
                >
                  Browse Workers
                  <ArrowRight size={17} />
                </button>
              </div>
            </div>

            <div className="dashboard-hero-visual">
              <div className="dashboard-hero-orbit dashboard-orbit-one">
                <span>Post</span>
              </div>

              <div className="dashboard-hero-orbit dashboard-orbit-two">
                <span>Match</span>
              </div>

              <div className="dashboard-hero-orbit dashboard-orbit-three">
                <span>Trust</span>
              </div>

              <div className="dashboard-hero-center">
                <BriefcaseBusiness size={38} />
              </div>
            </div>
          </section>

          <section className="dashboard-stat-grid">
            <article className="dashboard-stat-card">
              <div className="dashboard-stat-icon">
                <BriefcaseBusiness size={21} />
              </div>

              <div>
                <span>Total Jobs</span>
                <strong>{stats.total}</strong>
                <small>
                  Jobs posted by you
                </small>
              </div>
            </article>

            <article className="dashboard-stat-card">
              <div className="dashboard-stat-icon dashboard-stat-icon-active">
                <Clock3 size={21} />
              </div>

              <div>
                <span>Active Jobs</span>
                <strong>{stats.active}</strong>
                <small>
                  Currently moving forward
                </small>
              </div>
            </article>

            <article className="dashboard-stat-card">
              <div className="dashboard-stat-icon dashboard-stat-icon-progress">
                <FolderKanban size={21} />
              </div>

              <div>
                <span>In Progress</span>
                <strong>{stats.inProgress}</strong>
                <small>
                  Work currently underway
                </small>
              </div>
            </article>

            <article className="dashboard-stat-card">
              <div className="dashboard-stat-icon dashboard-stat-icon-complete">
                <CheckCircle2 size={21} />
              </div>

              <div>
                <span>Completed</span>
                <strong>{stats.completed}</strong>
                <small>
                  Verified outcomes
                </small>
              </div>
            </article>
          </section>

          <section className="dashboard-lower-grid">
            <article className="dashboard-panel dashboard-jobs-panel">
              <div className="dashboard-panel-header">
                <div>
                  <span className="dashboard-panel-kicker">
                    YOUR WORK
                  </span>

                  <h2>Recent Jobs</h2>
                </div>

                <button
                  type="button"
                  className="dashboard-link-button"
                  onClick={() =>
                    navigate('/jobs/mine')
                  }
                >
                  View all
                  <ArrowRight size={16} />
                </button>
              </div>

              {recentJobs.length === 0 ? (
                <div className="dashboard-empty-state">
                  <div className="dashboard-empty-icon">
                    <BriefcaseBusiness size={23} />
                  </div>

                  <h3>No jobs yet</h3>

                  <p>
                    Your posted jobs will appear here
                    once you create your first one.
                  </p>

                  <button
                    type="button"
                    className="dashboard-primary-button"
                    onClick={() =>
                      navigate('/jobs/new')
                    }
                  >
                    <Plus size={17} />
                    Post your first job
                  </button>
                </div>
              ) : (
                <div className="dashboard-job-list">
                  {recentJobs.map((job) => (
                    <article
                      className="dashboard-job-row"
                      key={job.id}
                    >
                      <div className="dashboard-job-icon">
                        <BriefcaseBusiness size={19} />
                      </div>

                      <div className="dashboard-job-main">
                        <h3>{job.title}</h3>

                        <p>
                          {job.location || 'Remote'}{' '}
                          <span>•</span>{' '}
                          {job.created_at
                            ? new Date(
                                job.created_at,
                              ).toLocaleDateString()
                            : 'Recently posted'}
                        </p>
                      </div>

                      <span
                        className={`dashboard-status dashboard-status-${job.status}`}
                      >
                        {formatStatus(job.status)}
                      </span>

                      <div className="dashboard-job-budget">
                        <span>Budget</span>

                        <strong>
                          ₹
                          {Number(
                            job.budget,
                          ).toLocaleString('en-IN')}
                        </strong>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </article>

            <article className="dashboard-panel dashboard-trust-panel">
              <div className="dashboard-panel-header">
                <div>
                  <span className="dashboard-panel-kicker">
                    MURPHAI TRUST
                  </span>

                  <h2>Your foundation</h2>
                </div>

                <ShieldCheck size={21} />
              </div>

              <div className="dashboard-trust-visual">
                <div className="dashboard-trust-ring">
                  <ShieldCheck size={38} />
                </div>

                <strong>
                  Building your trust profile
                </strong>

                <p>
                  Your completed work, confirmations,
                  payments, and reputation will become
                  part of your verified professional
                  history.
                </p>
              </div>

              <div className="dashboard-trust-steps">
                <div className="dashboard-trust-step">
                  <span>01</span>

                  <div>
                    <strong>
                      Post meaningful work
                    </strong>

                    <p>
                      Create jobs with clear outcomes.
                    </p>
                  </div>
                </div>

                <div className="dashboard-trust-step">
                  <span>02</span>

                  <div>
                    <strong>
                      Complete the workflow
                    </strong>

                    <p>
                      Assignment → Work → Evidence.
                    </p>
                  </div>
                </div>

                <div className="dashboard-trust-step">
                  <span>03</span>

                  <div>
                    <strong>
                      Build verified history
                    </strong>

                    <p>
                      Confirmation → Payment →
                      Reputation.
                    </p>
                  </div>
                </div>
              </div>
            </article>
          </section>

          <section className="dashboard-panel dashboard-quick-panel">
            <div className="dashboard-panel-header">
              <div>
                <span className="dashboard-panel-kicker">
                  QUICK ACTIONS
                </span>

                <h2>
                  Move your work forward
                </h2>
              </div>
            </div>

            <div className="dashboard-quick-grid">
              <button
                type="button"
                className="dashboard-quick-card"
                onClick={() =>
                  navigate('/jobs/new')
                }
              >
                <div className="dashboard-quick-icon">
                  <Plus size={21} />
                </div>

                <div>
                  <strong>Post a Job</strong>
                  <span>
                    Find skilled workers
                  </span>
                </div>

                <ArrowRight size={17} />
              </button>

              <button
                type="button"
                className="dashboard-quick-card"
                onClick={() =>
                  navigate('/workers/discover')
                }
              >
                <div className="dashboard-quick-icon">
                  <Search size={21} />
                </div>

                <div>
                  <strong>Browse Workers</strong>
                  <span>
                    Explore available talent
                  </span>
                </div>

                <ArrowRight size={17} />
              </button>

              <button
                type="button"
                className="dashboard-quick-card"
                onClick={() =>
                  navigate('/jobs/mine')
                }
              >
                <div className="dashboard-quick-icon">
                  <FolderKanban size={21} />
                </div>

                <div>
                  <strong>Manage Jobs</strong>
                  <span>
                    Track your projects
                  </span>
                </div>

                <ArrowRight size={17} />
              </button>

              <button
                type="button"
                className="dashboard-quick-card"
                onClick={() =>
                  navigate('/workers/history')
                }
              >
                <div className="dashboard-quick-icon">
                  <ShieldCheck size={21} />
                </div>

                <div>
                  <strong>Trust & Reputation</strong>
                  <span>
                    View your work history
                  </span>
                </div>

                <ArrowRight size={17} />
              </button>
            </div>
          </section>

          <footer className="dashboard-footer">
            <span>
              © {new Date().getFullYear()} MurphAI
            </span>

            <span>
              Get work done. Build trust that lasts.
            </span>
          </footer>
        </div>
      </section>
    </main>
  )
}

function formatStatus(status) {
  const labels = {
    open: 'Open',
    assigned: 'Assigned',
    in_progress: 'In Progress',
    completed: 'Completed',
    cancelled: 'Cancelled',
  }

  return labels[status] || status
}

export default DashboardPage