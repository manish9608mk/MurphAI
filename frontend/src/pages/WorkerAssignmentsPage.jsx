import { useEffect, useMemo, useState } from 'react'
import {
  ArrowLeft,
  BriefcaseBusiness,
  CheckCircle2,
  ChevronDown,
  Clock3,
  MapPin,
  ShieldCheck,
  UserRound,
  XCircle,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import {
  acceptAssignment,
  getCurrentUser,
  getMyAssignments,
  rejectAssignment,
} from '../services/api'
import './WorkerAssignmentsPage.css'

const FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'pending', label: 'Needs response' },
  { key: 'accepted', label: 'Accepted' },
  { key: 'rejected', label: 'Rejected' },
  { key: 'cancelled', label: 'Cancelled' },
]

function formatDate(value) {
  if (!value) return 'Recently'

  return new Date(value).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function formatStatus(status) {
  if (!status) return 'Unknown'

  return status
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function WorkerAssignmentsPage() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all')
  const [expandedId, setExpandedId] = useState(null)
  const [actionId, setActionId] = useState(null)
  const [actionError, setActionError] = useState('')
  const [actionMessage, setActionMessage] = useState('')

  async function loadAssignments() {
    setError('')

    try {
      const [userData, assignmentData] = await Promise.all([
        getCurrentUser(),
        getMyAssignments(),
      ])

      setUser(userData)
      setAssignments(
        Array.isArray(assignmentData)
          ? assignmentData
          : [],
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load your assignments.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    async function loadAssignments() {
      try {
        setLoading(true)
        setError('')

        const data = await getMyAssignments()

        if (!cancelled) {
          setAssignments(
            Array.isArray(data) ? data : [],
          )
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load your assignments.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadAssignments()

    return () => {
      cancelled = true
    }
  }, [])

  const counts = useMemo(() => ({
    all: assignments.length,
    pending: assignments.filter(
      (assignment) => assignment.status === 'pending',
    ).length,
    accepted: assignments.filter(
      (assignment) => assignment.status === 'accepted',
    ).length,
    rejected: assignments.filter(
      (assignment) => assignment.status === 'rejected',
    ).length,
    cancelled: assignments.filter(
      (assignment) => assignment.status === 'cancelled',
    ).length,
  }), [assignments])

  const visibleAssignments = useMemo(() => (
    assignments.filter((assignment) => (
      filter === 'all' || assignment.status === filter
    ))
  ), [assignments, filter])

  async function handleAccept(assignment) {
    if (assignment.status !== 'pending' || actionId) return

    setActionId(assignment.id)
    setActionError('')
    setActionMessage('')

    try {
      const updated = await acceptAssignment(assignment.id)

      setAssignments((current) => current.map((item) => (
        item.id === assignment.id
          ? {
              ...item,
              ...updated,
              status: updated.status,
              job_status: 'assigned',
            }
          : item
      )))

      setActionMessage(
        `You accepted “${assignment.job_title}”. The job is now assigned to you.`,
      )
      setExpandedId(assignment.id)
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : 'Unable to accept this assignment.',
      )
    } finally {
      setActionId(null)
    }
  }

  async function handleReject(assignment) {
    if (assignment.status !== 'pending' || actionId) return

    const confirmed = window.confirm(
      `Reject the assignment for “${assignment.job_title}”?`,
    )

    if (!confirmed) return

    setActionId(assignment.id)
    setActionError('')
    setActionMessage('')

    try {
      const updated = await rejectAssignment(assignment.id)

      setAssignments((current) => current.map((item) => (
        item.id === assignment.id
          ? {
              ...item,
              ...updated,
              status: updated.status,
            }
          : item
      )))

      setActionMessage(
        `You declined “${assignment.job_title}”.`,
      )
      setExpandedId(null)
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : 'Unable to reject this assignment.',
      )
    } finally {
      setActionId(null)
    }
  }

  if (loading) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />
            <h2>Loading your assignments...</h2>
            <p>Checking for new work and decisions.</p>
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
            <h1>We couldn't load your assignments</h1>
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
    <main className="dashboard-shell worker-assignments-shell">
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
              value="My assignments"
              readOnly
              aria-label="Current page"
            />
          </div>

          <div className="dashboard-topbar-actions">
            {user && (
              <div className="dashboard-user-menu">
                <div className="dashboard-avatar">
                  {user.name?.charAt(0)?.toUpperCase()}
                </div>
                <div className="dashboard-user-copy">
                  <strong>
                    Hello, {user.name?.split(' ')[0]}
                  </strong>
                  <span>Worker</span>
                </div>
              </div>
            )}
          </div>
        </header>

        <div className="worker-assignments-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft size={16} />
            Back to dashboard
          </button>

          <section className="worker-assignments-hero">
            <div>
              <span className="dashboard-eyebrow">
                YOUR WORK
              </span>
              <h1>Assignments waiting on you.</h1>
              <p>
                Review the work customers have chosen you for,
                then accept the assignment to begin the verified
                MurphAI workflow.
              </p>
            </div>

            <div className="worker-assignments-hero-icon">
              <BriefcaseBusiness size={34} />
            </div>
          </section>

          <section className="worker-assignment-stats">
            <article>
              <span>Needs response</span>
              <strong>{counts.pending}</strong>
              <small>Customer assignments awaiting you</small>
            </article>
            <article>
              <span>Accepted</span>
              <strong>{counts.accepted}</strong>
              <small>Work you have agreed to do</small>
            </article>
            <article>
              <span>Total</span>
              <strong>{counts.all}</strong>
              <small>Your assignment history</small>
            </article>
          </section>

          {(actionMessage || actionError) && (
            <div
              className={`worker-assignment-feedback ${
                actionError
                  ? 'worker-assignment-feedback-error'
                  : ''
              }`}
            >
              {actionError ? (
                <XCircle size={18} />
              ) : (
                <CheckCircle2 size={18} />
              )}
              <span>{actionError || actionMessage}</span>
            </div>
          )}

          <section className="worker-assignment-toolbar">
            <div className="worker-assignment-filters">
              {FILTERS.map((item) => (
                <button
                  type="button"
                  key={item.key}
                  className={
                    filter === item.key
                      ? 'worker-assignment-filter-active'
                      : ''
                  }
                  onClick={() => setFilter(item.key)}
                >
                  {item.label}
                  <span>{counts[item.key]}</span>
                </button>
              ))}
            </div>

            <button
              type="button"
              className="worker-assignment-refresh"
              onClick={loadAssignments}
            >
              Refresh
            </button>
          </section>

          <section className="worker-assignment-panel">
            <div className="worker-assignment-panel-header">
              <div>
                <span className="dashboard-panel-kicker">
                  ASSIGNMENTS
                </span>
                <h2>Work selected for you</h2>
              </div>
              <div className="worker-assignment-count">
                {visibleAssignments.length}
              </div>
            </div>

            {visibleAssignments.length === 0 ? (
              <div className="worker-assignment-empty">
                <div className="worker-assignment-empty-icon">
                  <BriefcaseBusiness size={23} />
                </div>
                <h3>No assignments here</h3>
                <p>
                  New customer selections and your accepted work
                  will appear in this space.
                </p>
                <button
                  type="button"
                  className="dashboard-secondary-button"
                  onClick={() => navigate('/jobs/available')}
                >
                  Browse more jobs
                </button>
              </div>
            ) : (
              <div className="worker-assignment-list">
                {visibleAssignments.map((assignment) => {
                  const isPending = assignment.status === 'pending'
                  const isAccepted = assignment.status === 'accepted'
                  const isExpanded = expandedId === assignment.id
                  const isBusy = actionId === assignment.id

                  return (
                    <article
                      className={`worker-assignment-card ${
                        isAccepted
                          ? 'worker-assignment-card-accepted'
                          : ''
                      } ${
                        isPending
                          ? 'worker-assignment-card-pending'
                          : ''
                      }`}
                      key={assignment.id}
                    >
                      <div className="worker-assignment-card-main">
                        <div className="worker-assignment-icon">
                          <BriefcaseBusiness size={20} />
                        </div>

                        <div className="worker-assignment-copy">
                          <div className="worker-assignment-title-row">
                            <h3>{assignment.job_title}</h3>
                            <span
                              className={`worker-assignment-status worker-assignment-status-${assignment.status}`}
                            >
                              {isAccepted ? (
                                <CheckCircle2 size={13} />
                              ) : (
                                <Clock3 size={13} />
                              )}
                              {formatStatus(assignment.status)}
                            </span>
                          </div>

                          <p>
                            {assignment.job_description}
                          </p>

                          <div className="worker-assignment-meta">
                            <span>
                              <MapPin size={14} />
                              {assignment.location}
                            </span>
                            <span>
                              ₹{Number(assignment.budget).toLocaleString('en-IN')}
                            </span>
                            <span>
                              Sent {formatDate(assignment.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="worker-assignment-actions">
                        <button
                          type="button"
                          className="dashboard-secondary-button worker-assignment-details-button"
                          onClick={() =>
                            setExpandedId((current) =>
                              current === assignment.id
                                ? null
                                : assignment.id,
                            )
                          }
                        >
                          {isExpanded ? 'Hide details' : 'View details'}
                          <ChevronDown
                            size={16}
                            className={
                              isExpanded
                                ? 'worker-assignment-chevron-open'
                                : ''
                            }
                          />
                        </button>

                        {isPending && (
                          <>
                            <button
                              type="button"
                              className="worker-assignment-reject-button"
                              disabled={isBusy}
                              onClick={() =>
                                handleReject(assignment)
                              }
                            >
                              Decline
                            </button>
                            <button
                              type="button"
                              className="worker-assignment-accept-button"
                              disabled={isBusy}
                              onClick={() =>
                                handleAccept(assignment)
                              }
                            >
                              {isBusy ? 'Updating...' : 'Accept assignment'}
                            </button>
                          </>
                        )}
                      </div>

                      {isExpanded && (
                        <div className="worker-assignment-expanded">
                          <div className="worker-assignment-detail-grid">
                            <div>
                              <span>Budget</span>
                              <strong>
                                ₹{Number(assignment.budget).toLocaleString('en-IN')}
                              </strong>
                            </div>
                            <div>
                              <span>Location</span>
                              <strong>{assignment.location}</strong>
                            </div>
                            <div>
                              <span>Job status</span>
                              <strong>{formatStatus(assignment.job_status)}</strong>
                            </div>
                          </div>

                          <div className="worker-assignment-note">
                            {isAccepted ? (
                              <>
                                <CheckCircle2 size={16} />
                                <span>
                                  You accepted this work. MurphAI can now move
                                  the job into the work and evidence stages.
                                </span>
                              </>
                            ) : (
                              <>
                                <UserRound size={16} />
                                <span>
                                  The customer selected you for this job.
                                  Accepting creates your commitment to the work.
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      )}
                    </article>
                  )
                })}
              </div>
            )}
          </section>
        </div>
      </section>
    </main>
  )
}

export default WorkerAssignmentsPage
