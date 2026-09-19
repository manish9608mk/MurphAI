import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  BriefcaseBusiness,
  CheckCircle2,
  Clock3,
  MapPin,
  ShieldCheck,
} from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'

import {
  createJobInterest,
  getJob,
  getMyJobInterests,
  withdrawJobInterest,
} from '../services/api'


function JobDetailsPage() {
  const navigate = useNavigate()
  const { jobId } = useParams()

  const [job, setJob] = useState(null)
  const [interest, setInterest] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')

  useEffect(() => {
    async function loadJobDetails() {
      try {
        const jobData = await getJob(jobId)

        setJob(jobData)

        try {
          const interests = await getMyJobInterests()

          const existingInterest = Array.isArray(interests)
            ? interests.find(
                (item) =>
                  item.job_id === jobData.id,
              )
            : null

          setInterest(existingInterest)
        } catch (err) {
          /*
           * A user without a Worker profile cannot have
           * job interests yet. The job itself should still
           * remain viewable.
           *
           * Authentication errors should still be surfaced.
           */
          if (
            err instanceof Error &&
            err.message === 'Not authenticated'
          ) {
            throw err
          }
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load this job.',
        )
      } finally {
        setLoading(false)
      }
    }

    loadJobDetails()
  }, [jobId])

  async function handleInterest() {
    if (!job) {
      return
    }

    setActionError('')
    setIsSubmitting(true)

    try {
      const result = await createJobInterest(job.id)

      setInterest(result)
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : 'Unable to express interest.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleWithdraw() {
    if (!interest) {
      return
    }

    setActionError('')
    setIsSubmitting(true)

    try {
      const result = await withdrawJobInterest(
        interest.id,
      )

      setInterest(result)
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : 'Unable to withdraw interest.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />

            <h2>Loading job details...</h2>

            <p>
              Getting the work details ready for you.
            </p>
          </div>
        </div>
      </main>
    )
  }

  if (error || !job) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-error-screen">
          <div className="dashboard-error-card">
            <div className="dashboard-error-icon">
              <ShieldCheck size={24} />
            </div>

            <h1>
              We couldn't load this job
            </h1>

            <p>
              {error || 'Job not found.'}
            </p>

            <button
              type="button"
              className="dashboard-primary-button"
              onClick={() =>
                navigate('/jobs/available')
              }
            >
              <ArrowLeft size={17} />
              Back to jobs
            </button>
          </div>
        </div>
      </main>
    )
  }

  const isOpen = job.status === 'open'

  return (
    <main className="dashboard-shell">
      <section className="dashboard-main job-details-main">
        <div className="dashboard-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() =>
              navigate('/jobs/available')
            }
          >
            <ArrowLeft size={17} />
            Back to jobs
          </button>

          <div className="job-details-layout">
            <article className="job-details-card">
              <div className="job-details-top">
                <div className="job-details-icon">
                  <BriefcaseBusiness size={24} />
                </div>

                <span
                  className={`dashboard-status dashboard-status-${job.status}`}
                >
                  {formatStatus(job.status)}
                </span>
              </div>

              <div className="job-details-header">
                <span className="dashboard-panel-kicker">
                  JOB DETAILS
                </span>

                <h1>{job.title}</h1>

                <div className="job-details-meta">
                  <span>
                    <MapPin size={16} />
                    {job.location}
                  </span>

                  <span>
                    <Clock3 size={16} />
                    {formatDate(job.created_at)}
                  </span>
                </div>
              </div>

              <div className="job-details-section">
                <span className="job-details-section-label">
                  DESCRIPTION
                </span>

                <p className="job-details-description">
                  {job.description}
                </p>
              </div>

              <div className="job-details-budget">
                <div>
                  <span>Budget</span>

                  <strong>
                    ₹
                    {Number(
                      job.budget,
                    ).toLocaleString('en-IN')}
                  </strong>
                </div>

                <span className="job-details-budget-note">
                  Customer-set budget
                </span>
              </div>

              {actionError && (
                <p
                  className="job-details-action-error"
                  role="alert"
                >
                  {actionError}
                </p>
              )}

              <div className="job-details-action">
                {!isOpen ? (
                  <div className="job-details-closed">
                    <ShieldCheck size={18} />

                    <span>
                      This job is no longer accepting
                      interest.
                    </span>
                  </div>
                ) : interest?.status === 'pending' ? (
                  <div className="job-details-interest-state job-details-interest-pending">
                    <div>
                      <CheckCircle2 size={18} />

                      <span>
                        Interest sent
                      </span>
                    </div>

                    <button
                      type="button"
                      className="dashboard-secondary-button"
                      onClick={handleWithdraw}
                      disabled={isSubmitting}
                    >
                      {isSubmitting
                        ? 'Withdrawing...'
                        : 'Withdraw'}
                    </button>
                  </div>
                ) : interest?.status === 'withdrawn' ? (
                  <button
                    type="button"
                    className="dashboard-primary-button"
                    onClick={handleInterest}
                    disabled={isSubmitting}
                  >
                    <BriefcaseBusiness size={18} />

                    {isSubmitting
                      ? 'Sending...'
                      : 'Apply again'}
                  </button>
                ) : interest?.status === 'selected' ? (
                  <div className="job-details-interest-state job-details-interest-selected">
                    <CheckCircle2 size={18} />

                    <span>
                      You have been selected for this job.
                    </span>
                  </div>
                ) : interest?.status === 'rejected' ? (
                  <div className="job-details-interest-state job-details-interest-rejected">
                    <span>
                      Your previous interest was not selected.
                    </span>
                  </div>
                ) : (
                  <button
                    type="button"
                    className="dashboard-primary-button job-details-interest-button"
                    onClick={handleInterest}
                    disabled={isSubmitting}
                  >
                    <BriefcaseBusiness size={18} />

                    {isSubmitting
                      ? 'Sending...'
                      : "I'm Interested"}
                  </button>
                )}
              </div>
            </article>

            <aside className="job-details-side">
              <section className="job-details-trust-card">
                <div className="job-details-trust-icon">
                  <ShieldCheck size={21} />
                </div>

                <span className="dashboard-panel-kicker">
                  MURPHAI TRUST
                </span>

                <h2>Work with clarity</h2>

                <p>
                  MurphAI connects the job, worker,
                  evidence, confirmation, payment, and
                  reputation into one verified workflow.
                </p>
              </section>

              <section className="job-details-summary-card">
                <span className="dashboard-panel-kicker">
                  AT A GLANCE
                </span>

                <div className="job-details-summary-row">
                  <span>Location</span>
                  <strong>
                    {job.location}
                  </strong>
                </div>

                <div className="job-details-summary-row">
                  <span>Budget</span>
                  <strong>
                    ₹
                    {Number(
                      job.budget,
                    ).toLocaleString('en-IN')}
                  </strong>
                </div>

                <div className="job-details-summary-row">
                  <span>Status</span>
                  <strong>
                    {formatStatus(job.status)}
                  </strong>
                </div>
              </section>
            </aside>
          </div>
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


function formatDate(value) {
  if (!value) {
    return 'Recently posted'
  }

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


export default JobDetailsPage