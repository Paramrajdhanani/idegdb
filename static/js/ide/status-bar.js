/**
 * CodeForge IDE - Workspace Bottom Status Bar Controller
 */

class StatusBarController {
  constructor() {
    this.lineColEl = document.getElementById('status-line-col');
    this.spacesEl = document.getElementById('status-spaces');
    this.encodingEl = document.getElementById('status-encoding');
    this.languageEl = document.getElementById('status-language-label');
    this.wordCountEl = document.getElementById('status-word-count');
    this.execStatsEl = document.getElementById('status-exec-stats');
    this.aiStatusEl = document.getElementById('status-ai-label');
  }

  updateCursor(lineNumber, column) {
    if (this.lineColEl) {
      this.lineColEl.textContent = `Ln ${lineNumber}, Col ${column}`;
    }
  }

  updateContentMetrics(code) {
    if (!code) {
      if (this.wordCountEl) this.wordCountEl.textContent = '0 chars, 0 lines';
      return;
    }
    const chars = code.length;
    const lines = code.split('\n').length;
    if (this.wordCountEl) {
      this.wordCountEl.textContent = `${lines} lines, ${chars} chars`;
    }
  }

  updateLanguage(languageObj) {
    if (!languageObj) return;
    if (this.languageEl) {
      this.languageEl.textContent = `${languageObj.name} ${languageObj.version || ''}`.trim();
    }
  }

  updateExecutionStats(timeMs, memoryBytes) {
    if (this.execStatsEl) {
      const mb = (memoryBytes / (1024 * 1024)).toFixed(1);
      this.execStatsEl.innerHTML = `<i data-lucide="zap" style="width:11px;height:11px;color:var(--accent-primary);"></i> ${timeMs}ms &bull; ${mb}MB`;
      if (window.lucide) window.lucide.createIcons();
    }
  }
}

window.StatusBarController = StatusBarController;
