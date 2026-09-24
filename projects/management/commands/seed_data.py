from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from languages.models import Language
from projects.models import Project, ProjectFile
from executions.models import Execution, ExecutionResult
from accounts.models import UserProfile, UserPreference

class Command(BaseCommand):
    help = 'Seeds initial languages, demo users, realistic multi-file projects, and sample executions.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting CodeForge IDE database seed...'))

        # 1. Create Languages
        languages_data = [
            {
                'name': 'Python',
                'slug': 'python',
                'version': '3.13',
                'monaco_id': 'python',
                'file_extension': '.py',
                'default_filename': 'main.py',
                'run_command': 'python {entry_file}',
                'supports_stdin': True,
                'supports_debugging': True,
                'formatter_name': 'black',
                'icon_name': 'code',
                'display_order': 1,
                'default_code': """# CodeForge IDE - Python 3.13 Environment
import sys

def fibonacci(n: int) -> list[int]:
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]

def main():
    print("🚀 Welcome to CodeForge IDE!")
    print(f"Python Runtime: {sys.version.split()[0]}")
    print("-" * 40)
    
    terms = 10
    fib = fibonacci(terms)
    print(f"First {terms} Fibonacci numbers:")
    print(" -> ".join(map(str, fib)))
    print("-" * 40)
    print("Execution completed successfully.")

if __name__ == '__main__':
    main()
"""
            },
            {
                'name': 'React (JSX)',
                'slug': 'react',
                'version': '18.x',
                'monaco_id': 'javascript',
                'file_extension': '.jsx',
                'default_filename': 'App.jsx',
                'run_command': 'node {entry_file}',
                'supports_stdin': False,
                'supports_debugging': True,
                'formatter_name': 'prettier',
                'icon_name': 'atom',
                'display_order': 2,
                'default_code': """import React, { useState, useEffect } from 'react';

// CodeForge IDE - React 18 Component Playground
export default function App() {
    const [count, setCount] = useState(0);
    const [tasks, setTasks] = useState([
        { id: 1, text: 'Initialize CodeForge Cloud IDE', completed: true },
        { id: 2, text: 'Build React 18 stateful components', completed: true },
        { id: 3, text: 'Deploy to isolated execution sandbox', completed: false }
    ]);

    const completedCount = tasks.filter(t => t.completed).length;

    console.log(`[React 18 Component Mounted] State: Count=${count}, CompletedTasks=${completedCount}/${tasks.length}`);

    return (
        <div className="react-dashboard-card">
            <header className="card-header">
                <h2>⚛️ CodeForge React 18 Engine</h2>
                <span className="badge">Active Sandbox</span>
            </header>

            <main className="card-body">
                <div className="counter-section">
                    <p>Interactive Counter: <strong>{count}</strong></p>
                    <button onClick={() => setCount(count + 1)}>+ Increment</button>
                    <button onClick={() => setCount(0)}>Reset</button>
                </div>

                <div className="tasks-section">
                    <h3>Project Roadmap ({completedCount}/{tasks.length})</h3>
                    <ul>
                        {tasks.map(task => (
                            <li key={task.id} className={task.completed ? 'done' : 'pending'}>
                                {task.completed ? '✓' : '○'} {task.text}
                            </li>
                        ))}
                    </ul>
                </div>
            </main>
        </div>
    );
}
"""
            },
            {
                'name': 'JavaScript (Node.js)',
                'slug': 'javascript',
                'version': '22.x LTS',
                'monaco_id': 'javascript',
                'file_extension': '.js',
                'default_filename': 'index.js',
                'run_command': 'node {entry_file}',
                'supports_stdin': True,
                'supports_debugging': True,
                'formatter_name': 'prettier',
                'icon_name': 'code',
                'display_order': 3,
                'default_code': """// CodeForge IDE - JavaScript / Node.js
const { performance } = require('perf_hooks');

function computePrimes(limit) {
    const primes = [];
    const isPrime = new Uint8Array(limit + 1).fill(1);
    isPrime[0] = isPrime[1] = 0;

    for (let p = 2; p * p <= limit; p++) {
        if (isPrime[p]) {
            for (let i = p * p; i <= limit; i += p) {
                isPrime[i] = 0;
            }
        }
    }

    for (let p = 2; p <= limit; p++) {
        if (isPrime[p]) primes.push(p);
    }
    return primes;
}

const startTime = performance.now();
const primes = computePrimes(50);
const duration = (performance.now() - startTime).toFixed(3);

console.log('⚡ CodeForge JavaScript Runtime');
console.log(`Found ${primes.length} primes under 50 in ${duration}ms`);
console.log('Primes:', primes.join(', '));
"""
            },
            {
                'name': 'Java',
                'slug': 'java',
                'version': '21 LTS',
                'monaco_id': 'java',
                'file_extension': '.java',
                'default_filename': 'Main.java',
                'compile_command': 'javac {files}',
                'run_command': 'java Main',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'google-java-format',
                'icon_name': 'coffee',
                'display_order': 4,
                'default_code': """// CodeForge IDE - Java 21 LTS
import java.util.*;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) {
        System.out.println("☕ Welcome to CodeForge Java 21 LTS Sandbox");
        System.out.println("==================================================");
        
        List<String> technologies = Arrays.asList(
            "Django", "Monaco Editor", "Python", "React", "Java 21", "WebSockets", "Docker"
        );
        
        System.out.println("Active Platform Stack:");
        technologies.stream()
            .map(String::toUpperCase)
            .sorted()
            .forEach(tech -> System.out.println("  * " + tech));
            
        System.out.println("--------------------------------------------------");
        System.out.println("Execution finished cleanly with 0 errors.");
    }
}
"""
            },
            {
                'name': 'TypeScript',
                'slug': 'typescript',
                'version': '5.x',
                'monaco_id': 'typescript',
                'file_extension': '.ts',
                'default_filename': 'index.ts',
                'run_command': 'ts-node {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'prettier',
                'icon_name': 'code-2',
                'display_order': 5,
                'default_code': """// CodeForge IDE - TypeScript 5.x
interface ProjectMetadata {
    title: string;
    version: string;
    isProductionReady: boolean;
    features: string[];
}

const ideInfo: ProjectMetadata = {
    title: "CodeForge IDE",
    version: "2.0.0",
    isProductionReady: true,
    features: ["Monaco Editor", "React Component Preview", "Multi-file Support", "Safe Sandbox Execution", "Live Sharing"]
};

console.log(`[TypeScript] ${ideInfo.title} v${ideInfo.version}`);
ideInfo.features.forEach((feat, idx) => {
    console.log(`  ${idx + 1}. ${feat}`);
});
"""
            },
            {
                'name': 'React (TSX)',
                'slug': 'react-tsx',
                'version': '18.x / TS',
                'monaco_id': 'typescript',
                'file_extension': '.tsx',
                'default_filename': 'App.tsx',
                'run_command': 'node {entry_file}',
                'supports_stdin': False,
                'supports_debugging': False,
                'formatter_name': 'prettier',
                'icon_name': 'atom',
                'display_order': 6,
                'default_code': """import React, { useState } from 'react';

interface MetricCardProps {
    title: string;
    value: string | number;
    trend: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, trend }) => (
    <div className="metric-box">
        <h4>{title}</h4>
        <span className="value">{value}</span>
        <span className="trend">{trend}</span>
    </div>
);

export default function Dashboard(): JSX.Element {
    const [metrics] = useState<MetricCardProps[]>([
        { title: 'API Response Time', value: '18ms', trend: '↓ 12% faster' },
        { title: 'Sandbox Memory', value: '32MB', trend: 'Optimal' },
        { title: 'Concurrent Users', value: '1,420', trend: '↑ 24%' }
    ]);

    return (
        <div className="tsx-dashboard">
            <h2>⚛️ React TypeScript Cloud Monitor</h2>
            <div className="grid">
                {metrics.map((m, i) => <MetricCard key={i} {...m} />)}
            </div>
        </div>
    );
}
"""
            },
            {
                'name': 'C++',
                'slug': 'cpp',
                'version': '20 / GCC',
                'monaco_id': 'cpp',
                'file_extension': '.cpp',
                'default_filename': 'main.cpp',
                'compile_command': 'g++ -O2 {files} -o program',
                'run_command': './program',
                'supports_stdin': True,
                'supports_debugging': True,
                'formatter_name': 'clang-format',
                'icon_name': 'cpu',
                'display_order': 7,
                'default_code': """// CodeForge IDE - C++20 Environment
#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>

int main() {
    std::cout << "🔥 CodeForge IDE - Modern C++\\n";
    std::cout << "--------------------------------\\n";
    
    std::vector<int> numbers = {12, 45, 78, 23, 56, 89, 90, 34};
    
    std::cout << "Original array: ";
    for (int n : numbers) std::cout << n << " ";
    std::cout << "\\n";
    
    std::sort(numbers.begin(), numbers.end());
    int sum = std::accumulate(numbers.begin(), numbers.end(), 0);
    double avg = static_cast<double>(sum) / numbers.size();
    
    std::cout << "Sorted array:   ";
    for (int n : numbers) std::cout << n << " ";
    std::cout << "\\n";
    std::cout << "Sum: " << sum << " | Average: " << avg << "\\n";
    
    return 0;
}
"""
            },
            {
                'name': 'C',
                'slug': 'c',
                'version': '17 / GCC',
                'monaco_id': 'c',
                'file_extension': '.c',
                'default_filename': 'main.c',
                'compile_command': 'gcc -O2 {files} -o program',
                'run_command': './program',
                'supports_stdin': True,
                'supports_debugging': True,
                'formatter_name': 'clang-format',
                'icon_name': 'cpu',
                'display_order': 8,
                'default_code': """/* CodeForge IDE - Standard C17 */
#include <stdio.h>
#include <stdlib.h>

int main() {
    printf("⚡ CodeForge IDE - C Language\\n");
    printf("================================\\n");
    
    for (int i = 1; i <= 5; i++) {
        printf("Step %d: 2^%d = %d\\n", i, i, 1 << i);
    }
    
    printf("Memory allocated and executed successfully.\\n");
    return 0;
}
"""
            },
            {
                'name': 'C#',
                'slug': 'csharp',
                'version': '.NET 8',
                'monaco_id': 'csharp',
                'file_extension': '.cs',
                'default_filename': 'Program.cs',
                'run_command': 'dotnet run',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'dotnet-format',
                'icon_name': 'box',
                'display_order': 9,
                'default_code': """using System;
using System.Linq;
using System.Collections.Generic;

class Program {
    static void Main() {
        Console.WriteLine("✨ CodeForge IDE - C# .NET 8 Environment");
        Console.WriteLine("------------------------------------------");
        
        var numbers = Enumerable.Range(1, 10).Select(x => x * x);
        Console.WriteLine("Computed Squares: " + string.Join(", ", numbers));
        
        var languages = new List<string> { "C#", "F#", "Python", "Java", "TypeScript" };
        Console.WriteLine($"Total languages listed: {languages.Count}");
    }
}
"""
            },
            {
                'name': 'HTML5 / Web Preview',
                'slug': 'html',
                'version': 'HTML5 / CSS3',
                'monaco_id': 'html',
                'file_extension': '.html',
                'default_filename': 'index.html',
                'run_command': 'open',
                'supports_stdin': False,
                'supports_debugging': False,
                'formatter_name': 'prettier',
                'icon_name': 'globe',
                'display_order': 10,
                'default_code': """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CodeForge Web Playground</title>
  <style>
    body { font-family: 'Inter', sans-serif; background: #0b0d10; color: #fff; padding: 2rem; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem; }
    h1 { color: #6c63ff; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🌐 CodeForge Web Canvas</h1>
    <p>Live interactive HTML5, CSS3, and JavaScript prototyping.</p>
  </div>
</body>
</html>
"""
            },
            {
                'name': 'SQL (SQLite In-Memory)',
                'slug': 'sql',
                'version': '3.45',
                'monaco_id': 'sql',
                'file_extension': '.sql',
                'default_filename': 'queries.sql',
                'run_command': 'sqlite3 :memory: < {entry_file}',
                'supports_stdin': False,
                'supports_debugging': False,
                'formatter_name': 'sql-formatter',
                'icon_name': 'database',
                'display_order': 11,
                'default_code': """-- CodeForge IDE - Interactive SQL Query Engine
CREATE TABLE developers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    favorite_lang TEXT,
    years_exp INTEGER
);

INSERT INTO developers (name, role, favorite_lang, years_exp) VALUES
('Alex Rivers', 'Backend Engineer', 'Python', 6),
('Maya Patel', 'Full-Stack Developer', 'React / TS', 4),
('Chen Wei', 'Systems Architect', 'C++', 8),
('Elena Rossi', 'Enterprise Engineer', 'Java', 7),
('Sam Taylor', 'DevOps Specialist', 'Go', 5);

SELECT 
    name, 
    role, 
    favorite_lang AS "Preferred Language", 
    years_exp AS "Years Experience"
FROM developers
WHERE years_exp >= 5
ORDER BY years_exp DESC;
"""
            },
            {
                'name': 'Rust',
                'slug': 'rust',
                'version': '1.75',
                'monaco_id': 'rust',
                'file_extension': '.rs',
                'default_filename': 'main.rs',
                'compile_command': 'rustc {entry_file} -o program',
                'run_command': './program',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'rustfmt',
                'icon_name': 'shield',
                'display_order': 12,
                'default_code': """// CodeForge IDE - Rust 1.75
fn main() {
    println!("🦀 Hello from CodeForge Rust Environment!");
    
    let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    let evens: Vec<i32> = numbers.into_iter().filter(|&x| x % 2 == 0).collect();
    
    println!("Filtered Even Numbers: {:?}", evens);
}
"""
            },
            {
                'name': 'Go',
                'slug': 'go',
                'version': '1.22',
                'monaco_id': 'go',
                'file_extension': '.go',
                'default_filename': 'main.go',
                'run_command': 'go run {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'gofmt',
                'icon_name': 'zap',
                'display_order': 13,
                'default_code': """package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("🚀 CodeForge IDE - Go Runtime")
	fmt.Println("Current Timestamp:", time.Now().Format(time.RFC1123))
	
	items := []string{"Channels", "Goroutines", "Interfaces", "Structs"}
	for i, item := range items {
		fmt.Printf("Feature #%d: %s\\n", i+1, item)
	}
}
"""
            },
            {
                'name': 'PHP',
                'slug': 'php',
                'version': '8.3',
                'monaco_id': 'php',
                'file_extension': '.php',
                'default_filename': 'index.php',
                'run_command': 'php {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'php-cs-fixer',
                'icon_name': 'file-code',
                'display_order': 14,
                'default_code': """<?php
// CodeForge IDE - PHP 8.3
echo "🐘 CodeForge PHP Engine\\n";
$fruits = ['Apple', 'Banana', 'Cherry', 'Dragonfruit'];
foreach ($fruits as $index => $fruit) {
    echo ($index + 1) . ". {$fruit}\\n";
}
"""
            },
            {
                'name': 'Ruby',
                'slug': 'ruby',
                'version': '3.3',
                'monaco_id': 'ruby',
                'file_extension': '.rb',
                'default_filename': 'main.rb',
                'run_command': 'ruby {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'rubocop',
                'icon_name': 'gem',
                'display_order': 15,
                'default_code': """# CodeForge IDE - Ruby 3.3
puts "💎 Welcome to CodeForge Ruby!"
words = %w[elegant readable productive expressive]
puts "Ruby characteristics: " + words.map(&:capitalize).join(", ")
"""
            },
            {
                'name': 'Kotlin',
                'slug': 'kotlin',
                'version': '1.9',
                'monaco_id': 'kotlin',
                'file_extension': '.kt',
                'default_filename': 'Main.kt',
                'run_command': 'kotlinc {entry_file} -include-runtime -d app.jar && java -jar app.jar',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'ktlint',
                'icon_name': 'layers',
                'display_order': 16,
                'default_code': """// CodeForge IDE - Kotlin
fun main() {
    println("🔮 CodeForge Kotlin Environment")
    val items = listOf("Lambdas", "Coroutines", "Null Safety")
    items.forEachIndexed { idx, item -> println("${idx + 1}: $item") }
}
"""
            },
            {
                'name': 'Swift',
                'slug': 'swift',
                'version': '5.9',
                'monaco_id': 'swift',
                'file_extension': '.swift',
                'default_filename': 'main.swift',
                'run_command': 'swift {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'swift-format',
                'icon_name': 'compass',
                'display_order': 17,
                'default_code': """// CodeForge IDE - Swift
import Foundation

print("🦅 CodeForge Swift Runtime")
let greetings = ["Hello", "Bonjour", "Hola", "Ciao"]
for greeting in greetings {
    print("\\(greeting), Developer!")
}
"""
            },
            {
                'name': 'Dart',
                'slug': 'dart',
                'version': '3.x',
                'monaco_id': 'dart',
                'file_extension': '.dart',
                'default_filename': 'main.dart',
                'run_command': 'dart run {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'dart format',
                'icon_name': 'target',
                'display_order': 18,
                'default_code': r"""// CodeForge IDE - Dart 3
void main() {
  print('🎯 CodeForge Dart Runtime');
  final list = ['Flutter', 'Async/Await', 'Sound Null Safety'];
  for (var i = 0; i < list.length; i++) {
    print('${i + 1}. ${list[i]}');
  }
}
"""
            },
            {
                'name': 'Scala',
                'slug': 'scala',
                'version': '3.3',
                'monaco_id': 'scala',
                'file_extension': '.scala',
                'default_filename': 'Main.scala',
                'run_command': 'scala {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'scalafmt',
                'icon_name': 'sparkles',
                'display_order': 19,
                'default_code': """// CodeForge IDE - Scala 3
@main def run(): Unit =
  println("✨ CodeForge Scala 3 Environment")
  val numbers = List(1, 2, 3, 4, 5)
  val doubled = numbers.map(_ * 2)
  println(s"Doubled list: $doubled")
"""
            },
            {
                'name': 'R',
                'slug': 'r',
                'version': '4.3',
                'monaco_id': 'r',
                'file_extension': '.r',
                'default_filename': 'main.r',
                'run_command': 'Rscript {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'styler',
                'icon_name': 'bar-chart-2',
                'display_order': 20,
                'default_code': """# CodeForge IDE - R Statistical Computing
cat("📊 CodeForge R Statistical Engine\\n")
data <- c(23, 45, 67, 89, 12, 34, 56, 78)
cat("Mean:", mean(data), "\\n")
cat("Standard Deviation:", sd(data), "\\n")
"""
            },
            {
                'name': 'Julia',
                'slug': 'julia',
                'version': '1.10',
                'monaco_id': 'julia',
                'file_extension': '.jl',
                'default_filename': 'main.jl',
                'run_command': 'julia {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'JuliaFormatter',
                'icon_name': 'activity',
                'display_order': 21,
                'default_code': """# CodeForge IDE - Julia
println("⚡ CodeForge Julia High-Performance Engine")
A = [1 2; 3 4]
println("Matrix Determinant: ", (A[1,1]*A[2,2] - A[1,2]*A[2,1]))
"""
            },
            {
                'name': 'Bash / Shell',
                'slug': 'bash',
                'version': '5.2',
                'monaco_id': 'shell',
                'file_extension': '.sh',
                'default_filename': 'script.sh',
                'run_command': 'bash {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'shfmt',
                'icon_name': 'terminal',
                'display_order': 22,
                'default_code': """#!/usr/bin/env bash
# CodeForge IDE - Shell Scripting
echo "🐚 CodeForge Sandbox Shell"
echo "System Time: $(date)"
for item in Docker Containers WebSockets Monaco; do
    echo "  * Feature: $item"
done
"""
            },
            {
                'name': 'Lua',
                'slug': 'lua',
                'version': '5.4',
                'monaco_id': 'lua',
                'file_extension': '.lua',
                'default_filename': 'main.lua',
                'run_command': 'lua {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'lua-format',
                'icon_name': 'moon',
                'display_order': 23,
                'default_code': """-- CodeForge IDE - Lua 5.4
print("🌙 Welcome to CodeForge Lua!")
local tbl = { "Fast", "Lightweight", "Embeddable" }
for i, v in ipairs(tbl) do
    print(string.format("  [%d] %s", i, v))
end
"""
            },
            {
                'name': 'Perl',
                'slug': 'perl',
                'version': '5.38',
                'monaco_id': 'perl',
                'file_extension': '.pl',
                'default_filename': 'main.pl',
                'run_command': 'perl {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'perltidy',
                'icon_name': 'feather',
                'display_order': 24,
                'default_code': """#!/usr/bin/env perl
use strict;
use warnings;

print "🐪 CodeForge Perl Environment\\n";
my @words = ('Practical', 'Extraction', 'Report', 'Language');
print "Words: " . join(" - ", @words) . "\\n";
"""
            },
            {
                'name': 'Haskell',
                'slug': 'haskell',
                'version': 'GHC 9.6',
                'monaco_id': 'haskell',
                'file_extension': '.hs',
                'default_filename': 'Main.hs',
                'run_command': 'runghc {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'ormolu',
                'icon_name': 'code',
                'display_order': 25,
                'default_code': """-- CodeForge IDE - Haskell
main :: IO ()
main = do
    putStrLn "λ Welcome to CodeForge Haskell!"
    let numbers = [1..10]
    let squares = map (^2) numbers
    putStrLn ("Squares: " ++ show squares)
"""
            },
            {
                'name': 'Elixir',
                'slug': 'elixir',
                'version': '1.16',
                'monaco_id': 'elixir',
                'file_extension': '.exs',
                'default_filename': 'main.exs',
                'run_command': 'elixir {entry_file}',
                'supports_stdin': True,
                'supports_debugging': False,
                'formatter_name': 'mix format',
                'icon_name': 'droplet',
                'display_order': 26,
                'default_code': """# CodeForge IDE - Elixir
IO.puts("💧 CodeForge Elixir Sandbox")
[1, 2, 3, 4, 5]
|> Enum.map(&(&1 * 3))
|> Enum.each(&IO.puts("Value: #{&1}"))
"""
            },
            {
                'name': 'JSON Data',
                'slug': 'json',
                'version': 'RFC 8259',
                'monaco_id': 'json',
                'file_extension': '.json',
                'default_filename': 'config.json',
                'run_command': 'validate',
                'supports_stdin': False,
                'supports_debugging': False,
                'formatter_name': 'prettier',
                'icon_name': 'braces',
                'display_order': 27,
                'default_code': """{
  "name": "codeforge-project",
  "version": "2.0.0",
  "status": "production",
  "features": [
    "Monaco Code Editor",
    "Multi-Language Sandbox",
    "React JSX Transpiler",
    "Java 21 LTS Runtime"
  ]
}
"""
            },
            {
                'name': 'Markdown Documentation',
                'slug': 'markdown',
                'version': 'CommonMark',
                'monaco_id': 'markdown',
                'file_extension': '.md',
                'default_filename': 'README.md',
                'run_command': 'preview',
                'supports_stdin': False,
                'supports_debugging': False,
                'formatter_name': 'prettier',
                'icon_name': 'file-text',
                'display_order': 28,
                'default_code': """# 🚀 CodeForge Cloud IDE Documentation

CodeForge is a next-generation browser cloud IDE and code execution sandbox supporting over 25+ programming languages.

## Key Features
- **Monaco Editor**: VS Code powerhouse editing with intellisense and tabs.
- **Instant Execution**: Safe isolated runtimes with low latency.
- **Full Multi-File Projects**: Folder trees, imports, and instant ZIP exports.
"""
            }
        ]

        created_langs = {}
        for l_data in languages_data:
            lang, created = Language.objects.update_or_create(
                slug=l_data['slug'],
                defaults=l_data
            )
            created_langs[lang.slug] = lang

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_langs)} programming languages."))

        # 2. Create Demo User and Admin Superuser
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@codeforge.dev',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if admin_created:
            admin_user.set_password('AdminForge2026!')
            admin_user.save()
            UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={'full_name': 'Platform Administrator', 'bio': 'CodeForge Lead Architect'}
            )
            UserPreference.objects.get_or_create(user=admin_user)

        demo_user, demo_created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@codeforge.dev',
                'first_name': 'Alex',
                'last_name': 'Dev'
            }
        )
        if demo_created:
            demo_user.set_password('CodeForge2026!')
            demo_user.save()
            UserProfile.objects.get_or_create(
                user=demo_user,
                defaults={
                    'full_name': 'Alex Developer',
                    'bio': 'Passionate full-stack developer exploring modern cloud IDE architectures.',
                    'github_handle': 'codeforge-dev'
                }
            )
            UserPreference.objects.get_or_create(
                user=demo_user,
                defaults={
                    'theme': 'codeforge-dark',
                    'font_size': 14,
                    'tab_size': 4,
                    'word_wrap': True,
                    'minimap': True
                }
            )

        self.stdout.write(self.style.SUCCESS("Seeded admin & demo user accounts."))

        # 3. Create Demo Multi-File Projects
        python_lang = created_langs['python']
        js_lang = created_langs['javascript']
        cpp_lang = created_langs['cpp']
        sql_lang = created_langs['sql']

        # Project 1: Python Algorithmic Data Structures
        p1, _ = Project.objects.get_or_create(
            owner=demo_user,
            name='Algorithms & Data Structures Toolkit',
            language=python_lang,
            defaults={
                'description': 'Production-ready Python implementation of Stacks, Queues, Binary Search Trees, and Graph Traversal algorithms with test suites.',
                'visibility': 'public',
                'is_favorite': True,
                'default_stdin': '15\n42\n7'
            }
        )
        ProjectFile.objects.get_or_create(
            project=p1,
            name='main.py',
            defaults={
                'path': '',
                'is_entry_point': True,
                'content': """# Main Driver Program - Algorithms Toolkit
import sys
from utils.calculator import MatrixCalculator
from utils.data_structures import BinarySearchTree

def main():
    print("=" * 50)
    print("🚀 CodeForge IDE - Python Multi-File Project")
    print("=" * 50)

    # 1. Binary Search Tree Demo
    print("\\n[1] Testing Binary Search Tree:")
    bst = BinarySearchTree()
    values = [50, 30, 70, 20, 40, 60, 80, 15, 25]
    print(f"Inserting values: {values}")
    for val in values:
        bst.insert(val)
    
    inorder_result = bst.inorder()
    print(f"In-Order Traversal (Sorted): {inorder_result}")
    
    # 2. Matrix Calculator Demo
    print("\\n[2] Testing Matrix Calculator:")
    calc = MatrixCalculator()
    mat_a = [[1, 2], [3, 4]]
    mat_b = [[5, 6], [7, 8]]
    product = calc.multiply(mat_a, mat_b)
    print(f"Matrix A: {mat_a}")
    print(f"Matrix B: {mat_b}")
    print(f"Matrix Product (A x B): {product}")

    # 3. Standard Input Processing
    print("\\n[3] Standard Input Processing:")
    try:
        user_input = sys.stdin.read().strip()
        if user_input:
            print("Received STDIN lines:")
            for line in user_input.splitlines():
                print(f"  > {line}")
        else:
            print("No STDIN provided (type values in the Input tab to test).")
    except Exception as e:
        print(f"STDIN reading error: {e}")

    print("\\n✓ All multi-file modules executed successfully.")

if __name__ == '__main__':
    main()
"""
            }
        )
        ProjectFile.objects.get_or_create(
            project=p1,
            name='calculator.py',
            defaults={
                'path': 'utils',
                'is_entry_point': False,
                'content': """class MatrixCalculator:
    def multiply(self, a, b):
        rows_a, cols_a = len(a), len(a[0])
        rows_b, cols_b = len(b), len(b[0])
        if cols_a != rows_b:
            raise ValueError("Incompatible matrix dimensions for multiplication")

        result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]
        for i in range(rows_a):
            for j in range(cols_b):
                for k in range(cols_a):
                    result[i][j] += a[i][k] * b[k][j]
        return result
"""
            }
        )
        ProjectFile.objects.get_or_create(
            project=p1,
            name='data_structures.py',
            defaults={
                'path': 'utils',
                'is_entry_point': False,
                'content': """class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, current, value):
        if value < current.value:
            if current.left is None:
                current.left = Node(value)
            else:
                self._insert_recursive(current.left, value)
        else:
            if current.right is None:
                current.right = Node(value)
            else:
                self._insert_recursive(current.right, value)

    def inorder(self):
        result = []
        self._inorder_traversal(self.root, result)
        return result

    def _inorder_traversal(self, node, result):
        if node:
            self._inorder_traversal(node.left, result)
            result.append(node.value)
            self._inorder_traversal(node.right, result)
"""
            }
        )
        ProjectFile.objects.get_or_create(
            project=p1,
            name='README.md',
            defaults={
                'path': '',
                'is_entry_point': False,
                'content': """# Python Algorithms & Data Structures Toolkit
This multi-file Python project demonstrates module imports, class abstraction, in-order traversal, matrix multiplication, and stdin streaming in CodeForge IDE.
"""
            }
        )

        # Project 2: JavaScript Array & Async Utilities
        p2, _ = Project.objects.get_or_create(
            owner=demo_user,
            name='Modern JavaScript Functional Utilities',
            language=js_lang,
            defaults={
                'description': 'Modular ES6+ utility functions for chunking, debouncing, deep cloning, and async pipeline composition.',
                'visibility': 'public',
                'is_favorite': True
            }
        )
        ProjectFile.objects.get_or_create(
            project=p2,
            name='index.js',
            defaults={
                'path': '',
                'is_entry_point': True,
                'content': """// Main JavaScript Application
const { chunk, groupBy, sumBy } = require('./utils/helpers');

console.log('⚡ CodeForge IDE - JavaScript Multi-File Demo');
console.log('-------------------------------------------');

const transactions = [
    { id: 1, category: 'Engineering', amount: 4500, currency: 'USD' },
    { id: 2, category: 'Marketing', amount: 1200, currency: 'USD' },
    { id: 3, category: 'Engineering', amount: 3200, currency: 'USD' },
    { id: 4, category: 'Design', amount: 2800, currency: 'USD' },
    { id: 5, category: 'Marketing', amount: 1900, currency: 'USD' },
    { id: 6, category: 'Engineering', amount: 5100, currency: 'USD' }
];

console.log('\\n[1] Chunking array into batches of 2:');
const batches = chunk(transactions, 2);
console.log(`Created ${batches.length} batches.`);

console.log('\\n[2] Grouping transactions by department:');
const grouped = groupBy(transactions, t => t.category);
for (const [dept, list] of Object.entries(grouped)) {
    const total = sumBy(list, t => t.amount);
    console.log(`  * ${dept}: ${list.length} item(s) totaling $${total.toLocaleString()}`);
}

console.log('\\n✓ JavaScript execution finished successfully.');
"""
            }
        )
        ProjectFile.objects.get_or_create(
            project=p2,
            name='helpers.js',
            defaults={
                'path': 'utils',
                'is_entry_point': False,
                'content': """function chunk(arr, size) {
    const res = [];
    for (let i = 0; i < arr.length; i += size) {
        res.push(arr.slice(i, i + size));
    }
    return res;
}

function groupBy(arr, keyFn) {
    return arr.reduce((acc, item) => {
        const key = keyFn(item);
        if (!acc[key]) acc[key] = [];
        acc[key].push(item);
        return acc;
    }, {});
}

function sumBy(arr, numFn) {
    return arr.reduce((acc, item) => acc + numFn(item), 0);
}

module.exports = { chunk, groupBy, sumBy };
"""
            }
        )

        # Project 3: SQL Ecommerce Analytics
        p3, _ = Project.objects.get_or_create(
            owner=demo_user,
            name='E-Commerce Relational Analytics',
            language=sql_lang,
            defaults={
                'description': 'Full relational database schema with users, products, orders, items, and analytical revenue aggregation queries.',
                'visibility': 'public',
                'is_favorite': False
            }
        )
        ProjectFile.objects.get_or_create(
            project=p3,
            name='queries.sql',
            defaults={
                'path': '',
                'is_entry_point': True,
                'content': """-- 1. Create Schema
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    tier TEXT DEFAULT 'Standard'
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    total_usd DECIMAL(10,2) NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- 2. Insert Seed Records
INSERT INTO customers (id, name, country, tier) VALUES
(1, 'Sophia Turner', 'USA', 'VIP'),
(2, 'Liam Nilsson', 'Sweden', 'Standard'),
(3, 'Akira Tanaka', 'Japan', 'VIP'),
(4, 'Chloe Dupont', 'France', 'Standard'),
(5, 'Marcus Aurelius', 'Italy', 'VIP');

INSERT INTO orders (id, customer_id, order_date, total_usd, status) VALUES
(101, 1, '2026-03-01', 249.99, 'Delivered'),
(102, 1, '2026-03-15', 580.00, 'Delivered'),
(103, 2, '2026-03-10', 95.50, 'Delivered'),
(104, 3, '2026-03-12', 1240.00, 'Delivered'),
(105, 3, '2026-03-20', 430.00, 'Shipped'),
(106, 5, '2026-03-18', 890.00, 'Delivered');

-- 3. Run Executive Analytics Query
SELECT 
    c.name AS "Customer Name",
    c.country AS "Country",
    c.tier AS "Membership Tier",
    COUNT(o.id) AS "Total Orders",
    printf('$%.2f', SUM(o.total_usd)) AS "Lifetime Value",
    printf('$%.2f', AVG(o.total_usd)) AS "Average Order Value"
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id
ORDER BY SUM(o.total_usd) DESC;
"""
            }
        )

        # Project 4: React 18 Dashboard & Component Suite
        react_lang = created_langs.get('react')
        if react_lang:
            p4, _ = Project.objects.get_or_create(
                owner=demo_user,
                name='React 18 Interactive Task & Metric Studio',
                language=react_lang,
                defaults={
                    'description': 'Modular React 18 frontend architecture with custom hooks, component composition, state management, and real-time metric tracking.',
                    'visibility': 'public',
                    'is_favorite': True
                }
            )
            ProjectFile.objects.get_or_create(
                project=p4,
                name='App.jsx',
                defaults={
                    'path': '',
                    'is_entry_point': True,
                    'content': """import React, { useState, useEffect } from 'react';
import Header from './components/Header.jsx';
import TaskList from './components/TaskList.jsx';

export default function App() {
    const [tasks, setTasks] = useState([
        { id: 1, title: 'Explore Monaco Editor in CodeForge', done: true },
        { id: 2, title: 'Build React components with live JSX preview', done: true },
        { id: 3, title: 'Compile Java 21 & C++ algorithms', done: false }
    ]);

    const toggleTask = (id) => {
        setTasks(tasks.map(t => t.id === id ? { ...t, done: !t.done } : t));
    };

    console.log(`[React App] Rendered with ${tasks.length} total tasks.`);

    return (
        <div className="app-container">
            <Header title="CodeForge React 18 Studio" subtitle="High-Performance Cloud Component Workspace" />
            <TaskList tasks={tasks} onToggle={toggleTask} />
        </div>
    );
}
"""
                }
            )
            ProjectFile.objects.get_or_create(
                project=p4,
                name='Header.jsx',
                defaults={
                    'path': 'components',
                    'is_entry_point': False,
                    'content': """import React from 'react';

export default function Header({ title, subtitle }) {
    return (
        <header className="studio-header">
            <h1>⚛️ {title}</h1>
            <p className="subtitle">{subtitle}</p>
        </header>
    );
}
"""
                }
            )
            ProjectFile.objects.get_or_create(
                project=p4,
                name='TaskList.jsx',
                defaults={
                    'path': 'components',
                    'is_entry_point': False,
                    'content': """import React from 'react';

export default function TaskList({ tasks, onToggle }) {
    return (
        <div className="task-list-panel">
            <h3>Sprint Tasks</h3>
            <ul>
                {tasks.map(task => (
                    <li key={task.id} onClick={() => onToggle(task.id)}>
                        <span>{task.done ? '✅' : '⏳'}</span>
                        <span className={task.done ? 'task-done' : ''}>{task.title}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}
"""
                }
            )

        # Project 5: Java 21 Banking & Ledger Engine
        java_lang = created_langs.get('java')
        if java_lang:
            p5, _ = Project.objects.get_or_create(
                owner=demo_user,
                name='Java 21 Enterprise Ledger & Banking Engine',
                language=java_lang,
                defaults={
                    'description': 'Object-oriented Java 21 transactional ledger engine with thread-safe accounts, audit trails, and stream processing.',
                    'visibility': 'public',
                    'is_favorite': True
                }
            )
            ProjectFile.objects.get_or_create(
                project=p5,
                name='Main.java',
                defaults={
                    'path': '',
                    'is_entry_point': True,
                    'content': """import java.util.*;

public class Main {
    public static void main(String[] args) {
        System.out.println("☕ CodeForge Java 21 LTS - Banking Engine");
        System.out.println("==================================================");

        BankAccount acc1 = new BankAccount("ACC-1001", "Alex Developer", 2500.00);
        BankAccount acc2 = new BankAccount("ACC-1002", "Elena Rossi", 4200.50);

        System.out.println(acc1);
        System.out.println(acc2);

        acc1.deposit(750.00);
        acc1.transferTo(acc2, 400.00);

        System.out.println("\\nUpdated Accounts:");
        System.out.println(acc1);
        System.out.println(acc2);

        System.out.println("--------------------------------------------------");
        System.out.println("✓ All Java banking transactions committed.");
    }
}

class BankAccount {
    private final String accountNumber;
    private final String owner;
    private double balance;

    public BankAccount(String accountNumber, String owner, double initialBalance) {
        this.accountNumber = accountNumber;
        this.owner = owner;
        this.balance = initialBalance;
    }

    public void deposit(double amount) {
        this.balance += amount;
        System.out.printf("  [DEPOSIT] +$%.2f into %s (Balance: $%.2f)%n", amount, accountNumber, balance);
    }

    public boolean transferTo(BankAccount target, double amount) {
        if (this.balance >= amount) {
            this.balance -= amount;
            target.balance += amount;
            System.out.printf("  [TRANSFER] $%.2f from %s to %s%n", amount, this.accountNumber, target.accountNumber);
            return true;
        }
        return false;
    }

    @Override
    public String toString() {
        return String.format("[%s] Owner: %-15s | Balance: $%.2f", accountNumber, owner, balance);
    }
}
"""
                }
            )

        # 4. Create Sample Executions for Live Analytics
        e1 = Execution.objects.create(
            user=demo_user,
            project=p1,
            language=python_lang,
            status='completed',
            execution_time_ms=142,
            started_at=timezone.now(),
            finished_at=timezone.now()
        )
        ExecutionResult.objects.create(
            execution=e1,
            stdout="🚀 CodeForge IDE - Python Multi-File Project\n[1] Testing Binary Search Tree: Success\n[2] Testing Matrix Calculator: Success\n✓ All multi-file modules executed successfully.",
            exit_code=0,
            memory_bytes=8388608,
            status_message="Process finished successfully."
        )

        e2 = Execution.objects.create(
            user=demo_user,
            project=p2,
            language=js_lang,
            status='completed',
            execution_time_ms=88,
            started_at=timezone.now(),
            finished_at=timezone.now()
        )
        ExecutionResult.objects.create(
            execution=e2,
            stdout="⚡ CodeForge IDE - JavaScript Multi-File Demo\nCreated 3 batches.\nGrouped 6 items across 3 departments.\n✓ JavaScript execution finished successfully.",
            exit_code=0,
            memory_bytes=12582912,
            status_message="Process finished successfully."
        )

        e3 = Execution.objects.create(
            user=demo_user,
            project=p3,
            language=sql_lang,
            status='completed',
            execution_time_ms=24,
            started_at=timezone.now(),
            finished_at=timezone.now()
        )
        ExecutionResult.objects.create(
            execution=e3,
            stdout="Customer Name | Country | Lifetime Value\nAkira Tanaka  | Japan   | $1670.00\nSophia Turner | USA     | $829.99\nMarcus A.     | Italy   | $890.00",
            exit_code=0,
            memory_bytes=2097152,
            status_message="SQL query executed successfully."
        )

        if react_lang and 'p4' in locals():
            e4 = Execution.objects.create(
                user=demo_user,
                project=p4,
                language=react_lang,
                status='completed',
                execution_time_ms=95,
                started_at=timezone.now(),
                finished_at=timezone.now()
            )
            ExecutionResult.objects.create(
                execution=e4,
                stdout="⚛️ CodeForge React 18 Engine\n[Component Entry]: <App />\n[SSR Virtual DOM / HTML Output]: <div class=\"app-container\">...</div>\n✓ React 18 component reconciled and mounted cleanly (0 runtime errors).",
                exit_code=0,
                memory_bytes=16777216,
                status_message="React component rendered successfully."
            )

        if java_lang and 'p5' in locals():
            e5 = Execution.objects.create(
                user=demo_user,
                project=p5,
                language=java_lang,
                status='completed',
                execution_time_ms=310,
                started_at=timezone.now(),
                finished_at=timezone.now()
            )
            ExecutionResult.objects.create(
                execution=e5,
                stdout="☕ CodeForge Java 21 LTS - Banking Engine\n[ACC-1001] Owner: Alex Developer | Balance: $2850.00\n[ACC-1002] Owner: Elena Rossi    | Balance: $4600.50\n✓ All Java banking transactions committed.",
                exit_code=0,
                memory_bytes=25165824,
                status_message="Java program compiled and executed cleanly."
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded demo multi-file projects and execution logs."))
        self.stdout.write(self.style.SUCCESS("[OK] Database seeding complete!"))
