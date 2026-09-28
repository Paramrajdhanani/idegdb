/**
 * CodeForge IDE - Starter Project Templates Wizard
 */

class ProjectTemplatesController {
  constructor() {
    this.templates = [
      {
        id: 'tmpl-react',
        title: 'React 18 Stateful Dashboard',
        icon: 'atom',
        languageSlug: 'react',
        description: 'Interactive counter, custom tasks hook, and modular CSS styling.',
        files: [
          {
            name: 'App.jsx',
            path: '',
            is_entry_point: true,
            content: `import React, { useState } from 'react';
import Header from './components/Header.jsx';
import TaskList from './components/TaskList.jsx';

export default function App() {
    const [tasks, setTasks] = useState([
        { id: 1, title: 'Learn CodeForge Cloud IDE', done: true },
        { id: 2, title: 'Build React 18 component', done: true },
        { id: 3, title: 'Connect execution sandbox', done: false }
    ]);

    const toggle = (id) => {
        setTasks(tasks.map(t => t.id === id ? { ...t, done: !t.done } : t));
    };

    return (
        <div className="app-container">
            <Header title="React 18 Studio" />
            <TaskList tasks={tasks} onToggle={toggle} />
        </div>
    );
}`
          },
          {
            name: 'Header.jsx',
            path: 'components',
            is_entry_point: false,
            content: `import React from 'react';

export default function Header({ title }) {
    return (
        <header style={{borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '12px'}}>
            <h2>⚛️ {title}</h2>
            <p style={{color: '#94a3b8', fontSize: '13px'}}>Live interactive component playground</p>
        </header>
    );
}`
          },
          {
            name: 'TaskList.jsx',
            path: 'components',
            is_entry_point: false,
            content: `import React from 'react';

export default function TaskList({ tasks, onToggle }) {
    return (
        <div style={{marginTop: '16px'}}>
            <h4>Sprint Checklist:</h4>
            <ul>
                {tasks.map(t => (
                    <li key={t.id} onClick={() => onToggle(t.id)} style={{cursor: 'pointer', padding: '6px 0'}}>
                        {t.done ? '✅ ' : '⏳ '} 
                        <span style={{textDecoration: t.done ? 'line-through' : 'none'}}>{t.title}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}`
          }
        ]
      },
      {
        id: 'tmpl-java',
        title: 'Java 21 Banking & Transaction Engine',
        icon: 'coffee',
        languageSlug: 'java',
        description: 'Multi-class banking ledger with thread-safe account balances and transfers.',
        files: [
          {
            name: 'Main.java',
            path: '',
            is_entry_point: true,
            content: `public class Main {
    public static void main(String[] args) {
        System.out.println("☕ CodeForge Java 21 LTS - Banking Sandbox");
        System.out.println("==================================================");

        BankAccount acc1 = new BankAccount("ACC-101", "Alex Dev", 5000.00);
        BankAccount acc2 = new BankAccount("ACC-102", "Elena Rossi", 3200.00);

        System.out.println(acc1);
        System.out.println(acc2);

        acc1.transfer(acc2, 1200.00);

        System.out.println("\\nUpdated Balances:");
        System.out.println(acc1);
        System.out.println(acc2);
    }
}

class BankAccount {
    private String id;
    private String owner;
    private double balance;

    public BankAccount(String id, String owner, double balance) {
        this.id = id;
        this.owner = owner;
        this.balance = balance;
    }

    public void transfer(BankAccount to, double amount) {
        if (this.balance >= amount) {
            this.balance -= amount;
            to.balance += amount;
            System.out.printf("  [TRANSFER] $%.2f transferred from %s to %s%n", amount, this.id, to.id);
        }
    }

    @Override
    public String toString() {
        return String.format("[%s] Owner: %-12s | Balance: $%.2f", id, owner, balance);
    }
}`
          }
        ]
      },
      {
        id: 'tmpl-python',
        title: 'Python Data Science & Algorithms Hub',
        icon: 'code',
        languageSlug: 'python',
        description: 'Binary Search Tree, Matrix multiplication, and statistics analyzer.',
        files: [
          {
            name: 'main.py',
            path: '',
            is_entry_point: true,
            content: `import math

def calculate_metrics(numbers: list[float]) -> dict:
    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    std_dev = math.sqrt(variance)
    return {
        "count": len(numbers),
        "mean": round(mean, 2),
        "std_dev": round(std_dev, 2),
        "min": min(numbers),
        "max": max(numbers)
    }

def main():
    print("🚀 CodeForge Python 3.13 Data Engine")
    data = [14.2, 23.5, 45.8, 12.0, 67.4, 89.1, 33.7]
    metrics = calculate_metrics(data)
    for k, v in metrics.items():
        print(f"  * {k.capitalize()}: {v}")

if __name__ == '__main__':
    main()`
          }
        ]
      }
    ];
  }

  openModal() {
    ModalsManager.open('templates-modal');
    this.renderList();
  }

  renderList() {
    const listEl = document.getElementById('templates-list-container');
    if (!listEl) return;

    listEl.innerHTML = this.templates.map(t => `
      <div class="template-card" onclick="ide.projectTemplates.loadTemplate('${t.id}')">
        <div class="template-icon">
          <i data-lucide="${t.icon}" style="width:24px;height:24px;color:var(--accent-primary);"></i>
        </div>
        <div class="template-info">
          <div class="template-title">${t.title}</div>
          <div class="template-desc">${t.description}</div>
          <div class="template-files-count">${t.files.length} file(s) included</div>
        </div>
        <button class="btn btn-secondary btn-sm">Load Project</button>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  }

  loadTemplate(templateId) {
    const template = this.templates.find(t => t.id === templateId);
    if (!template) return;

    if (window.ide) {
      window.ide.setLanguage(template.languageSlug);
      window.ide.fileExplorer.loadFiles(template.files);
      window.ide.updateProjectTitle(template.title);
      ModalsManager.close('templates-modal');
      Toast.success(`Loaded project template: "${template.title}"`);
    }
  }
}

window.ProjectTemplatesController = ProjectTemplatesController;
