/* ── Config ─────────────────────────────────────────────────────────────── */
// Change this to your deployed Render backend URL before hosting on Netlify
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : 'https://tempmail-backend-y1y6.onrender.com'   // ← update after deploying

/* ── State ──────────────────────────────────────────────────────────────── */
const state = {
  email: null,
  createdAt: null,
  messages: [],
  msgCount: 0,
  otpCount: 0,
};

/* ── DOM refs ───────────────────────────────────────────────────────────── */
const $ = id => document.getElementById(id);

const emailDisplay    = $('email-display');
const sidebarEmail    = $('sidebar-email');
const btnGenerate     = $('btn-generate');
const btnCopy         = $('btn-copy');
const btnRefresh      = $('btn-refresh');
const btnGetOtp       = $('btn-get-otp');
const generateStatus  = $('generate-status');
const infoCreated     = $('info-created');
const infoMsgs        = $('info-msgs');
const infoOtps        = $('info-otps');
const msgCount        = $('msg-count');
const messagesList    = $('messages-list');
const refreshIcon     = $('refresh-icon');
const otpValue        = $('otp-value');
const otpType         = $('otp-type');
const otpStatus       = $('otp-status');

/* ── Tabs ───────────────────────────────────────────────────────────────── */
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    $(`tab-${btn.dataset.tab}`).classList.add('active');
  });
});

/* ── Modal ──────────────────────────────────────────────────────────────── */
const overlay   = $('modal-overlay');
const modalClose = $('modal-close');
modalClose.addEventListener('click', closeModal);
overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });

function openModal(msg) {
  $('modal-sender').textContent  = `From: ${msg.sender}`;
  $('modal-subject').textContent = msg.subject || '(no subject)';
  $('modal-meta').textContent    = `Received: ${formatDate(msg.received_at)}`;
  $('modal-body').textContent    = msg.body || '(empty message body)';
  overlay.classList.add('open');
}

function closeModal() { overlay.classList.remove('open'); }

/* ── Helpers ────────────────────────────────────────────────────────────── */
function formatDate(ts) {
  if (!ts) return '—';
  const d = new Date(ts);
  return isNaN(d) ? ts : d.toLocaleString();
}

function setStatus(el, msg, type = '') {
  el.textContent = msg;
  el.className = 'status-bar ' + type;
}

async function apiFetch(path, method = 'GET') {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: method,
    headers: { 'Content-Type': 'application/json' },
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || 'Unknown error');
  }
  return resp.json();
}

/* ── Generate Email ─────────────────────────────────────────────────────── */
btnGenerate.addEventListener('click', async () => {
  btnGenerate.disabled = true;
  setStatus(generateStatus, '⟳ Generating…', '');

  try {
    const data = await apiFetch('/create-email', 'POST');
    state.email     = data.email;
    state.createdAt = data.created_at;
    state.messages  = [];
    state.msgCount  = 0;
    state.otpCount  = 0;

    emailDisplay.innerHTML = `<span class="email-ready">${data.email}</span>`;
    sidebarEmail.textContent = data.email;
    btnCopy.disabled = false;

    infoCreated.textContent = formatDate(data.created_at).split(',')[0];
    infoMsgs.textContent    = '0';
    infoOtps.textContent    = '0';

    otpValue.textContent = '—';
    otpValue.classList.remove('revealed');
    otpType.textContent  = '';

    messagesList.innerHTML = `<div class="empty-state"><div class="empty-icon">⊡</div><div>Inbox empty — refresh to check for messages</div></div>`;
    msgCount.textContent   = '0 messages';

    setStatus(generateStatus, `✓ ${data.email} created`, 'success');
  } catch (e) {
    setStatus(generateStatus, `✗ ${e.message}`, 'error');
  } finally {
    btnGenerate.disabled = false;
  }
});

/* ── Copy Email ─────────────────────────────────────────────────────────── */
btnCopy.addEventListener('click', () => {
  if (!state.email) return;
  navigator.clipboard.writeText(state.email).then(() => {
    btnCopy.querySelector('.btn-icon').textContent = '✓';
    setTimeout(() => btnCopy.querySelector('.btn-icon').textContent = '⊡', 1500);
  });
});

/* ── Refresh Inbox ──────────────────────────────────────────────────────── */
btnRefresh.addEventListener('click', async () => {
  if (!state.email) {
    alert('Generate an email first.');
    return;
  }

  btnRefresh.disabled = true;
  refreshIcon.classList.add('spinning');

  try {
    const data = await apiFetch(`/get-messages?email=${encodeURIComponent(state.email)}`);
    state.messages = data.messages || [];
    state.msgCount = data.count || 0;

    infoMsgs.textContent = state.msgCount;
    msgCount.textContent = `${state.msgCount} message${state.msgCount !== 1 ? 's' : ''}`;

    renderMessages();
  } catch (e) {
    messagesList.innerHTML = `<div class="empty-state"><div class="empty-icon">✗</div><div>${e.message}</div></div>`;
  } finally {
    btnRefresh.disabled = false;
    refreshIcon.classList.remove('spinning');
  }
});

function renderMessages() {
  if (!state.messages.length) {
    messagesList.innerHTML = `<div class="empty-state"><div class="empty-icon">⊡</div><div>No messages yet</div></div>`;
    return;
  }

  // Detect OTPs in messages for badge display
  const otpPattern = /\b(\d{4,8})\b/;

  messagesList.innerHTML = state.messages.map(msg => {
    const hasOtp = otpPattern.test(`${msg.subject} ${msg.body}`);
    const time   = formatDate(msg.received_at);

    return `
      <div class="msg-card" data-id="${msg.id}">
        <div>
          <div class="msg-sender">${escHtml(msg.sender || 'unknown')}</div>
          <div class="msg-subject">${escHtml(msg.subject || '(no subject)')}</div>
          ${hasOtp ? '<span class="otp-badge">OTP detected</span>' : ''}
        </div>
        <div class="msg-time">${time}</div>
      </div>
    `;
  }).join('');

  messagesList.querySelectorAll('.msg-card').forEach((card, i) => {
    card.addEventListener('click', () => openModal(state.messages[i]));
  });
}

/* ── Get OTP ────────────────────────────────────────────────────────────── */
btnGetOtp.addEventListener('click', async () => {
  if (!state.email) {
    setStatus(otpStatus, '✗ Generate an email first', 'error');
    return;
  }

  btnGetOtp.disabled = true;
  setStatus(otpStatus, '⟳ Fetching…', '');

  try {
    const data = await apiFetch(`/get-otp?email=${encodeURIComponent(state.email)}`);

    if (data.success) {
      otpValue.textContent = data.otp;
      otpValue.classList.add('revealed');
      otpType.textContent  = data.type ? `Type: ${data.type}` : '';
      state.otpCount++;
      infoOtps.textContent = state.otpCount;
      setStatus(otpStatus, `✓ Found at ${formatDate(data.created_at)}`, 'success');
    } else {
      otpValue.textContent = '—';
      otpValue.classList.remove('revealed');
      setStatus(otpStatus, data.message || 'No OTP found', '');
    }
  } catch (e) {
    setStatus(otpStatus, `✗ ${e.message}`, 'error');
  } finally {
    btnGetOtp.disabled = false;
  }
});

/* ── Util: escape HTML ──────────────────────────────────────────────────── */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
