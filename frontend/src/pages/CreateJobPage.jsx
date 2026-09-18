import { useState } from 'react'
import {
  ArrowLeft,
  BriefcaseBusiness,
  FileText,
  IndianRupee,
  MapPin,
  Send,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { createJob } from '../services/api'

function CreateJobPage() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    budget: '',
  })

  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((current) => ({
      ...current,
      [name]: value,
    }))

    if (error) {
      setError('')
    }
  }

  function validateForm() {
    const title = formData.title.trim()
    const description = formData.description.trim()
    const location = formData.location.trim()
    const budget = Number(formData.budget)

    if (title.length < 3 || title.length > 100) {
      return 'Job title must be between 3 and 100 characters.'
    }

    if (
      description.length < 10 ||
      description.length > 2000
    ) {
      return 'Description must be between 10 and 2000 characters.'
    }

    if (
      location.length < 2 ||
      location.length > 200
    ) {
      return 'Location must be between 2 and 200 characters.'
    }

    if (!Number.isFinite(budget) || budget <= 0) {
      return 'Budget must be greater than ₹0.'
    }

    return ''
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const validationError = validateForm()

    if (validationError) {
      setError(validationError)
      return
    }

    setError('')
    setIsSubmitting(true)

    try {
      await createJob({
        title: formData.title.trim(),
        description: formData.description.trim(),
        location: formData.location.trim(),
        budget: Number(formData.budget),
      })

      navigate('/dashboard')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to create the job.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="create-job-page">
      <div className="create-job-container">
        <button
          type="button"
          className="create-job-back"
          onClick={() => navigate('/dashboard')}
        >
          <ArrowLeft size={17} />
          Back to dashboard
        </button>

        <header className="create-job-header">
          <span className="eyebrow">
            CREATE WORK
          </span>

          <h1>Post a Job</h1>

          <p>
            Describe the work clearly so the right people can
            understand the outcome you need.
          </p>
        </header>

        <div className="create-job-layout">
          <section className="create-job-card">
            <form onSubmit={handleSubmit}>
              {error && (
                <p
                  className="create-job-error"
                  role="alert"
                >
                  {error}
                </p>
              )}

              <div className="create-job-field">
                <label htmlFor="title">
                  Job title
                </label>

                <div className="create-job-input-wrap">
                  <BriefcaseBusiness
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id="title"
                    name="title"
                    type="text"
                    value={formData.title}
                    onChange={handleChange}
                    placeholder="e.g. Fix a leaking tap"
                    minLength={3}
                    maxLength={100}
                    autoComplete="off"
                    required
                  />
                </div>

                <span>
                  {formData.title.length}/100
                </span>
              </div>

              <div className="create-job-field">
                <label htmlFor="description">
                  Describe the work
                </label>

                <div className="create-job-input-wrap create-job-textarea-wrap">
                  <FileText
                    size={18}
                    aria-hidden="true"
                  />

                  <textarea
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="e.g. Repair the kitchen tap and stop the water leak"
                    minLength={10}
                    maxLength={2000}
                    required
                  />
                </div>

                <span>
                  {formData.description.length}/2000
                </span>
              </div>

              <div className="create-job-two-column">
                <div className="create-job-field">
                  <label htmlFor="location">
                    Location *
                  </label>

                  <div className="create-job-input-wrap">
                    <MapPin
                      size={18}
                      aria-hidden="true"
                    />

                    <input
                      id="location"
                      name="location"
                      type="text"
                      value={formData.location}
                      onChange={handleChange}
                      placeholder="e.g. Arera Colony, Bhopal"
                      minLength={2}
                      maxLength={200}
                      autoComplete="street-address"
                      required
                    />
                  </div>
                </div>

                <div className="create-job-field">
                  <label htmlFor="budget">
                    Budget
                  </label>

                  <div className="create-job-input-wrap">
                    <IndianRupee
                      size={18}
                      aria-hidden="true"
                    />

                    <input
                      id="budget"
                      name="budget"
                      type="number"
                      value={formData.budget}
                      onChange={handleChange}
                      placeholder="e.g. 1500"
                      min="0.01"
                      step="0.01"
                      inputMode="decimal"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="create-job-actions">
                <button
                  type="button"
                  className="dashboard-secondary-button"
                  onClick={() => navigate('/dashboard')}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="dashboard-primary-button create-job-primary-button"
                  disabled={isSubmitting}
                >
                  <Send
                    size={17}
                    aria-hidden="true"
                  />

                  {isSubmitting
                    ? 'Posting...'
                    : 'Post Job'}
                </button>
              </div>
            </form>
          </section>

          <aside className="create-job-info">
            <div className="create-job-info-icon">
              <BriefcaseBusiness
                size={22}
                aria-hidden="true"
              />
            </div>

            <h2>Make the job clear</h2>

            <p>
              A good job gives workers enough context to
              understand what success looks like.
            </p>

            <div className="create-job-info-item">
              <strong>Clear outcome</strong>
              <span>
                Explain what should be delivered.
              </span>
            </div>

            <div className="create-job-info-item">
              <strong>Realistic budget</strong>
              <span>
                Set a budget that matches the work.
              </span>
            </div>

            <div className="create-job-info-item">
              <strong>Useful context</strong>
              <span>
                Mention location and important
                requirements.
              </span>
            </div>
          </aside>
        </div>
      </div>
    </main>
  )
}

export default CreateJobPage