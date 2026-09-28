/**
 * CodeForge IDE - Snippets & Algorithms Template Library
 */

class SnippetsLibraryController {
  constructor() {
    this.snippets = [
      // 1. React Snippets
      {
        id: 'react-state-effect',
        title: 'React 18 State & Effect Component',
        language: 'react',
        category: 'React & UI',
        code: `import React, { useState, useEffect } from 'react';

export default function CounterComponent() {
    const [count, setCount] = useState(0);
    const [status, setStatus] = useState('Idle');

    useEffect(() => {
        setStatus(count > 0 ? 'Active' : 'Idle');
    }, [count]);

    return (
        <div className="card">
            <h3>Counter: {count}</h3>
            <p>Status: {status}</p>
            <button onClick={() => setCount(c => c + 1)}>Increment</button>
            <button onClick={() => setCount(0)}>Reset</button>
        </div>
    );
}`
      },
      {
        id: 'react-custom-hook',
        title: 'React Custom Hook (useLocalStorage)',
        language: 'react',
        category: 'React & UI',
        code: `import { useState, useEffect } from 'react';

export function useLocalStorage(key, initialValue) {
    const [value, setValue] = useState(() => {
        try {
            const item = window.localStorage.getItem(key);
            return item ? JSON.parse(item) : initialValue;
        } catch (error) {
            return initialValue;
        }
    });

    useEffect(() => {
        try {
            window.localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error(error);
        }
    }, [key, value]);

    return [value, setValue];
}`
      },

      // 2. Python Snippets
      {
        id: 'py-binary-search',
        title: 'Binary Search Algorithm (Python)',
        language: 'python',
        category: 'Algorithms & DS',
        code: `def binary_search(arr: list[int], target: int) -> int:
    """Returns index of target in sorted array, or -1 if not found."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Test driver
nums = [10, 23, 35, 47, 59, 68, 77, 88, 99]
target = 59
idx = binary_search(nums, target)
print(f"Index of {target}: {idx}")`
      },
      {
        id: 'py-graph-bfs',
        title: 'Breadth-First Search (BFS) Traversal',
        language: 'python',
        category: 'Algorithms & DS',
        code: `from collections import deque

def bfs(graph: dict[str, list[str]], start_node: str):
    visited = set([start_node])
    queue = deque([start_node])
    traversal_order = []

    while queue:
        node = queue.popleft()
        traversal_order.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return traversal_order

# Graph adjacency list
network = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

print("BFS Traversal:", " -> ".join(bfs(network, 'A')))`
      },

      // 3. Java Snippets
      {
        id: 'java-threadpool',
        title: 'Java 21 ExecutorService & CompletableFuture',
        language: 'java',
        category: 'Concurrency',
        code: `import java.util.concurrent.*;
import java.util.List;

public class Main {
    public static void main(String[] args) throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(4);
        
        CompletableFuture<String> task1 = CompletableFuture.supplyAsync(() -> {
            return "Task 1 completed by " + Thread.currentThread().getName();
        }, executor);
        
        CompletableFuture<String> task2 = CompletableFuture.supplyAsync(() -> {
            return "Task 2 completed by " + Thread.currentThread().getName();
        }, executor);

        CompletableFuture.allOf(task1, task2).join();
        System.out.println(task1.get());
        System.out.println(task2.get());

        executor.shutdown();
    }
}`
      },

      // 4. C++ Snippets
      {
        id: 'cpp-fast-io',
        title: 'C++20 Fast I/O & Priority Queue Template',
        language: 'cpp',
        category: 'Competitive Programming',
        code: `#include <iostream>
#include <vector>
#include <queue>

using namespace std;

int main() {
    // Fast I/O
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    priority_queue<int, vector<int>, greater<int>> minHeap;
    vector<int> stream = {50, 20, 80, 10, 40, 90};

    for (int x : stream) minHeap.push(x);

    cout << "Min-Heap Sorted Order: ";
    while (!minHeap.empty()) {
        cout << minHeap.top() << " ";
        minHeap.pop();
    }
    cout << "\\n";
    return 0;
}`
      },

      // 5. JavaScript / TypeScript Snippets
      {
        id: 'js-debounce',
        title: 'Debounce Function with TypeScript types',
        language: 'typescript',
        category: 'Utilities',
        code: `function debounce<T extends (...args: any[]) => any>(
    func: T,
    delayMs: number
): (...args: Parameters<T>) => void {
    let timeoutId: ReturnType<typeof setTimeout> | undefined;

    return (...args: Parameters<T>) => {
        if (timeoutId !== undefined) {
            clearTimeout(timeoutId);
        }
        timeoutId = setTimeout(() => {
            func(...args);
        }, delayMs);
    };
}

const logSearch = debounce((query: string) => {
    console.log(\`Searching for: \${query}\`);
}, 300);

logSearch('react');
logSearch('react 18 hooks');`
      },

      // 6. SQL Snippets
      {
        id: 'sql-window-funcs',
        title: 'SQL Window Functions & Running Totals',
        language: 'sql',
        category: 'Data Engineering',
        code: `-- Window Functions Demonstration
CREATE TABLE monthly_sales (
    month_id INT,
    region TEXT,
    revenue DECIMAL(10,2)
);

INSERT INTO monthly_sales VALUES
(1, 'North', 12000), (2, 'North', 15000), (3, 'North', 18000),
(1, 'South', 9000), (2, 'South', 11000), (3, 'South', 14000);

SELECT 
    month_id,
    region,
    revenue,
    SUM(revenue) OVER(PARTITION BY region ORDER BY month_id) AS running_total,
    RANK() OVER(PARTITION BY month_id ORDER BY revenue DESC) AS regional_rank
FROM monthly_sales;`
      }
    ];
  }

  openModal() {
    ModalsManager.open('snippets-modal');
    this.renderList();
  }

  renderList(filterCategory = 'all', searchQuery = '') {
    const listEl = document.getElementById('snippets-list-container');
    if (!listEl) return;

    let filtered = this.snippets;
    if (filterCategory !== 'all') {
      filtered = filtered.filter(s => s.category.toLowerCase().includes(filterCategory.toLowerCase()));
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(s => s.title.toLowerCase().includes(q) || s.language.toLowerCase().includes(q));
    }

    if (filtered.length === 0) {
      listEl.innerHTML = '<div style="color:var(--text-dim);text-align:center;padding:24px;">No snippets match your search.</div>';
      return;
    }

    listEl.innerHTML = filtered.map(s => `
      <div class="snippet-card" onclick="ide.snippets.insertSnippet('${s.id}')">
        <div class="snippet-card-header">
          <span class="snippet-title">${this.escapeHtml(s.title)}</span>
          <span class="badge badge-secondary">${this.escapeHtml(s.language.toUpperCase())}</span>
        </div>
        <div class="snippet-category">${this.escapeHtml(s.category)}</div>
        <pre class="snippet-preview"><code>${this.escapeHtml(s.code.slice(0, 150))}...</code></pre>
        <button class="btn btn-primary btn-sm snippet-insert-btn">
          <i data-lucide="corner-down-left" style="width:12px;height:12px;"></i> Insert Code
        </button>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  }

  insertSnippet(snippetId) {
    const snippet = this.snippets.find(s => s.id === snippetId);
    if (!snippet) return;

    if (window.ide && window.ide.monaco) {
      const editor = window.ide.monaco.editor;
      if (editor) {
        const position = editor.getPosition();
        editor.executeEdits('snippets-library', [{
          range: new monaco.Range(position.lineNumber, position.column, position.lineNumber, position.column),
          text: snippet.code + '\n'
        }]);
        ModalsManager.close('snippets-modal');
        Toast.success(`Inserted snippet: "${snippet.title}"`);
      }
    }
  }

  escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

window.SnippetsLibraryController = SnippetsLibraryController;
