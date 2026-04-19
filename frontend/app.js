const API_URL = 'http://localhost:8000';
let selectedLength = 'medium';

function selectLength(length) {
  selectedLength = length;
  document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
  document.querySelector(`[data-length="${length}"]`).classList.add('active');
}

function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

function setStep(n, status) {
  const step = document.getElementById(`step${n}`);
  if (!step) return;
  step.className = 'step ' + status;
}

function resetForm() {
  hide('outputSection');
  hide('progressSection');
  show('formSection');
  document.getElementById('topicInput').value = '';
  document.getElementById('audienceInput').value = '';
  for (let i = 1; i <= 9; i++) setStep(i, '');
}

async function generateBlog() {
  const topic = document.getElementById('topicInput').value.trim();
  const audience = document.getElementById('audienceInput').value.trim();

  if (!topic) {
    document.getElementById('topicInput').focus();
    document.getElementById('topicInput').style.borderColor = '#ef4444';
    setTimeout(() => document.getElementById('topicInput').style.borderColor = '', 2000);
    return;
  }

  const btn = document.getElementById('generateBtn');
  btn.disabled = true;
  document.getElementById('btnText').textContent = 'Generating...';

  hide('formSection');
  show('progressSection');

  // Animate steps while waiting
  const stepTimings = [0, 3000, 6000, 12000, 15000, 30000, 50000, 60000, 65000];
  stepTimings.forEach((delay, i) => {
    setTimeout(() => {
      if (i > 0) setStep(i, 'done');
      setStep(i + 1, 'active');
    }, delay);
  });

  try {
    const response = await fetch(`${API_URL}/generate-blog`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, audience: audience || 'general readers', length: selectedLength })
    });

    if (!response.ok) throw new Error('API error');
    const data = await response.json();

    for (let i = 1; i <= 9; i++) setStep(i, 'done');

    setTimeout(() => {
      hide('progressSection');
      renderOutput(data);
      show('outputSection');
    }, 800);

  } catch (err) {
    hide('progressSection');
    show('formSection');
    btn.disabled = false;
    document.getElementById('btnText').textContent = 'Generate Blog';
    alert('Something went wrong. Make sure the API server is running.');
  }
}

function renderOutput(data) {
  renderScore(data.scores);
  renderBlog(data);
}

function renderScore(scores) {
  const overall = parseFloat(scores['Overall Score']) || 0;
  const dims = [
    { key: 'Readability', label: 'Read' },
    { key: 'Hook Strength', label: 'Hook' },
    { key: 'Content Depth', label: 'Depth' },
    { key: 'SEO Strength', label: 'SEO' },
    { key: 'Conclusion Quality', label: 'End' },
  ];

  const barsHtml = dims.map(d => {
    const val = parseFloat(scores[d.key]) || 0;
    const pct = (val / 10) * 100;
    return `
      <div class="score-bar-item">
        <div class="score-bar-track">
          <div class="score-bar-fill" style="height:${pct}%"></div>
        </div>
        <span class="score-bar-label">${d.label}</span>
      </div>`;
  }).join('');

  document.getElementById('scoreCard').innerHTML = `
    <div class="score-overall">
      <span class="score-number">${overall}</span>
      <span class="score-denom">/10</span>
    </div>
    <p class="score-verdict">${scores['Verdict'] || ''}</p>
    <div class="score-bars">${barsHtml}</div>
  `;
}

async function fetchUnsplashImage(query) {
  try {
    const res = await fetch(`https://source.unsplash.com/800x400/?${encodeURIComponent(query)}`);
    return res.url;
  } catch {
    return null;
  }
}

async function renderBlog(data) {
  const { topic, final_blog, extras, seo } = data;

  // TL;DR
  const tldrItems = (extras.tldr || []).map(b => `<li>${b}</li>`).join('');
  const tldrHtml = tldrItems ? `
    <div class="blog-tldr">
      <div class="blog-tldr-title">TL;DR</div>
      <ul>${tldrItems}</ul>
    </div>` : '';

  // Meta
  const readTime = seo['Estimated Read Time'] || '';
  const metaHtml = `
    <div class="blog-meta">
      ${readTime ? `<span class="blog-meta-item">${readTime}</span>` : ''}
      <span class="blog-meta-item">${data.length || 'medium'}</span>
      <span class="blog-meta-item">AI Generated</span>
    </div>`;

  // Parse blog into sections and inject images
  const paragraphs = final_blog.split('\n').filter(l => l.trim());
  let bodyHtml = '';
  let imageCount = 0;
  const maxImages = data.length === 'long' ? 3 : data.length === 'medium' ? 2 : 1;
  const imageKeywords = topic.split(' ').slice(0, 3).join(' ');

  for (let i = 0; i < paragraphs.length; i++) {
    const line = paragraphs[i].trim();
    if (!line) continue;

    // Detect section headings — short lines without punctuation at end
    const isHeading = line.length < 80 && !line.endsWith('.') && !line.endsWith(',') && !line.startsWith('-') && i > 0;

    if (isHeading && line.split(' ').length <= 10) {
      bodyHtml += `<h2 class="blog-section-heading">${line}</h2>`;
      // Inject image after every 2nd heading
      if (imageCount < maxImages && i % 3 === 0) {
        const imgUrl = `https://source.unsplash.com/800x400/?${encodeURIComponent(imageKeywords)}&sig=${imageCount}`;
        bodyHtml += `<img src="${imgUrl}" alt="${topic}" class="blog-image" loading="lazy" />`;
        imageCount++;
      }
    } else {
      bodyHtml += `<p>${line}</p>`;
    }
  }

  // Pull quote
  const pullQuoteHtml = extras.pull_quote ? `
    <blockquote class="blog-pull-quote">"${extras.pull_quote}"</blockquote>` : '';

  // Key takeaway
  const takeawayHtml = extras.key_takeaway ? `
    <div class="blog-key-takeaway">
      <div class="blog-key-takeaway-label">Key Takeaway</div>
      <p>${extras.key_takeaway}</p>
    </div>` : '';

  // SEO section
  const seoHtml = `
    <div class="seo-section">
      <div class="seo-title">SEO Metadata</div>
      <div class="seo-grid">
        <div class="seo-item"><label>Meta Title</label><p>${seo['Meta Title'] || ''}</p></div>
        <div class="seo-item"><label>Focus Keyword</label><p>${seo['Focus Keyword'] || ''}</p></div>
        <div class="seo-item"><label>Meta Description</label><p>${seo['Meta Description'] || ''}</p></div>
        <div class="seo-item"><label>Read Time</label><p>${seo['Estimated Read Time'] || ''}</p></div>
      </div>
    </div>`;

  document.getElementById('blogContent').innerHTML = `
    ${tldrHtml}
    ${metaHtml}
    <h1 class="blog-title">${topic}</h1>
    <div class="blog-body">${bodyHtml}</div>
    ${pullQuoteHtml}
    ${takeawayHtml}
    ${seoHtml}
  `;
}

function downloadPDF() {
  const element = document.getElementById('blogContent');
  const topic = document.getElementById('topicInput').value.trim() || 'blog';
  const filename = topic.replace(/[^a-z0-9]/gi, '_').toLowerCase().slice(0, 50) + '.pdf';

  const opt = {
    margin: [15, 20],
    filename,
    image: { type: 'jpeg', quality: 0.95 },
    html2canvas: { scale: 2, backgroundColor: '#ffffff' },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };

  // Temporarily style for PDF
  element.style.background = 'white';
  element.style.color = 'black';
  element.style.padding = '0';

  html2pdf().set(opt).from(element).save().then(() => {
    element.style.background = '';
    element.style.color = '';
    element.style.padding = '';
  });
}
