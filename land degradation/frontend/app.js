import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js'
import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut, getIdToken } from 'https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js'

// Configure this for your Firebase project
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT",
  appId: "YOUR_APP_ID",
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const provider = new GoogleAuthProvider()

const userEmailEl = document.getElementById('userEmail')
const signInBtn = document.getElementById('signInBtn')
const signOutBtn = document.getElementById('signOutBtn')
const analyzeBtn = document.getElementById('analyzeBtn')
const agrometBtn = document.getElementById('agrometBtn')
const resultEl = document.getElementById('result')
const kpisEl = document.getElementById('kpis')
const projectsEl = document.getElementById('projects')

signInBtn.addEventListener('click', async () => {
  try {
    await signInWithPopup(auth, provider)
  } catch (e) {
    alert('Sign-in failed: ' + e.message)
  }
})

signOutBtn.addEventListener('click', async () => {
  await signOut(auth)
})

onAuthStateChanged(auth, async (user) => {
  if (user) {
    userEmailEl.textContent = user.email
    signInBtn.classList.add('hidden')
    signOutBtn.classList.remove('hidden')
    await loadProjects()
  } else {
    userEmailEl.textContent = 'Not signed in'
    signInBtn.classList.remove('hidden')
    signOutBtn.classList.add('hidden')
    projectsEl.innerHTML = ''
  }
})

async function authFetch(url, options = {}) {
  const user = auth.currentUser
  if (!user) throw new Error('Please sign in first')
  const token = await getIdToken(user, true)
  const headers = Object.assign({}, options.headers || {}, { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' })
  const res = await fetch(url, Object.assign({}, options, { headers }))
  if (!res.ok) {
    const t = await res.text()
    throw new Error('Request failed: ' + res.status + ' ' + t)
  }
  return res.json()
}

function getBackendBase() {
  // Point this to your Django backend host during dev/prod
  // Example: return 'http://127.0.0.1:8000'
  return ''
}

analyzeBtn.addEventListener('click', async () => {
  try {
    const payload = {
      location: document.getElementById('location').value,
      observations: document.getElementById('observations').value,
      goals: Array.from(document.getElementById('goals').selectedOptions).map(o => o.value),
      data: {
        ndvi: parseFloat(document.getElementById('ndvi').value || '0.36'),
        rainfall: parseFloat(document.getElementById('rainfall').value || '12.8'),
      }
    }
    const json = await authFetch(getBackendBase() + '/api/analyze', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    renderPlan(json.plan)
    await loadProjects()
  } catch (e) {
    alert(e.message)
  }
})

agrometBtn.addEventListener('click', async () => {
  try {
    const json = await authFetch(getBackendBase() + '/api/agromet')
    resultEl.textContent = JSON.stringify(json.agromet, null, 2)
  } catch (e) {
    alert(e.message)
  }
})

async function loadProjects() {
  try {
    const json = await authFetch(getBackendBase() + '/api/projects')
    projectsEl.innerHTML = ''
    for (const item of json.items) {
      const li = document.createElement('li')
      li.textContent = `${item.location} — ${item.createdAt}`
      projectsEl.appendChild(li)
    }
  } catch (e) {
    projectsEl.innerHTML = ''
  }
}

function renderPlan(plan) {
  resultEl.textContent = JSON.stringify(plan, null, 2)
  kpisEl.innerHTML = ''
  for (const k of plan.kpis || []) {
    const el = document.createElement('div')
    el.className = 'kpi'
    el.textContent = k
    kpisEl.appendChild(el)
  }
}
