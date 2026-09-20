import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  BadgeCheck,
  Check,
  CheckCircle2,
  Clock3,
  MapPin,
  Plus,
  RefreshCw,
  ShieldCheck,
  UserRound,
  X,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import {
  addWorkerSkill,
  createWorker,
  getCurrentUser,
  getMyWorker,
  getWorkerSkills,
  removeWorkerSkill,
  updateWorker,
} from '../services/api'
import './WorkerProfilePage.css'

const INITIAL_FORM = {
  bio: '',
  location: '',
  experience_years: 0,
  is_available: true,
}

function WorkerProfilePage() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [worker, setWorker] = useState(null)
  const [skills, setSkills] = useState([])
  const [form, setForm] = useState(INITIAL_FORM)
  const [newSkill, setNewSkill] = useState('')

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [skillLoading, setSkillLoading] = useState(false)
  const [removingSkillId, setRemovingSkillId] = useState(null)

  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadProfile() {
      try {
        const userData = await getCurrentUser()

        let workerData = null

        try {
          workerData = await getMyWorker()
        } catch {
          workerData = null
        }

        if (cancelled) {
          return
        }

        setUser(userData)

        if (!workerData) {
          setWorker(null)
          setSkills([])
          setForm(INITIAL_FORM)
          return
        }

        const skillsData = await getWorkerSkills(
          workerData.id,
        )

        if (cancelled) {
          return
        }

        setWorker(workerData)
        setForm({
          bio: workerData.bio || '',
          location: workerData.location || '',
          experience_years:
            workerData.experience_years ?? 0,
          is_available: workerData.is_available,
        })
        setSkills(
          Array.isArray(skillsData)
            ? skillsData
            : [],
        )
      } catch (err) {
        if (cancelled) {
          return
        }

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load your worker profile.',
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadProfile()

    return () => {
      cancelled = true
    }
  }, [])

  function handleChange(event) {
    const { name, value, checked, type } = event.target

    setForm((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  async function handleSave(event) {
    event.preventDefault()

    setSaving(true)
    setError('')
    setMessage('')

    const payload = {
      bio: form.bio.trim() || null,
      location: form.location.trim() || null,
      experience_years: Number(form.experience_years),
      is_available: form.is_available,
    }

    try {
      const workerData = worker
        ? await updateWorker(worker.id, payload)
        : await createWorker(payload)

      setWorker(workerData)

      setForm({
        bio: workerData.bio || '',
        location: workerData.location || '',
        experience_years:
          workerData.experience_years ?? 0,
        is_available: workerData.is_available,
      })

      if (!worker) {
        const skillsData = await getWorkerSkills(
          workerData.id,
        )

        setSkills(
          Array.isArray(skillsData) ? skillsData : [],
        )
      }

      setMessage(
        worker
          ? 'Profile changes saved successfully.'
          : 'Worker profile created successfully.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to save your worker profile.',
      )
    } finally {
      setSaving(false)
    }
  }

  async function handleAddSkill(event) {
    event.preventDefault()

    const skillName = newSkill.trim()

    if (!worker || !skillName) {
      return
    }

    setSkillLoading(true)
    setError('')
    setMessage('')

    try {
      const skill = await addWorkerSkill(
        worker.id,
        skillName,
      )

      setSkills((current) => [...current, skill])
      setNewSkill('')
      setMessage(`${skill.name} added to your skills.`)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to add this skill.',
      )
    } finally {
      setSkillLoading(false)
    }
  }

  async function handleRemoveSkill(skillId, skillName) {
    if (!worker) {
      return
    }

    setRemovingSkillId(skillId)
    setError('')
    setMessage('')

    try {
      await removeWorkerSkill(worker.id, skillId)

      setSkills((current) =>
        current.filter((skill) => skill.id !== skillId),
      )

      setMessage(`${skillName} removed from your skills.`)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to remove this skill.',
      )
    } finally {
      setRemovingSkillId(null)
    }
  }

  if (loading) {
    return (
      <main className="dashboard-shell worker-profile-shell">
        <div className="dashboard-loading-screen">
          <div className="dashboard-loading-card">
            <div className="dashboard-loading-spinner" />
            <h2>Loading your worker profile...</h2>
            <p>
              Getting your professional profile ready.
            </p>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="dashboard-shell worker-profile-shell">
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
            <UserRound size={18} />

            <input
              type="text"
              value="My worker profile"
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

        <div className="worker-profile-content">
          <button
            type="button"
            className="create-job-back"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft size={16} />
            Back to dashboard
          </button>

          <section className="worker-profile-hero">
            <div className="worker-profile-hero-copy">
              <span className="dashboard-eyebrow">
                PROFESSIONAL PROFILE
              </span>

              <h1>
                Build the profile customers can trust.
              </h1>

              <p>
                Keep your professional details and skills
                current. Customers see the public version
                of this information when evaluating your
                profile.
              </p>

              <div className="worker-profile-hero-meta">
                <div>
                  <BadgeCheck size={16} />
                  <span>
                    {worker
                      ? 'Profile active'
                      : 'Profile not created'}
                  </span>
                </div>

                {worker && (
                  <div>
                    <ShieldCheck size={16} />
                    <span>
                      {skills.length} listed skills
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="worker-profile-hero-icon">
              <UserRound size={36} />
            </div>
          </section>

          {(error || message) && (
            <div
              className={`worker-profile-feedback ${
                error
                  ? 'worker-profile-feedback-error'
                  : ''
              }`}
            >
              {error ? (
                <X size={17} />
              ) : (
                <Check size={17} />
              )}

              <span>{error || message}</span>
            </div>
          )}

          <div className="worker-profile-layout">
            <section className="worker-profile-panel">
              <div className="worker-profile-panel-header">
                <div>
                  <span className="dashboard-panel-kicker">
                    PROFILE DETAILS
                  </span>

                  <h2>
                    {worker
                      ? 'Update your profile'
                      : 'Create your worker profile'}
                  </h2>

                  <p>
                    These details become part of your
                    customer-facing professional identity.
                  </p>
                </div>
              </div>

              <form
                className="worker-profile-form"
                onSubmit={handleSave}
              >
                <label>
                  <span>Professional bio</span>

                  <textarea
                    name="bio"
                    value={form.bio}
                    onChange={handleChange}
                    placeholder="Tell customers what you do and what you are experienced with."
                    maxLength={2000}
                    rows={5}
                  />

                  <small>
                    {form.bio.length}/2000
                  </small>
                </label>

                <div className="worker-profile-form-grid">
                  <label>
                    <span>Location</span>

                    <div className="worker-profile-input-wrap">
                      <MapPin size={16} />

                      <input
                        type="text"
                        name="location"
                        value={form.location}
                        onChange={handleChange}
                        placeholder="Bhopal"
                        maxLength={200}
                      />
                    </div>
                  </label>

                  <label>
                    <span>Experience</span>

                    <div className="worker-profile-input-wrap">
                      <Clock3 size={16} />

                      <input
                        type="number"
                        name="experience_years"
                        value={form.experience_years}
                        onChange={handleChange}
                        min="0"
                        max="60"
                      />

                      <small>years</small>
                    </div>
                  </label>
                </div>

                <label className="worker-profile-availability">
                  <span>
                    <strong>
                      Available for new work
                    </strong>

                    <small>
                      Customers can see whether you are
                      currently available.
                    </small>
                  </span>

                  <input
                    type="checkbox"
                    name="is_available"
                    checked={form.is_available}
                    onChange={handleChange}
                  />

                  <span className="worker-profile-toggle" />
                </label>

                <div className="worker-profile-form-actions">
                  <button
                    type="button"
                    className="dashboard-secondary-button"
                    onClick={() =>
                      navigate('/workers/history')
                    }
                  >
                    <ShieldCheck size={16} />
                    View verified history
                  </button>

                  <button
                    type="submit"
                    className="dashboard-primary-button"
                    disabled={saving}
                  >
                    {saving ? (
                      <>
                        <RefreshCw
                          size={16}
                          className="worker-profile-spinning"
                        />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Check size={16} />
                        Save profile
                      </>
                    )}
                  </button>
                </div>
              </form>
            </section>

            <section className="worker-profile-panel">
              <div className="worker-profile-panel-header">
                <div>
                  <span className="dashboard-panel-kicker">
                    SKILLS
                  </span>

                  <h2>Professional skills</h2>

                  <p>
                    Add the skills customers should associate
                    with your verified professional identity.
                  </p>
                </div>
              </div>

              {!worker ? (
                <div className="worker-profile-empty">
                  <ShieldCheck size={18} />
                  <span>
                    Save your worker profile first, then add
                    professional skills.
                  </span>
                </div>
              ) : (
                <>
                  <form
                    className="worker-profile-skill-form"
                    onSubmit={handleAddSkill}
                  >
                    <input
                      type="text"
                      value={newSkill}
                      onChange={(event) =>
                        setNewSkill(event.target.value)
                      }
                      placeholder="Add a skill, e.g. Electrical Wiring"
                      maxLength={100}
                    />

                    <button
                      type="submit"
                      className="dashboard-primary-button"
                      disabled={
                        skillLoading ||
                        !newSkill.trim()
                      }
                    >
                      <Plus size={16} />
                      {skillLoading ? 'Adding...' : 'Add'}
                    </button>
                  </form>

                  {skills.length === 0 ? (
                    <div className="worker-profile-empty">
                      <ShieldCheck size={18} />
                      <span>
                        No skills added yet.
                      </span>
                    </div>
                  ) : (
                    <div className="worker-profile-skill-list">
                      {skills.map((skill) => (
                        <div
                          className="worker-profile-skill-chip"
                          key={skill.id}
                        >
                          <span>
                            <CheckCircle2 size={13} />
                            {skill.name}
                          </span>

                          <button
                            type="button"
                            onClick={() =>
                              handleRemoveSkill(
                                skill.id,
                                skill.name,
                              )
                            }
                            disabled={
                              removingSkillId === skill.id
                            }
                            aria-label={`Remove ${skill.name}`}
                          >
                            {removingSkillId === skill.id ? (
                              <RefreshCw
                                size={13}
                                className="worker-profile-spinning"
                              />
                            ) : (
                              <X size={13} />
                            )}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </section>
          </div>
        </div>
      </section>
    </main>
  )
}

export default WorkerProfilePage
