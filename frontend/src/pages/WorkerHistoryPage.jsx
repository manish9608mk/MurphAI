import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  BadgeCheck,
  BriefcaseBusiness,
  CalendarDays,
  CheckCircle2,
  CreditCard,
  ExternalLink,
  Image,
  MapPin,
  RefreshCw,
  ShieldCheck,
  Star,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import {
  getCurrentUser,
  getMyVerifiedHistory,
} from '../services/api'
import './WorkerHistoryPage.css'

function formatDate(value) {
  if (!value) return 'Not available'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Not available'
  }

  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function formatCurrency(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN')}`
}

function WorkerHistoryPage() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [history, setHistory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')

  async function loadHistory(showRefreshState = false) {
    if (showRefreshState) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }

    setError('')

    try {
      const [userData, historyData] = await Promise.all([
        getCurrentUser(),
        getMyVerifiedHistory(),
      ])

      setUser(userData)
      setHistory(historyData)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load your verified history.',
      )
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    async function loadPage() {
      setError('')

      try {
        const [userData, historyData] = await Promise.all([
          getCurrentUser(),
          getMyVerifiedHistory(),
        ])

        if (!cancelled) {
          setUser(userData)
          setHistory(historyData)
          setLoading(false)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load your verified history.',
          )
          setLoading(false)
        }
      }
    }

    loadPage()

    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <main className="dashboard-shell worker-history-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />
            <h2>Loading your verified history...</h2>
            <p>
              Gathering completed work, proof, payments,
              and reputation.
            </p>
          </div>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="dashboard-shell worker-history-shell">
        <div className="dashboard-error-screen">
          <div className="dashboard-error-card">
            <div className="dashboard-error-icon">
              <ShieldCheck size={24} />
            </div>

            <h1>We couldn't load your verified history</h1>

            <p>{error}</p>

            <div className="worker-history-error-actions">
              <button
                type="button"
                className="dashboard-secondary-button"
                onClick={() => navigate('/dashboard')}
              >
                <ArrowLeft size={17} />
                Back to dashboard
              </button>

              <button
                type="button"
                className="dashboard-primary-button"
                onClick={() => loadHistory()}
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

  const works = Array.isArray(history?.works)
    ? history.works
    : []

  return (
    <main className="dashboard-shell worker-history-shell">
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
            <ShieldCheck size={18} />
            <input
              type="text"
              value="Verified professional history"
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

        <div className="worker-history-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft size={16} />
            Back to dashboard
          </button>

          <section className="worker-history-hero">
            <div className="worker-history-hero-copy">
              <span className="dashboard-eyebrow">
                VERIFIED PROFESSIONAL HISTORY
              </span>

              <h1>
                Let the work speak for itself.
              </h1>

              <p>
                Completed jobs become part of a professional
                record when the customer confirms the work
                and payment is completed.
              </p>

              <div className="worker-history-hero-meta">
                <div>
                  <BadgeCheck size={16} />
                  <span>
                    {history?.total_verified_works || 0}
                    {' '}
                    verified works
                  </span>
                </div>

                {history?.average_rating != null && (
                  <div>
                    <Star size={16} />
                    <span>
                      {history.average_rating.toFixed(2)}
                      {' '}
                      average rating
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="worker-history-hero-icon">
              <ShieldCheck size={38} />
            </div>
          </section>

          <section className="worker-history-summary-grid">
            <article className="worker-history-summary-card">
              <div className="worker-history-summary-icon">
                <BadgeCheck size={20} />
              </div>

              <div>
                <span>Verified work</span>
                <strong>
                  {history?.total_verified_works || 0}
                </strong>
                <small>
                  Completed, confirmed, and paid
                </small>
              </div>
            </article>

            <article className="worker-history-summary-card">
              <div className="worker-history-summary-icon worker-history-summary-icon-rating">
                <Star size={20} />
              </div>

              <div>
                <span>Average rating</span>
                <strong>
                  {history?.average_rating != null
                    ? history.average_rating.toFixed(2)
                    : '—'}
                </strong>
                <small>
                  Based on submitted customer ratings
                </small>
              </div>
            </article>

            <article className="worker-history-summary-card">
              <div className="worker-history-summary-icon worker-history-summary-icon-payment">
                <CreditCard size={20} />
              </div>

              <div>
                <span>Verified earnings</span>
                <strong>
                  {formatCurrency(
                    works.reduce(
                      (total, work) =>
                        total + Number(work.budget || 0),
                      0,
                    ),
                  )}
                </strong>
                <small>
                  From the verified work shown here
                </small>
              </div>
            </article>
          </section>

          <section className="worker-history-panel">
            <div className="worker-history-panel-header">
              <div>
                <span className="dashboard-panel-kicker">
                  WORK RECORD
                </span>

                <h2>
                  Verified work history
                </h2>

                <p>
                  Each record contains the proof trail behind
                  the completed job.
                </p>
              </div>

              <button
                type="button"
                className="worker-history-refresh"
                onClick={() => loadHistory(true)}
                disabled={refreshing}
              >
                <RefreshCw
                  size={15}
                  className={
                    refreshing
                      ? 'worker-history-refresh-spinning'
                      : ''
                  }
                />
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>

            {works.length === 0 ? (
              <div className="worker-history-empty">
                <div className="worker-history-empty-icon">
                  <BriefcaseBusiness size={25} />
                </div>

                <h3>
                  Your verified history starts here.
                </h3>

                <p>
                  Complete a job, have the customer confirm
                  it, and finish payment to create your first
                  verified work record.
                </p>

                <button
                  type="button"
                  className="dashboard-secondary-button"
                  onClick={() => navigate('/assignments')}
                >
                  <BriefcaseBusiness size={16} />
                  View assignments
                </button>
              </div>
            ) : (
              <div className="worker-history-list">
                {works.map((work) => (
                  <article
                    className="worker-history-card"
                    key={work.work_id}
                  >
                    <div className="worker-history-card-top">
                      <div className="worker-history-card-title">
                        <div className="worker-history-card-icon">
                          <BriefcaseBusiness size={19} />
                        </div>

                        <div>
                          <div className="worker-history-title-row">
                            <h3>{work.job_title}</h3>

                            <span className="worker-history-verified-badge">
                              <BadgeCheck size={13} />
                              Verified
                            </span>
                          </div>

                          <div className="worker-history-job-meta">
                            <span>
                              <MapPin size={13} />
                              {work.location}
                            </span>

                            <span>
                              <CalendarDays size={13} />
                              {formatDate(work.completed_at)}
                            </span>

                            <strong>
                              {formatCurrency(work.budget)}
                            </strong>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="worker-history-card-body">
                      <div className="worker-history-section">
                        <span className="worker-history-section-label">
                          JOB
                        </span>

                        <p>
                          {work.job_description}
                        </p>
                      </div>

                      <div className="worker-history-section">
                        <span className="worker-history-section-label">
                          WORK COMPLETED
                        </span>

                        <p>
                          {work.work_description ||
                            'No additional work notes were recorded.'}
                        </p>
                      </div>

                      <div className="worker-history-proof-grid">
                        <div className="worker-history-proof-card">
                          <div className="worker-history-proof-icon">
                            <Image size={17} />
                          </div>

                          <div>
                            <strong>
                              Evidence
                            </strong>

                            <span>
                              {work.evidence?.length || 0}
                              {' '}
                              proof item
                              {work.evidence?.length === 1
                                ? ''
                                : 's'}
                            </span>
                          </div>

                          {work.evidence?.length > 0 && (
                            <a
                              href={work.evidence[0].url}
                              target="_blank"
                              rel="noreferrer"
                              aria-label="Open evidence"
                              className="worker-history-proof-link"
                            >
                              <ExternalLink size={14} />
                            </a>
                          )}
                        </div>

                        <div className="worker-history-proof-card">
                          <div className="worker-history-proof-icon">
                            <CheckCircle2 size={17} />
                          </div>

                          <div>
                            <strong>
                              Customer confirmed
                            </strong>

                            <span>
                              {formatDate(
                                work.confirmation?.confirmed_at,
                              )}
                            </span>
                          </div>
                        </div>

                        <div className="worker-history-proof-card">
                          <div className="worker-history-proof-icon">
                            <CreditCard size={17} />
                          </div>

                          <div>
                            <strong>
                              Payment verified
                            </strong>

                            <span>
                              {work.payment?.status === 'paid'
                                ? formatCurrency(
                                    work.payment.amount,
                                  )
                                : 'Not paid'}
                            </span>
                          </div>
                        </div>

                        <div className="worker-history-proof-card">
                          <div className="worker-history-proof-icon">
                            <Star size={17} />
                          </div>

                          <div>
                            <strong>
                              Customer reputation
                            </strong>

                            <span>
                              {work.reputation
                                ? `${work.reputation.rating}/5`
                                : 'Not rated yet'}
                            </span>
                          </div>
                        </div>
                      </div>

                      {work.confirmation?.comment && (
                        <div className="worker-history-confirmation">
                          <span>
                            CUSTOMER CONFIRMATION
                          </span>

                          <p>
                            “{work.confirmation.comment}”
                          </p>
                        </div>
                      )}

                      {work.reputation && (
                        <div className="worker-history-reputation">
                          <div className="worker-history-reputation-rating">
                            <Star size={16} />
                            <strong>
                              {work.reputation.rating}/5
                            </strong>
                          </div>

                          {work.reputation.comment && (
                            <p>
                              “{work.reputation.comment}”
                            </p>
                          )}

                          <span>
                            Customer feedback
                          </span>
                        </div>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>
      </section>
    </main>
  )
}

export default WorkerHistoryPage
