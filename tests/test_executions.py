from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from languages.models import Language
from executions.models import Execution

class ExecutionAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.python_lang = Language.objects.create(
            name='Python',
            slug='python',
            version='3.13',
            monaco_id='python',
            file_extension='.py',
            default_filename='main.py',
            run_command='python {entry_file}',
            supports_stdin=True,
            is_active=True
        )
        self.sql_lang = Language.objects.create(
            name='SQL',
            slug='sql',
            version='3.45',
            monaco_id='sql',
            file_extension='.sql',
            default_filename='queries.sql',
            run_command='sqlite3 :memory:',
            supports_stdin=False,
            is_active=True
        )

    def test_python_execution_success(self):
        payload = {
            'language_slug': 'python',
            'files': [
                {
                    'name': 'main.py',
                    'path': '',
                    'content': 'print("CodeForge Test Output")\nprint(40 + 2)',
                    'is_entry_point': True
                }
            ],
            'entry_file': 'main.py'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'completed')
        self.assertIn('CodeForge Test Output', res.data['result']['stdout'])
        self.assertIn('42', res.data['result']['stdout'])
        self.assertEqual(res.data['result']['exit_code'], 0)

    def test_python_execution_with_stdin(self):
        payload = {
            'language_slug': 'python',
            'files': [
                {
                    'name': 'main.py',
                    'path': '',
                    'content': 'import sys\nname = sys.stdin.read().strip()\nprint(f"Hello, {name}!")',
                    'is_entry_point': True
                }
            ],
            'entry_file': 'main.py',
            'stdin': 'Alex'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('Hello, Alex!', res.data['result']['stdout'])

    def test_python_multi_file_import_execution(self):
        payload = {
            'language_slug': 'python',
            'files': [
                {
                    'name': 'main.py',
                    'path': '',
                    'content': 'from utils.math_helper import square\nprint(f"Result: {square(9)}")',
                    'is_entry_point': True
                },
                {
                    'name': 'math_helper.py',
                    'path': 'utils',
                    'content': 'def square(n): return n * n',
                    'is_entry_point': False
                }
            ],
            'entry_file': 'main.py'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('Result: 81', res.data['result']['stdout'])

    def test_sql_execution(self):
        payload = {
            'language_slug': 'sql',
            'files': [
                {
                    'name': 'queries.sql',
                    'path': '',
                    'content': 'CREATE TABLE users (id INT, name TEXT);\nINSERT INTO users VALUES (1, "Alice");\nSELECT * FROM users;',
                    'is_entry_point': True
                }
            ],
            'entry_file': 'queries.sql'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('Alice', res.data['result']['stdout'])

    def test_python_syntax_error_handling(self):
        payload = {
            'language_slug': 'python',
            'files': [
                {
                    'name': 'main.py',
                    'path': '',
                    'content': 'def broken_func(\n  print("syntax error here")',
                    'is_entry_point': True
                }
            ],
            'entry_file': 'main.py'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'failed')
        self.assertNotEqual(res.data['result']['exit_code'], 0)
        self.assertIn('SyntaxError', res.data['result']['stderr'])

    def test_python_unicode_and_currency_symbol_execution(self):
        payload = {
            'language_slug': 'python',
            'files': [
                {
                    'name': 'main.py',
                    'path': '',
                    'content': 'amount = 10000\nprint(f"\\u20b9{amount} deposited successfully.")\nprint("Unicode: € $ ¥ £ 🚀 ★")',
                    'is_entry_point': True
                }
            ],
            'entry_file': 'main.py'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'completed')
        self.assertIn('₹10000 deposited successfully.', res.data['result']['stdout'])
        self.assertIn('🚀', res.data['result']['stdout'])
        self.assertEqual(res.data['result']['exit_code'], 0)

    def test_python_large_code_execution(self):
        # Generates multiple classes, calculations, and extensive output
        large_code = '''
class Account:
    def __init__(self, balance):
        self.balance = balance
    def deposit(self, amt):
        self.balance += amt
        print(f"₹{amt} deposited successfully.")

accounts = [Account(i * 100) for i in range(50)]
for a in accounts:
    a.deposit(500)
print(f"Total accounts processed: {len(accounts)}")
'''
        payload = {
            'language_slug': 'python',
            'files': [
                {
                    'name': 'main.py',
                    'path': '',
                    'content': large_code,
                    'is_entry_point': True
                }
            ],
            'entry_file': 'main.py'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'completed')
        self.assertIn('Total accounts processed: 50', res.data['result']['stdout'])
        self.assertIn('₹500 deposited successfully.', res.data['result']['stdout'])
        self.assertEqual(res.data['result']['exit_code'], 0)

    def test_react_jsx_execution(self):
        Language.objects.get_or_create(
            slug='react',
            defaults={
                'name': 'React (JSX)',
                'version': '18.x',
                'monaco_id': 'javascript',
                'file_extension': '.jsx',
                'default_filename': 'App.jsx',
                'run_command': 'node {entry_file}',
                'is_active': True
            }
        )
        react_code = """
import React, { useState } from 'react';

export default function App() {
    const [count, setCount] = useState(5);
    console.log("React component test log: count=" + count);
    return (
        <div className="card">
            <h1>CodeForge React Sandbox</h1>
            <p>Count: {count}</p>
        </div>
    );
}
"""
        payload = {
            'language_slug': 'react',
            'files': [
                {
                    'name': 'App.jsx',
                    'path': '',
                    'content': react_code,
                    'is_entry_point': True
                }
            ],
            'entry_file': 'App.jsx'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'completed')
        self.assertIn('React', res.data['result']['stdout'])
        self.assertIn('CodeForge React', res.data['result']['stdout'])

    def test_html_document_execution(self):
        Language.objects.get_or_create(
            slug='html',
            defaults={
                'name': 'HTML5',
                'version': '5',
                'monaco_id': 'html',
                'file_extension': '.html',
                'default_filename': 'index.html',
                'run_command': 'open',
                'is_active': True
            }
        )
        html_code = """<!DOCTYPE html>
<html>
<head><title>Test Web Page</title></head>
<body><h1>Hello World</h1></body>
</html>"""
        payload = {
            'language_slug': 'html',
            'files': [
                {
                    'name': 'index.html',
                    'path': '',
                    'content': html_code,
                    'is_entry_point': True
                }
            ],
            'entry_file': 'index.html'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'completed')
        self.assertIn('Test Web Page', res.data['result']['stdout'])

    def test_json_document_execution(self):
        Language.objects.get_or_create(
            slug='json',
            defaults={
                'name': 'JSON Data',
                'version': '1',
                'monaco_id': 'json',
                'file_extension': '.json',
                'default_filename': 'data.json',
                'run_command': 'validate',
                'is_active': True
            }
        )
        json_code = '{"name": "CodeForge", "active": true, "languages": 28}'
        payload = {
            'language_slug': 'json',
            'files': [
                {
                    'name': 'data.json',
                    'path': '',
                    'content': json_code,
                    'is_entry_point': True
                }
            ],
            'entry_file': 'data.json'
        }
        res = self.client.post('/api/executions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'completed')
        self.assertIn('Valid JSON', res.data['result']['status_message'])

