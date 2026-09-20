import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  BadgeCheck,
  BriefcaseBusiness,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  MapPin,
  RefreshCw,
  Search,
  ShieldCheck,
  Star,
  UserRound,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import {
  discoverWorkers,
  getCurrentUser,
} from '../services/api'
import './BrowseWorkersPage.css'

const PAGE_SIZE = 9

function WorkerCard({ worker, onViewProfile }) {
  const rating =
    worker.average_rating != null
      ? Number(worker.average_rating).toFixed(2)
      : null

  return (
    <article className="browse-workers-card">
      <div className="browse-workers-card-top">
        <div className="browse-workers-avatar">
          {worker.name?.charAt(0)?.toUpperCase() || 'W'}
        </div>

        <div className="browse-workers-identity">
          <div className="browse-workers-name-row">
            <h3>{worker.name}</h3>

            {worker.verified_work_count > 0 && (
              <BadgeCheck
                size={16}
                className="browse-workers-verified-icon"
                aria-label="Has verified work history"
              />
            )}
          </div>

          <span
            className={
              worker.is_available
                ? 'browse-workers-availability browse-workers-available'
                : 'browse-workers-availability browse-workers-unavailable'
            }
          >
            {worker.is_available ? (
              <>
                <CheckCircle2 size={13} />
                Available
              </>
            ) : (
              <>
                <Clock3 size={13} />
                Unavailable
              </>
            )}
          </span>
        </div>
      </div>

      <p className="browse-workers-bio">
        {worker.bio ||
          'This worker has not added a professional bio yet.'}
      </p>

      <div className="browse-workers-meta">
        <span>
          <MapPin size={14} />
          {worker.location || 'Location not provided'}
        </span>

        <span>
          <Clock3 size={14} />
          {worker.experience_years} years experience
        </span>
      </div>

      {worker.skills?.length > 0 ? (
        <div className="browse-workers-skills">
          {worker.skills.slice(0, 5).map((skill) => (
            <span key={skill}>{skill}</span>
          ))}

          {worker.skills.length > 5 && (
            <span>
              +{worker.skills.length - 5}
            </span>
          )}
        </div>
      ) : (
        <div className="browse-workers-no-skills">
          No skills added yet
        </div>
      )}

      <div className="browse-workers-stats">
        <div>
          <span>Verified work</span>
          <strong>
            {worker.verified_work_count}
          </strong>
        </div>

        <div>
          <span>Rating</span>
          <strong className="browse-workers-rating">
            <Star
              size={14}
              fill={
                rating
                  ? 'currentColor'
                  : 'none'
              }
            />
            {rating || '—'}
          </strong>
        </div>
      </div>

      <button
        type="button"
        className="browse-workers-profile-button"
        onClick={() => onViewProfile(worker.worker_id)}
      >
        View profile
        <ArrowLeft
          size={16}
          className="browse-workers-profile-arrow"
        />
      </button>
    </article>
  )
}

function BrowseWorkersPage() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [workers, setWorkers] = useState([])
  const [total, setTotal] = useState(0)

  const [search, setSearch] = useState('')
  const [location, setLocation] = useState('')
  const [skill, setSkill] = useState('')
  const [availableOnly, setAvailableOnly] =
    useState(false)

  const [page, setPage] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadWorkers(
    nextPage = page,
    filters = {
      search,
      location,
      skill,
      availableOnly,
    },
  ) {
    setLoading(true)
    setError('')

    try {
      const data = await discoverWorkers({
        search: filters.search,
        location: filters.location,
        skill: filters.skill,
        available_only: filters.availableOnly,
        limit: PAGE_SIZE,
        offset: nextPage * PAGE_SIZE,
      })

      setWorkers(
        Array.isArray(data.workers)
          ? data.workers
          : [],
      )

      setTotal(
        Number(data.total || 0),
      )
      setPage(nextPage)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load workers.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [userData, workerData] =
          await Promise.all([
            getCurrentUser(),
            discoverWorkers({
              limit: PAGE_SIZE,
              offset: 0,
            }),
          ])

        setUser(userData)
        setWorkers(
          Array.isArray(workerData.workers)
            ? workerData.workers
            : [],
        )
        setTotal(
          Number(workerData.total || 0),
        )
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load workers.',
        )
      } finally {
        setLoading(false)
      }
    }

    loadInitialData()
  }, [])

  function handleSearchSubmit(event) {
    event.preventDefault()

    loadWorkers(0, {
      search,
      location,
      skill,
      availableOnly,
    })
  }

  function handleClearFilters() {
    setSearch('')
    setLocation('')
    setSkill('')
    setAvailableOnly(false)

    loadWorkers(0, {
      search: '',
      location: '',
      skill: '',
      availableOnly: false,
    })
  }

  function handlePreviousPage() {
    if (page === 0) {
      return
    }

    loadWorkers(page - 1)
  }

  function handleNextPage() {
    if (
      (page + 1) * PAGE_SIZE >= total
    ) {
      return
    }

    loadWorkers(page + 1)
  }

  const totalPages = Math.max(
    1,
    Math.ceil(total / PAGE_SIZE),
  )

  return (
    <main className="dashboard-shell browse-workers-shell">
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
            <Search size={18} />

            <input
              type="text"
              value="Browse workers"
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

                  <span>
                    {user.role || 'Customer'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </header>

        <div className="browse-workers-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft size={16} />
            Back to dashboard
          </button>

          <section className="browse-workers-hero">
            <div>
              <span className="dashboard-eyebrow">
                MURPHAI DIRECTORY
              </span>

              <h1>Find skilled workers you can trust.</h1>

              <p>
                Explore worker profiles, skills, availability,
                verified work history, and customer-backed
                reputation before choosing who to contact.
              </p>
            </div>

            <div className="browse-workers-hero-icon">
              <UserRound size={30} />
            </div>
          </section>

          <section className="browse-workers-filter-panel">
            <form onSubmit={handleSearchSubmit}>
              <div className="browse-workers-filter-grid">
                <label>
                  <span>Search</span>
                  <div className="browse-workers-input">
                    <Search size={16} />
                    <input
                      type="text"
                      value={search}
                      onChange={(event) =>
                        setSearch(event.target.value)
                      }
                      placeholder="Name, skill, or bio"
                    />
                  </div>
                </label>

                <label>
                  <span>Location</span>
                  <div className="browse-workers-input">
                    <MapPin size={16} />
                    <input
                      type="text"
                      value={location}
                      onChange={(event) =>
                        setLocation(event.target.value)
                      }
                      placeholder="Bhopal"
                    />
                  </div>
                </label>

                <label>
                  <span>Skill</span>
                  <div className="browse-workers-input">
                    <BriefcaseBusiness size={16} />
                    <input
                      type="text"
                      value={skill}
                      onChange={(event) =>
                        setSkill(event.target.value)
                      }
                      placeholder="Electrical wiring"
                    />
                  </div>
                </label>

                <label className="browse-workers-availability-filter">
                  <span>Availability</span>

                  <button
                    type="button"
                    className={
                      availableOnly
                        ? 'browse-workers-toggle browse-workers-toggle-on'
                        : 'browse-workers-toggle'
                    }
                    onClick={() =>
                      setAvailableOnly(
                        (current) => !current,
                      )
                    }
                    aria-pressed={availableOnly}
                  >
                    <span className="browse-workers-toggle-track">
                      <span />
                    </span>

                    <strong>
                      Available only
                    </strong>
                  </button>
                </label>
              </div>

              <div className="browse-workers-filter-actions">
                <button
                  type="submit"
                  className="dashboard-primary-button"
                  disabled={loading}
                >
                  <Search size={17} />
                  Apply filters
                </button>

                <button
                  type="button"
                  className="dashboard-secondary-button"
                  onClick={handleClearFilters}
                  disabled={loading}
                >
                  Clear
                </button>
              </div>
            </form>
          </section>

          <div className="browse-workers-results-header">
            <div>
              <span className="dashboard-panel-kicker">
                WORKER DIRECTORY
              </span>

              <h2>
                {total} {total === 1 ? 'worker' : 'workers'} found
              </h2>
            </div>

            <div className="browse-workers-results-trust">
              <ShieldCheck size={17} />
              Public-safe professional information
            </div>
          </div>

          {error ? (
            <section className="browse-workers-state">
              <div className="browse-workers-state-icon">
                <ShieldCheck size={23} />
              </div>

              <h3>We couldn't load the directory</h3>

              <p>{error}</p>

              <button
                type="button"
                className="dashboard-primary-button"
                onClick={() =>
                  loadWorkers(0)
                }
              >
                <RefreshCw size={17} />
                Try again
              </button>
            </section>
          ) : loading ? (
            <section className="browse-workers-state">
              <div className="dashboard-loading-spinner" />
              <h3>Finding workers...</h3>
              <p>
                Gathering profiles, skills, and verified reputation.
              </p>
            </section>
          ) : workers.length === 0 ? (
            <section className="browse-workers-state">
              <div className="browse-workers-state-icon">
                <Search size={23} />
              </div>

              <h3>No workers matched your filters</h3>

              <p>
                Try a broader search or clear your filters
                to explore the full directory.
              </p>

              <button
                type="button"
                className="dashboard-secondary-button"
                onClick={handleClearFilters}
              >
                Clear filters
              </button>
            </section>
          ) : (
            <>
              <section className="browse-workers-grid">
                {workers.map((worker) => (
                  <WorkerCard
                    key={worker.worker_id}
                    worker={worker}
                    onViewProfile={(workerId) =>
                      navigate(
                        `/workers/${workerId}/profile`,
                      )
                    }
                  />
                ))}
              </section>

              <nav
                className="browse-workers-pagination"
                aria-label="Worker directory pagination"
              >
                <button
                  type="button"
                  className="browse-workers-page-button"
                  onClick={handlePreviousPage}
                  disabled={page === 0 || loading}
                  aria-label="Previous page"
                >
                  <ChevronLeft size={17} />
                </button>

                <span>
                  Page {page + 1} of {totalPages}
                </span>

                <button
                  type="button"
                  className="browse-workers-page-button"
                  onClick={handleNextPage}
                  disabled={
                    page + 1 >= totalPages ||
                    loading
                  }
                  aria-label="Next page"
                >
                  <ChevronRight size={17} />
                </button>
              </nav>
            </>
          )}

          <div className="browse-workers-trust-note">
            <ShieldCheck size={18} />

            <div>
              <strong>
                Choose from evidence, not just claims.
              </strong>

              <span>
                Verified work counts and ratings are based on
                MurphAI's completed workflow: work completed,
                customer confirmation, and payment. Private
                customer and payment information is not shown.
              </span>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default BrowseWorkersPage
