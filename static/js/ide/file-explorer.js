/**
 * CodeForge IDE - File Explorer & Multi-Tab File Manager
 */

class FileExplorer {
  constructor(treeContainerId, tabsContainerId, breadcrumbsId, options = {}) {
    this.treeContainer = document.getElementById(treeContainerId);
    this.tabsContainer = document.getElementById(tabsContainerId);
    this.breadcrumbsEl = document.getElementById(breadcrumbsId);
    this.options = options;

    this.files = []; // List of file objects: { id, name, path, content, is_entry_point, is_directory, isDirty }
    this.openTabs = []; // List of file IDs currently in open tabs
    this.activeFileId = null;

    this.onFileSelectCallback = null;
    this.onFileChangeCallback = null;
  }

  loadFiles(files, defaultEntryId = null) {
    this.files = files.map(f => ({
      ...f,
      isDirty: false
    }));

    // Find initial file to open
    let initialFile = null;
    if (defaultEntryId) {
      initialFile = this.files.find(f => f.id === defaultEntryId);
    }
    if (!initialFile) {
      initialFile = this.files.find(f => f.is_entry_point && !f.is_directory);
    }
    if (!initialFile && this.files.length > 0) {
      initialFile = this.files.find(f => !f.is_directory);
    }

    if (initialFile) {
      this.openFile(initialFile.id);
    }

    this.renderTree();
    this.renderTabs();
  }

  getActiveFile() {
    return this.files.find(f => f.id === this.activeFileId) || null;
  }

  openFile(fileId) {
    const file = this.files.find(f => f.id === fileId);
    if (!file || file.is_directory) return;

    if (!this.openTabs.includes(fileId)) {
      this.openTabs.push(fileId);
    }
    this.activeFileId = fileId;

    this.renderTabs();
    this.renderTree();
    this.updateBreadcrumbs();

    if (this.onFileSelectCallback) {
      this.onFileSelectCallback(file);
    }
  }

  closeTab(fileId, event) {
    if (event) event.stopPropagation();

    this.openTabs = this.openTabs.filter(id => id !== fileId);

    if (this.activeFileId === fileId) {
      if (this.openTabs.length > 0) {
        this.openFile(this.openTabs[this.openTabs.length - 1]);
      } else {
        this.activeFileId = null;
        if (this.onFileSelectCallback) {
          this.onFileSelectCallback(null);
        }
      }
    }

    this.renderTabs();
    this.updateBreadcrumbs();
  }

  updateActiveFileContent(newContent) {
    const activeFile = this.getActiveFile();
    if (activeFile) {
      if (activeFile.content !== newContent) {
        activeFile.content = newContent;
        activeFile.isDirty = true;
        this.renderTabs();
        if (this.onFileChangeCallback) {
          this.onFileChangeCallback(activeFile);
        }
      }
    }
  }

  markSaved() {
    this.files.forEach(f => f.isDirty = false);
    this.renderTabs();
  }

  getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    switch (ext) {
      case 'py': return 'code-2';
      case 'js': case 'ts': return 'file-code';
      case 'cpp': case 'c': case 'h': case 'hpp': return 'cpu';
      case 'java': return 'coffee';
      case 'sql': return 'database';
      case 'rs': return 'shield';
      case 'go': return 'zap';
      case 'json': return 'braces';
      case 'md': case 'txt': return 'file-text';
      default: return 'file';
    }
  }

  renderTree() {
    if (!this.treeContainer) return;
    this.treeContainer.innerHTML = '';

    if (this.files.length === 0) {
      this.treeContainer.innerHTML = `
        <div style="padding:16px;text-align:center;color:var(--text-dim);font-size:12px;">
          No files in project
        </div>
      `;
      return;
    }

    // Group files by path
    const nonDirs = this.files.filter(f => !f.is_directory);
    nonDirs.forEach(file => {
      const el = document.createElement('div');
      el.className = `file-tree-item ${file.id === this.activeFileId ? 'active' : ''} ${file.path ? 'file-indent-1' : ''}`;
      
      const iconName = this.getFileIcon(file.name);
      const isEntryBadge = file.is_entry_point ? '<span style="font-size:9px;color:var(--accent-primary);margin-left:4px;">[main]</span>' : '';

      el.innerHTML = `
        <div class="file-item-left" title="${file.path ? file.path + '/' : ''}${file.name}">
          <i data-lucide="${iconName}" style="width:15px;height:15px;"></i>
          <span>${file.name}</span>
          ${isEntryBadge}
        </div>
        <div class="file-item-actions">
          <button class="btn btn-ghost btn-icon-only" title="Rename file" onclick="ide.renameFileModal('${file.id}')">
            <i data-lucide="edit-2" style="width:12px;height:12px;"></i>
          </button>
          <button class="btn btn-ghost btn-icon-only" title="Delete file" onclick="ide.deleteFileModal('${file.id}')">
            <i data-lucide="trash-2" style="width:12px;height:12px;color:var(--error);"></i>
          </button>
        </div>
      `;

      el.addEventListener('click', (e) => {
        if (!e.target.closest('.file-item-actions')) {
          this.openFile(file.id);
        }
      });

      this.treeContainer.appendChild(el);
    });

    if (window.lucide) window.lucide.createIcons();
  }

  renderTabs() {
    if (!this.tabsContainer) return;
    this.tabsContainer.innerHTML = '';

    this.openTabs.forEach(tabId => {
      const file = this.files.find(f => f.id === tabId);
      if (!file) return;

      const tabEl = document.createElement('div');
      tabEl.className = `editor-tab ${file.id === this.activeFileId ? 'active' : ''} ${file.isDirty ? 'dirty' : ''}`;

      const iconName = this.getFileIcon(file.name);
      tabEl.innerHTML = `
        <i data-lucide="${iconName}" style="width:14px;height:14px;"></i>
        <span>${file.name}</span>
        <span class="tab-dirty-indicator"></span>
        <button class="tab-close-btn btn-ghost" title="Close">
          <i data-lucide="x" style="width:12px;height:12px;"></i>
        </button>
      `;

      tabEl.addEventListener('click', () => this.openFile(file.id));
      const closeBtn = tabEl.querySelector('.tab-close-btn');
      closeBtn.addEventListener('click', (e) => this.closeTab(file.id, e));

      this.tabsContainer.appendChild(tabEl);
    });

    if (window.lucide) window.lucide.createIcons();
  }

  updateBreadcrumbs() {
    if (!this.breadcrumbsEl) return;
    const activeFile = this.getActiveFile();
    if (!activeFile) {
      this.breadcrumbsEl.innerHTML = '<span>No active file</span>';
      return;
    }

    const parts = [];
    if (activeFile.path) {
      parts.push(...activeFile.path.split('/'));
    }
    parts.push(activeFile.name);

    this.breadcrumbsEl.innerHTML = parts.map((p, idx) => `
      <span>${p}</span>
      ${idx < parts.length - 1 ? '<i data-lucide="chevron-right" style="width:10px;height:10px;"></i>' : ''}
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  }

  addFile(fileData) {
    const newFile = {
      id: fileData.id || 'temp_' + Date.now(),
      name: fileData.name,
      path: fileData.path || '',
      content: fileData.content || '',
      is_entry_point: fileData.is_entry_point || false,
      is_directory: fileData.is_directory || false,
      isDirty: false
    };
    this.files.push(newFile);
    this.openFile(newFile.id);
    return newFile;
  }

  removeFile(fileId) {
    this.closeTab(fileId);
    this.files = this.files.filter(f => f.id !== fileId);
    this.renderTree();
  }

  renameFile(fileId, newName) {
    const file = this.files.find(f => f.id === fileId);
    if (file) {
      file.name = newName;
      this.renderTree();
      this.renderTabs();
      this.updateBreadcrumbs();
    }
  }
}

window.FileExplorer = FileExplorer;
