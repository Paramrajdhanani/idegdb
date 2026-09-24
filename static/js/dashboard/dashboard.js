/**
 * CodeForge IDE - Dashboard Controller
 */

class DashboardController {
  constructor() {
    this.currentFilter = 'all';
    this.searchQuery = '';
    this.currentLanguage = '';
    this.projects = [];
    this.stats = null;
  }

  async init() {
    await this.loadStats();
    await this.loadProjects();
    this._initEvents();
  }

  _initEvents() {
    // Search input
    const searchInput = document.getElementById('dashboard-search-input');
    if (searchInput) {
      let timeout = null;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          this.searchQuery = e.target.value.trim();
          this.loadProjects();
        }, 300);
      });
    }

    // Filter pills
    document.querySelectorAll('.filter-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.currentFilter = pill.getAttribute('data-filter');
        this.loadProjects();
      });
    });

    // Language filter dropdown
    const langFilter = document.getElementById('dashboard-language-filter');
    if (langFilter) {
      langFilter.addEventListener('change', (e) => {
        this.currentLanguage = e.target.value;
        this.loadProjects();
      });
    }
  }

  async loadStats() {
    try {
      const data = await ApiClient.get('/api/dashboard/stats/');
      this.stats = data;

      // Update stat cards
      const totalProjEl = document.getElementById('stat-total-projects');
      const totalExecEl = document.getElementById('stat-total-executions');
      const successRateEl = document.getElementById('stat-success-rate');
      const avgTimeEl = document.getElementById('stat-avg-time');

      if (totalProjEl) totalProjEl.textContent = data.total_projects;
      if (totalExecEl) totalExecEl.textContent = data.total_executions;
      if (successRateEl) successRateEl.textContent = `${data.success_rate}%`;
      if (avgTimeEl) avgTimeEl.textContent = `${data.avg_execution_time_ms}ms`;

      // Render 7-day activity sparkline bars
      const activityContainer = document.getElementById('activity-bars-container');
      if (activityContainer && data.activity) {
        const maxCount = Math.max(...data.activity.map(a => a.count), 1);
        activityContainer.innerHTML = data.activity.map(a => {
          const heightPercent = Math.max(8, (a.count / maxCount) * 100);
          return `
            <div class="activity-bar-col">
              <div class="activity-bar" style="height: ${heightPercent}%;" title="${a.count} runs on ${a.date}"></div>
              <span class="activity-date">${a.date}</span>
            </div>
          `;
        }).join('');
      }

    } catch (e) {
      console.error('Failed to load dashboard stats:', e);
    }
  }

  async loadProjects() {
    const container = document.getElementById('projects-grid-container');
    if (!container) return;

    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding: 40px; color:var(--text-dim);">
        <i data-lucide="loader" class="spin" style="width:24px;height:24px;"></i>
        <div style="margin-top:8px;">Loading projects...</div>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();

    try {
      const params = {};
      if (this.searchQuery) params.search = this.searchQuery;
      if (this.currentLanguage) params.language = this.currentLanguage;
      if (this.currentFilter === 'my') params.filter = 'my';
      if (this.currentFilter === 'favorite') params.favorite = 'true';
      if (this.currentFilter === 'public') params.filter = 'public';

      const data = await ApiClient.get('/api/projects/', params);
      this.projects = data.results || (Array.isArray(data) ? data : []);

      if (this.projects.length === 0) {
        container.innerHTML = `
          <div class="empty-state" style="grid-column: 1/-1;">
            <div class="empty-icon">
              <i data-lucide="folder-plus" style="width:28px;height:28px;"></i>
            </div>
            <h3 style="margin-bottom:8px;font-size:18px;">No projects found</h3>
            <p style="color:var(--text-muted);font-size:14px;margin-bottom:20px;">
              ${this.searchQuery ? 'Try adjusting your search query or filters.' : 'Create your first project and start coding.'}
            </p>
            <button class="btn btn-primary" onclick="dashboard.openNewProjectModal()">
              <i data-lucide="plus" style="width:14px;height:14px;"></i> Create Project
            </button>
          </div>
        `;
        if (window.lucide) window.lucide.createIcons();
        return;
      }

      container.innerHTML = this.projects.map(p => `
        <div class="project-card">
          <div>
            <div class="project-card-header">
              <div>
                <a href="/ide/${p.id}/" class="project-card-title">${p.name}</a>
                <div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
                  <span class="badge badge-primary">${p.language.name}</span>
                  <span class="badge badge-neutral">${p.file_count || 1} file(s)</span>
                  <span class="badge badge-neutral">${p.visibility}</span>
                </div>
              </div>
              <button class="btn btn-ghost btn-icon-only" title="${p.is_favorite ? 'Favorited' : 'Favorite'}" onclick="dashboard.toggleFavorite('${p.id}', ${!p.is_favorite})">
                <i data-lucide="star" style="width:16px;height:16px;${p.is_favorite ? 'color:#FFBD2E;fill:#FFBD2E;' : 'color:var(--text-dim);'}"></i>
              </button>
            </div>
            <p class="project-card-desc">${p.description || 'No description provided.'}</p>
          </div>

          <div class="project-card-footer">
            <span>Updated ${new Date(p.updated_at).toLocaleDateString()}</span>
            <div class="project-card-actions">
              <a href="/ide/${p.id}/" class="btn btn-sm btn-primary" title="Open in IDE">
                <i data-lucide="code" style="width:12px;height:12px;"></i> Open
              </a>
              <button class="btn btn-sm btn-secondary btn-icon-only" title="Duplicate Project" onclick="dashboard.duplicateProject('${p.id}')">
                <i data-lucide="copy" style="width:13px;height:13px;"></i>
              </button>
              <button class="btn btn-sm btn-secondary btn-icon-only" title="Download ZIP" onclick="window.location.href='/api/projects/${p.id}/download/'">
                <i data-lucide="download" style="width:13px;height:13px;"></i>
              </button>
              <button class="btn btn-sm btn-ghost btn-icon-only" title="Delete Project" onclick="dashboard.deleteProject('${p.id}', '${p.name}')">
                <i data-lucide="trash-2" style="width:13px;height:13px;color:var(--error);"></i>
              </button>
            </div>
          </div>
        </div>
      `).join('');

      if (window.lucide) window.lucide.createIcons();
    } catch (e) {
      console.error('Failed to load projects:', e);
      container.innerHTML = `<div style="grid-column: 1/-1; text-align:center; color:var(--error);">Failed to load projects.</div>`;
    }
  }

  openNewProjectModal() {
    ModalsManager.open('create-project-modal');
  }

  async createProject() {
    const nameInput = document.getElementById('create-project-name');
    const descInput = document.getElementById('create-project-desc');
    const langSelect = document.getElementById('create-project-language');

    const name = nameInput.value.trim() || 'Untitled Project';
    const description = descInput ? descInput.value.trim() : '';
    const langSlug = langSelect.value;

    try {
      const newProj = await ApiClient.post('/api/projects/', {
        name,
        description,
        language_slug: langSlug
      });

      Toast.success('Project created successfully!');
      ModalsManager.close('create-project-modal');
      window.location.href = `/ide/${newProj.id}/`;
    } catch (e) {
      Toast.error('Failed to create project: ' + e.message);
    }
  }

  async duplicateProject(projectId) {
    try {
      const copy = await ApiClient.post(`/api/projects/${projectId}/duplicate/`);
      Toast.success('Project duplicated!');
      this.loadProjects();
    } catch (e) {
      Toast.error('Failed to duplicate project: ' + e.message);
    }
  }

  async toggleFavorite(projectId, isFav) {
    try {
      await ApiClient.patch(`/api/projects/${projectId}/`, { is_favorite: isFav });
      this.loadProjects();
    } catch (e) {
      Toast.error('Failed to update favorite status');
    }
  }

  async deleteProject(projectId, projectName) {
    if (confirm(`Are you sure you want to permanently delete "${projectName}"?`)) {
      try {
        await ApiClient.delete(`/api/projects/${projectId}/`);
        Toast.success('Project deleted');
        this.loadProjects();
        this.loadStats();
      } catch (e) {
        Toast.error('Failed to delete project');
      }
    }
  }
}

window.DashboardController = DashboardController;
