/**
 * CodeForge IDE - Interactive Live Web & React Canvas Preview Controller
 */

class LivePreviewController {
  constructor() {
    this.iframeEl = document.getElementById('live-preview-iframe');
    this.deviceMode = 'desktop';
    this.autoReload = true;
    this.previewLogs = [];
    this.debounceTimer = null;
    this.consoleLogsEl = document.getElementById('preview-console-logs');
  }

  init() {
    // Listen for messages from inside sandbox iframe
    window.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'preview_console_log') {
        this.appendConsoleLog(event.data.level || 'log', event.data.message);
      }
    });
  }

  setDeviceMode(mode) {
    this.deviceMode = mode;
    const wrapper = document.getElementById('preview-viewport-wrapper');
    if (!wrapper) return;

    wrapper.classList.remove('device-desktop', 'device-tablet', 'device-mobile');
    wrapper.classList.add(`device-${mode}`);

    document.querySelectorAll('.preview-device-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-device') === mode);
    });

    Toast.info(`Switched preview mode to ${mode.toUpperCase()}`);
  }

  updatePreview() {
    if (!this.iframeEl) return;
    if (this.debounceTimer) clearTimeout(this.debounceTimer);

    this.debounceTimer = setTimeout(() => {
      this._renderLiveContent();
    }, 300);
  }

  _renderLiveContent() {
    if (!this.iframeEl) return;
    const files = window.ide && window.ide.fileExplorer ? window.ide.fileExplorer.files : [];
    const activeFile = window.ide && window.ide.fileExplorer ? window.ide.fileExplorer.getActiveFile() : null;
    const currentLang = window.ide && window.ide.currentLanguage ? window.ide.currentLanguage.slug : '';

    let htmlContent = '';
    let isReact = currentLang.includes('react') || (activeFile && (activeFile.name.endsWith('.jsx') || activeFile.name.endsWith('.tsx')));

    if (isReact) {
      // Build React preview bundle with Babel standalone & React 18 CDN
      const reactCode = activeFile ? activeFile.content : '';
      htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>React 18 Live Canvas</title>
  <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background: #0f141e;
      color: #e2e8f0;
      padding: 24px;
      min-height: 100vh;
    }
    .react-dashboard-card, .card, .app-container {
      background: #161f30;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    button {
      background: linear-gradient(135deg, #0ea5e9, #38bdf8);
      color: #fff;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      margin-right: 8px;
      transition: all 0.2s;
    }
    button:hover { opacity: 0.9; transform: translateY(-1px); }
    ul { list-style: none; margin-top: 12px; }
    li { padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .badge { background: #38bdf8; color: #000; font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 700; margin-left: 8px; }
  </style>
</head>
<body>
  <div id="root"></div>

  <script>
    // Forward console logs to IDE preview dock
    const originalLog = console.log;
    console.log = function(...args) {
      originalLog.apply(console, args);
      window.parent.postMessage({ type: 'preview_console_log', level: 'log', message: args.map(String).join(' ') }, '*');
    };
    window.onerror = function(msg, url, line) {
      window.parent.postMessage({ type: 'preview_console_log', level: 'error', message: msg + ' (line ' + line + ')' }, '*');
    };
  </script>

  <script type="text/babel">
    ${this._cleanReactImports(reactCode)}

    const container = document.getElementById('root');
    const root = ReactDOM.createRoot(container);
    // Render either App or export default
    try {
      if (typeof App !== 'undefined') {
        root.render(<App />);
      } else if (typeof Dashboard !== 'undefined') {
        root.render(<Dashboard />);
      } else {
        root.render(<div style={{padding: '20px'}}>Ready for React component code</div>);
      }
    } catch(err) {
      document.body.innerHTML = '<div style="color:#ef4444;padding:20px;"><h3>React Render Error</h3><pre>' + err.message + '</pre></div>';
    }
  </script>
</body>
</html>`;
    } else {
      // Find index.html or construct web canvas
      const htmlFile = files.find(f => f.name.endsWith('.html')) || activeFile;
      const cssFile = files.find(f => f.name.endsWith('.css'));
      const jsFile = files.find(f => f.name.endsWith('.js') && !f.name.endsWith('.jsx'));

      let rawHtml = htmlFile ? htmlFile.content : '<h1>Welcome to Live Web Preview</h1>';

      // Inject custom CSS if exists
      if (cssFile && !rawHtml.includes(cssFile.name)) {
        rawHtml = rawHtml.replace('</head>', `<style>${cssFile.content}</style></head>`);
      }

      // Inject custom JS if exists
      if (jsFile && !rawHtml.includes(jsFile.name)) {
        rawHtml = rawHtml.replace('</body>', `<script>${jsFile.content}</script></body>`);
      }

      htmlContent = rawHtml;
    }

    // Set srcdoc
    this.iframeEl.srcdoc = htmlContent;
  }

  _cleanReactImports(code) {
    let clean = code;
    clean = clean.replace(/import\s+React.*?from\s+['"].*?['"];?/g, '');
    clean = clean.replace(/import\s+.*?from\s+['"].*?['"];?/g, '');
    clean = clean.replace(/export\s+default\s+/g, '');
    return clean;
  }

  appendConsoleLog(level, message) {
    if (!this.consoleLogsEl) return;
    const logItem = document.createElement('div');
    logItem.className = `preview-log-line log-${level}`;
    logItem.innerHTML = `<span class="log-time">${new Date().toLocaleTimeString()}</span> <span class="log-msg">${this.escapeHtml(message)}</span>`;
    this.consoleLogsEl.appendChild(logItem);
    this.consoleLogsEl.scrollTop = this.consoleLogsEl.scrollHeight;
  }

  clearConsoleLogs() {
    if (this.consoleLogsEl) {
      this.consoleLogsEl.innerHTML = '<div style="color:var(--text-dim);font-size:11px;">Preview console logs cleared.</div>';
    }
  }

  escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

window.LivePreviewController = LivePreviewController;
