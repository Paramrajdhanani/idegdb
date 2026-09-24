/**
 * CodeForge IDE - Global Command Palette (Ctrl + P / Ctrl + K)
 */

class CommandPalette {
  constructor() {
    this.modal = document.getElementById('command-palette-modal');
    this.input = document.getElementById('palette-search-input');
    this.resultsContainer = document.getElementById('palette-results-container');
    this.selectedIndex = 0;
    this.currentItems = [];

    this._initEvents();
  }

  _initEvents() {
    if (!this.input) return;

    this.input.addEventListener('input', (e) => this.handleSearch(e.target.value));

    this.input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.moveSelection(1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.moveSelection(-1);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        this.executeSelected();
      } else if (e.key === 'Escape') {
        this.hide();
      }
    });

    // Close when clicking outside
    window.addEventListener('click', (e) => {
      if (this.modal && this.modal.classList.contains('show') && !this.modal.contains(e.target)) {
        if (!e.target.closest('#btn-open-palette')) {
          this.hide();
        }
      }
    });
  }

  show() {
    if (!this.modal) return;
    this.modal.classList.add('show');
    if (this.input) {
      this.input.value = '';
      this.input.focus();
    }
    this.handleSearch('');
  }

  hide() {
    if (!this.modal) return;
    this.modal.classList.remove('show');
  }

  toggle() {
    if (this.modal && this.modal.classList.contains('show')) {
      this.hide();
    } else {
      this.show();
    }
  }

  async handleSearch(query) {
    if (!query) {
      // Show default common actions
      this.currentItems = [
        { title: 'Run Program', action: 'run', icon: 'play', shortcut: 'Ctrl+Enter' },
        { title: 'Debug Program', action: 'debug', icon: 'bug', shortcut: 'F8' },
        { title: 'Save Current File', action: 'save', icon: 'save', shortcut: 'Ctrl+S' },
        { title: 'New File', action: 'new_file', icon: 'file-plus', shortcut: 'Ctrl+M' },
        { title: 'Format Code', action: 'format', icon: 'wand-2', shortcut: 'Ctrl+B' },
        { title: 'Share Project', action: 'share', icon: 'share-2', shortcut: '' },
        { title: 'Download Project ZIP', action: 'download', icon: 'download', shortcut: '' },
        { title: 'Open Settings', action: 'settings', icon: 'settings', shortcut: 'Ctrl+Shift+S' },
      ];
      this.renderItems();
      return;
    }

    try {
      const data = await ApiClient.get('/api/search/', { q: query });
      const items = [];

      // Add matching commands
      (data.commands || []).forEach(cmd => {
        items.push({
          title: cmd.name,
          action: cmd.action,
          icon: 'terminal',
          shortcut: cmd.shortcut,
          category: cmd.category
        });
      });

      // Add matching files
      (data.files || []).forEach(file => {
        items.push({
          title: file.name,
          action: 'open_file',
          fileId: file.id,
          icon: 'file-code',
          subtitle: file.path || file.project_name
        });
      });

      // Add matching projects
      (data.projects || []).forEach(proj => {
        items.push({
          title: proj.name,
          action: 'open_project',
          projectId: proj.id,
          icon: 'folder',
          subtitle: proj.language
        });
      });

      this.currentItems = items;
      this.selectedIndex = 0;
      this.renderItems();
    } catch (err) {
      console.error('Palette search error:', err);
    }
  }

  renderItems() {
    if (!this.resultsContainer) return;
    this.resultsContainer.innerHTML = '';

    if (this.currentItems.length === 0) {
      this.resultsContainer.innerHTML = `
        <div style="padding:16px;text-align:center;color:var(--text-dim);font-size:13px;">
          No matching files or commands
        </div>
      `;
      return;
    }

    this.currentItems.forEach((item, index) => {
      const el = document.createElement('div');
      el.className = `palette-item ${index === this.selectedIndex ? 'selected' : ''}`;
      
      const shortcutHtml = item.shortcut ? `<kbd>${item.shortcut}</kbd>` : (item.subtitle ? `<span style="font-size:11px;color:var(--text-dim);">${item.subtitle}</span>` : '');

      el.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;">
          <i data-lucide="${item.icon || 'command'}" style="width:15px;height:15px;"></i>
          <span>${item.title}</span>
        </div>
        ${shortcutHtml}
      `;

      el.addEventListener('click', () => {
        this.selectedIndex = index;
        this.executeSelected();
      });

      this.resultsContainer.appendChild(el);
    });

    if (window.lucide) window.lucide.createIcons();
  }

  moveSelection(delta) {
    if (this.currentItems.length === 0) return;
    this.selectedIndex = (this.selectedIndex + delta + this.currentItems.length) % this.currentItems.length;
    this.renderItems();
  }

  executeSelected() {
    const item = this.currentItems[this.selectedIndex];
    if (!item) return;

    this.hide();

    const action = item.action;
    if (action === 'run' || action === 'run_code') window.ide.runCode();
    else if (action === 'debug' || action === 'debug_code') window.ide.debugCode();
    else if (action === 'stop' || action === 'stop_code') window.ide.stopCode();
    else if (action === 'save' || action === 'save_project') window.ide.saveProject();
    else if (action === 'format' || action === 'format_code') window.ide.formatCode();
    else if (action === 'share' || action === 'share_project') window.ide.openShareModal();
    else if (action === 'download' || action === 'download_project') window.ide.downloadProject();
    else if (action === 'settings' || action === 'open_settings') window.ide.openSettingsModal();
    else if (action === 'new_file') window.ide.openNewFileModal();
    else if (action === 'clear_terminal') window.ide.terminal.clearOutput();
    else if (action === 'toggle_theme') {
      const themes = ['codeforge-dark', 'midnight', 'vs-dark', 'vs-light'];
      const nextTheme = (window.ide.monaco.options.theme === 'codeforge-dark') ? 'midnight' : 'codeforge-dark';
      window.ide.monaco.setTheme(nextTheme);
      window.ide.monaco.options.theme = nextTheme;
      Toast.info(`Theme set to ${nextTheme}`);
    }
    else if (action === 'open_file' && item.fileId) window.ide.fileExplorer.openFile(item.fileId);
    else if (action === 'open_project' && item.projectId) window.location.href = `/ide/${item.projectId}/`;
  }
}

window.CommandPalette = CommandPalette;
