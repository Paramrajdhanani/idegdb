/**
 * CodeForge IDE - Terminal & Output Dock Controller
 */

class TerminalDock {
  constructor(dockContainerId, options = {}) {
    this.container = document.getElementById(dockContainerId);
    this.activeTab = 'output';
    this.outputContentEl = document.getElementById('dock-output-content');
    this.terminalContentEl = document.getElementById('dock-terminal-content');
    this.stdinInputEl = document.getElementById('dock-stdin-input');
    this.errorsContentEl = document.getElementById('dock-errors-content');
    this.metaBarEl = document.getElementById('output-meta-bar');

    this._initTabs();
  }

  _initTabs() {
    const tabButtons = this.container.querySelectorAll('.dock-tab-btn');
    tabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetTab = btn.getAttribute('data-tab');
        this.switchTab(targetTab);
      });
    });
  }

  switchTab(tabName) {
    this.activeTab = tabName;

    // Update buttons
    const tabButtons = this.container.querySelectorAll('.dock-tab-btn');
    tabButtons.forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
    });

    // Update panels
    const panels = this.container.querySelectorAll('.dock-panel');
    panels.forEach(panel => {
      panel.classList.toggle('active', panel.id === `dock-panel-${tabName}`);
    });
  }

  getStdin() {
    return this.stdinInputEl ? this.stdinInputEl.value : '';
  }

  setStdin(text) {
    if (this.stdinInputEl) {
      this.stdinInputEl.value = text;
    }
  }

  showRunningState() {
    this.switchTab('output');
    if (this.metaBarEl) {
      this.metaBarEl.innerHTML = `
        <span class="badge badge-primary">
          <i data-lucide="loader" class="spin" style="width:12px;height:12px;"></i> Running...
        </span>
        <span style="color:var(--text-dim);font-size:12px;">Executing in isolated sandbox...</span>
      `;
      if (window.lucide) window.lucide.createIcons();
    }
    if (this.outputContentEl) {
      this.outputContentEl.innerHTML = '<span style="color:var(--text-dim);">Compiling and executing program...</span>';
    }
  }

  displayResult(resultData) {
    const { status, stdout, stderr, exit_code, execution_time_ms, memory_bytes, status_message } = resultData;
    const isAwaitingInput = Boolean((stderr && (stderr.includes('EOFError') || stderr.includes('NoSuchElementException'))) || (status_message && status_message.includes('waiting for user input')));

    // Switch to output tab
    this.switchTab(status === 'failed' && !stdout && stderr && !isAwaitingInput ? 'errors' : 'output');

    // Render Status Meta Bar
    if (this.metaBarEl) {
      let badgeClass = 'badge-success';
      let statusIcon = 'check-circle';
      let statusText = status.toUpperCase();

      if (isAwaitingInput) {
        badgeClass = 'badge-primary';
        statusIcon = 'text-cursor-input';
        statusText = 'AWAITING INPUT';
      } else if (status === 'failed') {
        badgeClass = 'badge-error';
        statusIcon = 'alert-circle';
      } else if (status === 'timeout') {
        badgeClass = 'badge-warning';
        statusIcon = 'clock';
      }

      const memoryMb = (memory_bytes / (1024 * 1024)).toFixed(1);
      const timeSec = (execution_time_ms / 1000).toFixed(2);

      this.metaBarEl.innerHTML = `
        <span class="badge ${badgeClass}">
          <i data-lucide="${statusIcon}" style="width:12px;height:12px;"></i> ${statusText}
        </span>
        <span style="color:var(--text-secondary);font-weight:500;">Exit Code: ${exit_code}</span>
        <span style="color:var(--text-dim);">&bull;</span>
        <span style="color:var(--text-secondary);">Time: ${timeSec}s (${execution_time_ms}ms)</span>
        <span style="color:var(--text-dim);">&bull;</span>
        <span style="color:var(--text-secondary);">Memory: ${memoryMb} MB</span>
      `;
      if (window.lucide) window.lucide.createIcons();
    }

    // Render Standard Output
    if (this.outputContentEl) {
      let html = '';
      if (stdout) {
        html += `<div class="output-text-stdout">${this.escapeHtml(stdout)}</div>`;
      }

      if (isAwaitingInput) {
        html += `
          <div style="margin-top:10px;padding:8px 12px;background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3);border-radius:6px;font-family:var(--font-code);font-size:12px;color:var(--accent-primary);display:flex;align-items:center;justify-content:space-between;">
            <span><i data-lucide="corner-down-left" style="width:13px;height:13px;display:inline-block;vertical-align:middle;margin-right:4px;"></i> Program is waiting for input: Type value below & press <b>Enter</b></span>
            <button class="btn btn-ghost btn-sm" onclick="ide.terminal.resetInteractiveSession()" style="font-size:11px;padding:2px 8px;height:22px;color:var(--text-muted);">Reset</button>
          </div>
        `;
      } else if (stderr) {
        html += `<div class="output-text-stderr" style="margin-top:12px;">${this.escapeHtml(stderr)}</div>`;
      }

      if (!stdout && !stderr) {
        html = '<span style="color:var(--text-dim);">[Process completed with empty output]</span>';
      }
      this.outputContentEl.innerHTML = html;
      this.outputContentEl.scrollTop = this.outputContentEl.scrollHeight;

      if (window.lucide) window.lucide.createIcons();
    }

    // Auto-focus interactive console input
    const consoleInput = document.getElementById('interactive-console-input');
    if (consoleInput) {
      setTimeout(() => consoleInput.focus(), 50);
    }

    // Update Errors tab
    if (this.errorsContentEl) {
      if (stderr) {
        this.errorsContentEl.innerHTML = `<div class="output-text-stderr">${this.escapeHtml(stderr)}</div>`;
      } else {
        this.errorsContentEl.innerHTML = '<span style="color:var(--text-dim);">No errors detected.</span>';
      }
    }
  }

  submitInteractiveInput(value) {
    if (value === undefined || value === null) return;
    const inputEl = document.getElementById('interactive-console-input');
    const trimmed = (value || '').trim();

    // Append entered input line to STDIN buffer
    const currentStdin = this.getStdin();
    const newStdin = currentStdin ? currentStdin + '\n' + trimmed : trimmed;
    this.setStdin(newStdin);

    if (inputEl) {
      inputEl.value = '';
    }

    // Echo input directly to the Output Console
    if (this.outputContentEl) {
      const echoDiv = document.createElement('div');
      echoDiv.style.color = 'var(--accent-primary, #6366f1)';
      echoDiv.style.fontFamily = 'var(--font-code, monospace)';
      echoDiv.style.fontSize = '13px';
      echoDiv.style.fontWeight = '600';
      echoDiv.style.margin = '4px 0';
      echoDiv.textContent = `> ${trimmed}`;
      this.outputContentEl.appendChild(echoDiv);
      this.outputContentEl.scrollTop = this.outputContentEl.scrollHeight;
    }

    // Automatically re-run the code with updated standard input
    if (window.ide && typeof window.ide.runCode === 'function') {
      window.ide.runCode();
    }
  }

  resetInteractiveSession() {
    this.setStdin('');
    const inputEl = document.getElementById('interactive-console-input');
    if (inputEl) inputEl.value = '';
    if (this.outputContentEl) {
      this.outputContentEl.innerHTML = '<span style="color:var(--text-dim);">Inputs reset. Ready for new run.</span>';
    }
    Toast.info('Interactive session inputs reset');
  }

  clearOutput() {
    if (this.outputContentEl) {
      this.outputContentEl.innerHTML = '<span style="color:var(--text-dim);">Output cleared. Run code to view results.</span>';
    }
    if (this.metaBarEl) {
      this.metaBarEl.innerHTML = '';
    }
    if (this.errorsContentEl) {
      this.errorsContentEl.innerHTML = '<span style="color:var(--text-dim);">No errors.</span>';
    }
  }

  copyOutput() {
    if (!this.outputContentEl) return;
    const text = this.outputContentEl.innerText;
    navigator.clipboard.writeText(text).then(() => {
      Toast.success('Output copied to clipboard');
    }).catch(() => {
      Toast.error('Failed to copy output');
    });
  }

  handleCliCommand(cmdText) {
    const cmd = (cmdText || '').trim();
    if (!cmd) return;

    this.appendTerminalLog(`$ ${cmd}`);

    const lower = cmd.toLowerCase();
    if (lower === 'run' || lower.startsWith('run ') || lower === 'python main.py' || lower === 'node index.js') {
      this.appendTerminalLog('Dispatching execution to isolated sandbox...');
      if (window.ide) window.ide.runCode();
    } else if (lower === 'clear' || lower === 'cls') {
      const log = document.getElementById('dock-terminal-log');
      if (log) log.innerHTML = '<span style="color:var(--text-muted);">$ CodeForge terminal cleared.</span>';
    } else if (lower === 'help') {
      this.appendTerminalLog('Available commands:\n  run         - Execute the active code\n  debug       - Launch debug console\n  save        - Save project workspace\n  format      - Format document code\n  ls          - List project files\n  clear / cls - Clear terminal output\n  help        - Show this help text');
    } else if (lower === 'ls' || lower === 'dir') {
      if (window.ide && window.ide.fileExplorer) {
        const fileNames = window.ide.fileExplorer.files.map(f => f.name).join('   ');
        this.appendTerminalLog(fileNames || 'No files.');
      }
    } else if (lower === 'debug') {
      if (window.ide) window.ide.debugCode();
    } else if (lower === 'save') {
      if (window.ide) window.ide.saveProject();
    } else if (lower === 'format') {
      if (window.ide) window.ide.formatCode();
    } else {
      this.appendTerminalLog(`Command not recognized: '${cmd}'. Type 'help' for available commands or click Run.`);
    }
  }

  appendTerminalLog(text) {
    const log = document.getElementById('dock-terminal-log');
    if (!log) return;
    const line = document.createElement('div');
    line.style.whiteSpace = 'pre-wrap';
    line.style.marginTop = '4px';
    line.style.color = text.startsWith('$') ? 'var(--accent-primary)' : 'var(--text-secondary)';
    line.textContent = text;
    log.appendChild(line);
    log.scrollTop = log.scrollHeight;
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

window.TerminalDock = TerminalDock;
