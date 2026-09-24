from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseExecutionRunner(ABC):
    """
    Abstract interface for code execution runners.
    Ensures safe isolation and standardized execution results.
    """

    @abstractmethod
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
        """
        Execute code and return standardized result dictionary.
        Returns:
            {
                'status': 'completed' | 'failed' | 'timeout' | 'cancelled',
                'stdout': str,
                'stderr': str,
                'exit_code': int,
                'execution_time_ms': int,
                'memory_bytes': int,
                'status_message': str
            }
        """
        pass
