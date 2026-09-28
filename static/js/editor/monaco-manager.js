/**
 * CodeForge IDE - Monaco Editor Integration Controller
 */

class MonacoManager {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.editor = null;
    this.currentModel = null;
    this.options = {
      theme: 'codeforge-dark',
      fontSize: 14,
      tabSize: 4,
      wordWrap: 'on',
      minimap: { enabled: true },
      automaticLayout: true,
      fontFamily: "'JetBrains Mono', 'Fira Code', Menlo, Monaco, Consolas, monospace",
      fontLigatures: true,
      bracketPairColorization: { enabled: true },
      lineNumbers: 'on',
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: 'on',
      smoothScrolling: true,
      renderWhitespace: 'selection',
      padding: { top: 12, bottom: 12 },
      ...options
    };
    this.onContentChangeCallbacks = [];
  }

  async init(initialCode = '', language = 'python') {
    return new Promise((resolve) => {
      // Configure Monaco AMD loader path
      window.require.config({
        paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }
      });

      window.require(['vs/editor/editor.main'], () => {
        this._defineThemes();

        this.editor = monaco.editor.create(this.container, {
          value: initialCode,
          language: this._mapLanguage(language),
          ...this.options
        });

        // Listen for content changes
        this.editor.onDidChangeModelContent((e) => {
          const value = this.editor.getValue();
          this.onContentChangeCallbacks.forEach((cb) => cb(value, e));
          if (window.ide && window.ide.statusBar) {
            window.ide.statusBar.updateContentMetrics(value);
          }
          if (window.ide && window.ide.livePreview && window.ide.livePreview.autoReload) {
            window.ide.livePreview.updatePreview();
          }
        });

        // Listen for cursor position changes
        this.editor.onDidChangeCursorPosition((e) => {
          if (window.ide && window.ide.statusBar) {
            window.ide.statusBar.updateCursor(e.position.lineNumber, e.position.column);
          }
        });

        // Add Keybindings to Monaco instance
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
          if (window.ide) window.ide.saveProject();
        });
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
          if (window.ide) window.ide.runCode();
        });
        this.editor.addCommand(monaco.KeyCode.F9, () => {
          if (window.ide) window.ide.runCode();
        });
        this.editor.addCommand(monaco.KeyCode.F8, () => {
          if (window.ide) window.ide.debugCode();
        });
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyB, () => {
          if (window.ide) window.ide.formatCode();
        });
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyP, () => {
          if (window.ide && window.ide.commandPalette) window.ide.commandPalette.toggle();
        });
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyM, () => {
          if (window.ide) window.ide.openNewFileModal();
        });
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyA, () => {
          if (window.ide && window.ide.aiAssistant) window.ide.aiAssistant.toggle();
        });

        resolve(this.editor);
      });
    });
  }

  _defineThemes() {
    // 1. CodeForge Dark Custom Theme
    monaco.editor.defineTheme('codeforge-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '8B949E', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'FF7B72', fontStyle: 'bold' },
        { token: 'string', foreground: 'A5D6FF' },
        { token: 'number', foreground: '79C0FF' },
        { token: 'type', foreground: 'FFA657' },
        { token: 'function', foreground: 'D2A8FF' },
        { token: 'variable', foreground: 'E6EDF3' },
      ],
      colors: {
        'editor.background': '#0B0D10',
        'editor.foreground': '#E6EDF3',
        'editor.lineHighlightBackground': '#161B22',
        'editorLineNumber.foreground': '#484F58',
        'editorLineNumber.activeForeground': '#E6EDF3',
        'editorCursor.foreground': '#6C63FF',
        'editor.selectionBackground': '#264F78',
        'editor.inactiveSelectionBackground': '#1F242C',
        'editorIndentGuide.background': '#21262D',
        'editorIndentGuide.activeBackground': '#30363D',
      }
    });

    // 2. Midnight High Contrast Theme
    monaco.editor.defineTheme('midnight', {
      base: 'hc-black',
      inherit: true,
      rules: [],
      colors: {
        'editor.background': '#000000',
        'editor.foreground': '#FFFFFF',
        'editor.lineHighlightBackground': '#111111',
        'editorCursor.foreground': '#00D2FF',
      }
    });

    monaco.editor.setTheme(this.options.theme || 'codeforge-dark');
  }

  _mapLanguage(lang) {
    if (!lang) return 'plaintext';
    const map = {
      'python': 'python',
      'python3': 'python',
      'py': 'python',
      'react': 'javascript',
      'react-jsx': 'javascript',
      'react-tsx': 'typescript',
      'jsx': 'javascript',
      'tsx': 'typescript',
      'javascript': 'javascript',
      'node': 'javascript',
      'js': 'javascript',
      'typescript': 'typescript',
      'ts': 'typescript',
      'cpp': 'cpp',
      'c++': 'cpp',
      'c': 'c',
      'java': 'java',
      'sql': 'sql',
      'sqlite': 'sql',
      'rust': 'rust',
      'rs': 'rust',
      'go': 'go',
      'golang': 'go',
      'csharp': 'csharp',
      'cs': 'csharp',
      'php': 'php',
      'ruby': 'ruby',
      'rb': 'ruby',
      'kotlin': 'kotlin',
      'kt': 'kotlin',
      'swift': 'swift',
      'dart': 'dart',
      'scala': 'scala',
      'r': 'r',
      'julia': 'julia',
      'jl': 'julia',
      'bash': 'shell',
      'sh': 'shell',
      'shell': 'shell',
      'zsh': 'shell',
      'lua': 'lua',
      'perl': 'perl',
      'pl': 'perl',
      'haskell': 'haskell',
      'hs': 'haskell',
      'elixir': 'elixir',
      'ex': 'elixir',
      'exs': 'elixir',
      'html': 'html',
      'web': 'html',
      'css': 'css',
      'json': 'json',
      'yaml': 'yaml',
      'yml': 'yaml',
      'xml': 'xml',
      'markdown': 'markdown',
      'md': 'markdown'
    };
    return map[lang.toLowerCase()] || 'plaintext';
  }

  setValue(code, language = null) {
    if (!this.editor) return;
    this.editor.setValue(code);
    if (language) {
      this.setLanguage(language);
    }
  }

  getValue() {
    return this.editor ? this.editor.getValue() : '';
  }

  setLanguage(language) {
    if (!this.editor) return;
    const monacoLang = this._mapLanguage(language);
    const model = this.editor.getModel();
    if (model) {
      monaco.editor.setModelLanguage(model, monacoLang);
    }
  }

  setTheme(themeName) {
    if (window.monaco) {
      monaco.editor.setTheme(themeName);
    }
  }

  updateSettings(settings) {
    if (!this.editor) return;
    this.editor.updateOptions(settings);
  }

  toggleWordWrap() {
    if (!this.editor) return;
    const current = this.editor.getOption(monaco.editor.EditorOption.wordWrap);
    const newVal = current === 'on' ? 'off' : 'on';
    this.editor.updateOptions({ wordWrap: newVal });
    Toast.info(`Word Wrap: ${newVal.toUpperCase()}`);
  }

  toggleMinimap() {
    if (!this.editor) return;
    const current = this.editor.getOption(monaco.editor.EditorOption.minimap).enabled;
    this.editor.updateOptions({ minimap: { enabled: !current } });
    Toast.info(`Minimap: ${!current ? 'ENABLED' : 'DISABLED'}`);
  }

  adjustFontSize(delta) {
    if (!this.editor) return;
    const current = this.editor.getOption(monaco.editor.EditorOption.fontSize) || 14;
    const nextSize = Math.max(10, Math.min(28, current + delta));
    this.editor.updateOptions({ fontSize: nextSize });
    Toast.info(`Font Size: ${nextSize}px`);
  }

  formatCode() {
    if (!this.editor) return;
    const action = this.editor.getAction('editor.action.formatDocument');
    if (action) {
      action.run();
    }
  }

  onContentChange(callback) {
    this.onContentChangeCallbacks.push(callback);
  }

  focus() {
    if (this.editor) this.editor.focus();
  }
}

window.MonacoManager = MonacoManager;
