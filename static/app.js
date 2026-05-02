// ============================================================
// app.js — Frontend interactivity for Resume Matcher
// ============================================================
// Responsibilities:
//   1. Show selected filenames below the upload zone
//   2. Drag-and-drop visual feedback on the upload zone
//   3. Disable the submit button + show spinner on submit
//   4. Basic client-side validation before sending the form
//
// NO data processing happens here — all ML logic is in Python.
// This file purely improves the user experience.
// ============================================================


// ── Grab DOM elements ────────────────────────────────────────
const form       = document.getElementById('match-form');
const fileInput  = document.getElementById('resumes');
const fileList   = document.getElementById('file-list');
const fileCount  = document.getElementById('file-count');
const uploadZone = document.getElementById('upload-zone');
const submitBtn  = document.getElementById('submit-btn');
const btnText    = submitBtn.querySelector('.btn-text');
const spinner    = document.getElementById('spinner');


// ── 1. Show selected filenames ────────────────────────────────
//
// When a user picks files, the browser fires a 'change' event
// on the <input type="file">. We read input.files (a FileList
// object) and build a visual list below the upload zone.

fileInput.addEventListener('change', () => {
  renderFileList(fileInput.files);
});

function renderFileList(files) {
  // Clear previous list
  fileList.innerHTML = '';

  if (!files || files.length === 0) {
    fileCount.textContent = 'No files selected';
    return;
  }

  fileCount.textContent = `${files.length} file${files.length > 1 ? 's' : ''} selected`;

  // Build one <li> per file
  Array.from(files).forEach(file => {
    const li = document.createElement('li');
    li.textContent = file.name;

    // Show file size in a muted span
    const size = document.createElement('span');
    size.style.cssText = 'margin-left:auto; opacity:0.45; font-size:0.72rem;';
    size.textContent = formatBytes(file.size);
    li.appendChild(size);

    fileList.appendChild(li);
  });
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}


// ── 2. Drag-and-drop visual feedback ─────────────────────────
//
// The hidden <input> already handles the actual file drop.
// We just add/remove a CSS class to give visual feedback
// when files are dragged over the upload zone.

uploadZone.addEventListener('dragover', e => {
  // Prevent browser from opening the file (default behaviour)
  e.preventDefault();
  uploadZone.classList.add('dragging');
});

uploadZone.addEventListener('dragleave', () => {
  uploadZone.classList.remove('dragging');
});

uploadZone.addEventListener('drop', () => {
  // The input's change event fires automatically after drop,
  // so renderFileList() is called from there.
  uploadZone.classList.remove('dragging');
});


// ── 3. Submit button — spinner + disable ─────────────────────
//
// When the form submits, we:
//   a. Run client-side validation first
//   b. Show a spinner so the user knows something is happening
//      (sentence-transformer inference takes 1-3 seconds)
//   c. Disable the button to prevent double-submission

form.addEventListener('submit', e => {
  const jd      = document.getElementById('job_description').value.trim();
  const files   = fileInput.files;

  // Client-side guard — the server validates too, but this
  // gives instant feedback without a round-trip.
  if (!jd) {
    e.preventDefault();
    showInlineError('Please enter a job description.');
    return;
  }

  if (!files || files.length === 0) {
    e.preventDefault();
    showInlineError('Please select at least one resume file.');
    return;
  }

  // All good — show loading state
  setLoading(true);
  // Note: we do NOT call e.preventDefault() here, so the form
  // submits normally as a standard HTML POST request.
});

function setLoading(on) {
  submitBtn.disabled = on;
  btnText.hidden     = on;
  spinner.hidden     = !on;
}

function showInlineError(msg) {
  // Remove any previous inline error
  const prev = form.querySelector('.inline-error');
  if (prev) prev.remove();

  const div = document.createElement('div');
  div.className = 'alert alert-error inline-error';
  div.style.marginBottom = '1rem';
  div.textContent = msg;
  submitBtn.before(div);

  // Auto-remove after 4 seconds
  setTimeout(() => div.remove(), 4000);
}


// ── 4. Reset loading state if user navigates back ────────────
//
// In some browsers, hitting the back button restores the page
// from cache with the button still disabled. pageshow fires
// on back-navigation and lets us reset it.

window.addEventListener('pageshow', () => {
  setLoading(false);
});