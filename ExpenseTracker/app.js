const profiles = {
  software: {
    title: 'Software Developer',
    roadmap: [
      'Master Python or JavaScript fundamentals and practice daily coding.',
      'Learn data structures, arrays, strings, linked lists, stack, queue, and trees.',
      'Build 3 mini-projects: a to-do app, a calculator API, and a portfolio website.',
      'Practice SQL, Git, Docker basics, and deployment on Vercel or Render.'
    ],
    schedule: [
      'Day 1-7: Python/JavaScript basics, variables, loops, functions.',
      'Day 8-14: DSA practice with arrays, strings, and recursion.',
      'Day 15-21: Build a small full-stack project and deploy it.',
      'Day 22-30: Prepare for interviews, revise Git, and solve mock questions.'
    ],
    questions: [
      'Explain the difference between a list and a tuple.',
      'How do you reverse a string in Python?',
      'What is the difference between SQL and NoSQL?',
      'Why is version control important in a team project?'
    ],
    checklist: [
      'Professional GitHub profile with 3 projects',
      'One strong resume tailored for IT roles',
      'LinkedIn profile with a clear headline',
      'Mock interview answers for common questions'
    ]
  },
  data: {
    title: 'Data Analyst',
    roadmap: [
      'Strengthen Excel, SQL, and statistics basics.',
      'Learn Python for data cleaning, pandas, and visualization.',
      'Practice dashboard creation using Power BI or Tableau.',
      'Work on a small business analysis project with real sample data.'
    ],
    schedule: [
      'Day 1-7: Excel formulas, charts, and pivot tables.',
      'Day 8-14: SQL joins, subqueries, and data modeling.',
      'Day 15-21: Build charts and dashboards in Python or Power BI.',
      'Day 22-30: Create a portfolio case study and practice storytelling.'
    ],
    questions: [
      'What is the difference between data cleaning and data transformation?',
      'How do you handle missing values in a dataset?',
      'What is the difference between mean and median?',
      'How would you explain a dashboard insight to a non-technical person?'
    ],
    checklist: [
      'Portfolio dashboard with 2 case studies',
      'SQL query examples in GitHub',
      'Resume highlighting analytics projects',
      'Clear explanation of metrics and business impact'
    ]
  },
  embedded: {
    title: 'Embedded / IoT Engineer',
    roadmap: [
      'Improve C/C++, microcontroller basics, and embedded protocols.',
      'Learn UART, SPI, I2C, ADC, PWM, and interrupts.',
      'Build a simple sensor-based project with Arduino or ESP32.',
      'Understand basic Linux, networking, and IoT communication.'
    ],
    schedule: [
      'Day 1-7: C programming and debugging fundamentals.',
      'Day 8-14: Embedded peripherals and timing concepts.',
      'Day 15-21: Build a sensor interface project and document it.',
      'Day 22-30: Practice interview questions and prepare a GitHub demo.'
    ],
    questions: [
      'What is the difference between polling and interrupts?',
      'Why is memory optimization important in embedded systems?',
      'What is the role of a watchdog timer?',
      'How would you debug a sensor that gives unstable readings?'
    ],
    checklist: [
      'Working hardware project with photos and code',
      'Clear explanation of circuit and firmware logic',
      'Resume with embedded tools and protocols',
      'One short technical demo for interviews'
    ]
  },
  qa: {
    title: 'QA / Automation Engineer',
    roadmap: [
      'Learn testing concepts, test cases, bug life cycle, and regression testing.',
      'Practice manual testing with real sample apps and write clear reports.',
      'Learn automation basics with Selenium or Playwright.',
      'Build a mini test automation suite and document it.'
    ],
    schedule: [
      'Day 1-7: Testing fundamentals, SDLC, and bug tracking.',
      'Day 8-14: Write test cases for a sample website and report issues.',
      'Day 15-21: Automate a login or form flow using Selenium/Playwright.',
      'Day 22-30: Revise interviews, API testing basics, and GitHub portfolio.'
    ],
    questions: [
      'What is the difference between functional and non-functional testing?',
      'How do you report a bug effectively?',
      'What is regression testing?',
      'How do you test a login feature thoroughly?'
    ],
    checklist: [
      'Test cases and bug reports in a portfolio folder',
      'One automation script in GitHub',
      'Resume highlighting QA tools and methodologies',
      'Ability to explain a test strategy clearly'
    ]
  }
};

const roleSelect = document.getElementById('roleSelect');
const planBtn = document.getElementById('planBtn');
const roadmapEl = document.getElementById('roadmap');
const scheduleEl = document.getElementById('schedule');
const questionsEl = document.getElementById('questions');
const checklistEl = document.getElementById('checklist');

function renderProfile(role) {
  const profile = profiles[role];
  roadmapEl.innerHTML = profile.roadmap
    .map((item) => `<div class="item">${item}</div>`)
    .join('');

  scheduleEl.innerHTML = profile.schedule
    .map((item) => `<div class="day">${item}</div>`)
    .join('');

  questionsEl.innerHTML = profile.questions
    .map((item) => `<li>${item}</li>`)
    .join('');

  checklistEl.innerHTML = profile.checklist
    .map((item) => `<div class="item">${item}</div>`)
    .join('');

  const title = document.querySelector('.hero h1');
  title.textContent = `Turn your engineering background into a strong ${profile.title.toLowerCase()} career launchpad.`;
}

function loadSavedRole() {
  const savedRole = localStorage.getItem('eee-it-role') || 'software';
  roleSelect.value = savedRole;
  renderProfile(savedRole);
}

planBtn.addEventListener('click', () => {
  const role = roleSelect.value;
  localStorage.setItem('eee-it-role', role);
  renderProfile(role);
});

roleSelect.addEventListener('change', () => {
  const role = roleSelect.value;
  localStorage.setItem('eee-it-role', role);
  renderProfile(role);
});

loadSavedRole();
