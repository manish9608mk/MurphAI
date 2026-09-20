import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  Clock3,
  MapPin,
  Plus,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import {
  getCurrentUser,
  getMyJobs,
} from '../services/api'
import './MyJobsPage.css'

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

function getStatusIcon(status) {
  if (status === 'completed') {
    return <CheckCircle2 size={15} />
  }

  if (
    status === 'assigned' ||
    status === 'in_progress'
  ) {
    return <Clock3 size={15} />
  }

  return <BriefcaseBusiness size={15} />
}

function MyJobsPage() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadJobs() {
    setLoading(true)
    setError('')

    try {
      const [userData, jobsData] =
        await Promise.all([
          getCurrentUser(),
          getMyJobs(),
        ])

      setUser(userData)
      setJobs(
        Array.isArray(jobsData)
          ? jobsData
          : [],
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load your jobs.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    Promise.all([
      getCurrentUser(),
      getMyJobs(),
    ])
      .then(([userData, jobsData]) => {
        if (cancelled) {
          return
        }

        setUser(userData)
        setJobs(
          Array.isArray(jobsData)
            ? jobsData
            : [],
        )
      })
      .catch((err) => {
        if (cancelled) {
          return
        }

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load your jobs.',
        )
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <main className="dashboard-shell my-jobs-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />

            <h2>Loading your jobs...</h2>

            <p>
              Gathering the work you have posted.
            </p>
          </div>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="dashboard-shell my-jobs-shell">
        <div className="dashboard-error-screen">
          <div className="dashboard-error-card">
            <div className="dashboard-error-icon">
              <ShieldCheck size={24} />
            </div>

            <h1>
              We couldn't load your jobs
            </h1>

            <p>{error}</p>

            <div className="my-jobs-error-actions">
              <button
                type="button"
                className="dashboard-secondary-button"
                onClick={() =>
                  navigate('/dashboard')
                }
              >
                <ArrowLeft size={17} />
                Back to dashboard
              </button>

              <button
                type="button"
                className="dashboard-primary-button"
                onClick={loadJobs}
              >
                <RefreshCw size={17} />
                Try again
              </button>
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="dashboard-shell my-jobs-shell">
      <section className="dashboard-main">
        <header className="dashboard-topbar">
          <button
            type="button"
            className="dashboard-menu-button"
            onClick={() => navigate('/dashboard')}
            aria-label="Back to dashboard"
          >
            <ArrowLeft size={20} />
          </button>

          <div className="dashboard-search">
            <BriefcaseBusiness size={18} />

            <input
              type="text"
              value="My jobs"
              readOnly
              aria-label="Current page"
            />
          </div>

          {user && (
            <div className="dashboard-topbar-actions">
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

                  <span>
                    {user.role || 'Customer'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </header>

        <div className="my-jobs-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft size={16} />
            Back to dashboard
          </button>

          <section className="my-jobs-hero">
            <div>
              <span className="dashboard-eyebrow">
                YOUR WORKSPACE
              </span>

              <h1>My Jobs</h1>

              <p>
                Manage the work you have posted and
                follow each job through the MurphAI
                workflow.
              </p>
            </div>

            <button
              type="button"
              className="dashboard-primary-button"
              onClick={() => navigate('/jobs/new')}
            >
              <Plus size={17} />
              Post a Job
            </button>
          </section>

          <section className="my-jobs-summary">
            <article>
              <span>Total jobs</span>
              <strong>{jobs.length}</strong>
            </article>

            <article>
              <span>Active</span>
              <strong>
                {
                  jobs.filter(
                    (job) =>
                      job.status === 'open' ||
                      job.status === 'assigned' ||
                      job.status === 'in_progress',
                  ).length
                }
              </strong>
            </article>

            <article>
              <span>Completed</span>
              <strong>
                {
                  jobs.filter(
                    (job) =>
                      job.status === 'completed',
                  ).length
                }
              </strong>
            </article>
          </section>

          {jobs.length === 0 ? (
            <section className="my-jobs-empty">
              <div className="my-jobs-empty-icon">
                <BriefcaseBusiness size={23} />
              </div>

              <h2>No jobs yet</h2>

              <p>
                Create your first job to start finding
                skilled workers through MurphAI.
              </p>

              <button
                type="button"
                className="dashboard-primary-button"
                onClick={() => navigate('/jobs/new')}
              >
                <Plus size={17} />
                Create your first job
              </button>
            </section>
          ) : (
            <section className="my-jobs-list">
              {jobs.map((job) => (
                <article
                  className="my-jobs-card"
                  key={job.id}
                >
                  <div className="my-jobs-card-icon">
                    <BriefcaseBusiness size={20} />
                  </div>

                  <div className="my-jobs-card-main">
                    <div className="my-jobs-card-heading">
                      <div>
                        <span>
                          JOB #{job.id}
                        </span>

                        <h2>{job.title}</h2>
                      </div>

                      <span
                        className={`my-jobs-status my-jobs-status-${job.status}`}
                      >
                        {getStatusIcon(job.status)}
                        {formatStatus(job.status)}
                      </span>
                    </div>

                    <p>
                      {job.description ||
                        'No description provided.'}
                    </p>

                    <div className="my-jobs-meta">
                      <span>
                        <MapPin size={14} />
                        {job.location || 'Remote'}
                      </span>

                      <span>
                        <BriefcaseBusiness size={14} />
                        ₹
                        {Number(
                          job.budget || 0,
                        ).toLocaleString('en-IN')}
                      </span>

                      {job.created_at && (
                        <span>
                          <Clock3 size={14} />
                          {new Date(
                            job.created_at,
                          ).toLocaleDateString(
                            'en-IN',
                          )}
                        </span>
                      )}
                    </div>
                  </div>

                  <button
                    type="button"
                    className="my-jobs-view-button"
                    onClick={() =>
                      navigate(`/jobs/${job.id}`)
                    }
                  >
                    View job
                    <ArrowRight size={16} />
                  </button>
                </article>
              ))}
            </section>
          )}

          <div className="my-jobs-trust-note">
            <ShieldCheck size={18} />

            <div>
              <strong>
                Your jobs feed the MurphAI trust workflow.
              </strong>

              <span>
                Jobs can move from posting to assignment,
                work, evidence, customer confirmation,
                payment, and verified reputation.
              </span>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default MyJobsPage
