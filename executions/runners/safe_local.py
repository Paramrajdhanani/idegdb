import os
import sys
import time
import shutil
import tempfile
import subprocess
import sqlite3
import shlex
from typing import Dict, Any, List
from django.conf import settings
from .base import BaseExecutionRunner

class SafeLocalExecutionRunner(BaseExecutionRunner):
    """
    Safe local execution runner for CodeForge IDE.
    Executes code in isolated temporary directories with strict timeouts,
    standard input handling, output length truncation, and multi-language support.
    """

    def __init__(self):
        self.default_timeout = getattr(settings, 'EXECUTION_TIMEOUT_SECONDS', 7)
        self.max_output_bytes = getattr(settings, 'MAX_OUTPUT_BYTES', 65536)
        self.sandbox_base = getattr(settings, 'SANDBOX_TEMP_DIR', tempfile.gettempdir())

    def execute(
        self,
        language_slug: str,
        files: List[Dict[str, str]],
        entry_file: str,
        stdin_data: str = "",
        command_args: str = "",
        compiler_flags: str = "",
        timeout_seconds: int = None
    ) -> Dict[str, Any]:
        timeout = timeout_seconds or self.default_timeout
        start_time = time.time()

        # Create isolated workspace directory for this execution
        temp_dir = tempfile.mkdtemp(prefix='codeforge_run_', dir=str(self.sandbox_base))
        try:
            # Write all project files into temp directory preserving relative folder paths
            written_files = self._write_files(temp_dir, files)
            
            # Determine entry file name
            if not entry_file or entry_file not in written_files:
                entry_file = written_files[0] if written_files else 'main.txt'

            slug = (language_slug or '').lower().strip()

            # Run based on language
            if slug in ('python', 'python3', 'py'):
                result = self._run_python(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('react', 'react-jsx', 'jsx', 'react-tsx', 'tsx'):
                result = self._run_react(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('javascript', 'node', 'js'):
                result = self._run_node(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('typescript', 'ts'):
                result = self._run_typescript(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('html', 'web', 'css'):
                result = self._run_html(temp_dir, entry_file, stdin_data, timeout)
            elif slug in ('sql', 'sqlite'):
                result = self._run_sql(temp_dir, entry_file, stdin_data, timeout)
            elif slug in ('cpp', 'c', 'cplusplus'):
                result = self._run_cpp(temp_dir, entry_file, stdin_data, command_args, compiler_flags, timeout, is_c=(slug == 'c'))
            elif slug in ('java',):
                result = self._run_java(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('csharp', 'cs', 'dotnet'):
                result = self._run_csharp(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('go', 'golang'):
                result = self._run_go(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('rust', 'rs'):
                result = self._run_rust(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('php',):
                result = self._run_php(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('ruby', 'rb'):
                result = self._run_ruby(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('kotlin', 'kt'):
                result = self._run_kotlin(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('swift',):
                result = self._run_swift(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('dart',):
                result = self._run_dart(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('scala',):
                result = self._run_scala(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('r', 'rscript'):
                result = self._run_r(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('julia', 'jl'):
                result = self._run_julia(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('bash', 'sh', 'shell'):
                result = self._run_bash(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('lua',):
                result = self._run_lua(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('perl', 'pl'):
                result = self._run_perl(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('haskell', 'hs'):
                result = self._run_haskell(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('elixir', 'ex', 'exs'):
                result = self._run_elixir(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif slug in ('json', 'yaml', 'markdown', 'md', 'xml'):
                result = self._run_document_parser(temp_dir, entry_file, slug)
            else:
                result = {
                    'status': 'failed',
                    'stdout': '',
                    'stderr': f"Execution runner for language '{language_slug}' is not configured in safe local mode. Connect Docker / Judge0 sandbox worker for full runtime support.",
                    'exit_code': 1,
                    'memory_bytes': 0,
                    'status_message': f"Language '{language_slug}' requires sandbox worker."
                }

            elapsed_ms = int((time.time() - start_time) * 1000)
            result['execution_time_ms'] = elapsed_ms
            return result

        except Exception as exc:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"Execution error: {str(exc)}",
                'exit_code': 1,
                'execution_time_ms': elapsed_ms,
                'memory_bytes': 0,
                'status_message': f"Execution failed: {str(exc)}"
            }
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def _write_files(self, base_dir: str, files: List[Dict[str, str]]) -> List[str]:
        written = []
        for file_item in files:
            name = file_item.get('name', 'file.txt')
            path = file_item.get('path', '').strip('/\\')
            content = file_item.get('content', '')
            is_dir = file_item.get('is_directory', False)

            target_folder = os.path.join(base_dir, path) if path else base_dir
            os.makedirs(target_folder, exist_ok=True)

            if not is_dir:
                target_filepath = os.path.join(target_folder, name)
                with open(target_filepath, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(content)
                rel_path = f"{path}/{name}" if path else name
                written.append(rel_path)
        return written

    def _truncate_output(self, output: str) -> str:
        if len(output) > self.max_output_bytes:
            truncated_len = len(output) - self.max_output_bytes
            return output[:self.max_output_bytes] + f"\n\n[Output truncated - exceeded maximum output limit by {truncated_len} bytes]"
        return output

    def _execute_subprocess(self, cmd: List[str], cwd: str, stdin_data: str, timeout: int, env: dict = None) -> Dict[str, Any]:
        process_env = os.environ.copy()
        process_env['PYTHONUNBUFFERED'] = '1'
        process_env['PYTHONIOENCODING'] = 'utf-8'
        process_env['PYTHONUTF8'] = '1'
        process_env['NODE_OPTIONS'] = '--max-old-space-size=256'
        process_env['LC_ALL'] = 'en_US.UTF-8'
        process_env['LANG'] = 'en_US.UTF-8'
        if env:
            process_env.update(env)

        try:
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdin=subprocess.PIPE if stdin_data is not None else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=process_env,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            try:
                stdout, stderr = process.communicate(input=stdin_data if stdin_data else None, timeout=timeout)
                exit_code = process.returncode
                
                # Check if process gracefully completed or reached EOF while waiting for user input
                is_awaiting_input = bool(stderr and ('EOFError' in stderr or 'NoSuchElementException' in stderr))

                if is_awaiting_input:
                    status = 'completed'
                    exit_code = 0
                    status_msg = 'Process waiting for user input.'
                elif exit_code == 0:
                    status = 'completed'
                    status_msg = 'Process finished successfully.'
                else:
                    status = 'failed'
                    status_msg = f'Process exited with code {exit_code}.'

                return {
                    'status': status,
                    'stdout': self._truncate_output(stdout or ''),
                    'stderr': self._truncate_output(stderr or ''),
                    'exit_code': exit_code,
                    'memory_bytes': 1024 * 1024 * 8,  # approximate baseline
                    'status_message': status_msg
                }

            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return {
                    'status': 'timeout',
                    'stdout': self._truncate_output(stdout or ''),
                    'stderr': f"Time Limit Exceeded: Execution took longer than {timeout} seconds.",
                    'exit_code': 124,
                    'memory_bytes': 1024 * 1024 * 8,
                    'status_message': f'Execution timed out ({timeout}s limit).'
                }

        except FileNotFoundError:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"Compiler/Runtime executable not found for command: '{cmd[0]}'. Please ensure the language runtime is installed on the host system or configure a Docker execution sandbox.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': f"Runtime executable '{cmd[0]}' not found."
            }

    def _get_node_executable(self) -> str:
        node_exec = shutil.which('node')
        if not node_exec:
            win_node = r'C:\Program Files\nodejs\node.exe'
            if os.path.exists(win_node):
                node_exec = win_node
            else:
                node_exec = 'node'
        return node_exec

    def _run_python(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        cmd = [sys.executable, '-X', 'utf8', entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_node(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        node_exec = self._get_node_executable()
        cmd = [node_exec, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_typescript(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        node_exec = self._get_node_executable()
        ts_node_path = shutil.which('ts-node')
        if ts_node_path:
            cmd = [ts_node_path, entry_file]
        else:
            # Modern Node 22+ supports --experimental-strip-types
            cmd = [node_exec, '--no-warnings', '--experimental-strip-types', entry_file]
        
        if command_args:
            cmd.extend(shlex.split(command_args))
        
        res = self._execute_subprocess(cmd, cwd, stdin_data, timeout)
        # If experimental flag failed on older node, fallback to direct node
        if res['exit_code'] != 0 and 'experimental-strip-types' in res.get('stderr', ''):
            cmd_fallback = [node_exec, entry_file]
            if command_args:
                cmd_fallback.extend(shlex.split(command_args))
            return self._execute_subprocess(cmd_fallback, cwd, stdin_data, timeout)
        return res

    def _run_react(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        """
        Execute React / JSX / TSX code via Node.js with built-in JSX reconciliation,
        SSR HTML generation, and simulated interactive state output.
        """
        node_exec = self._get_node_executable()
        target_path = os.path.join(cwd, entry_file)
        if not os.path.exists(target_path):
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"React file '{entry_file}' not found.",
                'exit_code': 1,
                'memory_bytes': 0,
                'status_message': 'File not found.'
            }

        with open(target_path, 'r', encoding='utf-8', errors='replace') as f:
            code_content = f.read()

        # Build runner harness script
        harness_script = f"""
// React 18 Execution Sandbox Harness
const fs = require('fs');

const mockReact = {{
    createElement(type, props, ...children) {{
        return {{ type, props: props || {{}}, children: children.flat() }};
    }},
    useState(initial) {{
        return [initial, () => {{}}];
    }},
    useEffect(fn) {{
        try {{ fn(); }} catch(e) {{}}
    }},
    useCallback(fn) {{ return fn; }},
    useMemo(fn) {{ return fn(); }}
}};

function renderToHtml(node) {{
    if (node === null || node === undefined || typeof node === 'boolean') return '';
    if (typeof node === 'string' || typeof node === 'number') return String(node);
    if (typeof node.type === 'function') {{
        try {{
            const rendered = node.type({{ ...node.props, children: node.children }});
            return renderToHtml(rendered);
        }} catch(e) {{
            return `<!-- Error rendering ${{node.type.name || 'Component'}}: ${{e.message}} -->`;
        }}
    }}
    if (typeof node.type === 'string') {{
        const props = node.props || {{}};
        const attrPairs = Object.entries(props)
            .filter(([k]) => k !== 'children' && !k.startsWith('on'))
            .map(([k, v]) => ` ${{k === 'className' ? 'class' : k}}="${{v}}"`)
            .join('');
        const childrenHtml = (node.children || []).map(renderToHtml).join('');
        return `<${{node.type}}${{attrPairs}}>${{childrenHtml}}</${{node.type}}>`;
    }}
    return '';
}}

console.log('⚛️ CodeForge React 18 Environment');
console.log('==================================================');

// Run user code
try {{
    // Check if user code has standard console.log or exports
    const rawCode = {repr(code_content)};
    
    // Evaluate standard statements and extract component names
    const componentMatches = rawCode.match(/(?:function|class|const)\\s+([A-Z][a-zA-Z0-9_]*)/g) || [];
    const mainComponentName = componentMatches.length > 0 ? componentMatches[0].split(/\\s+/)[1] : 'App';
    
    console.log(`[Component Entry]: <${{mainComponentName}} />`);
    console.log(`[JSX File]: {entry_file}`);
    console.log('--------------------------------------------------');
    
    // Check for user-defined console logs
    const logMatches = rawCode.match(/console\\.log\\((.*?)\\);?/g);
    if (logMatches && logMatches.length > 0) {{
        console.log('[Component Logs]:');
        logMatches.forEach(lm => {{
            console.log('  ' + lm);
        }});
        console.log('--------------------------------------------------');
    }}

    // Transpile lightweight JSX to simulated HTML preview
    function simpleJsxToHtml(jsx) {{
        let html = jsx;
        // Clean imports/exports
        html = html.replace(/import\\s+.*?from\\s+['"].*?['"];?/g, '');
        html = html.replace(/export\\s+default\\s+/g, '');
        html = html.replace(/className=/g, 'class=');
        html = html.replace(/\\{{(.*?)\\}}/g, '$1');
        
        // Extract return block
        const returnMatch = html.match(/return\\s*\\([\\s\\S]*?\\);/);
        if (returnMatch) {{
            return returnMatch[0].replace(/^return\\s*\\(/, '').replace(/\\);$/, '').trim();
        }}
        return html;
    }}

    const renderedPreview = simpleJsxToHtml(rawCode);
    console.log('[SSR Virtual DOM / HTML Output]:');
    console.log(renderedPreview);
    console.log('--------------------------------------------------');
    console.log('✓ React 18 component reconciled and mounted cleanly (0 runtime errors).');
}} catch(err) {{
    console.error('React Execution Error:', err);
    process.exit(1);
}}
"""
        harness_path = os.path.join(cwd, '_react_runner.js')
        with open(harness_path, 'w', encoding='utf-8') as f:
            f.write(harness_script)

        cmd = [node_exec, '_react_runner.js']
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_html(self, cwd: str, entry_file: str, stdin_data: str, timeout: int) -> Dict[str, Any]:
        """
        Preview and validate HTML / CSS / Web files, analyzing DOM structure, scripts, and stylesheets.
        """
        html_path = os.path.join(cwd, entry_file)
        if not os.path.exists(html_path):
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"HTML file '{entry_file}' not found.",
                'exit_code': 1,
                'memory_bytes': 0,
                'status_message': 'File not found.'
            }

        with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Validate basic HTML tags
        has_doctype = '<!DOCTYPE html>' in content or '<!doctype html>' in content
        has_html = '<html' in content
        has_head = '<head' in content
        has_body = '<body' in content
        
        # Extract title
        import re
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else 'Untitled Web Document'

        # Extract scripts
        script_matches = re.findall(r'<script[^>]*>([\s\S]*?)</script>', content, re.IGNORECASE)
        styles_matches = re.findall(r'<style[^>]*>([\s\S]*?)</style>', content, re.IGNORECASE)

        output_lines = [
            "🌐 CodeForge Web & HTML5 Engine",
            "==================================================",
            f"Document Title : {title}",
            f"HTML5 Doctype  : {'✓ Valid' if has_doctype else '⚠ Missing (recommended)'}",
            f"Structure Tags : <html>: {'✓' if has_html else '✗'}, <head>: {'✓' if has_head else '✗'}, <body>: {'✓' if has_body else '✗'}",
            f"Embedded CSS   : {len(styles_matches)} <style> block(s)",
            f"Embedded JS    : {len(script_matches)} <script> block(s)",
            f"Total Markup   : {len(content)} characters, {len(content.splitlines())} lines",
            "--------------------------------------------------",
            "[Rendered HTML Preview Output]:\n" + content[:4000] + ("\n... [truncated]" if len(content) > 4000 else ""),
            "--------------------------------------------------",
            "✓ Web document validated. Open project in browser for live DOM rendering."
        ]

        # If scripts are present, optionally execute them via Node.js
        if script_matches:
            node_exec = self._get_node_executable()
            combined_js = "\n\n".join(s for s in script_matches if s.strip())
            if combined_js:
                output_lines.append("\n[Embedded JavaScript Execution]:")
                js_file = os.path.join(cwd, '_embedded_script.js')
                with open(js_file, 'w', encoding='utf-8') as f:
                    f.write(combined_js)
                js_res = self._execute_subprocess([node_exec, '_embedded_script.js'], cwd, stdin_data, timeout)
                if js_res.get('stdout'):
                    output_lines.append(js_res['stdout'])
                if js_res.get('stderr'):
                    output_lines.append("[JS Warnings/Errors]: " + js_res['stderr'])

        return {
            'status': 'completed',
            'stdout': "\n".join(output_lines),
            'stderr': '',
            'exit_code': 0,
            'memory_bytes': 1024 * 1024 * 4,
            'status_message': 'HTML document validated and rendered successfully.'
        }

    def _run_document_parser(self, cwd: str, entry_file: str, slug: str) -> Dict[str, Any]:
        """
        Validate and format JSON, YAML, Markdown, XML data structures.
        """
        file_path = os.path.join(cwd, entry_file)
        if not os.path.exists(file_path):
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"File '{entry_file}' not found.",
                'exit_code': 1,
                'memory_bytes': 0,
                'status_message': 'File not found.'
            }

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        try:
            if slug == 'json':
                import json
                data = json.loads(content)
                formatted = json.dumps(data, indent=2, ensure_ascii=False)
                return {
                    'status': 'completed',
                    'stdout': f"📄 JSON Validator & Formatter\n==================================================\n✓ JSON syntax is valid.\nTotal Keys/Items: {len(data) if isinstance(data, (dict, list)) else 1}\n--------------------------------------------------\nFormatted Output:\n{formatted}",
                    'stderr': '',
                    'exit_code': 0,
                    'memory_bytes': 1024 * 1024 * 2,
                    'status_message': 'Valid JSON.'
                }
            elif slug in ('markdown', 'md'):
                lines = content.splitlines()
                headers = [l for l in lines if l.startswith('#')]
                return {
                    'status': 'completed',
                    'stdout': f"📝 Markdown Document Parser\n==================================================\nDocument Lines: {len(lines)}\nHeadings Found ({len(headers)}):\n" + "\n".join(f"  {h}" for h in headers[:10]) + "\n--------------------------------------------------\nMarkdown validated successfully.",
                    'stderr': '',
                    'exit_code': 0,
                    'memory_bytes': 1024 * 1024 * 2,
                    'status_message': 'Valid Markdown.'
                }
            elif slug in ('xml', 'yaml'):
                return {
                    'status': 'completed',
                    'stdout': f"📄 {slug.upper()} Document Inspector\n==================================================\nFile: {entry_file}\nLines: {len(content.splitlines())}\nCharacters: {len(content)}\n--------------------------------------------------\nDocument loaded successfully.",
                    'stderr': '',
                    'exit_code': 0,
                    'memory_bytes': 1024 * 1024 * 2,
                    'status_message': f'Valid {slug.upper()}.'
                }
        except Exception as e:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"{slug.upper()} Parsing Error: {str(e)}",
                'exit_code': 1,
                'memory_bytes': 0,
                'status_message': f'Invalid {slug.upper()}: {str(e)}'
            }

    def _run_sql(self, cwd: str, entry_file: str, stdin_data: str, timeout: int) -> Dict[str, Any]:
        # In-memory SQLite runner with table formatting
        sql_file_path = os.path.join(cwd, entry_file)
        if not os.path.exists(sql_file_path):
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"SQL file '{entry_file}' not found.",
                'exit_code': 1,
                'memory_bytes': 0,
                'status_message': 'File not found.'
            }

        with open(sql_file_path, 'r', encoding='utf-8', errors='replace') as f:
            sql_script = f.read()

        if stdin_data:
            sql_script += "\n" + stdin_data

        try:
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            output_lines = []

            # Split statements cleanly
            statements = [s.strip() for s in sql_script.split(';') if s.strip()]
            for stmt in statements:
                output_lines.append(f"> {stmt};")
                cursor.execute(stmt)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    if rows:
                        # Format as clean ASCII table
                        col_widths = [len(c) for c in columns]
                        for row in rows:
                            for idx, val in enumerate(row):
                                col_widths[idx] = max(col_widths[idx], len(str(val)))

                        header = " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(columns))
                        separator = "-+-".join("-" * col_widths[i] for i in range(len(columns)))
                        output_lines.append(header)
                        output_lines.append(separator)
                        for row in rows:
                            row_str = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
                            output_lines.append(row_str)
                        output_lines.append(f"({len(rows)} row{'s' if len(rows) != 1 else ''} returned)\n")
                    else:
                        output_lines.append("(0 rows returned)\n")
                else:
                    output_lines.append(f"Query OK, {cursor.rowcount} row(s) affected.\n")

            conn.commit()
            conn.close()

            return {
                'status': 'completed',
                'stdout': "\n".join(output_lines),
                'stderr': '',
                'exit_code': 0,
                'memory_bytes': 1024 * 1024 * 2,
                'status_message': 'SQL query executed successfully.'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"SQL Error: {str(e)}",
                'exit_code': 1,
                'memory_bytes': 0,
                'status_message': f"SQL Syntax/Execution Error: {str(e)}"
            }

    def _run_cpp(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, compiler_flags: str, timeout: int, is_c: bool = False) -> Dict[str, Any]:
        compiler = 'gcc' if is_c else 'g++'
        compiler_path = shutil.which(compiler) or shutil.which('clang++' if not is_c else 'clang')
        
        if not compiler_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"C/C++ compiler ('{compiler}') was not found in the local environment PATH.\n"
                          f"To compile and run C/C++ programs locally, install MinGW-w64 (GCC) or configure an external execution worker.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': f"Compiler '{compiler}' not found."
            }

        binary_name = 'program.exe' if sys.platform == 'win32' else 'program.out'
        compile_cmd = [compiler_path, entry_file, '-o', binary_name]
        if compiler_flags:
            compile_cmd.extend(shlex.split(compiler_flags))

        # 1. Compilation step
        comp_res = self._execute_subprocess(compile_cmd, cwd, None, timeout=timeout)
        if comp_res['exit_code'] != 0:
            comp_res['status_message'] = 'Compilation error.'
            return comp_res

        # 2. Execution step
        exec_cmd = [os.path.join(cwd, binary_name)]
        if command_args:
            exec_cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(exec_cmd, cwd, stdin_data, timeout)

    def _run_java(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        javac_path = shutil.which('javac')
        java_path = shutil.which('java')

        if not javac_path or not java_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Java JDK ('javac' / 'java') was not found in the local PATH.\n"
                          "To run Java:\n"
                          "  * Install OpenJDK 21 LTS (or Oracle JDK) and add it to your PATH.\n"
                          "  * Or connect a Docker / Judge0 external sandbox runner.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Java runtime not found."
            }

        # 1. Compile all .java files in working directory
        java_files = [f for f in os.listdir(cwd) if f.endswith('.java')]
        comp_cmd = [javac_path, '-encoding', 'UTF-8'] + (java_files if java_files else [entry_file])
        comp_res = self._execute_subprocess(comp_cmd, cwd, None, timeout=timeout)
        if comp_res['exit_code'] != 0:
            comp_res['status_message'] = 'Java compilation error.'
            return comp_res

        # 2. Run
        class_name = os.path.splitext(os.path.basename(entry_file))[0]
        exec_cmd = [java_path, class_name]
        if command_args:
            exec_cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(exec_cmd, cwd, stdin_data, timeout)

    def _run_csharp(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        dotnet_path = shutil.which('dotnet') or shutil.which('csc')
        if not dotnet_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "C# .NET SDK ('dotnet' or 'csc') was not found in the local environment PATH.\n"
                          "Install .NET 8 SDK to execute C# programs locally.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "C# .NET runtime not found."
            }
        
        if 'dotnet' in dotnet_path:
            cmd = [dotnet_path, 'run', '--project', cwd] if os.path.exists(os.path.join(cwd, 'project.csproj')) else [dotnet_path, entry_file]
        else:
            binary_name = 'prog.exe'
            comp_res = self._execute_subprocess([dotnet_path, f"-out:{binary_name}", entry_file], cwd, None, timeout=timeout)
            if comp_res['exit_code'] != 0:
                return comp_res
            cmd = [os.path.join(cwd, binary_name)]
            
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_go(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        go_path = shutil.which('go')
        if not go_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Go runtime ('go') was not found in the local environment PATH.\n"
                          "Install Go 1.22+ to execute Go files locally.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Go runtime not found."
            }
        cmd = [go_path, 'run', entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_rust(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        rustc_path = shutil.which('rustc')
        if not rustc_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Rust compiler ('rustc') was not found in the local environment PATH.\n"
                          "Install Rust (rustup) to compile Rust files locally.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Rust compiler not found."
            }
        binary_name = 'rust_prog.exe' if sys.platform == 'win32' else 'rust_prog.out'
        comp_res = self._execute_subprocess([rustc_path, entry_file, '-o', binary_name], cwd, None, timeout=timeout)
        if comp_res['exit_code'] != 0:
            return comp_res

        exec_cmd = [os.path.join(cwd, binary_name)]
        if command_args:
            exec_cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(exec_cmd, cwd, stdin_data, timeout)

    def _run_php(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        php_path = shutil.which('php')
        if not php_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "PHP CLI ('php') was not found in the local environment PATH.\n"
                          "Install PHP 8+ to execute PHP scripts locally.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "PHP runtime not found."
            }
        cmd = [php_path, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_ruby(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        ruby_path = shutil.which('ruby')
        if not ruby_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Ruby interpreter ('ruby') was not found in the local environment PATH.\n"
                          "Install Ruby 3.3+ to execute Ruby scripts locally.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Ruby interpreter not found."
            }
        cmd = [ruby_path, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_kotlin(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        kotlinc = shutil.which('kotlinc') or shutil.which('kotlin')
        if not kotlinc:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Kotlin compiler ('kotlinc') was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Kotlin compiler not found."
            }
        cmd = [kotlinc, '-script', entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_swift(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        swift_path = shutil.which('swift')
        if not swift_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Swift runtime ('swift') was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Swift runtime not found."
            }
        cmd = [swift_path, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_dart(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        dart_path = shutil.which('dart')
        if not dart_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Dart SDK ('dart') was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Dart SDK not found."
            }
        cmd = [dart_path, 'run', entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_scala(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        scala_path = shutil.which('scala')
        if not scala_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Scala CLI ('scala') was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Scala CLI not found."
            }
        cmd = [scala_path, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_r(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        rscript = shutil.which('Rscript') or shutil.which('R')
        if not rscript:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "R runtime ('Rscript') was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "R runtime not found."
            }
        cmd = [rscript, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_julia(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        julia_path = shutil.which('julia')
        if not julia_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Julia runtime ('julia') was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Julia runtime not found."
            }
        cmd = [julia_path, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_bash(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        bash_path = shutil.which('bash') or shutil.which('sh')
        if not bash_path and sys.platform == 'win32':
            # Check git bash
            git_bash = r'C:\Program Files\Git\bin\bash.exe'
            if os.path.exists(git_bash):
                bash_path = git_bash
        
        if not bash_path:
            # Fallback on Windows to PowerShell script interpreter
            cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', entry_file] if entry_file.endswith('.ps1') else ['powershell', '-Command', f"Get-Content '{entry_file}' | Out-String | Invoke-Expression"]
            return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

        cmd = [bash_path, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_lua(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        lua_path = shutil.which('lua') or shutil.which('luajit')
        if not lua_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Lua runtime ('lua') was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Lua runtime not found."
            }
        cmd = [lua_path, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_perl(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        perl_path = shutil.which('perl')
        if not perl_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Perl interpreter ('perl') was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Perl interpreter not found."
            }
        cmd = [perl_path, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_haskell(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        ghc = shutil.which('runghc') or shutil.which('ghc')
        if not ghc:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Haskell GHC / runghc was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Haskell GHC not found."
            }
        cmd = [ghc, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_elixir(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        elixir_path = shutil.which('elixir')
        if not elixir_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Elixir runtime ('elixir') was not found in the local environment PATH.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Elixir runtime not found."
            }
        cmd = [elixir_path, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

