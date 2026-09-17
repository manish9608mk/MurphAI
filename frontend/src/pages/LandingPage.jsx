import { ArrowRight, BriefcaseBusiness, ShieldCheck, Users } from 'lucide-react'
import { Link } from 'react-router-dom'

function LandingPage() {
  return (
    <main className="landing">
      <nav className="navbar">
        <Link to="/" className="brand">
          MurphAI
        </Link>

        <div className="nav-actions">
          <Link to="/login" className="nav-link">
            Sign in
          </Link>

          <Link to="/register" className="button button-primary">
            Get started
          </Link>
        </div>
      </nav>

      <section className="hero-section">
        <div className="hero-content">
          <span className="eyebrow">REAL WORK. VERIFIED REPUTATION.</span>

          <h1>
            Get work done.
            <br />
            Build trust that lasts.
          </h1>

          <p className="hero-description">
            MurphAI connects customers with workers and turns completed work
            into a verified professional reputation.
          </p>

          <div className="hero-actions">
            <Link to="/register" className="button button-primary">
              Get started
              <ArrowRight size={18} />
            </Link>

            <Link to="/register" className="button button-secondary">
              I’m a worker
            </Link>
          </div>
        </div>
      </section>

      <section className="value-section">
        <div className="section-heading">
          <span className="eyebrow">HOW IT WORKS</span>
          <h2>One workflow. One trusted history.</h2>
          <p>
            From the first job request to completed work and reputation,
            MurphAI keeps the workflow connected.
          </p>
        </div>

        <div className="value-grid">
          <article className="value-card">
            <BriefcaseBusiness size={28} />
            <h3>Post real work</h3>
            <p>
              Customers create jobs with the details workers need to get the
              work done.
            </p>
          </article>

          <article className="value-card">
            <Users size={28} />
            <h3>Work with the right people</h3>
            <p>
              Worker profiles, skills, experience and matching intelligence
              support better assignments.
            </p>
          </article>

          <article className="value-card">
            <ShieldCheck size={28} />
            <h3>Build verified trust</h3>
            <p>
              Completed work, confirmation, payment and reputation become part
              of a worker’s history.
            </p>
          </article>
        </div>
      </section>

      <section className="workflow-section">
        <div className="section-heading">
          <span className="eyebrow">THE MURPHAI LOOP</span>
          <h2>Work becomes reputation.</h2>
        </div>

        <div className="workflow">
          {[
            'Job',
            'Assignment',
            'Work',
            'Evidence',
            'Confirmation',
            'Payment',
            'Reputation',
          ].map((step, index) => (
            <div className="workflow-step" key={step}>
              <span>{index + 1}</span>
              <strong>{step}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="cta-section">
        <div>
          <span className="eyebrow">START WITH ONE JOB</span>
          <h2>Ready to build your verified work history?</h2>
          <p>
            Join MurphAI and turn completed work into something you can build
            on.
          </p>
        </div>

        <Link to="/register" className="button button-primary">
          Create your account
          <ArrowRight size={18} />
        </Link>
      </section>

      <footer className="footer">
        <span>© 2026 MurphAI</span>
        <span>Real work. Verified reputation.</span>
      </footer>
    </main>
  )
}

export default LandingPage