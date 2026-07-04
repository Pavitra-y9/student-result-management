import { useEffect, useState } from 'react'
import './App.css'

const featureCards = [
  {
    id: '01',
    title: 'Landing Page',
    text: 'Clear headline, strong CTA, feature highlights, and a simple clean entry experience for new users.',
  },
  {
    id: '02',
    title: 'Authentication',
    text: 'Email/password login plus Google and GitHub OAuth with a lightweight onboarding flow.',
  },
  {
    id: '03',
    title: 'Dashboard',
    text: 'Daily challenge access, streak tracking, XP progress, and a fast overview of learning momentum.',
  },
]

const controlRows = [
  { label: 'Core challenge', value: 'Daily Bug Fix' },
  { label: 'Hint system', value: 'Instant assist' },
  { label: 'Feedback loop', value: 'Real-time results' },
]

const timeline = [
  {
    step: 'Learn',
    title: 'Start each day with one practical bug challenge',
    text: 'The platform keeps users engaged with focused debugging tasks that are short, repeatable, and skill-building.',
  },
  {
    step: 'Practice',
    title: 'Debug inside an editor built for experimentation',
    text: 'Users inspect buggy code, run it, submit fixes, and immediately understand what passed or failed.',
  },
  {
    step: 'Grow',
    title: 'Review explanations, track XP, and climb the leaderboard',
    text: 'Learning continues after submission through best practices, summaries, and visible progress.',
  },
]

const modules = [
  'Daily Bug Challenge',
  'Hint System',
  'Instant Feedback',
  'Progress Tracking',
  'OAuth Sign In',
  'Weekly Leaderboard',
]

const terminalLines = [
  'Loading daily challenge...',
  'Connecting editor session...',
  'Syncing streak progress...',
  'Leaderboard updated.',
]

const experiencePages = [
  {
    name: 'Code Editor Page',
    label: 'Practice',
    text: 'Monaco Editor, buggy code display, run and submit controls, and a test results panel.',
  },
  {
    name: 'Explanation Page',
    label: 'Review',
    text: 'Show the correct solution, explain the bug type, teach best practices, and summarize the lesson.',
  },
  {
    name: 'Leaderboard',
    label: 'Compete',
    text: 'Weekly rankings with optional participation so users stay motivated without pressure.',
  },
]

function RobotFace() {
  return (
    <div className="robot-shell" aria-hidden="true">
      <div className="robot-antenna" />
      <div className="robot-head">
        <div className="robot-eyes">
          <span />
          <span />
        </div>
        <div className="robot-mouth" />
      </div>
      <div className="robot-neck" />
      <div className="robot-body">
        <div className="robot-core" />
      </div>
      <div className="robot-shadow" />
    </div>
  )
}

function App() {
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    const updatePointer = (event) => {
      const { innerWidth, innerHeight } = window
      const x = (event.clientX / innerWidth - 0.5) * 2
      const y = (event.clientY / innerHeight - 0.5) * 2

      document.documentElement.style.setProperty('--pointer-x', x.toFixed(3))
      document.documentElement.style.setProperty('--pointer-y', y.toFixed(3))
    }

    window.addEventListener('pointermove', updatePointer)

    return () => window.removeEventListener('pointermove', updatePointer)
  }, [])

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setActiveIndex((current) => (current + 1) % featureCards.length)
    }, 3200)

    return () => window.clearInterval(intervalId)
  }, [])

  const activeFeature = featureCards[activeIndex]

  return (
    <main className="app-shell">
      <section className="hero-section">
        <header className="topbar">
          <div className="brand-lockup">
            <div className="brand-mark" />
            <span>FMC</span>
          </div>
          <nav className="topnav" aria-label="Primary">
            <a href="#experience">Experience</a>
            <a href="#systems">Systems</a>
            <a href="#pages">Pages</a>
            <a href="#launch">Launch</a>
          </nav>
          <a className="ghost-button" href="#launch">
            Book a demo
          </a>
        </header>

        <div className="hero-grid">
          <div className="hero-copy">
            <p className="eyebrow">Bug Fix Learning Platform</p>
            <h1>Build an FMC bug-fixing platform that feels focused, modern, and motivating.</h1>
            <p className="lede">
              This website is based on your PowerPoint structure: landing page,
              sign up and login, dashboard, code editor, explanation page, and
              leaderboard, all presented as one polished product experience.
            </p>

            <div className="hero-actions">
              <a className="primary-button" href="#experience">
                Explore the world
              </a>
              <a className="secondary-button" href="#systems">
                View control deck
              </a>
            </div>

            <div className="hero-metrics">
              <div>
                <strong>6</strong>
                <span>core product pages</span>
              </div>
              <div>
                <strong>1x</strong>
                <span>daily bug challenge</span>
              </div>
              <div>
                <strong>XP</strong>
                <span>progress motivation</span>
              </div>
            </div>

            <div className="signal-strip" aria-label="Live system updates">
              {terminalLines.map((line) => (
                <span key={line}>{line}</span>
              ))}
            </div>
          </div>

          <div className="hero-visual">
            <div className="orbital-stage">
              <div className="stage-glow stage-glow-a" />
              <div className="stage-glow stage-glow-b" />
              <div className="orbital-ring orbital-ring-a" />
              <div className="orbital-ring orbital-ring-b" />
              <div className="scan-column" />
              <div className="hex-grid" />
              <div className="target-beam" />
              <RobotFace />
              <article className="floating-card route-card">
                <span>User flow</span>
                <strong>Landing to Challenge Run</strong>
                <p>Sign in, open dashboard, launch the daily debugging task.</p>
              </article>
              <article className="floating-card status-card">
                <span>Main value</span>
                <strong>Learn by fixing real bugs</strong>
                <p>Short sessions, fast feedback, and practical coding repetition.</p>
              </article>
              <article className="floating-card pulse-card">
                <span>Featured page</span>
                <strong>{activeFeature.title}</strong>
                <p>{activeFeature.text}</p>
              </article>
              <article className="floating-card command-card">
                <span>Platform note</span>
                <strong>Designed for consistency and growth</strong>
                <p>Combine challenge flow, explanation, and gamification in one system.</p>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section className="logo-band" aria-label="Key capabilities">
        {modules.map((module) => (
          <span key={module}>{module}</span>
        ))}
      </section>

      <section className="feature-section" id="experience">
        <div className="section-heading">
          <p className="eyebrow">Experience Layer</p>
          <h2>The website follows the exact structure defined in the presentation.</h2>
          <p>
            Each major screen from the PowerPoint becomes a visible product
            module so stakeholders can understand the full flow at a glance.
          </p>
        </div>

        <div className="feature-grid">
          <div className="feature-stack">
            {featureCards.map((card, index) => (
              <button
                key={card.id}
                type="button"
                className={`feature-card ${index === activeIndex ? 'active' : ''}`}
                onClick={() => setActiveIndex(index)}
              >
                <span>{card.id}</span>
                <div>
                  <strong>{card.title}</strong>
                  <p>{card.text}</p>
                </div>
              </button>
            ))}
          </div>

          <div className="preview-panel">
            <div className="panel-toolbar">
              <span className="toolbar-dot" />
              <span className="toolbar-dot" />
              <span className="toolbar-dot" />
              <p>world-preview.exe</p>
            </div>
            <div className="preview-grid">
              <div className="preview-display">
                <div className="preview-hud">
                  <span>Flow 03</span>
                  <span>FMC flow map</span>
                </div>
                <div className="preview-surface">
                  <div className="preview-node preview-node-a" />
                  <div className="preview-node preview-node-b" />
                  <div className="preview-node preview-node-c" />
                  <div className="preview-path preview-path-a" />
                  <div className="preview-path preview-path-b" />
                </div>
              </div>
              <div className="preview-text">
                <p className="eyebrow">Selected system</p>
                <h3>{activeFeature.title}</h3>
                <p>{activeFeature.text}</p>
                <div className="mini-stats">
                  <div>
                    <strong>XP</strong>
                    <span>reward loop</span>
                  </div>
                  <div>
                    <strong>Run</strong>
                    <span>test feedback</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="systems-section" id="systems">
        <div className="systems-panel">
          <div className="section-heading compact">
            <p className="eyebrow">Systems Deck</p>
            <h2>Core product features from the deck are surfaced as the website’s main selling points.</h2>
          </div>

          <div className="control-grid">
            <div className="control-card large">
              <div className="control-header">
                <span>Feature overview</span>
                <strong>Daily engagement systems</strong>
              </div>
              <div className="bot-grid">
                <div className="mini-bot active" />
                <div className="mini-bot" />
                <div className="mini-bot active" />
                <div className="mini-bot" />
                <div className="mini-bot active" />
                <div className="mini-bot" />
              </div>
              <div className="spectrum-bar" aria-hidden="true">
                <span />
                <span />
                <span />
                <span />
                <span />
                <span />
                <span />
                <span />
              </div>
            </div>

            <div className="control-card">
              {controlRows.map((row) => (
                <div className="data-row" key={row.label}>
                  <span>{row.label}</span>
                  <strong>{row.value}</strong>
                </div>
              ))}
              <div className="mission-pill">Current objective: make debugging feel daily, rewarding, and easy to return to</div>
            </div>
          </div>
        </div>
      </section>

      <section className="journey-section" id="pages">
        <div className="section-heading">
          <p className="eyebrow">Product Pages</p>
          <h2>Three supporting pages complete the learning loop after login.</h2>
        </div>

        <div className="timeline">
          {experiencePages.map((item) => (
            <article className="timeline-card" key={item.name}>
              <span>{item.label}</span>
              <h3>{item.name}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="journey-section">
        <div className="section-heading">
          <p className="eyebrow">Learning Journey</p>
          <h2>From first visit to weekly ranking, the experience stays simple and purposeful.</h2>
        </div>

        <div className="timeline">
          {timeline.map((item) => (
            <article className="timeline-card" key={item.step}>
              <span>{item.step}</span>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="launch-section" id="launch">
        <div className="launch-card">
          <p className="eyebrow">Website Summary</p>
          <h2>FMC is positioned as a daily bug-fixing platform with clean onboarding, guided practice, and gamified progress.</h2>
          <p>
            The site now reflects the PowerPoint structure directly, so it can be
            expanded into real product pages, authentication flows, and a working
            coding challenge platform next.
          </p>
          <a className="primary-button" href="mailto:hello@fmc.dev">
            Start building FMC
          </a>
        </div>
      </section>
    </main>
  )
}

export default App
