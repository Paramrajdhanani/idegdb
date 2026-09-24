import os
import requests
from typing import Dict, Any, List
from .base import BaseExecutionRunner

class Judge0ExecutionRunner(BaseExecutionRunner):
    """
    Judge0 / Docker sandbox API adapter.
    For production deployments where all languages execute inside containerized environments.
    """

    LANGUAGE_MAP = {
        'python': 71,       # Python (3.8.1)
        'python3': 71,
        'react': 63,        # JavaScript (Node.js 12.14.0)
        'react-jsx': 63,
        'react-tsx': 74,    # TypeScript
        'javascript': 63,   # JavaScript (Node.js 12.14.0)
        'typescript': 74,   # TypeScript (3.7.4)
        'cpp': 54,          # C++ (GCC 9.2.0)
        'c': 50,            # C (GCC 9.2.0)
        'java': 62,         # Java (OpenJDK 13.0.1)
        'csharp': 51,       # C# (Mono 6.6.0.161)
        'rust': 73,         # Rust (1.40.0)
        'go': 60,           # Go (1.13.5)
        'sql': 82,          # SQL (SQLite 3.27.2)
        'php': 68,          # PHP (7.4.1)
        'ruby': 72,         # Ruby (2.7.0)
        'kotlin': 78,       # Kotlin (1.3.70)
        'swift': 83,        # Swift (5.2.3)
        'dart': 90,         # Dart (2.19.2)
        'scala': 81,        # Scala (2.13.2)
        'r': 80,            # R (4.0.0)
        'julia': 94,        # Julia (1.4.0)
        'bash': 46,         # Bash (5.0.0)
        'lua': 64,          # Lua (5.3.5)
        'perl': 85,         # Perl (5.28.1)
        'haskell': 61,      # Haskell (GHC 8.8.3)
        'elixir': 57,       # Elixir (1.9.4)
        'html': 63,         # HTML / Web
    }

    def __init__(self):
        self.api_url = os.environ.get('JUDGE0_API_URL', 'https://judge0-ce.p.rapidapi.com')
        self.api_key = os.environ.get('JUDGE0_API_KEY', '')

    def execute(
        self,
        language_slug: str,
        files: List[Dict[str, str]],
        entry_file: str,
        stdin_data: str = "",
        command_args: str = "",
        compiler_flags: str = "",
        timeout_seconds: int = 7
    ) -> Dict[str, Any]:
        language_id = self.LANGUAGE_MAP.get(language_slug, 71)
        # Find main file source
        source_code = ""
        for f in files:
            if f.get('name') == entry_file or not source_code:
                source_code = f.get('content', '')

        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['X-RapidAPI-Key'] = self.api_key

        payload = {
            'language_id': language_id,
            'source_code': source_code,
            'stdin': stdin_data,
            'command_line_arguments': command_args,
            'compiler_options': compiler_flags,
            'cpu_time_limit': timeout_seconds
        }

        try:
            response = requests.post(
                f"{self.api_url}/submissions?wait=true",
                json=payload,
                headers=headers,
                timeout=timeout_seconds + 5
            )
            if response.status_code in (200, 201):
                data = response.json()
                status_id = data.get('status', {}).get('id', 3)
                is_success = status_id == 3
                return {
                    'status': 'completed' if is_success else 'failed',
                    'stdout': data.get('stdout', '') or '',
                    'stderr': data.get('stderr', '') or data.get('compile_output', '') or '',
                    'exit_code': 0 if is_success else 1,
                    'execution_time_ms': int(float(data.get('time', '0') or '0') * 1000),
                    'memory_bytes': int(float(data.get('memory', '0') or '0') * 1024),
                    'status_message': data.get('status', {}).get('description', 'Execution completed.')
                }
            else:
                return {
                    'status': 'failed',
                    'stdout': '',
                    'stderr': f"Judge0 sandbox returned error: {response.text}",
                    'exit_code': 1,
                    'execution_time_ms': 0,
                    'memory_bytes': 0,
                    'status_message': f"Judge0 error {response.status_code}"
                }
        except Exception as e:
            return {
                'status': 'failed',
                'stdout': '',
                'stderr': f"External sandbox connection error: {str(e)}",
                'exit_code': 1,
                'execution_time_ms': 0,
                'memory_bytes': 0,
                'status_message': f"Connection failure: {str(e)}"
            }
