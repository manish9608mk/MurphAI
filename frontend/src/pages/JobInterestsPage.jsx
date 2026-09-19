import { useEffect, useMemo, useState } from 'react'
import {
  ArrowLeft,
  BriefcaseBusiness,
  Check,
  CheckCircle2,
  ChevronDown,
  Clock3,
  Filter,
  MapPin,
  ShieldCheck,
  UserRound,
} from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  createAssignment,
  getCurrentUser,
  getJob,
  getJobInterests,
} from '../services/api'

const FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'pending', label: 'Pending' },
  { key: 'selected', label: 'Selected' },
  { key: 'rejected', label: 'Rejected' },
]

function formatStatus(status) {
  if (!status) {
    return 'Unknown'
  }

  return status
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    )
}

function formatDate(value) {
  if (!value) {
    return 'Recently'
  }

  return new Date(value).toLocaleDateString(
    'en-IN',
    {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    },
  )
}

function JobInterestsPage() {
  const navigate = useNavigate()
  const { jobId } = useParams()

  const [user, setUser] = useState(null)
  const [job, setJob] = useState(null)
  const [interests, setInterests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all')
  const [availableOnly, setAvailableOnly] =
    useState(false)
  const [expandedId, setExpandedId] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [createdAssignment, setCreatedAssignment] = useState(null)
  const [assignmentLoading, setAssignmentLoading] = useState(false)
  const [assignmentError, setAssignmentError] = useState('')

  useEffect(() => {
    async function loadPage() {
      try {
        const [
          userData,
          jobData,
          interestsData,
        ] = await Promise.all([
          getCurrentUser(),
          getJob(jobId),
          getJobInterests(jobId),
        ])

        setUser(userData)
        setJob(jobData)
        setInterests(
          Array.isArray(interestsData)
            ? interestsData
            : [],
        )
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load interested workers.',
        )
      } finally {
        setLoading(false)
      }
    }

    loadPage()
  }, [jobId])

  const counts = useMemo(() => {
    return {
      all: interests.length,
      pending: interests.filter(
        (interest) =>
          interest.status === 'pending',
      ).length,
      selected: interests.filter(
        (interest) =>
          interest.status === 'selected',
      ).length,
      rejected: interests.filter(
        (interest) =>
          interest.status === 'rejected',
      ).length,
    }
  }, [interests])

  const visibleInterests = useMemo(() => {
    return interests.filter((interest) => {
      const matchesFilter =
        filter === 'all' ||
        interest.status === filter

      const matchesAvailability =
        !availableOnly ||
        interest.is_available === true

      return (
        matchesFilter &&
        matchesAvailability
      )
    })
  }, [availableOnly, filter, interests])

  const selectedWorker = interests.find(
    (interest) => interest.id === selectedId,
  )

  function toggleProfile(interestId) {
    setExpandedId((currentId) =>
      currentId === interestId
        ? null
        : interestId,
    )
  }

  function handleSelectWorker(interest) {
    if (
      createdAssignment ||
      interest.status !== 'pending' ||
      !interest.is_available
    ) {
      return
    }

    setAssignmentError('')
    setSelectedId((currentId) =>
      currentId === interest.id
        ? null
        : interest.id,
    )
  }

  async function handleCreateAssignment() {
    if (!selectedWorker || createdAssignment) {
      return
    }

    setAssignmentLoading(true)
    setAssignmentError('')

    try {
      const assignment = await createAssignment(
        jobId,
        selectedWorker.worker_id,
      )

      setCreatedAssignment(assignment)
      setSelectedId(selectedWorker.id)
    } catch (err) {
      setAssignmentError(
        err instanceof Error
          ? err.message
          : 'Unable to create the assignment.',
      )
    } finally {
      setAssignmentLoading(false)
    }
  }

  if (loading) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />

            <h2>
              Loading interested workers...
            </h2>

            <p>
              Getting the latest worker responses.
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

            <h1>
              We couldn't load interested workers
            </h1>

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
    <main className="dashboard-shell job-interests-page-shell">
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
              value="Interested workers"
              readOnly
              aria-label="Current page"
            />
          </div>

          <div className="dashboard-topbar-actions">
            {user && (
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
              </div>
            )}
          </div>
        </header>

        <div className="job-interests-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft size={16} />
            Back to dashboard
          </button>

          <div className="job-interests-header">
            <div>
              <span className="dashboard-eyebrow">
                WORKER INTEREST
              </span>

              <h1>
                {job?.title || 'Job'}
              </h1>

              <p>
                Review the people who want to take
                this job, compare their availability
                and experience, then move the right
                person into the assignment step.
              </p>
            </div>

            <div className="job-interests-job-summary">
              <span>Budget</span>

              <strong>
                ₹
                {Number(job?.budget || 0).toLocaleString(
                  'en-IN',
                )}
              </strong>

              <small>
                {job?.location || 'Remote'}
              </small>
            </div>
          </div>

          <div className="job-interests-toolbar">
            <div className="job-interests-filters">
              <Filter size={15} />

              {FILTERS.map((item) => (
                <button
                  key={item.key}
                  type="button"
                  className={`job-interests-filter-button ${
                    filter === item.key
                      ? 'job-interests-filter-button-active'
                      : ''
                  }`}
                  onClick={() =>
                    setFilter(item.key)
                  }
                >
                  {item.label}

                  <span className="job-interests-filter-count">
                    {counts[item.key]}
                  </span>
                </button>
              ))}
            </div>

            <button
              type="button"
              className={`job-interests-availability-toggle ${
                availableOnly
                  ? 'job-interests-availability-toggle-active'
                  : ''
              }`}
              onClick={() =>
                setAvailableOnly(
                  (current) => !current,
                )
              }
            >
              <CheckCircle2 size={14} />
              Available only
            </button>
          </div>

          {selectedWorker && !createdAssignment && (
            <div className="job-interests-selection-banner">
              <div>
                <strong>
                  {selectedWorker.worker_name ||
                    'Worker'} is chosen for the next step
                </strong>

                <span>
                  Review the worker once more, then create
                  a pending assignment for them to accept.
                </span>

                {assignmentError && (
                  <span className="job-interests-assignment-error">
                    {assignmentError}
                  </span>
                )}
              </div>

              <button
                type="button"
                className="job-interest-create-assignment-button"
                onClick={handleCreateAssignment}
                disabled={assignmentLoading}
              >
                {assignmentLoading
                  ? 'Creating...'
                  : 'Create Assignment'}
              </button>
            </div>
          )}

          {createdAssignment && selectedWorker && (
            <div className="job-interests-assignment-success">
              <div className="job-interests-assignment-success-icon">
                <Check size={17} />
              </div>

              <div>
                <strong>
                  Assignment created for {selectedWorker.worker_name || 'Worker'}
                </strong>

                <span>
                  Assignment #{createdAssignment.id} is pending.
                  The worker must accept it before the job becomes assigned.
                </span>
              </div>
            </div>
          )}

          <section className="job-interests-panel">
            <div className="job-interests-panel-header">
              <div>
                <span className="dashboard-panel-kicker">
                  APPLICANTS
                </span>

                <h2>
                  Interested Workers
                </h2>
              </div>

              <div className="job-interests-count">
                {visibleInterests.length}
              </div>
            </div>

            {visibleInterests.length === 0 ? (
              <div className="job-interests-empty">
                <div className="job-interests-empty-icon">
                  <UserRound size={24} />
                </div>

                <h3>
                  No workers match this view
                </h3>

                <p>
                  Try another filter or turn off
                  “Available only” to see everyone.
                </p>
              </div>
            ) : (
              <div className="job-interests-list">
                {visibleInterests.map(
                  (interest) => {
                    const isExpanded =
                      expandedId === interest.id

                    const isLocallySelected =
                      selectedId === interest.id

                    return (
                      <article
                        className={`job-interest-card ${
                          isLocallySelected
                            ? 'job-interest-card-local-selected'
                            : ''
                        }`}
                        key={interest.id}
                      >
                        <div className="job-interest-main">
                          <div className="job-interest-avatar">
                            {interest.worker_name
                              ?.charAt(0)
                              ?.toUpperCase() ||
                              'W'}
                          </div>

                          <div className="job-interest-copy">
                            <div className="job-interest-status-line">
                              <h3>
                                {interest.worker_name ||
                                  'Worker'}
                              </h3>

                              <span
                                className={`dashboard-status dashboard-status-${interest.status}`}
                              >
                                {formatStatus(
                                  interest.status,
                                )}
                              </span>

                              {isLocallySelected && (
                                <span className="job-interest-local-selection">
                                  <Check size={11} />
                                  Chosen for next step
                                </span>
                              )}
                            </div>

                            <p className="job-interest-bio">
                              {interest.bio ||
                                'No worker bio provided.'}
                            </p>

                            <div className="job-interest-meta">
                              <span>
                                <MapPin size={13} />
                                {interest.location ||
                                  'Location not provided'}
                              </span>

                              <span>
                                <Clock3 size={13} />
                                {interest.experience_years ??
                                  0}{' '}
                                years experience
                              </span>

                              <span
                                className={
                                  interest.is_available
                                    ? 'job-interest-available'
                                    : 'job-interest-unavailable'
                                }
                              >
                                {interest.is_available ? (
                                  <>
                                    <CheckCircle2
                                      size={13}
                                    />
                                    Available
                                  </>
                                ) : (
                                  <>
                                    <Clock3 size={13} />
                                    Currently unavailable
                                  </>
                                )}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="job-interest-actions">
                          <button
                            type="button"
                            className="dashboard-secondary-button"
                            onClick={() =>
                              toggleProfile(
                                interest.id,
                              )
                            }
                          >
                            {isExpanded
                              ? 'Hide Profile'
                              : 'View Profile'}

                            <ChevronDown
                              size={15}
                              style={{
                                transform:
                                  isExpanded
                                    ? 'rotate(180deg)'
                                    : 'rotate(0deg)',
                              }}
                            />
                          </button>

                          <button
                            type="button"
                            className={`dashboard-primary-button job-interest-select-button ${
                              isLocallySelected
                                ? 'job-interest-select-button-selected'
                                : ''
                            }`}
                            disabled={
                              Boolean(createdAssignment) ||
                              interest.status !==
                                'pending' ||
                              !interest.is_available
                            }
                            onClick={() =>
                              handleSelectWorker(
                                interest,
                              )
                            }
                          >
                            {createdAssignment &&
                            isLocallySelected ? (
                              <>
                                <Check size={16} />
                                Assignment Created
                              </>
                            ) : isLocallySelected ? (
                              <>
                                <Check size={16} />
                                Chosen
                              </>
                            ) : (
                              'Select Worker'
                            )}
                          </button>
                        </div>

                        {isExpanded && (
                          <div className="job-interest-expanded">
                            <div className="job-interest-expanded-item">
                              <span>
                                Experience
                              </span>

                              <strong>
                                {interest.experience_years ??
                                  0}{' '}
                                years
                              </strong>
                            </div>

                            <div className="job-interest-expanded-item">
                              <span>
                                Availability
                              </span>

                              <strong>
                                {interest.is_available
                                  ? 'Available for work'
                                  : 'Currently unavailable'}
                              </strong>
                            </div>

                            <div className="job-interest-expanded-item">
                              <span>
                                Interest sent
                              </span>

                              <strong>
                                {formatDate(
                                  interest.created_at,
                                )}
                              </strong>
                            </div>
                          </div>
                        )}

                        {isExpanded && (
                          <p className="job-interest-card-note">
                            MurphAI uses the verified
                            workflow to connect interest,
                            assignment, work evidence and
                            reputation.
                          </p>
                        )}
                      </article>
                    )
                  },
                )}
              </div>
            )}
          </section>
        </div>
      </section>
    </main>
  )
}

export default JobInterestsPage
