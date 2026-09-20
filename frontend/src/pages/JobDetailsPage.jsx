import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  BriefcaseBusiness,
  CheckCircle2,
  Clock3,
  ExternalLink,
  FileText,
  MapPin,
  Paperclip,
  ShieldCheck,
} from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'

import {
  createConfirmation,
  createJobInterest,
  getConfirmationForWork,
  getCurrentUser,
  getEvidenceForWork,
  getJob,
  getMyJobInterests,
  getWorkByJob,
  withdrawJobInterest,
} from '../services/api'

function JobDetailsPage() {
  const navigate = useNavigate()
  const { jobId } = useParams()

  const [user, setUser] = useState(null)
  const [job, setJob] = useState(null)
  const [interest, setInterest] = useState(null)
  const [work, setWork] = useState(null)
  const [evidence, setEvidence] = useState([])

  const [confirmation, setConfirmation] = useState(null)
  const [confirmationComment, setConfirmationComment] =
    useState('')
  const [confirmationLoading, setConfirmationLoading] =
    useState(true)
  const [confirmationSaving, setConfirmationSaving] =
    useState(false)

  const [deliveryLoading, setDeliveryLoading] = useState(true)
  const [loading, setLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadJobDetails() {
      try {
        const [jobData, userData] = await Promise.all([
          getJob(jobId),
          getCurrentUser(),
        ])

        if (cancelled) {
          return
        }

        setJob(jobData)
        setUser(userData)

        const isCustomerOwner =
          userData.id === jobData.customer_id

        if (!isCustomerOwner) {
          try {
            const interests = await getMyJobInterests()

            if (!cancelled) {
              const existingInterest = Array.isArray(interests)
                ? interests.find(
                    (item) =>
                      item.job_id === jobData.id,
                  )
                : null

              setInterest(existingInterest)
            }
          } catch (err) {
            if (
              err instanceof Error &&
              err.message === 'Not authenticated'
            ) {
              throw err
            }
          }
        }

        if (isCustomerOwner) {
          try {
            const workData = await getWorkByJob(
              jobData.id,
            )

            if (cancelled) {
              return
            }

            setWork(workData)

            try {
              const evidenceData =
                await getEvidenceForWork(
                  workData.id,
                )

              if (!cancelled) {
                setEvidence(
                  Array.isArray(evidenceData)
                    ? evidenceData
                    : [],
                )
              }
            } catch {
              if (!cancelled) {
                setEvidence([])
              }
            }

            try {
              const confirmationData =
                await getConfirmationForWork(
                  workData.id,
                )

              if (!cancelled) {
                setConfirmation(confirmationData)
              }
            } catch {
              if (!cancelled) {
                setConfirmation(null)
              }
            } finally {
              if (!cancelled) {
                setConfirmationLoading(false)
              }
            }
          } catch {
            if (!cancelled) {
              setWork(null)
              setEvidence([])
              setConfirmation(null)
              setConfirmationLoading(false)
            }
          }
        } else if (!cancelled) {
          setConfirmationLoading(false)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load this job.',
          )
        }
      } finally {
        if (!cancelled) {
          setDeliveryLoading(false)
          setLoading(false)
        }
      }
    }

    loadJobDetails()

    return () => {
      cancelled = true
    }
  }, [jobId])

  async function handleConfirmWork() {
    if (
      !work ||
      work.status !== 'completed' ||
      confirmation ||
      confirmationSaving
    ) {
      return
    }

    setActionError('')
    setConfirmationSaving(true)

    try {
      const result = await createConfirmation(
        work.id,
        confirmationComment.trim() || null,
      )

      setConfirmation(result)
      setConfirmationComment('')
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : 'Unable to confirm this work.',
      )
    } finally {
      setConfirmationSaving(false)
    }
  }

  async function handleInterest() {
    if (!job) {
      return
    }

    setActionError('')
    setIsSubmitting(true)

    try {
      const result = await createJobInterest(
        job.id,
      )

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

            <h2>
              Loading job details...
            </h2>

            <p>
              Getting the work details ready
              for you.
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
              {error ||
                'Job not found.'}
            </p>

            <button
              type="button"
              className="dashboard-primary-button"
              onClick={() =>
                navigate(
                  '/jobs/available',
                )
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

  const isOpen =
    job.status === 'open'

  const isCustomerOwner =
    user?.id === job.customer_id

  const isCompleted =
    job.status === 'completed'

  return (
    <main className="dashboard-shell">
      <section className="dashboard-main job-details-main">
        <div className="dashboard-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() =>
              navigate(
                '/jobs/available',
              )
            }
          >
            <ArrowLeft size={17} />
            Back to jobs
          </button>

          <div className="job-details-layout">
            <article className="job-details-card">
              <div className="job-details-top">
                <div className="job-details-icon">
                  <BriefcaseBusiness
                    size={24}
                  />
                </div>

                <span
                  className={`dashboard-status dashboard-status-${job.status}`}
                >
                  {formatStatus(
                    job.status,
                  )}
                </span>
              </div>

              <div className="job-details-header">
                <span className="dashboard-panel-kicker">
                  JOB DETAILS
                </span>

                <h1>
                  {job.title}
                </h1>

                <div className="job-details-meta">
                  <span>
                    <MapPin size={16} />
                    {job.location}
                  </span>

                  <span>
                    <Clock3 size={16} />
                    {formatDate(
                      job.created_at,
                    )}
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
                  <span>
                    Budget
                  </span>

                  <strong>
                    ₹
                    {Number(
                      job.budget,
                    ).toLocaleString(
                      'en-IN',
                    )}
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
                {isCustomerOwner ? (
                  <div className="job-details-owner-state">
                    <ShieldCheck size={18} />

                    <span>
                      This is your job.
                    </span>
                  </div>
                ) : !isOpen ? (
                  <div className="job-details-closed">
                    <ShieldCheck size={18} />

                    <span>
                      This job is no longer
                      accepting interest.
                    </span>
                  </div>
                ) : interest?.status ===
                  'pending' ? (
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
                      onClick={
                        handleWithdraw
                      }
                      disabled={
                        isSubmitting
                      }
                    >
                      {isSubmitting
                        ? 'Withdrawing...'
                        : 'Withdraw'}
                    </button>
                  </div>
                ) : interest?.status ===
                  'withdrawn' ? (
                  <button
                    type="button"
                    className="dashboard-primary-button"
                    onClick={
                      handleInterest
                    }
                    disabled={
                      isSubmitting
                    }
                  >
                    <BriefcaseBusiness size={18} />

                    {isSubmitting
                      ? 'Sending...'
                      : 'Apply again'}
                  </button>
                ) : interest?.status ===
                  'selected' ? (
                  <div className="job-details-interest-state job-details-interest-selected">
                    <CheckCircle2 size={18} />

                    <span>
                      You have been
                      selected for this
                      job.
                    </span>
                  </div>
                ) : interest?.status ===
                  'rejected' ? (
                  <div className="job-details-interest-state job-details-interest-rejected">
                    <span>
                      Your previous
                      interest was not
                      selected.
                    </span>
                  </div>
                ) : (
                  <button
                    type="button"
                    className="dashboard-primary-button job-details-interest-button"
                    onClick={
                      handleInterest
                    }
                    disabled={
                      isSubmitting
                    }
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
                  <ShieldCheck
                    size={21}
                  />
                </div>

                <span className="dashboard-panel-kicker">
                  MURPHAI TRUST
                </span>

                <h2>
                  Work with clarity
                </h2>

                <p>
                  MurphAI connects the
                  job, worker, evidence,
                  confirmation, payment,
                  and reputation into one
                  verified workflow.
                </p>
              </section>

              <section className="job-details-summary-card">
                <span className="dashboard-panel-kicker">
                  AT A GLANCE
                </span>

                <div className="job-details-summary-row">
                  <span>
                    Location
                  </span>

                  <strong>
                    {job.location}
                  </strong>
                </div>

                <div className="job-details-summary-row">
                  <span>
                    Budget
                  </span>

                  <strong>
                    ₹
                    {Number(
                      job.budget,
                    ).toLocaleString(
                      'en-IN',
                    )}
                  </strong>
                </div>

                <div className="job-details-summary-row">
                  <span>
                    Status
                  </span>

                  <strong>
                    {formatStatus(
                      job.status,
                    )}
                  </strong>
                </div>
              </section>
            </aside>
          </div>

          {isCustomerOwner && (
            <section className="job-details-delivery-section">
              <article className="job-details-delivery-card">
                <div className="job-details-delivery-header">
                  <div>
                    <span className="dashboard-panel-kicker">
                      DELIVERY
                    </span>

                    <h2>
                      Review the completed work
                    </h2>

                    <p>
                      Review the worker's
                      delivery record and
                      submitted proof before
                      the confirmation stage.
                    </p>
                  </div>

                  <div className="job-details-delivery-icon">
                    <ShieldCheck
                      size={22}
                    />
                  </div>
                </div>

                {deliveryLoading ? (
                  <div className="job-details-delivery-loading">
                    <div className="dashboard-loading-spinner" />

                    <span>
                      Loading delivery record...
                    </span>
                  </div>
                ) : !work ? (
                  <div className="job-details-delivery-empty">
                    <div className="job-details-delivery-empty-icon">
                      <Clock3 size={20} />
                    </div>

                    <strong>
                      No delivery record yet
                    </strong>

                    <span>
                      The worker's Work record
                      will appear here once
                      work has been started.
                    </span>
                  </div>
                ) : (
                  <>
                    <div className="job-details-work-summary">
                      <div>
                        <span>
                          Work status
                        </span>

                        <strong
                          className={`job-details-work-status job-details-work-status-${work.status}`}
                        >
                          {work.status ===
                          'completed' ? (
                            <CheckCircle2
                              size={15}
                            />
                          ) : (
                            <Clock3
                              size={15}
                            />
                          )}

                          {formatStatus(
                            work.status,
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Started
                        </span>

                        <strong>
                          {formatDateTime(
                            work.started_at,
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Completed
                        </span>

                        <strong>
                          {formatDateTime(
                            work.completed_at,
                          )}
                        </strong>
                      </div>
                    </div>

                    <div className="job-details-work-record">
                      <div className="job-details-work-record-header">
                        <div>
                          <span className="dashboard-panel-kicker">
                            WORK RECORD
                          </span>

                          <h3>
                            Worker's notes
                          </h3>
                        </div>

                        <FileText
                          size={20}
                        />
                      </div>

                      <div className="job-details-work-notes">
                        {work.description ? (
                          <p>
                            {work.description}
                          </p>
                        ) : (
                          <span>
                            No work notes were
                            provided.
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="job-details-evidence">
                      <div className="job-details-evidence-header">
                        <div>
                          <span className="dashboard-panel-kicker">
                            EVIDENCE
                          </span>

                          <h3>
                            Submitted proof
                          </h3>
                        </div>

                        <span className="job-details-evidence-count">
                          {evidence.length}
                        </span>
                      </div>

                      {evidence.length === 0 ? (
                        <div className="job-details-evidence-empty">
                          <Paperclip
                            size={19}
                          />

                          <strong>
                            No evidence submitted
                          </strong>

                          <span>
                            The worker has not
                            added proof to this
                            Work record yet.
                          </span>
                        </div>
                      ) : (
                        <div className="job-details-evidence-list">
                          {evidence.map(
                            (item) => (
                              <article
                                className="job-details-evidence-item"
                                key={item.id}
                              >
                                <div className="job-details-evidence-item-icon">
                                  <Paperclip
                                    size={18}
                                  />
                                </div>

                                <div className="job-details-evidence-item-content">
                                  <div className="job-details-evidence-item-top">
                                    <strong>
                                      {formatEvidenceType(
                                        item.evidence_type,
                                      )}
                                    </strong>

                                    <span>
                                      {formatDate(
                                        item.created_at,
                                      )}
                                    </span>
                                  </div>

                                  {item.description && (
                                    <p>
                                      {
                                        item.description
                                      }
                                    </p>
                                  )}

                                  <a
                                    href={
                                      item.url
                                    }
                                    target="_blank"
                                    rel="noreferrer"
                                  >
                                    Open evidence
                                    <ExternalLink
                                      size={14}
                                    />
                                  </a>
                                </div>
                              </article>
                            ),
                          )}
                        </div>
                      )}
                    </div>

                    {isCompleted && (
                      <div className="job-details-confirmation">
                        {confirmationLoading ? (
                          <div className="job-details-confirmation-loading">
                            <div className="dashboard-loading-spinner" />

                            <span>
                              Checking confirmation status...
                            </span>
                          </div>
                        ) : confirmation ? (
                          <div className="job-details-confirmation-complete">
                            <div className="job-details-confirmation-preview-icon">
                              <CheckCircle2 size={19} />
                            </div>

                            <div>
                              <span className="dashboard-panel-kicker">
                                CONFIRMED
                              </span>

                              <strong>
                                Work confirmed
                              </strong>

                              <span>
                                Confirmed on{' '}
                                {formatDateTime(
                                  confirmation.confirmed_at,
                                )}
                              </span>

                              {confirmation.comment && (
                                <p>
                                  {confirmation.comment}
                                </p>
                              )}
                            </div>
                          </div>
                        ) : (
                          <div className="job-details-confirmation-ready">
                            <div className="job-details-confirmation-ready-header">
                              <div>
                                <span className="dashboard-panel-kicker">
                                  CONFIRMATION
                                </span>

                                <h3>
                                  Ready for your confirmation
                                </h3>

                                <p>
                                  Review the work record and
                                  evidence above. Confirm only
                                  when the requested outcome has
                                  been delivered.
                                </p>
                              </div>

                              <div className="job-details-confirmation-preview-icon">
                                <CheckCircle2
                                  size={19}
                                />
                              </div>
                            </div>

                            <label
                              htmlFor="customer-confirmation-comment"
                              className="job-details-confirmation-label"
                            >
                              Optional comment
                            </label>

                            <textarea
                              id="customer-confirmation-comment"
                              className="job-details-confirmation-textarea"
                              value={
                                confirmationComment
                              }
                              onChange={(event) =>
                                setConfirmationComment(
                                  event.target.value,
                                )
                              }
                              placeholder="Add feedback about the completed work..."
                              maxLength={2000}
                              disabled={
                                confirmationSaving
                              }
                            />

                            <div className="job-details-confirmation-footer">
                              <span>
                                {
                                  confirmationComment.length
                                }{' '}
                                / 2000
                              </span>

                              <button
                                type="button"
                                className="job-details-confirmation-button"
                                onClick={
                                  handleConfirmWork
                                }
                                disabled={
                                  confirmationSaving
                                }
                              >
                                <CheckCircle2
                                  size={16}
                                />

                                {confirmationSaving
                                  ? 'Confirming...'
                                  : 'Confirm work'}
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </>
                )}
              </article>
            </section>
          )}
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

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return 'Recently posted'
  }

  return date.toLocaleDateString(
    'en-IN',
    {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    },
  )
}

function formatDateTime(value) {
  if (!value) {
    return 'Not recorded'
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return 'Not recorded'
  }

  return date.toLocaleString(
    'en-IN',
    {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    },
  )
}

function formatEvidenceType(type) {
  if (!type) {
    return 'Evidence'
  }

  return type
    .replaceAll('_', ' ')
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase(),
    )
}

export default JobDetailsPage