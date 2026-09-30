/**
 * CodeForge IDE - Main Application Controller
 */

class CodeForgeIDE {
  constructor() {
    this.projectId = null;
    this.project = null;
    this.currentLanguage = null;
    this.languages = [];
    this.isExecuting = false;
    this.autosaveTimer = null;
    this.isDirty = false;

    // Sub-components
    this.monaco = null;
    this.fileExplorer = null;
    this.terminal = null;
    this.debugger = null;
    this.commandPalette = null;
    this.aiAssistant = null;
    this.livePreview = null;
    this.snippets = null;
    this.statusBar = null;
    this.projectTemplates = null;
  }

  async init(config = {}) {
    this.projectId = config.projectId || null;
    this.languages = config.languages || [];
    
    // Check for ?lang= in URL query params
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    if (langParam) {
      this.currentLanguage = this.languages.find(l => l.slug.toLowerCase() === langParam.toLowerCase() || l.monaco_id === langParam.toLowerCase()) || null;
    }
    if (!this.currentLanguage) {
      this.currentLanguage = this.languages.find(l => l.slug === 'python') || this.languages[0] || null;
    }

    // 1. Initialize File Explorer
    this.fileExplorer = new FileExplorer('project-file-tree', 'editor-tabs-container', 'editor-breadcrumbs');
    this.fileExplorer.onFileSelectCallback = (file) => this.handleFileSelected(file);
    this.fileExplorer.onFileChangeCallback = (file) => this.handleFileContentChanged(file);

    // 2. Initialize Terminal Dock
    this.terminal = new TerminalDock('ide-bottom-dock');

    // 3. Initialize Debugger
    this.debugger = new DebuggerController();
    this.debugger.setLanguage(this.currentLanguage);

    // 4. Initialize Command Palette
    this.commandPalette = new CommandPalette();

    // 5. Initialize AI Assistant Copilot
    this.aiAssistant = new AIAssistantController();
    this.aiAssistant.init();

    // 6. Initialize Live Preview Web / React Canvas
    this.livePreview = new LivePreviewController();
    this.livePreview.init();

    // 7. Initialize Snippets Library
    this.snippets = new SnippetsLibraryController();

    // 8. Initialize Status Bar
    this.statusBar = new StatusBarController();
    this.statusBar.updateLanguage(this.currentLanguage);
    this.statusBar.updateContentMetrics(this.currentLanguage ? this.currentLanguage.default_code : '');

    // 9. Initialize Project Templates Wizard
    this.projectTemplates = new ProjectTemplatesController();

    // 10. Initialize Keyboard Shortcuts, Resizers & UI Listeners immediately
    this._initShortcuts();
    this._initResizers();
    this._initUIListeners();

    // 11. Load Project Data or Setup Blank Guest Project
    if (this.projectId) {
      await this.loadProject(this.projectId);
    } else {
      this.setupDefaultProject();
    }

    // 12. Initialize Monaco Editor
    this.monaco = new MonacoManager('monaco-editor-container');
    const initialCode = (this.fileExplorer && this.fileExplorer.getActiveFile())
      ? this.fileExplorer.getActiveFile().content
      : (this.currentLanguage ? this.currentLanguage.default_code : '');
    const initialMonacoLang = this.currentLanguage ? this.currentLanguage.monaco_id : 'python';

    await this.monaco.init(initialCode, initialMonacoLang);

    // 13. Monaco Editor content listener
    this.monaco.onContentChange((newVal) => {
      this.fileExplorer.updateActiveFileContent(newVal);
      this.triggerAutosave();
    });
  }

  setupDefaultProject() {
    const lang = this.currentLanguage;
    const defaultFile = {
      id: 'local_main',
      name: lang ? lang.default_filename : 'main.py',
      path: '',
      content: lang ? lang.default_code : '',
      is_entry_point: true,
      is_directory: false
    };
    this.fileExplorer.loadFiles([defaultFile]);
    this.updateLanguageDropdown(lang);
    this.updateProjectTitle('Untitled Project');
  }

  async loadProject(projectId) {
    try {
      const data = await ApiClient.get(`/api/projects/${projectId}/`);
      this.project = data;
      this.projectId = data.id;

      if (data.language) {
        this.currentLanguage = this.languages.find(l => l.id === data.language.id) || data.language;
        this.updateLanguageDropdown(this.currentLanguage);
        this.debugger.setLanguage(this.currentLanguage);
      }

      this.updateProjectTitle(data.name);

      if (data.default_stdin && this.terminal) {
        this.terminal.setStdin(data.default_stdin);
      }

      // Load files
      this.fileExplorer.loadFiles(data.files || []);
      this.setSaveStatus('saved');
    } catch (err) {
      console.error('Failed to load project:', err);
      Toast.error('Failed to load project. Loading default workspace.');
      this.setupDefaultProject();
    }
  }

  handleFileSelected(file) {
    if (!file) {
      this.monaco.setValue('// No file open', 'plaintext');
      return;
    }
    const ext = file.name.split('.').pop();
    const langObj = this.languages.find(l => l.file_extension.replace('.', '') === ext);
    const monacoLang = langObj ? langObj.monaco_id : ext;

    this.monaco.setValue(file.content || '', monacoLang);
    this.monaco.focus();

    if (this.statusBar) {
      this.statusBar.updateContentMetrics(file.content || '');
    }
    if (this.livePreview && this.livePreview.autoReload) {
      this.livePreview.updatePreview();
    }
  }

  handleFileContentChanged(file) {
    this.isDirty = true;
    this.setSaveStatus('unsaved');
    if (this.statusBar) {
      this.statusBar.updateContentMetrics(file.content || '');
    }
    if (this.livePreview && this.livePreview.autoReload) {
      this.livePreview.updatePreview();
    }
  }

  triggerAutosave() {
    this.isDirty = true;
    this.setSaveStatus('unsaved');

    if (this.autosaveTimer) clearTimeout(this.autosaveTimer);
    this.autosaveTimer = setTimeout(() => {
      if (this.projectId && this.isDirty) {
        this.saveProject(true);
      }
    }, 2000);
  }

  setSaveStatus(status) {
    const indicator = document.getElementById('save-status-indicator');
    const label = document.getElementById('save-status-label');
    if (!indicator || !label) return;

    indicator.className = `save-status-indicator ${status}`;
    if (status === 'saved') label.textContent = 'Saved';
    else if (status === 'saving') label.textContent = 'Saving...';
    else if (status === 'unsaved') label.textContent = 'Unsaved changes';
  }

  updateProjectTitle(name) {
    const titleInput = document.getElementById('project-name-input');
    if (titleInput) titleInput.value = name;
  }

  toggleLanguageDropdown(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    const menu = document.getElementById('language-dropdown-menu');
    const btn = document.getElementById('language-dropdown-btn');
    if (menu) {
      const isShow = menu.classList.toggle('show');
      if (btn) {
        btn.setAttribute('aria-expanded', isShow ? 'true' : 'false');
      }
    }
  }

  updateLanguageDropdown(lang) {
    if (!lang) return;
    this.currentLanguage = lang;
    const nameEl = document.getElementById('current-language-name');
    if (nameEl) nameEl.textContent = `${lang.name} (${lang.version})`;
    if (this.statusBar) {
      this.statusBar.updateLanguage(lang);
    }
  }

  async setLanguage(langSlug) {
    // Dismiss language dropdown menu
    const menu = document.getElementById('language-dropdown-menu');
    const btn = document.getElementById('language-dropdown-btn');
    if (menu) {
      menu.classList.remove('show');
    }
    if (btn) {
      btn.setAttribute('aria-expanded', 'false');
    }

    if (!langSlug) return;

    if (!this.languages || this.languages.length === 0) {
      try {
        const scriptEl = document.getElementById('languages-data');
        if (scriptEl) {
          this.languages = JSON.parse(scriptEl.textContent || '[]');
        }
      } catch (e) {
        console.error('Failed to parse languages-data fallback:', e);
      }
    }

    const lang = this.languages.find(l => l.slug.toLowerCase() === langSlug.toLowerCase()) ||
                 this.languages.find(l => l.monaco_id === langSlug.toLowerCase()) ||
                 this.languages.find(l => l.name.toLowerCase() === langSlug.toLowerCase());
    if (!lang) {
      console.warn('Language not found for identifier:', langSlug);
      return;
    }

    this.currentLanguage = lang;
    this.updateLanguageDropdown(lang);
    if (this.debugger) {
      this.debugger.setLanguage(lang);
    }
    if (this.statusBar) {
      this.statusBar.updateLanguage(lang);
    }

    const activeFile = this.fileExplorer ? this.fileExplorer.getActiveFile() : null;
    if (activeFile && (activeFile.content === '' || activeFile.name.startsWith('main.') || activeFile.name.startsWith('index.') || activeFile.name.startsWith('App.'))) {
      const newName = lang.default_filename;
      activeFile.name = newName;
      activeFile.content = lang.default_code;
      if (this.fileExplorer) {
        this.fileExplorer.renderTree();
        this.fileExplorer.renderTabs();
      }
      if (this.monaco) {
        this.monaco.setValue(lang.default_code, lang.monaco_id);
      }
    } else if (this.monaco) {
      this.monaco.setLanguage(lang.monaco_id);
    }

    if (this.livePreview) {
      this.livePreview.updatePreview();
    }

    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }

    Toast.info(`Language set to ${lang.name} ${lang.version}`);
  }

  toggleZenMode() {
    document.body.classList.toggle('zen-focus-mode');
    const isZen = document.body.classList.contains('zen-focus-mode');
    if (this.monaco && this.monaco.editor) {
      setTimeout(() => this.monaco.editor.layout(), 200);
    }
    Toast.info(isZen ? 'Zen Focus Mode ENABLED (Press Esc or click icon to exit)' : 'Zen Focus Mode DISABLED');
  }

  copyActiveFileCode() {
    if (this.monaco) {
      const code = this.monaco.getValue();
      navigator.clipboard.writeText(code).then(() => {
        Toast.success('Current document code copied!');
      }).catch(() => {
        Toast.error('Failed to copy code');
      });
    }
  }

  async runCode() {
    if (this.isExecuting) return;

    // Sync active editor code from Monaco editor to file explorer model
    if (this.monaco) {
      const currentCode = this.monaco.getValue();
      this.fileExplorer.updateActiveFileContent(currentCode);
    }

    const files = this.fileExplorer.files.map(f => ({
      name: f.name,
      path: f.path || '',
      content: f.content,
      is_entry_point: f.is_entry_point,
      is_directory: f.is_directory
    }));

    const entryFile = this.fileExplorer.getActiveFile() ? this.fileExplorer.getActiveFile().name : (this.currentLanguage ? this.currentLanguage.default_filename : 'main.py');
    const stdinData = this.terminal ? this.terminal.getStdin() : '';

    this.isExecuting = true;
    this.terminal.showRunningState();
    const runBtn = document.getElementById('btn-run-code');
    if (runBtn) {
      runBtn.classList.add('btn-secondary');
      runBtn.innerHTML = '<i data-lucide="loader" class="spin" style="width:14px;height:14px;"></i> <span>Running...</span>';
      if (window.lucide) window.lucide.createIcons();
    }

    try {
      const payload = {
        project_id: this.projectId,
        language_slug: this.currentLanguage ? this.currentLanguage.slug : 'python',
        files: files,
        entry_file: entryFile,
        stdin: stdinData
      };

      const response = await ApiClient.post('/api/executions/', payload);
      const result = response.result || {};

      this.terminal.displayResult({
        status: response.status,
        stdout: result.stdout || '',
        stderr: result.stderr || '',
        exit_code: result.exit_code !== undefined ? result.exit_code : 0,
        execution_time_ms: response.execution_time_ms || 0,
        memory_bytes: result.memory_bytes || 0,
        status_message: result.status_message || ''
      });

      if (this.statusBar) {
        this.statusBar.updateExecutionStats(response.execution_time_ms || 0, result.memory_bytes || 0);
      }

      const isAwaitingInput = (result.stderr || '').includes('EOFError') || (result.status_message || '').includes('waiting for user input');

      if (response.status === 'completed' && !isAwaitingInput) {
        Toast.success('Execution finished cleanly');
      } else if (isAwaitingInput) {
        // Smoothly acknowledge that program is awaiting user input
        Toast.info('Awaiting your input in console...');
      } else if (response.status === 'timeout') {
        Toast.warning('Execution timed out (limit exceeded)');
      } else {
        Toast.error('Execution finished with errors');
      }

    } catch (error) {
      console.error('Execution request error:', error);
      this.terminal.displayResult({
        status: 'failed',
        stdout: '',
        stderr: `Network/Execution Error: ${error.message}`,
        exit_code: 1,
        execution_time_ms: 0,
        memory_bytes: 0,
        status_message: 'Request failed.'
      });
      Toast.error('Execution request failed');
    } finally {
      this.isExecuting = false;
      if (runBtn) {
        runBtn.className = 'btn btn-run';
        runBtn.innerHTML = '<i data-lucide="play" style="width:14px;height:14px;fill:currentColor;"></i> <span>Run</span>';
        if (window.lucide) window.lucide.createIcons();
      }
    }
  }

  toggleZenMode() {
    const isZen = document.body.classList.toggle('zen-focus-mode');
    if (isZen) {
      Toast.info('Zen Focus Mode (Press F11 to restore)');
    } else {
      Toast.info('Exited Zen Focus Mode');
    }
    if (this.monaco) {
      setTimeout(() => this.monaco.layout(), 120);
    }
  }

  debugCode() {
    this.debugger.startDebugging();
  }

  stopCode() {
    this.debugger.stopDebugging();
    Toast.info('Execution stopped.');
  }

  async saveProject(isAutosave = false) {
    this.setSaveStatus('saving');
    const projectName = document.getElementById('project-name-input').value.trim() || 'Untitled Project';

    try {
      if (!this.projectId) {
        // Create new project in backend
        const payload = {
          name: projectName,
          language_slug: this.currentLanguage ? this.currentLanguage.slug : 'python',
          default_stdin: this.terminal ? this.terminal.getStdin() : ''
        };

        const newProj = await ApiClient.post('/api/projects/', payload);
        this.projectId = newProj.id;
        this.project = newProj;

        // Upsert all local files into project and update their IDs
        for (const file of this.fileExplorer.files) {
          const created = await ApiClient.post(`/api/projects/${this.projectId}/files/`, {
            name: file.name,
            path: file.path || '',
            content: file.content,
            is_entry_point: file.is_entry_point,
            is_directory: file.is_directory
          });
          if (created && created.id) {
            file.id = created.id;
          }
        }

        // Update URL cleanly without page reload
        window.history.replaceState({}, '', `/ide/${this.projectId}/`);
      } else {
        // Update existing project
        await ApiClient.patch(`/api/projects/${this.projectId}/`, {
          name: projectName,
          language_id: this.currentLanguage ? this.currentLanguage.id : null,
          default_stdin: this.terminal ? this.terminal.getStdin() : ''
        });

        // Update files
        for (const file of this.fileExplorer.files) {
          if (file.id && !file.id.startsWith('local_') && !file.id.startsWith('temp_')) {
            await ApiClient.patch(`/api/files/${file.id}/`, {
              name: file.name,
              content: file.content
            });
          } else {
            const created = await ApiClient.post(`/api/projects/${this.projectId}/files/`, {
              name: file.name,
              path: file.path || '',
              content: file.content,
              is_entry_point: file.is_entry_point,
              is_directory: file.is_directory
            });
            if (created && created.id) {
              file.id = created.id;
            }
          }
        }
      }

      this.isDirty = false;
      this.fileExplorer.markSaved();
      this.setSaveStatus('saved');
      if (!isAutosave) {
        Toast.success('Project saved successfully');
      }
    } catch (err) {
      console.error('Save failed:', err);
      this.setSaveStatus('unsaved');
      Toast.error('Failed to save project: ' + err.message);
    }
  }

  formatCode() {
    this.monaco.formatCode();
    Toast.success('Code formatted');
  }

  async openShareModal() {
    if (!this.projectId) {
      await this.saveProject();
    }
    ModalsManager.open('share-project-modal');
    this.generateShareLink('read_only');
  }

  async generateShareLink(permission = 'read_only') {
    if (!this.projectId) return;
    try {
      const data = await ApiClient.post(`/api/projects/${this.projectId}/share/`, { permission });
      const inputEl = document.getElementById('share-url-input');
      const embedEl = document.getElementById('share-embed-code');
      if (inputEl) inputEl.value = data.share_url;
      if (embedEl) embedEl.value = data.embed_code;
    } catch (e) {
      Toast.error('Failed to generate share link: ' + (e.message || ''));
    }
  }

  copyShareLink() {
    const inputEl = document.getElementById('share-url-input');
    if (inputEl && inputEl.value) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(inputEl.value).then(() => {
          Toast.success('Share link copied to clipboard!');
        }).catch(() => {
          inputEl.select();
          document.execCommand('copy');
          Toast.success('Share link copied!');
        });
      } else {
        inputEl.select();
        document.execCommand('copy');
        Toast.success('Share link copied!');
      }
    }
  }

  copyEmbedCode() {
    const embedEl = document.getElementById('share-embed-code');
    if (embedEl && embedEl.value) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(embedEl.value).then(() => {
          Toast.success('Embed code copied!');
        }).catch(() => {
          embedEl.select();
          document.execCommand('copy');
          Toast.success('Embed code copied!');
        });
      } else {
        embedEl.select();
        document.execCommand('copy');
        Toast.success('Embed code copied!');
      }
    }
  }

  downloadProject() {
    if (this.projectId) {
      window.location.href = `/api/projects/${this.projectId}/download/`;
    } else {
      // Download active file directly
      const active = this.fileExplorer.getActiveFile();
      if (!active) return;
      const blob = new Blob([active.content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = active.name;
      a.click();
      URL.revokeObjectURL(url);
    }
  }

  openNewFileModal() {
    ModalsManager.open('new-file-modal');
    setTimeout(() => {
      const input = document.getElementById('new-file-name-input');
      if (input) { input.value = ''; input.focus(); }
    }, 100);
  }

  async createFileFromModal() {
    const nameInput = document.getElementById('new-file-name-input');
    const fileName = nameInput.value.trim();
    if (!fileName) {
      Toast.warning('Please enter a file name');
      return;
    }

    const newFile = this.fileExplorer.addFile({
      name: fileName,
      path: '',
      content: ''
    });

    ModalsManager.close('new-file-modal');

    // If project is already persisted on server, create file on server too
    if (this.projectId) {
      try {
        const created = await ApiClient.post(`/api/projects/${this.projectId}/files/`, {
          name: fileName,
          path: '',
          content: '',
          is_entry_point: false
        });
        if (created && created.id) {
          newFile.id = created.id;
        }
      } catch (e) {
        console.error('File server creation error:', e);
      }
    }

    Toast.success(`File ${fileName} created`);
  }

  async renameFileModal(fileId) {
    const file = this.fileExplorer.files.find(f => f.id === fileId);
    if (!file) return;
    const newName = prompt('Enter new file name:', file.name);
    if (newName && newName.trim() && newName !== file.name) {
      this.fileExplorer.renameFile(fileId, newName.trim());
      if (this.projectId && fileId && !fileId.startsWith('local_') && !fileId.startsWith('temp_')) {
        try {
          await ApiClient.patch(`/api/files/${fileId}/`, { name: newName.trim() });
        } catch (e) {
          console.error('Rename error on server:', e);
        }
      }
      Toast.success('File renamed');
    }
  }

  async deleteFileModal(fileId) {
    const file = this.fileExplorer.files.find(f => f.id === fileId);
    if (!file) return;
    if (confirm(`Are you sure you want to delete ${file.name}?`)) {
      this.fileExplorer.removeFile(fileId);
      if (this.projectId && fileId && !fileId.startsWith('local_') && !fileId.startsWith('temp_')) {
        try {
          await ApiClient.delete(`/api/files/${fileId}/`);
        } catch (e) {
          console.error('Delete error on server:', e);
        }
      }
      Toast.info(`File ${file.name} deleted`);
    }
  }

  openSettingsModal() {
    ModalsManager.open('settings-modal');
  }

  applySettings() {
    const theme = document.getElementById('setting-theme-select').value;
    const fontSize = parseInt(document.getElementById('setting-font-size-input').value, 10) || 14;
    const tabSize = parseInt(document.getElementById('setting-tab-size-input').value, 10) || 4;
    const wordWrap = document.getElementById('setting-word-wrap-toggle').checked ? 'on' : 'off';
    const minimap = document.getElementById('setting-minimap-toggle').checked;

    this.monaco.setTheme(theme);
    this.monaco.updateSettings({
      fontSize,
      tabSize,
      wordWrap,
      minimap: { enabled: minimap }
    });

    ModalsManager.close('settings-modal');
    Toast.success('Settings updated');
  }

  _initShortcuts() {
    ShortcutManager.init();
    ShortcutManager.register('ctrl+s', () => this.saveProject(), 'Save project');
    ShortcutManager.register('ctrl+enter', () => this.runCode(), 'Run program');
    ShortcutManager.register('f9', () => this.runCode(), 'Run program');
    ShortcutManager.register('f8', () => this.debugCode(), 'Debug program');
    ShortcutManager.register('ctrl+b', () => this.formatCode(), 'Format document');
    ShortcutManager.register('ctrl+p', () => this.commandPalette.toggle(), 'Command Palette');
    ShortcutManager.register('ctrl+k', () => this.commandPalette.toggle(), 'Command Palette');
    ShortcutManager.register('ctrl+m', () => this.openNewFileModal(), 'New file');
    ShortcutManager.register('ctrl+shift+s', () => this.openSettingsModal(), 'Settings');
    ShortcutManager.register('ctrl+shift+a', () => this.aiAssistant ? this.aiAssistant.toggleDrawer() : null, 'Toggle AI Assistant');
    ShortcutManager.register('ctrl+shift+l', () => this.snippets ? this.snippets.openModal() : null, 'Snippets Library');
    ShortcutManager.register('ctrl+shift+t', () => this.projectTemplates ? this.projectTemplates.openModal() : null, 'Project Templates');
    ShortcutManager.register('f11', () => this.toggleZenMode(), 'Toggle Zen Mode');
    ShortcutManager.register('escape', () => ModalsManager.closeAll(), 'Close modals');
  }

  _initResizers() {
    // Left Sidebar Horizontal Resizer
    const vResizer = document.getElementById('sidebar-resizer');
    const sidebar = document.getElementById('ide-sidebar');
    if (vResizer && sidebar) {
      let isResizing = false;
      vResizer.addEventListener('mousedown', (e) => {
        isResizing = true;
        vResizer.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
      });

      window.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const newWidth = Math.max(160, Math.min(e.clientX, 500));
        sidebar.style.width = `${newWidth}px`;
      });

      window.addEventListener('mouseup', () => {
        if (isResizing) {
          isResizing = false;
          vResizer.classList.remove('resizing');
          document.body.style.cursor = '';
        }
      });
    }

    // Bottom Dock Vertical Resizer
    const hResizer = document.getElementById('dock-resizer');
    const dock = document.getElementById('ide-bottom-dock');
    if (hResizer && dock) {
      let isResizing = false;
      hResizer.addEventListener('mousedown', () => {
        isResizing = true;
        hResizer.classList.add('resizing');
        document.body.style.cursor = 'row-resize';
      });

      window.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const newHeight = Math.max(80, Math.min(window.innerHeight - e.clientY, window.innerHeight * 0.7));
        dock.style.height = `${newHeight}px`;
      });

      window.addEventListener('mouseup', () => {
        if (isResizing) {
          isResizing = false;
          hResizer.classList.remove('resizing');
          document.body.style.cursor = '';
        }
      });
    }

    // Right AI Drawer Horizontal Resizer
    const aiResizer = document.getElementById('ai-resizer');
    const aiDrawer = document.getElementById('ai-assistant-drawer');
    if (aiResizer && aiDrawer) {
      let isResizing = false;
      aiResizer.addEventListener('mousedown', () => {
        isResizing = true;
        aiResizer.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
      });

      window.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const newWidth = Math.max(280, Math.min(window.innerWidth - e.clientX, 650));
        aiDrawer.style.width = `${newWidth}px`;
      });

      window.addEventListener('mouseup', () => {
        if (isResizing) {
          isResizing = false;
          aiResizer.classList.remove('resizing');
          document.body.style.cursor = '';
          if (this.monaco) this.monaco.layout();
        }
      });
    }
  }

  _initUIListeners() {
    // Language dropdown toggle
    const langBtn = document.getElementById('language-dropdown-btn');
    const langMenu = document.getElementById('language-dropdown-menu');
    const langWrapper = document.getElementById('language-dropdown-wrapper') || (langBtn ? langBtn.parentElement : null);

    if (langBtn && langMenu) {
      langBtn.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.toggleLanguageDropdown(e);
      };

      // Delegated click handler on language options inside the menu
      langMenu.onclick = (e) => {
        const option = e.target.closest('.language-option');
        if (option) {
          e.preventDefault();
          e.stopPropagation();
          const langSlug = option.getAttribute('data-lang') || option.dataset.lang;
          if (langSlug) {
            this.setLanguage(langSlug);
          }
          langMenu.classList.remove('show');
          if (langBtn) langBtn.setAttribute('aria-expanded', 'false');
        }
      };

      // Close dropdown when clicking anywhere outside
      document.addEventListener('click', (e) => {
        if (langWrapper && !langWrapper.contains(e.target)) {
          langMenu.classList.remove('show');
          if (langBtn) langBtn.setAttribute('aria-expanded', 'false');
        }
      });
    }

    // Project title input auto-width & save trigger
    const titleInput = document.getElementById('project-name-input');
    if (titleInput) {
      titleInput.addEventListener('change', () => this.triggerAutosave());
    }

    // Sidebar toggle button
    const sidebarToggle = document.getElementById('btn-toggle-sidebar');
    const sidebar = document.getElementById('ide-sidebar');
    if (sidebarToggle && sidebar) {
      sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
      });
    }
  }
}

window.CodeForgeIDE = CodeForgeIDE;
window.toggleAICopilot = function() {
  if (window.ide && window.ide.aiAssistant) {
    window.ide.aiAssistant.toggleDrawer();
  }
};
window.toggleLanguageDropdown = function(e) {
  if (window.ide) {
    window.ide.toggleLanguageDropdown(e);
  } else {
    const menu = document.getElementById('language-dropdown-menu');
    if (menu) menu.classList.toggle('show');
  }
};
window.setLanguage = function(slug) {
  if (window.ide) {
    window.ide.setLanguage(slug);
  }
};
