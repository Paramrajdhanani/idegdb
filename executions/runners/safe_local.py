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

            # Run based on language
            if language_slug in ('python', 'python3', 'py'):
                result = self._run_python(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif language_slug in ('javascript', 'node', 'js', 'typescript', 'ts'):
                result = self._run_node(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif language_slug in ('sql', 'sqlite'):
                result = self._run_sql(temp_dir, entry_file, stdin_data, timeout)
            elif language_slug in ('cpp', 'c', 'cplusplus'):
                result = self._run_cpp(temp_dir, entry_file, stdin_data, command_args, compiler_flags, timeout, is_c=(language_slug == 'c'))
            elif language_slug in ('java',):
                result = self._run_java(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif language_slug in ('go', 'golang'):
                result = self._run_go(temp_dir, entry_file, stdin_data, command_args, timeout)
            elif language_slug in ('rust', 'rs'):
                result = self._run_rust(temp_dir, entry_file, stdin_data, command_args, timeout)
            else:
                result = {
                    'status': 'failed',
                    'stdout': '',
                    'stderr': f"Execution runner for language '{language_slug}' is not supported in safe local mode. Connect Docker / Judge0 sandbox worker for full runtime support.",
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

    def _run_python(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        cmd = [sys.executable, '-X', 'utf8', entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

    def _run_node(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        node_exec = shutil.which('node')
        if not node_exec:
            win_node = r'C:\Program Files\nodejs\node.exe'
            if os.path.exists(win_node):
                node_exec = win_node
            else:
                node_exec = 'node'
        cmd = [node_exec, entry_file]
        if command_args:
            cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(cmd, cwd, stdin_data, timeout)

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
                          "Install OpenJDK to run Java files locally or connect to Judge0 sandbox worker.",
                'exit_code': 127,
                'memory_bytes': 0,
                'status_message': "Java runtime not found."
            }

        # 1. Compile
        comp_res = self._execute_subprocess([javac_path, entry_file], cwd, None, timeout=timeout)
        if comp_res['exit_code'] != 0:
            comp_res['status_message'] = 'Java compilation error.'
            return comp_res

        # 2. Run
        class_name = os.path.splitext(os.path.basename(entry_file))[0]
        exec_cmd = [java_path, class_name]
        if command_args:
            exec_cmd.extend(shlex.split(command_args))
        return self._execute_subprocess(exec_cmd, cwd, stdin_data, timeout)

    def _run_go(self, cwd: str, entry_file: str, stdin_data: str, command_args: str, timeout: int) -> Dict[str, Any]:
        go_path = shutil.which('go')
        if not go_path:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': "Go runtime ('go') was not found in the local environment PATH.",
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
                'stderr': "Rust compiler ('rustc') was not found in the local environment PATH.",
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
