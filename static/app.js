/* ══ TrackShield AI • Frontend Controller ══ */

let state = { summary: {}, scams: [], columns: { applied:[], interview:[], offer:[], rejected:[] }, applications: [], raw_emails: [] };
let currentDate = "2026-10-24";

// Fallback offline dataset (Rule 06: no network needed)
const OFFLINE = {
  summary: { total_emails_analyzed:20, scams_blocked:5, active_applications:14, follow_ups_due:4, interview_count:3, offer_count:2, rejected_count:3, applied_count:6 },
  scams: [
    { id:2, company:"Infosys", role:"Systems Associate", date:"2026-10-14", from:"hr.infosys.jobs@gmail.com", subject:"Offer letter - pay Rs 4,999 training fee", body:"Dear Candidate,\n\nYou have been selected for the position of Systems Associate at Infosys Technologies without examination based on your profile. To secure your corporate training batch slot and company laptop, please pay the mandatory refundable training fee of Rs 4,999 via UPI to info.batch@upi.\n\nAlso send high-resolution photos of your original Aadhaar card and PAN card to confirm your background verification.\n\nRegards,\nInfosys Recruitment Cell", scam_reasons:["Domain spoofing: Free-mail @gmail.com impersonating Infosys","Demands upfront refundable training fee of Rs 4,999","Sensitive identity harvesting (Aadhaar & PAN card requested via email)","Unsolicited offer without interview or examination"], confidence:0.99 },
    { id:16, company:"Tech Mahindra", role:"Junior Software Trainee", date:"2026-10-17", from:"hr-onboarding@techmahindra-careers.co", subject:"Provisional Selection Offer: Junior Software Trainee - Refundable Security & Training Fee", body:"Dear Candidate,\n\nCongratulations! Based on your resume uploaded on online job boards, you have been selected for direct joining as Junior Software Trainee at Tech Mahindra. Package offered: Rs 6.8 LPA.\n\nTo confirm your seat in the corporate induction batch starting Monday, deposit Rs 6,500 refundable security and documentation charge to UPI ID tm-onboard@icici today before 5:00 PM. Failure to pay will cancel your appointment.\n\nCorporate HR Desk,\nTech Mahindra Careers Portal", scam_reasons:["Lookalike domain spoofing: techmahindra-careers.co impersonating official techmahindra.com","Demands upfront refundable security & training fee of Rs 6,500 via UPI","High-pressure deadline to pay before 5:00 PM today or forfeit offer","Guaranteed selection without any interview or assessment"], confidence:0.99 },
    { id:17, company:"Apex Global Hiring", role:"Remote Operations Analyst", date:"2026-10-13", from:"verify-documents@apex-hiring.net", subject:"Immediate Employment: Submit Aadhaar Card and PAN Card for Payroll Verification", body:"Dear Applicant,\n\nWe are pleased to select you for the Remote Operations Analyst role at Rs 75,000 monthly stipend. No prior interview needed.\n\nFor immediate issuance of your offer letter and payroll setup, you must reply immediately to this email attaching high-resolution scanned copies of your Aadhaar Card (both sides), PAN Card, and your internet banking cancelled cheque. Documents must be submitted within 24 hours.\n\nYours sincerely,\nApex Global Hiring", scam_reasons:["Identity theft / document harvesting: Requests unencrypted Aadhaar, PAN, and cancelled cheque via email reply","Unrealistic salary (Rs 75,000/mo) for entry-level remote operations with 'no prior interview needed'","High-risk arbitrary 24-hour urgency deadline"], confidence:0.98 },
    { id:18, company:"CloudScale Analytics", role:"Remote Cloud Associate", date:"2026-10-19", from:"talent-outreach@cloudscale.io", subject:"Urgent Interview Invitation: Remote Cloud Associate (Chat on Telegram)", body:"Hello Alex,\n\nYour profile has been shortlisted for the Remote Cloud Associate role ($45/hr). Our VP of Engineering Mr. Andrew is conducting preliminary text interviews exclusively over Telegram today.\n\nPlease install Telegram Messenger immediately and text our lead recruiter @CloudScale_HR_Interviews with interview invitation code #CS-8921 to begin your chat assessment right now.\n\nRegards,\nCloudScale Talent Outreach", scam_reasons:["Redirects candidate interview to anonymous off-platform Telegram channel (@CloudScale_HR_Interviews)","Vague hiring claims with urgent text-only screening by executive","Inflated hourly rate without verified credentials"], confidence:0.96 },
    { id:19, company:"Tata Consultancy Services (TCS)", role:"Associate Software Engineer", date:"2026-10-15", from:"hr@tcs-careers-portal.com", subject:"TCS Expedited Joining Letter - Gate Pass & Verification Charge", body:"Dear Candidate,\n\nTata Consultancy Services (TCS) announces your provisional selection as Associate Software Engineer. Please review your appointment terms.\n\nYou are instructed to deposit Rs 3,500 towards mandatory security badge and gate pass issuance at the TCS campus. The payment should be made to our treasury account via IMPS/UPI. Your joining letter will be released immediately upon receipt.\n\nTCS NextStep Recruitment Directorate", scam_reasons:["Typosquatting/Lookalike domain: tcs-careers-portal.com mimicking legitimate tcs.com","Demands Rs 3,500 advance payment for security badge and campus gate pass","Immediate joining letter contingent on advance fee transfer"], confidence:0.99 }
  ]
};

/* ── Init ── */
document.addEventListener("DOMContentLoaded", () => {
  setupNav();
  setupDateControls();
  document.getElementById("btnRunPipeline").addEventListener("click", () => loadPipeline(currentDate));
  document.getElementById("btnViewInbox").addEventListener("click", openInboxModal);
  document.getElementById("btnSandboxTest").addEventListener("click", runSandbox);
  document.getElementById("btnCopyDraft").addEventListener("click", copyDraft);
  loadPipeline(currentDate);
});

/* ── Navigation ── */
function setupNav() {
  document.querySelectorAll(".nav-tab").forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });
}

function switchTab(name) {
  document.querySelectorAll(".nav-tab").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.toggle("active", p.id === `tab-${name}`));
}
window.switchTab = switchTab;

/* ── Date Sim ── */
function setupDateControls() {
  document.getElementById("inputTodayDate").addEventListener("change", e => {
    currentDate = e.target.value;
    document.querySelectorAll(".preset-pill").forEach(b => b.classList.remove("active"));
    loadPipeline(currentDate);
  });
  document.querySelectorAll(".preset-pill").forEach(btn => {
    btn.addEventListener("click", () => {
      currentDate = btn.dataset.date;
      document.getElementById("inputTodayDate").value = currentDate;
      document.querySelectorAll(".preset-pill").forEach(b => b.classList.toggle("active", b === btn));
      loadPipeline(currentDate);
    });
  });
}

/* ── Pipeline Loader ── */
async function loadPipeline(date) {
  const icon = document.getElementById("refreshIcon");
  icon.classList.add("spin");
  try {
    const r = await fetch(`/api/pipeline?today=${date}`);
    if (!r.ok) throw new Error("API fail");
    state = await r.json();
  } catch {
    state = { ...OFFLINE };
    recalcFollowups(date);
  } finally {
    icon.classList.remove("spin");
    render();
  }
}

function recalcFollowups(date) {
  // Rough client-side follow-up recalc for offline fallback
  const today = new Date(date);
  if (!state.columns) return;
  let count = 0;
  (state.columns.applied || []).forEach(a => {
    const d = new Date(a.last_email_date || "2026-10-10");
    const days = Math.floor((today - d) / 86400000);
    a.days_since_last_email = Math.max(0, days);
    a.follow_up_due = days >= 7;
    if (a.follow_up_due) count++;
  });
  if (state.summary) state.summary.follow_ups_due = count;
}

/* ── Render All ── */
function render() {
  const s = state.summary || {};
  const cols = state.columns || {};

  // Metrics
  setText("statEmails",   s.total_emails_analyzed || 20);
  setText("statScams",    s.scams_blocked || 5);
  setText("statFollowups",s.follow_ups_due || 4);
  setText("statActive",   s.active_applications || 14);

  // Tab badges
  setText("tabCountTracker",  s.active_applications || 14);
  setText("tabCountScams",    s.scams_blocked || 5);
  setText("tabCountFollowups",s.follow_ups_due || 4);

  // Snapshot
  setText("snapApplied",  (cols.applied   || []).length);
  setText("snapInterview",(cols.interview || []).length);
  setText("snapOffer",    (cols.offer     || []).length);
  setText("snapRejected", (cols.rejected  || []).length);

  // Hero
  setText("heroEmailCount", `${s.total_emails_analyzed || 20} emails`);

  // Scam pill
  setText("scamPillCount", `${s.scams_blocked || 5} threats blocked`);

  // Column counts
  setText("countApplied",  (cols.applied   || []).length);
  setText("countInterview",(cols.interview || []).length);
  setText("countOffer",    (cols.offer     || []).length);
  setText("countRejected", (cols.rejected  || []).length);

  renderKanban(cols);
  renderScams(state.scams || OFFLINE.scams);
  renderFollowups(cols.applied || []);
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

/* ── Kanban ── */
function renderKanban(cols) {
  renderCol("colApplied",   cols.applied   || [], renderAppliedCard);
  renderCol("colInterview", cols.interview || [], renderInterviewCard);
  renderCol("colOffer",     cols.offer     || [], renderOfferCard);
  renderCol("colRejected",  cols.rejected  || [], renderRejectedCard);
}

function renderCol(id, items, cardFn) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = items.map(cardFn).join("") || `<p style="color:var(--text-3);font-size:12px;padding:8px;">Nothing here yet.</p>`;
}

function renderAppliedCard(app) {
  const days = app.days_since_last_email || 0;
  const overdue = app.follow_up_due;
  const chip = overdue
    ? `<div class="chip chip-amber"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Follow up due (${days}d)</div>`
    : `<div class="k-card-date">Applied ${app.first_date || app.last_email_date} &nbsp;·&nbsp; ${days} days ago</div>`;
  const actions = overdue
    ? `<div class="k-card-actions">
        <button class="k-btn k-btn-amber" onclick='openFollowupModal(${safeJson(app)})'>Draft Email</button>
        <button class="k-btn" onclick='openTimelineModal(${safeJson(app)})'>History (${app.email_count || 1})</button>
       </div>`
    : `<div class="k-card-actions"><button class="k-btn" onclick='openTimelineModal(${safeJson(app)})'>View Email</button></div>`;
  return `<div class="k-card"><div class="k-card-company">${esc(app.company)}</div><div class="k-card-role">${esc(app.role)}</div>${chip}${actions}</div>`;
}

function renderInterviewCard(app) {
  const merged = (app.email_count || 1) > 1
    ? `<div class="chip chip-blue"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 3h5v5M4 20L21 3"/></svg>2 emails merged</div>` : "";
  const idate = app.interview_date
    ? `<div class="chip chip-purple"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="4" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>${app.interview_date}</div>` : "";
  return `<div class="k-card">
    <div class="k-card-company">${esc(app.company)}</div>
    <div class="k-card-role">${esc(app.role)}</div>
    ${idate}${merged}
    <div class="k-card-actions">
      <button class="k-btn k-btn-purple" onclick='openPrepModal(${safeJson(app)})'>Prep Notes</button>
      <button class="k-btn" onclick='openTimelineModal(${safeJson(app)})'>History (${app.email_count || 1})</button>
    </div>
  </div>`;
}

function renderOfferCard(app) {
  return `<div class="k-card">
    <div class="k-card-company">${esc(app.company)}</div>
    <div class="k-card-role">${esc(app.role)}</div>
    <div class="chip chip-green"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Genuine offer verified</div>
    <div class="k-card-date">Received ${app.last_email_date}</div>
    <div class="k-card-actions"><button class="k-btn" onclick='openTimelineModal(${safeJson(app)})'>View Offer</button></div>
  </div>`;
}

function renderRejectedCard(app) {
  return `<div class="k-card">
    <div class="k-card-company">${esc(app.company)}</div>
    <div class="k-card-role">${esc(app.role)}</div>
    <div class="k-card-date">Decision on ${app.last_email_date}</div>
    <div class="k-card-actions"><button class="k-btn" onclick='openTimelineModal(${safeJson(app)})'>View Email</button></div>
  </div>`;
}

/* ── Scam Shield ── */
function renderScams(scams) {
  const el = document.getElementById("scamList");
  if (!el) return;
  if (!scams || scams.length === 0) { el.innerHTML = `<p style="color:var(--text-2)">No scams detected.</p>`; return; }
  el.innerHTML = scams.map(s => {
    const reasons = (s.scam_reasons || []).map(r =>
      `<div class="scam-reason"><div class="scam-reason-dot"></div><span>${esc(r)}</span></div>`
    ).join("");
    return `<div class="scam-row-card">
      <span class="scam-blocked-badge">Blocked</span>
      <div class="scam-row-main">
        <div class="scam-row-company">${esc(s.company)}</div>
        <div class="scam-row-role">${esc(s.role)}</div>
        <div class="scam-row-sender">${esc(s.from)}</div>
        <div class="scam-reason-list">${reasons}</div>
      </div>
      <div class="scam-row-meta">
        <span class="scam-conf">${Math.round((s.confidence||.98)*100)}% conf</span>
        <span class="scam-date">${s.date}</span>
        <button class="btn-inspect" onclick="openEmailInspect(${s.id})">Inspect</button>
      </div>
    </div>`;
  }).join("");
}

/* ── Follow-Ups ── */
function renderFollowups(applied) {
  const overdue = applied.filter(a => a.follow_up_due);
  const list = document.getElementById("followupList");
  const none = document.getElementById("noFollowups");
  if (!list || !none) return;
  if (overdue.length === 0) { list.innerHTML = ""; none.style.display = "flex"; return; }
  none.style.display = "none";
  list.innerHTML = overdue.map(a => `
    <div class="fu-card" onclick='openFollowupModal(${safeJson(a)})'>
      <div class="fu-icon-wrap">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      </div>
      <div class="fu-main">
        <div class="fu-company">${esc(a.company)}</div>
        <div class="fu-role">${esc(a.role)}</div>
        <div class="fu-days">${a.days_since_last_email} days without reply</div>
      </div>
      <div class="fu-action-hint">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m22 2-7 20-4-9-9-4Z"/></svg>
        Click to draft follow up
      </div>
    </div>`).join("");
}

/* ── Modals ── */
window.openFollowupModal = function(app) {
  document.getElementById("fuModalTitle").textContent = `${app.company} • ${app.role}`;
  document.getElementById("fuCompany").textContent = app.company;
  document.getElementById("fuDays").textContent = `${app.days_since_last_email || 7} days`;
  const draft = app.follow_up_draft || {
    subject: `Following up: ${app.role} | Alex Chen`,
    body: `Hi ${app.company} Hiring Team,\n\nI hope you're well. I wanted to follow up on the ${app.role} position I applied for on ${app.first_date || app.last_email_date}. I remain very enthusiastic about the opportunity.\n\nPlease let me know if you need any additional information from my end.\n\nThank you,\nAlex Chen`
  };
  document.getElementById("fuSubject").value = draft.subject;
  document.getElementById("fuBody").value = draft.body;
  openModal("modalFollowup");
};

function copyDraft() {
  const s = document.getElementById("fuSubject").value;
  const b = document.getElementById("fuBody").value;
  navigator.clipboard.writeText(`Subject: ${s}\n\n${b}`).then(() => {
    const t = document.getElementById("copyToast");
    t.classList.add("show");
    setTimeout(() => t.classList.remove("show"), 2500);
  });
}

window.openPrepModal = async function(app) {
  document.getElementById("prepModalTitle").textContent = `${app.company} • ${app.role}`;
  document.getElementById("prepModalBody").innerHTML = `<p style="color:var(--text-2);padding:20px 0;">Loading prep notes...</p>`;
  openModal("modalPrep");
  try {
    let prep = app.interview_prep;
    if (!prep) {
      const r = await fetch(`/api/prep?company=${encodeURIComponent(app.company)}&role=${encodeURIComponent(app.role)}`);
      prep = await r.json();
    }
    renderPrepModal(prep);
  } catch { document.getElementById("prepModalBody").innerHTML = `<p style="color:var(--red)">Failed to load prep notes.</p>`; }
};

function renderPrepModal(prep) {
  const pills = (prep.tech_focus || []).map(t => `<span class="prep-pill">${esc(t)}</span>`).join("");
  const qs = (prep.key_questions || []).map(q => `
    <div class="prep-q">
      <div class="prep-q-text">${esc(q.question)}</div>
      <div class="prep-q-tip"><strong>Tip:</strong> ${esc(q.answer_tip)}</div>
    </div>`).join("");
  const sqs = (prep.smart_questions_to_ask || []).map(q =>
    `<div class="prep-smart-q"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>${esc(q)}</div>`
  ).join("");

  document.getElementById("prepModalBody").innerHTML = `
    <div class="prep-brief-section">
      <div class="prep-section-label">Company Brief</div>
      <p style="font-size:13px;color:var(--text-2);line-height:1.6">${esc(prep.company_brief || "")}</p>
    </div>
    <div class="prep-brief-section">
      <div class="prep-section-label">Core Technical Focus Areas</div>
      <div class="prep-pills">${pills}</div>
    </div>
    <div class="prep-brief-section">
      <div class="prep-section-label">Key Questions & Answer Frameworks</div>
      ${qs}
    </div>
    <div class="prep-brief-section">
      <div class="prep-section-label">Questions to Ask the Interviewer</div>
      ${sqs}
    </div>`;
}

window.openTimelineModal = function(app) {
  document.getElementById("emailModalTitle").textContent = `${app.company} • ${app.role}`;
  const timeline = app.timeline || [];
  document.getElementById("emailModalBody").innerHTML = `
    <p style="font-size:13px;color:var(--text-2);margin-bottom:14px;">
      ${timeline.length > 1 ? `<strong>${timeline.length} emails merged</strong> • Status resolved to <strong>${app.status.toUpperCase()}</strong>` : `Status: <strong>${(app.status||"").toUpperCase()}</strong>`}
    </p>
    ${timeline.map((e, i) => `
      <div class="email-event-card">
        <div class="email-event-meta"><span>Email ${i+1} • ${(e.status_signal||"").toUpperCase()}</span><span>${e.date}</span></div>
        <div class="email-event-subject">${esc(e.subject)}</div>
        <div class="email-event-from">${esc(e.from)}</div>
        <div class="email-event-body">${esc(e.body || "")}</div>
      </div>`).join("")}`;
  openModal("modalEmail");
};

window.openEmailInspect = function(id) {
  const emails = [...(state.raw_emails || []), ...(state.scams || OFFLINE.scams)];
  const email = emails.find(e => e.id === id);
  if (!email) return;
  document.getElementById("emailModalTitle").textContent = `Email #${id}`;
  document.getElementById("emailModalBody").innerHTML = `
    <div class="email-event-card">
      <div class="email-event-meta"><span>Date: ${email.date}</span></div>
      <div class="email-event-subject">${esc(email.subject)}</div>
      <div class="email-event-from" style="color:var(--red)">${esc(email.from)}</div>
      <div class="email-event-body">${esc(email.body || "")}</div>
    </div>`;
  openModal("modalEmail");
};

async function openInboxModal() {
  document.getElementById("inboxTbody").innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-2)">Loading...</td></tr>`;
  openModal("modalInbox");
  let emails = state.raw_emails;
  if (!emails || !emails.length) {
    try { const r = await fetch("/api/inbox"); emails = (await r.json()).emails; } catch {}
  }
  if (!emails || !emails.length) { document.getElementById("inboxTbody").innerHTML = `<tr><td colspan="5">No data</td></tr>`; return; }
  document.getElementById("inboxTbody").innerHTML = emails.map(e =>
    `<tr><td><strong>#${e.id}</strong></td><td>${e.date}</td><td>${esc(e.from)}</td><td>${esc(e.subject)}</td><td><button class="tbl-view-btn" onclick="openEmailInspect(${e.id})">View</button></td></tr>`
  ).join("");
}

/* ── Sandbox Classifier ── */
async function runSandbox() {
  const btn = document.getElementById("btnSandboxTest");
  const resultEl = document.getElementById("sandboxResult");
  btn.textContent = "Analyzing...";
  btn.disabled = true;
  resultEl.style.display = "none";
  try {
    const payload = { id:999, from:document.getElementById("sbFrom").value, subject:document.getElementById("sbSubject").value, body:document.getElementById("sbBody").value };
    const r = await fetch("/api/inbox/test_classify", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
    const data = await r.json();
    const cl = data.classification || {};
    const isScam = cl.status === "scam";
    const col = isScam ? "var(--red)" : cl.status === "interview" ? "var(--purple)" : cl.status === "offer" ? "var(--green)" : "var(--blue)";
    const reasons = cl.scam_reasons && cl.scam_reasons.length
      ? `<div style="margin-top:10px">${cl.scam_reasons.map(r => `<div style="font-size:12px;color:#fca5a5;margin-bottom:3px">• ${esc(r)}</div>`).join("")}</div>` : "";
    resultEl.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="font-weight:700;font-size:15px;color:${col}">${cl.status?.toUpperCase()}</span>
        <span style="font-size:12px;color:var(--text-2)">${Math.round((cl.confidence||.9)*100)}% confidence</span>
      </div>
      <div style="font-size:13px;margin-bottom:2px"><strong>Company:</strong> ${esc(cl.company||"N/A")}</div>
      <div style="font-size:13px"><strong>Role:</strong> ${esc(cl.role||"N/A")}</div>
      ${reasons}`;
    resultEl.style.display = "block";
  } catch (e) {
    resultEl.innerHTML = `<span style="color:var(--red)">Error: ${e.message}</span>`;
    resultEl.style.display = "block";
  } finally {
    btn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> Analyze with Gemini`;
    btn.disabled = false;
  }
}

/* ── Helpers ── */
function openModal(id) { document.getElementById(id).classList.add("open"); }
window.closeModal = function(id) { document.getElementById(id).classList.remove("open"); };

// Close modal on backdrop click
document.querySelectorAll(".modal-overlay").forEach(m => {
  m.addEventListener("click", e => { if (e.target === m) m.classList.remove("open"); });
});

function esc(s) {
  if (!s) return "";
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;");
}

function safeJson(obj) {
  return JSON.stringify(obj).replace(/'/g, "&#39;").replace(/"/g, "&quot;");
}
