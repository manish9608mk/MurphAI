import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  BadgeCheck,
  BriefcaseBusiness,
  CheckCircle2,
  Clock3,
  MapPin,
  RefreshCw,
  ShieldCheck,
  Star,
  UserRound,
} from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  createAssignment,
  getCurrentUser,
  getMyJobs,
  getWorkerPublicProfile,
} from '../services/api'
import './WorkerPublicProfilePage.css'

function formatDate(value) {
  if (!value) return 'Date unavailable'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Date unavailable'
  }

  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function formatRole(value) {
  if (!value) return 'Member'

  return value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function RatingStars({ rating }) {
  const roundedRating = Math.round(Number(rating || 0))

  return (
    <div
      className="worker-public-profile-stars"
      aria-label={`${rating} out of 5 stars`}
    >
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          size={15}
          fill={star <= roundedRating ? 'currentColor' : 'none'}
        />
      ))}
    </div>
  )
}

function WorkerPublicProfilePage() {
  const navigate = useNavigate()
  const { workerId } = useParams()

  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [hireOpen, setHireOpen] = useState(false)
  const [hireJobs, setHireJobs] = useState([])
  const [hireLoading, setHireLoading] = useState(false)
  const [hireSaving, setHireSaving] = useState(false)
  const [hireError, setHireError] = useState('')
  const [hireSuccess, setHireSuccess] = useState('')

  async function openHirePanel() {
    setHireOpen(true)
    setHireLoading(true)
    setHireError('')
    setHireSuccess('')

    try {
      const jobsData = await getMyJobs()

      const openJobs = (
        Array.isArray(jobsData)
          ? jobsData
          : []
      ).filter(
        (job) => job.status === 'open',
      )

      setHireJobs(openJobs)
    } catch (err) {
      setHireError(
        err instanceof Error
          ? err.message
          : 'Unable to load your open jobs.',
      )
    } finally {
      setHireLoading(false)
    }
  }

  function closeHirePanel() {
    if (hireSaving) {
      return
    }

    setHireOpen(false)
    setHireError('')
  }

  async function handleHire(jobId) {
    setHireSaving(true)
    setHireError('')
    setHireSuccess('')

    try {
      await createAssignment(
        jobId,
        profile.worker_id,
      )

      setHireSuccess(
        'Assignment request created successfully. The worker can now review and respond to it.',
      )

      setHireJobs((currentJobs) =>
        currentJobs.filter(
          (job) => job.id !== jobId,
        ),
      )
    } catch (err) {
      setHireError(
        err instanceof Error
          ? err.message
          : 'Unable to create the assignment.',
      )
    } finally {
      setHireSaving(false)
    }
  }

  async function loadProfile() {
    setLoading(true)
    setError('')

    try {
      const [userData, profileData] = await Promise.all([
        getCurrentUser(),
        getWorkerPublicProfile(workerId),
      ])

      setUser(userData)
      setProfile(profileData)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load this worker profile.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    Promise.all([
      getCurrentUser(),
      getWorkerPublicProfile(workerId),
    ])
      .then(([userData, profileData]) => {
        if (cancelled) {
          return
        }

        setUser(userData)
        setProfile(profileData)
      })
      .catch((err) => {
        if (cancelled) {
          return
        }

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load this worker profile.',
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
  }, [workerId])

  if (loading) {
    return (
      <main className="dashboard-shell worker-public-profile-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />
            <h2>Loading worker profile...</h2>
            <p>
              Gathering professional details and verified reputation.
            </p>
          </div>
        </div>
      </main>
    )
  }

  if (error || !profile) {
    return (
      <main className="dashboard-shell worker-public-profile-shell">
        <div className="dashboard-error-screen">
          <div className="dashboard-error-card">
            <div className="dashboard-error-icon">
              <ShieldCheck size={24} />
            </div>

            <h1>We couldn't load this worker profile</h1>

            <p>{error || 'Worker profile not found.'}</p>

            <div className="worker-public-profile-error-actions">
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
                onClick={loadProfile}
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

  const skills = Array.isArray(profile.skills)
    ? profile.skills
    : []

  const reviews = Array.isArray(profile.reviews)
    ? profile.reviews
    : []

  return (
    <main className="dashboard-shell worker-public-profile-shell">
      <section className="dashboard-main">
        <header className="dashboard-topbar">
          <button
            type="button"
            className="dashboard-menu-button"
            onClick={() => navigate(-1)}
            aria-label="Go back"
          >
            <ArrowLeft size={20} />
          </button>

          <div className="dashboard-search">
            <UserRound size={18} />

            <input
              type="text"
              value="Worker profile"
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

                  <span>
                    {formatRole(user.role)}
                  </span>
                </div>
              </div>
            )}
          </div>
        </header>

        <div className="worker-public-profile-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft size={16} />
            Back
          </button>

          <section className="worker-public-profile-hero">
            <div className="worker-public-profile-identity">
              <div className="worker-public-profile-avatar">
                {profile.name?.charAt(0)?.toUpperCase() || 'W'}
              </div>

              <div className="worker-public-profile-identity-copy">
                <div className="worker-public-profile-kicker">
                  <span className="dashboard-eyebrow">
                    PUBLIC WORKER PROFILE
                  </span>

                  <span className="worker-public-profile-verified">
                    <BadgeCheck size={14} />
                    Verified history available
                  </span>
                </div>

                <h1>{profile.name}</h1>

                <p>
                  {profile.bio ||
                    'This worker has not added a professional bio yet.'}
                </p>

                <div className="worker-public-profile-meta">
                  <span>
                    <MapPin size={14} />
                    {profile.location || 'Location not provided'}
                  </span>

                  <span>
                    <Clock3 size={14} />
                    {profile.experience_years} years experience
                  </span>

                  <span
                    className={
                      profile.is_available
                        ? 'worker-public-profile-available'
                        : 'worker-public-profile-unavailable'
                    }
                  >
                    {profile.is_available ? (
                      <>
                        <CheckCircle2 size={14} />
                        Available for work
                      </>
                    ) : (
                      <>
                        <Clock3 size={14} />
                        Currently unavailable
                      </>
                    )}
                  </span>
                </div>

                <div className="worker-public-profile-hero-actions">
                  <button
                    type="button"
                    className="dashboard-primary-button"
                    onClick={openHirePanel}
                  >
                    <BriefcaseBusiness size={17} />
                    Hire this worker
                  </button>
                </div>
              </div>
            </div>
          </section>

          {hireOpen && (
            <div
              className="worker-public-profile-hire-overlay"
              role="presentation"
              onMouseDown={(event) => {
                if (
                  event.target === event.currentTarget
                ) {
                  closeHirePanel()
                }
              }}
            >
              <section
                className="worker-public-profile-hire-dialog"
                role="dialog"
                aria-modal="true"
                aria-labelledby="hire-worker-title"
              >
                <div className="worker-public-profile-hire-dialog-header">
                  <div>
                    <span className="dashboard-panel-kicker">
                      HIRE WORKER
                    </span>

                    <h2 id="hire-worker-title">
                      Choose a job for {profile.name}
                    </h2>

                    <p>
                      Select one of your open jobs to send this
                      worker an assignment request.
                    </p>
                  </div>

                  <button
                    type="button"
                    className="worker-public-profile-hire-close"
                    onClick={closeHirePanel}
                    disabled={hireSaving}
                    aria-label="Close hire dialog"
                  >
                    ×
                  </button>
                </div>

                {hireError && (
                  <div className="worker-public-profile-hire-alert worker-public-profile-hire-alert-error">
                    <ShieldCheck size={16} />
                    <span>{hireError}</span>
                  </div>
                )}

                {hireSuccess && (
                  <div className="worker-public-profile-hire-alert worker-public-profile-hire-alert-success">
                    <CheckCircle2 size={16} />
                    <span>{hireSuccess}</span>
                  </div>
                )}

                {hireLoading ? (
                  <div className="worker-public-profile-hire-state">
                    <div className="dashboard-loading-spinner" />
                    <strong>Loading your open jobs...</strong>
                    <span>
                      Finding jobs that can accept a new worker.
                    </span>
                  </div>
                ) : hireJobs.length === 0 ? (
                  <div className="worker-public-profile-hire-state">
                    <BriefcaseBusiness size={25} />

                    <strong>
                      No open jobs available
                    </strong>

                    <span>
                      Create an open job first, then return here
                      to send {profile.name} an assignment request.
                    </span>

                    <button
                      type="button"
                      className="dashboard-primary-button"
                      onClick={() =>
                        navigate('/jobs/new')
                      }
                    >
                      <BriefcaseBusiness size={16} />
                      Create a job
                    </button>
                  </div>
                ) : (
                  <div className="worker-public-profile-hire-jobs">
                    {hireJobs.map((job) => (
                      <article
                        className="worker-public-profile-hire-job"
                        key={job.id}
                      >
                        <div className="worker-public-profile-hire-job-icon">
                          <BriefcaseBusiness size={18} />
                        </div>

                        <div className="worker-public-profile-hire-job-copy">
                          <span>JOB #{job.id}</span>
                          <h3>{job.title}</h3>

                          <div>
                            <span>
                              <MapPin size={13} />
                              {job.location || 'Remote'}
                            </span>

                            <span>
                              ₹
                              {Number(
                                job.budget || 0,
                              ).toLocaleString('en-IN')}
                            </span>
                          </div>
                        </div>

                        <button
                          type="button"
                          className="worker-public-profile-hire-job-button"
                          onClick={() =>
                            handleHire(job.id)
                          }
                          disabled={hireSaving}
                        >
                          {hireSaving
                            ? 'Sending...'
                            : 'Send request'}
                          <ArrowLeft
                            size={15}
                            className="worker-public-profile-hire-job-arrow"
                          />
                        </button>
                      </article>
                    ))}
                  </div>
                )}

                <div className="worker-public-profile-hire-footer">
                  <ShieldCheck size={15} />
                  <span>
                    The worker must accept the assignment before
                    the job moves forward.
                  </span>
                </div>
              </section>
            </div>
          )}

          <section className="worker-public-profile-summary-grid">
            <article className="worker-public-profile-summary-card">
              <div className="worker-public-profile-summary-icon">
                <BadgeCheck size={19} />
              </div>

              <div>
                <span>Verified work</span>
                <strong>
                  {profile.verified_work_count}
                </strong>
                <small>
                  Completed, customer-confirmed and paid work records
                </small>
              </div>
            </article>

            <article className="worker-public-profile-summary-card worker-public-profile-summary-rating">
              <div className="worker-public-profile-summary-icon">
                <Star size={19} />
              </div>

              <div>
                <span>Average rating</span>
                <strong>
                  {profile.average_rating != null
                    ? profile.average_rating.toFixed(2)
                    : '—'}
                </strong>
                <small>
                  Based on submitted customer reputation
                </small>
              </div>
            </article>

            <article className="worker-public-profile-summary-card">
              <div className="worker-public-profile-summary-icon">
                <BriefcaseBusiness size={19} />
              </div>

              <div>
                <span>Customer reviews</span>
                <strong>{reviews.length}</strong>
                <small>
                  Feedback from verified completed work
                </small>
              </div>
            </article>
          </section>

          <section className="worker-public-profile-panel">
            <div className="worker-public-profile-panel-header">
              <div>
                <span className="dashboard-panel-kicker">
                  SKILLS
                </span>

                <h2>Professional skills</h2>
              </div>
            </div>

            {skills.length === 0 ? (
              <div className="worker-public-profile-empty">
                <ShieldCheck size={18} />
                <span>No skills have been added yet.</span>
              </div>
            ) : (
              <div className="worker-public-profile-skills">
                {skills.map((skill) => (
                  <span key={skill}>
                    <CheckCircle2 size={13} />
                    {skill}
                  </span>
                ))}
              </div>
            )}
          </section>

          <section className="worker-public-profile-panel">
            <div className="worker-public-profile-panel-header">
              <div>
                <span className="dashboard-panel-kicker">
                  CUSTOMER FEEDBACK
                </span>

                <h2>Verified reviews</h2>

                <p>
                  Reviews appear here only when the underlying work
                  reached MurphAI's verified completion flow.
                </p>
              </div>
            </div>

            {reviews.length === 0 ? (
              <div className="worker-public-profile-empty">
                <ShieldCheck size={18} />
                <span>
                  No customer reviews have been submitted yet.
                </span>
              </div>
            ) : (
              <div className="worker-public-profile-reviews">
                {reviews.map((review) => (
                  <article
                    className="worker-public-profile-review"
                    key={review.work_id}
                  >
                    <div className="worker-public-profile-review-top">
                      <div>
                        <span className="worker-public-profile-review-label">
                          VERIFIED WORK
                        </span>

                        <h3>{review.job_title}</h3>
                      </div>

                      <div className="worker-public-profile-review-rating">
                        <RatingStars rating={review.rating} />
                        <strong>
                          {review.rating}/5
                        </strong>
                      </div>
                    </div>

                    <p className="worker-public-profile-review-comment">
                      {review.comment ||
                        'No written review was provided.'}
                    </p>

                    <div className="worker-public-profile-review-date">
                      <BadgeCheck size={14} />
                      Completed {formatDate(review.completed_at)}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>

          <div className="worker-public-profile-trust-note">
            <ShieldCheck size={18} />

            <div>
              <strong>MurphAI verified reputation</strong>
              <span>
                This profile separates verified customer-backed work
                from unverified claims. Private customer and payment
                information is never displayed here.
              </span>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default WorkerPublicProfilePage
