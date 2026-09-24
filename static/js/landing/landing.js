/**
 * CodeForge IDE - Landing Page Interactive Playground & Animations
 */

document.addEventListener('DOMContentLoaded', () => {
  // GSAP Entrance Animations
  if (window.gsap) {
    gsap.from('.hero-pill', { opacity: 0, y: -20, duration: 0.8, ease: 'power3.out' });
    gsap.from('.hero-title', { opacity: 0, y: 30, duration: 1, delay: 0.2, ease: 'power3.out' });
    gsap.from('.hero-subtitle', { opacity: 0, y: 20, duration: 1, delay: 0.4, ease: 'power3.out' });
    gsap.from('.hero-buttons', { opacity: 0, scale: 0.95, duration: 0.8, delay: 0.6, ease: 'power3.out' });
    gsap.from('.hero-preview-container', { opacity: 0, y: 40, duration: 1.2, delay: 0.8, ease: 'power3.out' });
  }

  // Interactive Code Playground Snippets
  const snippets = {
    python: {
      langName: 'Python 3.13',
      slug: 'python',
      filename: 'main.py',
      code: `# Live Python Execution Demo
import math

def calculate_stats(numbers):
    avg = sum(numbers) / len(numbers)
    variance = sum((x - avg) ** 2 for x in numbers) / len(numbers)
    return avg, math.sqrt(variance)

data = [12, 45, 67, 89, 34, 56, 78, 90, 23]
mean, std_dev = calculate_stats(data)

print(f"Sample Size: {len(data)}")
print(f"Mean Average: {mean:.2f}")
print(f"Standard Dev: {std_dev:.2f}")
print("✓ CodeForge Sandbox Running Fast.")`
    },
    javascript: {
      langName: 'JavaScript (Node.js)',
      slug: 'javascript',
      filename: 'index.js',
      code: `// Live JavaScript Sandbox
const items = ['Monaco', 'WebSockets', 'Subprocess Sandbox', 'PostgreSQL'];

console.log('⚡ CodeForge High-Performance Runtime');
items.forEach((item, idx) => {
    console.log(\`  [\${idx + 1}] Enabled: \${item}\`);
});

const timestamp = new Date().toISOString();
console.log(\`Ready for cloud development at \${timestamp}\`);`
    },
    sql: {
      langName: 'SQL (SQLite)',
      slug: 'sql',
      filename: 'queries.sql',
      code: `CREATE TABLE languages (id INT, name TEXT, speed TEXT);
INSERT INTO languages VALUES (1, 'Python', 'Fast'), (2, 'C++', 'Blazing'), (3, 'Rust', 'Ultra');

SELECT name, speed FROM languages ORDER BY id;`
    }
  };

  let currentPlaygroundLang = 'python';
  const codePane = document.getElementById('hero-code-pane');
  const outputPane = document.getElementById('hero-output-pane');
  const heroRunBtn = document.getElementById('hero-run-btn');

  function setPlaygroundLanguage(langKey) {
    if (!snippets[langKey]) return;
    currentPlaygroundLang = langKey;
    if (codePane) codePane.textContent = snippets[langKey].code;
    if (outputPane) outputPane.innerHTML = '<span style="color:var(--text-dim);">Click "▶ Run" to execute live code...</span>';

    document.querySelectorAll('.playground-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-lang') === langKey);
    });
  }

  // Language buttons in playground
  document.querySelectorAll('.playground-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const lang = btn.getAttribute('data-lang');
      setPlaygroundLanguage(lang);
    });
  });

  // Hero Run Button
  if (heroRunBtn) {
    heroRunBtn.addEventListener('click', async () => {
      const activeSnippet = snippets[currentPlaygroundLang];
      if (!activeSnippet) return;

      heroRunBtn.innerHTML = '<i data-lucide="loader" class="spin" style="width:13px;height:13px;"></i> Running...';
      if (outputPane) outputPane.innerHTML = '<span style="color:var(--text-dim);">Executing in isolated sandbox...</span>';
      if (window.lucide) window.lucide.createIcons();

      try {
        const payload = {
          language_slug: activeSnippet.slug,
          files: [{
            name: activeSnippet.filename,
            path: '',
            content: activeSnippet.code,
            is_entry_point: true
          }],
          entry_file: activeSnippet.filename
        };

        const res = await ApiClient.post('/api/executions/', payload);
        const result = res.result || {};

        let outputHtml = '';
        if (result.stdout) {
          outputHtml += `<div style="color:var(--text-primary);white-space:pre-wrap;">${result.stdout}</div>`;
        }
        if (result.stderr) {
          outputHtml += `<div style="color:var(--error);margin-top:8px;white-space:pre-wrap;">${result.stderr}</div>`;
        }
        if (!result.stdout && !result.stderr) {
          outputHtml = '<span style="color:var(--text-dim);">[Process completed successfully]</span>';
        }

        outputHtml += `<div style="margin-top:12px;padding-top:8px;border-top:1px solid var(--border-subtle);font-size:11px;color:var(--text-dim);">
          Time: ${(res.execution_time_ms / 1000).toFixed(2)}s &bull; Exit Code: ${result.exit_code} &bull; Status: ${res.status.toUpperCase()}
        </div>`;

        if (outputPane) outputPane.innerHTML = outputHtml;
        Toast.success('Execution finished!');

      } catch (err) {
        if (outputPane) outputPane.innerHTML = `<span style="color:var(--error);">Error: ${err.message}</span>`;
        Toast.error('Execution failed');
      } finally {
        heroRunBtn.innerHTML = '<i data-lucide="play" style="width:13px;height:13px;fill:currentColor;"></i> Run';
        if (window.lucide) window.lucide.createIcons();
      }
    });
  }

  // Initialize with python
  setPlaygroundLanguage('python');
});
