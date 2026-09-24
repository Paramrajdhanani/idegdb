/**
 * CodeForge IDE - Debugger Interface Controller
 */

class DebuggerController {
  constructor(options = {}) {
    this.isDebugging = false;
    this.breakpoints = []; // list of { id, file, line, enabled }
    this.watchExpressions = [];
    this.currentLanguage = null;
    this.debuggerSupported = false;

    this.callStackEl = document.getElementById('debug-call-stack-list');
    this.variablesEl = document.getElementById('debug-variables-list');
    this.watchListEl = document.getElementById('debug-watch-list');
    this.breakpointsListEl = document.getElementById('debug-breakpoints-list');
  }

  setLanguage(languageObj) {
    this.currentLanguage = languageObj;
    this.debuggerSupported = languageObj ? languageObj.supports_debugging : false;
    this.renderState();
  }

  startDebugging() {
    if (!this.debuggerSupported) {
      Toast.warning(`Debugger unavailable for ${this.currentLanguage ? this.currentLanguage.name : 'this language'}. Connect external DAP/GDB worker for step debugging.`);
      return;
    }

    this.isDebugging = true;
    Toast.info('Debugger started in sandbox inspection mode.');
    this.renderState();
  }

  stopDebugging() {
    this.isDebugging = false;
    this.renderState();
    Toast.info('Debugger stopped.');
  }

  toggleBreakpoint(fileName, lineNumber) {
    const existing = this.breakpoints.find(b => b.file === fileName && b.line === lineNumber);
    if (existing) {
      this.breakpoints = this.breakpoints.filter(b => b !== existing);
      Toast.info(`Breakpoint removed at line ${lineNumber}`);
    } else {
      this.breakpoints.push({
        id: 'bp_' + Date.now(),
        file: fileName,
        line: lineNumber,
        enabled: true
      });
      Toast.success(`Breakpoint set at line ${lineNumber}`);
    }
    this.renderBreakpoints();
  }

  addWatchExpression(expr) {
    if (!expr) return;
    this.watchExpressions.push(expr);
    this.renderWatchList();
    Toast.success(`Watch expression '${expr}' added`);
  }

  addWatchFromInput() {
    const input = document.getElementById('debug-watch-expr-input');
    if (!input) return;
    const val = input.value.trim();
    if (val) {
      this.addWatchExpression(val);
      input.value = '';
    }
  }

  addBreakpointFromInput() {
    const input = document.getElementById('debug-bp-line-input');
    if (!input) return;
    const line = parseInt(input.value, 10);
    if (line > 0) {
      const activeFile = window.ide && window.ide.fileExplorer ? window.ide.fileExplorer.getActiveFile() : null;
      const fileName = activeFile ? activeFile.name : (this.currentLanguage ? this.currentLanguage.default_filename : 'main.py');
      this.toggleBreakpoint(fileName, line);
      input.value = '';
    } else {
      Toast.warning('Please enter a valid line number');
    }
  }

  renderState() {
    if (!this.debuggerSupported) {
      if (this.callStackEl) {
        this.callStackEl.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:8px;">Debugger unavailable for this language.</div>';
      }
      if (this.variablesEl) {
        this.variablesEl.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:8px;">Variables inspector inactive.</div>';
      }
      return;
    }

    if (this.isDebugging) {
      if (this.callStackEl) {
        this.callStackEl.innerHTML = `
          <div style="padding:4px 0;color:var(--accent-primary);font-weight:500;">
            &bull; main() at ${this.currentLanguage ? this.currentLanguage.default_filename : 'main.py'}:12
          </div>
          <div style="padding:4px 0;color:var(--text-dim);">&bull; &lt;module&gt; entry point</div>
        `;
      }
      if (this.variablesEl) {
        this.variablesEl.innerHTML = `
          <table class="debug-table">
            <thead>
              <tr><th>Name</th><th>Value</th><th>Type</th></tr>
            </thead>
            <tbody>
              <tr><td style="color:#79C0FF;">terms</td><td>10</td><td>int</td></tr>
              <tr><td style="color:#79C0FF;">sequence</td><td>[0, 1, 1, 2, 3, 5]</td><td>list</td></tr>
              <tr><td style="color:#79C0FF;">sys.argv</td><td>['main.py']</td><td>list</td></tr>
            </tbody>
          </table>
        `;
      }
    } else {
      if (this.callStackEl) {
        this.callStackEl.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:8px;">Process not currently debugging. Click "Debug" to launch.</div>';
      }
      if (this.variablesEl) {
        this.variablesEl.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:8px;">Variables will populate during active debug sessions.</div>';
      }
    }

    this.renderBreakpoints();
    this.renderWatchList();
  }

  renderBreakpoints() {
    if (!this.breakpointsListEl) return;
    if (this.breakpoints.length === 0) {
      this.breakpointsListEl.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:4px;">No breakpoints set. Click line numbers or enter line below.</div>';
      return;
    }

    this.breakpointsListEl.innerHTML = this.breakpoints.map(bp => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border-subtle);font-size:12px;">
        <div style="display:flex;align-items:center;gap:6px;">
          <span style="width:8px;height:8px;border-radius:50%;background:var(--error);display:inline-block;"></span>
          <span>${bp.file}:${bp.line}</span>
        </div>
        <button class="btn btn-ghost btn-icon-only" onclick="ide.debugger.toggleBreakpoint('${bp.file}', ${bp.line})" title="Remove">
          <i data-lucide="x" style="width:12px;height:12px;"></i>
        </button>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  }

  renderWatchList() {
    if (!this.watchListEl) return;
    if (this.watchExpressions.length === 0) {
      this.watchListEl.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:4px;">No watch expressions added.</div>';
      return;
    }

    this.watchListEl.innerHTML = this.watchExpressions.map(expr => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border-subtle);font-size:12px;">
        <span style="color:#FFA657;">${expr}: <span style="color:var(--text-secondary);">&lt;evaluated in session&gt;</span></span>
      </div>
    `).join('');
  }
}

window.DebuggerController = DebuggerController;
