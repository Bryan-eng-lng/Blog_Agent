const API_URL = 'https://blog-agent-699e.onrender.com';
let selectedLength = 'medium';

// Wake up Render on page load
fetch(`${API_URL}/docs`).catch(() => {});

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
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 180000); // 3 min timeout

    const response = await fetch(`${API_URL}/generate-blog`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, audience: audience || 'general readers', length: selectedLength }),
      signal: controller.signal
    });

    clearTimeout(timeout);

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      const errMsg = errData.detail || 'Something went wrong. Please try again.';
      throw new Error(errMsg);
    }
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
    if (err.name === 'AbortError') {
      alert('Request timed out. The server may be waking up — please try again in 30 seconds.');
    } else {
      alert(err.message || 'Something went wrong. Please try again.');
    }
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

function cleanMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^#+\s/gm, '')
    .trim();
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
    <blockquote class="blog-pull-quote">"${cleanMarkdown(extras.pull_quote)}"</blockquote>` : '';

  // Key takeaway
  const takeawayHtml = extras.key_takeaway ? `
    <div class="blog-key-takeaway">
      <div class="blog-key-takeaway-label">Key Takeaway</div>
      <p>${cleanMarkdown(extras.key_takeaway)}</p>
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
  const topic = document.getElementById('topicInput').value.trim() || 'blog';
  const filename = topic.replace(/[^a-z0-9]/gi, '_').toLowerCase().slice(0, 50) + '.pdf';

  // Build a self-contained clone for PDF — no dependency on live DOM layout
  const source = document.getElementById('blogContent');

  const wrapper = document.createElement('div');
  wrapper.style.cssText = `
    width: 750px;
    background: #111111;
    color: #f0ece4;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    line-height: 1.8;
    padding: 48px 56px;
    box-sizing: border-box;
  `;

  const clone = source.cloneNode(true);

  // Apply inline styles to every element in the clone so html2canvas picks them up
  const applyStyles = (el) => {
    const tag = el.tagName && el.tagName.toLowerCase();
    const cls = el.className || '';

    if (cls.includes('blog-title'))            { el.style.cssText += 'color:#f0ece4!important;font-size:30px;font-weight:700;margin-bottom:24px;line-height:1.2;'; }
    else if (cls.includes('blog-section-heading')) { el.style.cssText += 'color:#f0ece4!important;font-size:20px;font-weight:600;margin:32px 0 12px;'; }
    else if (cls.includes('blog-body'))        { el.style.cssText += 'color:#d4cfc7!important;'; }
    else if (tag === 'p')                      { el.style.cssText += 'color:#d4cfc7!important;margin-bottom:16px;'; }
    else if (cls.includes('blog-tldr') && !cls.includes('title') && !cls.includes('li')) {
      el.style.cssText += 'background:#1a1a1a!important;border-left:3px solid #c9a96e;padding:16px 20px;margin-bottom:32px;border-radius:0 8px 8px 0;';
    }
    else if (cls.includes('blog-tldr-title')) { el.style.cssText += 'color:#c9a96e!important;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;'; }
    else if (tag === 'li')                     { el.style.cssText += 'color:#888880!important;font-size:14px;margin-bottom:6px;list-style:none;padding-left:16px;'; }
    else if (cls.includes('blog-meta-item'))   { el.style.cssText += 'color:#555550!important;background:#1a1a1a!important;border:1px solid #222!important;font-size:12px;padding:4px 12px;border-radius:20px;display:inline-block;margin-right:8px;'; }
    else if (cls.includes('blog-meta'))        { el.style.cssText += 'margin-bottom:24px;'; }
    else if (cls.includes('blog-pull-quote'))  { el.style.cssText += 'color:#e8d5b0!important;border-left:3px solid #c9a96e;padding:16px 24px;margin:32px 0;font-size:19px;font-style:italic;'; }
    else if (cls.includes('blog-key-takeaway') && !cls.includes('label') && !cls.includes('p')) {
      el.style.cssText += 'background:#1a1a1a!important;border:1px solid rgba(201,169,110,0.3)!important;border-radius:10px;padding:20px 24px;margin-top:32px;';
    }
    else if (cls.includes('blog-key-takeaway-label')) { el.style.cssText += 'color:#c9a96e!important;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'; }
    else if (cls.includes('seo-section'))      { el.style.cssText += 'background:#1a1a1a!important;border:1px solid #222!important;border-radius:12px;padding:20px 24px;margin-top:32px;'; }
    else if (cls.includes('seo-title'))        { el.style.cssText += 'color:#555550!important;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;'; }
    else if (tag === 'label')                  { el.style.cssText += 'color:#555550!important;font-size:11px;display:block;margin-bottom:4px;'; }
    else if (cls.includes('seo-grid'))         { el.style.cssText += 'display:grid;grid-template-columns:1fr 1fr;gap:12px;'; }
    else if (cls.includes('blog-image'))       { el.style.cssText += 'width:100%;border-radius:10px;margin:24px 0;opacity:0.85;'; }

    Array.from(el.children || []).forEach(applyStyles);
  };

  applyStyles(clone);
  wrapper.appendChild(clone);

  // Temporarily attach to DOM (off-screen) so html2canvas can render it
  wrapper.style.position = 'fixed';
  wrapper.style.top = '-99999px';
  wrapper.style.left = '0';
  document.body.appendChild(wrapper);

  const opt = {
    margin: 0,
    filename,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: {
      scale: 2,
      backgroundColor: '#111111',
      useCORS: true,
      logging: false,
      width: 750,
      windowWidth: 750
    },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };

  html2pdf().set(opt).from(wrapper).save().then(() => {
    document.body.removeChild(wrapper);
  });
}
