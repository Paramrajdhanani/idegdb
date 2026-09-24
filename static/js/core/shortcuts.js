/**
 * CodeForge IDE - Global Keyboard Shortcuts Listener
 */

class ShortcutManager {
  static shortcuts = {};

  static register(keyCombo, handler, description = '') {
    ShortcutManager.shortcuts[keyCombo.toLowerCase()] = { handler, description };
  }

  static init() {
    window.addEventListener('keydown', (e) => {
      const isCtrlOrCmd = e.ctrlKey || e.metaKey;
      const isShift = e.shiftKey;
      const key = e.key.toLowerCase();

      let combo = [];
      if (isCtrlOrCmd) combo.push('ctrl');
      if (isShift) combo.push('shift');
      combo.push(key);

      const comboStr = combo.join('+');

      if (ShortcutManager.shortcuts[comboStr]) {
        e.preventDefault();
        ShortcutManager.shortcuts[comboStr].handler(e);
      } else if (key === 'f9') {
        e.preventDefault();
        if (ShortcutManager.shortcuts['ctrl+enter']) {
          ShortcutManager.shortcuts['ctrl+enter'].handler(e);
        }
      } else if (key === 'f8') {
        e.preventDefault();
        if (ShortcutManager.shortcuts['f8']) {
          ShortcutManager.shortcuts['f8'].handler(e);
        }
      } else if (key === 'escape') {
        if (ShortcutManager.shortcuts['escape']) {
          ShortcutManager.shortcuts['escape'].handler(e);
        }
      }
    });
  }
}

window.ShortcutManager = ShortcutManager;
