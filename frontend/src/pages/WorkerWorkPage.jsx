import { useEffect, useMemo, useState } from 'react'
import {
  ArrowLeft,
  BriefcaseBusiness,
  CheckCircle2,
  Clock3,
  FileText,
  MapPin,
  PlayCircle,
  ShieldCheck,
  Sparkles,
  Timer,
} from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  getAssignment,
  getCurrentUser,
  getJob,
  getWork,
  updateWork,
  updateWorkStatus,
} from '../services/api'
import './WorkerWorkPage.css'

function formatDateTime(value) {
  if (!value) return 'Not recorded'

  return new Date(value).toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatStatus(status) {
  if (!status) return 'Unknown'

  return status
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function WorkerWorkPage() {
  const navigate = useNavigate()
  const { workId } = useParams()

  const [user, setUser] = useState(null)
  const [work, setWork] = useState(null)
  const [assignment, setAssignment] = useState(null)
  const [job, setJob] = useState(null)
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [actionMessage, setActionMessage] = useState('')
  const [actionError, setActionError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadPage() {
      try {
        const workData = await getWork(workId)
        const assignmentData = await getAssignment(
          workData.assignment_id,
        )

        const [userData, jobData] = await Promise.all([
          getCurrentUser(),
          getJob(assignmentData.job_id),
        ])

        if (!cancelled) {
          setUser(userData)
          setWork(workData)
          setDescription(workData.description || '')
          setAssignment(assignmentData)
          setJob(jobData)
          setLoading(false)
        }
      } catch (err) {
        if (!cancelled) {
          setActionError(
            err instanceof Error
              ? err.message
              : 'Unable to load this work record.',
          )
          setLoading(false)
        }
      }
    }

    loadPage()

    return () => {
      cancelled = true
    }
  }, [workId])

  const progress = useMemo(() => {
    if (!work) return 2
    if (work.status === 'completed') return 4
    if (work.status === 'in_progress') return 3
    return 2
  }, [work])

  async function handleStartWork() {
    if (!work || work.status !== 'pending' || saving) return

    setSaving(true)
    setActionMessage('')
    setActionError('')

    try {
      const updated = await updateWorkStatus(
        work.id,
        'in_progress',
      )

      setWork((current) => ({
        ...current,
        ...updated,
      }))

      setActionMessage(
        'Work is now in progress. Keep the work record updated as you go.',
      )
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : 'Unable to start this work.',
      )
    } finally {
      setSaving(false)
    }
  }

  async function handleSaveNotes() {
    if (!work || work.status === 'completed' || saving) {
      return
    }

    setSaving(true)
    setActionMessage('')
    setActionError('')

    try {
      const updated = await updateWork(
        work.id,
        description || null,
      )

      setWork((current) => ({
        ...current,
        ...updated,
      }))

      setActionMessage('Work notes saved.')
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : 'Unable to save your notes.',
      )
    } finally {
      setSaving(false)
    }
  }

  async function handleCompleteWork() {
    if (!work || work.status !== 'in_progress' || saving) {
      return
    }

    const confirmed = window.confirm(
      'Mark this work as completed? Make sure the requested work is actually finished first.',
    )

    if (!confirmed) return

    setSaving(true)
    setActionMessage('')
    setActionError('')

    try {
      const updated = await updateWorkStatus(
        work.id,
        'completed',
      )

      setWork((current) => ({
        ...current,
        ...updated,
      }))

      setActionMessage(
        'Work marked as completed. Evidence and customer confirmation come next.',
      )
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : 'Unable to complete this work.',
      )
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />
            <h2>Loading your work...</h2>
            <p>Preparing the work record and job details.</p>
          </div>
        </div>
      </main>
    )
  }

  if (actionError && (!work || !assignment || !job)) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-error-screen">
          <div className="dashboard-error-card">
            <div className="dashboard-error-icon">
              <ShieldCheck size={24} />
            </div>
            <h1>We couldn't load this work</h1>
            <p>{actionError}</p>
            <button
              type="button"
              className="dashboard-primary-button"
              onClick={() => navigate('/assignments')}
            >
              <ArrowLeft size={17} />
              Back to assignments
            </button>
          </div>
        </div>
      </main>
    )
  }

  const isPending = work.status === 'pending'
  const isInProgress = work.status === 'in_progress'
  const isCompleted = work.status === 'completed'

  return (
    <main className="dashboard-shell worker-work-shell">
      <section className="dashboard-main">
        <header className="dashboard-topbar">
          <button
            type="button"
            className="dashboard-menu-button"
            onClick={() => navigate('/assignments')}
            aria-label="Back to assignments"
          >
            <ArrowLeft size={20} />
          </button>

          <div className="dashboard-search">
            <BriefcaseBusiness size={18} />
            <input
              type="text"
              value="Work workspace"
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

        <div className="worker-work-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() => navigate('/assignments')}
          >
            <ArrowLeft size={16} />
            Back to assignments
          </button>

          <section className="worker-work-hero">
            <div className="worker-work-hero-copy">
              <span className="dashboard-eyebrow">
                ACTIVE WORK
              </span>

              <div className="worker-work-title-row">
                <h1>{job.title}</h1>

                <span
                  className={`worker-work-status worker-work-status-${work.status}`}
                >
                  {isCompleted ? (
                    <CheckCircle2 size={14} />
                  ) : (
                    <Clock3 size={14} />
                  )}
                  {formatStatus(work.status)}
                </span>
              </div>

              <p>{job.description}</p>

              <div className="worker-work-meta">
                <span>
                  <MapPin size={15} />
                  {job.location}
                </span>

                <span className="worker-work-budget">
                  ₹{Number(job.budget).toLocaleString('en-IN')}
                </span>

                <span>
                  Assignment #{assignment.id}
                </span>
              </div>
            </div>

            <div className="worker-work-hero-icon">
              {isInProgress ? (
                <Timer size={34} />
              ) : isCompleted ? (
                <CheckCircle2 size={34} />
              ) : (
                <PlayCircle size={34} />
              )}
            </div>
          </section>

          <section className="worker-work-progress">
            <div className="worker-work-progress-top">
              <div>
                <span className="dashboard-panel-kicker">
                  DELIVERY
                </span>
                <h2>Work lifecycle</h2>
              </div>

              <span>Step {progress} of 4</span>
            </div>

            <div className="worker-work-progress-track">
              <div
                className="worker-work-progress-fill"
                style={{
                  width: `${((progress - 1) / 3) * 100}%`,
                }}
              />
            </div>

            <div className="worker-work-steps">
              <div className="worker-work-step worker-work-step-done">
                <span>01</span>
                <strong>Assignment accepted</strong>
                <small>Customer selected you</small>
              </div>

              <div
                className={`worker-work-step ${
                  progress >= 2
                    ? 'worker-work-step-done'
                    : ''
                }`}
              >
                <span>02</span>
                <strong>Work created</strong>
                <small>Delivery record exists</small>
              </div>

              <div
                className={`worker-work-step ${
                  progress >= 3
                    ? 'worker-work-step-done'
                    : ''
                }`}
              >
                <span>03</span>
                <strong>Work in progress</strong>
                <small>
                  {work.started_at
                    ? `Started ${formatDateTime(work.started_at)}`
                    : 'Ready to start'}
                </small>
              </div>

              <div
                className={`worker-work-step ${
                  progress >= 4
                    ? 'worker-work-step-done'
                    : ''
                }`}
              >
                <span>04</span>
                <strong>Completed</strong>
                <small>
                  {work.completed_at
                    ? formatDateTime(work.completed_at)
                    : 'Evidence comes next'}
                </small>
              </div>
            </div>
          </section>

          {(actionMessage || actionError) && (
            <div
              className={`worker-work-feedback ${
                actionError
                  ? 'worker-work-feedback-error'
                  : ''
              }`}
            >
              {actionError ? (
                <Clock3 size={18} />
              ) : (
                <CheckCircle2 size={18} />
              )}
              <span>{actionError || actionMessage}</span>
            </div>
          )}

          <section className="worker-work-layout">
            <article className="worker-work-card">
              <div className="worker-work-card-header">
                <div>
                  <span className="dashboard-panel-kicker">
                    WORK RECORD
                  </span>
                  <h2>Keep the delivery record clear</h2>
                </div>

                <FileText size={21} />
              </div>

              <label
                className="worker-work-description-label"
                htmlFor="work-description"
              >
                What are you doing or what was completed?
              </label>

              <textarea
                id="work-description"
                className="worker-work-description"
                value={description}
                onChange={(event) =>
                  setDescription(event.target.value)
                }
                placeholder="Add useful notes about the work, progress, parts replaced, checks performed, or the final result..."
                maxLength={2000}
                disabled={isCompleted}
              />

              <div className="worker-work-editor-footer">
                <span>{description.length} / 2000</span>

                <button
                  type="button"
                  className="worker-work-save-button"
                  onClick={handleSaveNotes}
                  disabled={isCompleted || saving}
                >
                  {saving ? 'Saving...' : 'Save notes'}
                </button>
              </div>

              <div className="worker-work-guidance">
                <Sparkles size={16} />
                <span>
                  Clear work notes help create a useful verified
                  record when evidence and confirmation are added.
                </span>
              </div>
            </article>

            <aside className="worker-work-summary">
              <div className="worker-work-summary-card">
                <span className="dashboard-panel-kicker">
                  JOB SUMMARY
                </span>

                <h2>{job.title}</h2>

                <div className="worker-work-summary-row">
                  <span>Budget</span>
                  <strong>
                    ₹{Number(job.budget).toLocaleString('en-IN')}
                  </strong>
                </div>

                <div className="worker-work-summary-row">
                  <span>Location</span>
                  <strong>{job.location}</strong>
                </div>

                <div className="worker-work-summary-row">
                  <span>Job status</span>
                  <strong>{formatStatus(job.status)}</strong>
                </div>

                <div className="worker-work-summary-row">
                  <span>Started</span>
                  <strong>
                    {formatDateTime(work.started_at)}
                  </strong>
                </div>
              </div>

              <div className="worker-work-action-card">
                {isPending && (
                  <>
                    <div className="worker-work-action-icon">
                      <PlayCircle size={22} />
                    </div>

                    <h3>Ready to start?</h3>

                    <p>
                      Start the delivery record when you are
                      physically ready to begin the job.
                    </p>

                    <button
                      type="button"
                      className="worker-work-primary-button"
                      onClick={handleStartWork}
                      disabled={saving}
                    >
                      <PlayCircle size={17} />
                      {saving ? 'Starting...' : 'Start work'}
                    </button>
                  </>
                )}

                {isInProgress && (
                  <>
                    <div className="worker-work-action-icon worker-work-action-icon-progress">
                      <Timer size={22} />
                    </div>

                    <h3>Work is in progress</h3>

                    <p>
                      Keep your notes current, then mark the work
                      complete when the requested outcome is finished.
                    </p>

                    <button
                      type="button"
                      className="worker-work-complete-button"
                      onClick={handleCompleteWork}
                      disabled={saving}
                    >
                      <CheckCircle2 size={17} />
                      {saving
                        ? 'Updating...'
                        : 'Mark work complete'}
                    </button>
                  </>
                )}

                {isCompleted && (
                  <>
                    <div className="worker-work-action-icon worker-work-action-icon-complete">
                      <CheckCircle2 size={22} />
                    </div>

                    <h3>Work completed</h3>

                    <p>
                      Your work record is complete. The next stage
                      is evidence and customer confirmation.
                    </p>

                    <button
                      type="button"
                      className="dashboard-secondary-button"
                      onClick={() => navigate('/assignments')}
                    >
                      Back to assignments
                    </button>
                  </>
                )}
              </div>
            </aside>
          </section>
        </div>
      </section>
    </main>
  )
}

export default WorkerWorkPage
