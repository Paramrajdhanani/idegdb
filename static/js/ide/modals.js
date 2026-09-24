/**
 * CodeForge IDE - Modals Manager (Share, Settings, Shortcuts, File CRUD)
 */

class ModalsManager {
  static open(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
    }
  }

  static close(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
    }
  }

  static closeAll() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
    if (window.ide && window.ide.commandPalette) {
      window.ide.commandPalette.hide();
    }
  }
}

window.ModalsManager = ModalsManager;
