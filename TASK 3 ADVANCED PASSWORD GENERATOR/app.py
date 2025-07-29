#!/usr/bin/env python3
"""
Advanced Password Generator with Web Interface
A comprehensive password generator that works both as a command-line tool
and as a web application using Python's built-in HTTP server.
"""

import random
import string
import secrets
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import threading
import time
import os
import sys

class PasswordGenerator:
    """Advanced password generator with multiple security features."""
    
    def __init__(self):
        self.char_sets = {
            'lowercase': string.ascii_lowercase,
            'uppercase': string.ascii_uppercase,
            'numbers': string.digits,
            'symbols': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            'extended_symbols': '!@#$%^&*()_+-=[]{}|;:,.<>?~`"\'\\/',
            'similar_chars': 'il1Lo0O'  # Characters that look similar
        }
        
        # Exclude similar looking characters for better readability
        self.readable_sets = {
            'lowercase': 'abcdefghijkmnpqrstuvwxyz',  # Removed: i, l, o
            'uppercase': 'ABCDEFGHJKLMNPQRSTUVWXYZ',   # Removed: I, O
            'numbers': '23456789',                      # Removed: 0, 1
            'symbols': '!@#$%^&*()_+-=[]{}|;:,.<>?'
        }
    
    def generate_password(self, length=12, include_lowercase=True, include_uppercase=True,
                         include_numbers=True, include_symbols=True, exclude_similar=False,
                         ensure_each_type=True):
        """
        Generate a secure password with specified criteria.
        
        Args:
            length (int): Password length (4-100)
            include_lowercase (bool): Include lowercase letters
            include_uppercase (bool): Include uppercase letters
            include_numbers (bool): Include numbers
            include_symbols (bool): Include symbols
            exclude_similar (bool): Exclude similar-looking characters
            ensure_each_type (bool): Ensure at least one char from each selected type
        
        Returns:
            str: Generated password
        """
        if length < 4 or length > 100:
            raise ValueError("Password length must be between 4 and 100 characters")
        
        # Choose character sets based on options
        char_sets = self.readable_sets if exclude_similar else self.char_sets
        
        # Build character pool
        char_pool = ''
        selected_sets = []
        
        if include_lowercase:
            char_pool += char_sets['lowercase']
            selected_sets.append(('lowercase', char_sets['lowercase']))
        if include_uppercase:
            char_pool += char_sets['uppercase']
            selected_sets.append(('uppercase', char_sets['uppercase']))
        if include_numbers:
            char_pool += char_sets['numbers']
            selected_sets.append(('numbers', char_sets['numbers']))
        if include_symbols:
            char_pool += char_sets['symbols']
            selected_sets.append(('symbols', char_sets['symbols']))
        
        if not char_pool:
            raise ValueError("At least one character type must be selected")
        
        # Generate password
        password = []
        
        # Ensure at least one character from each selected type
        if ensure_each_type and selected_sets:
            for name, charset in selected_sets:
                password.append(secrets.choice(charset))
        
        # Fill remaining length with random characters
        remaining_length = length - len(password)
        for _ in range(remaining_length):
            password.append(secrets.choice(char_pool))
        
        # Shuffle to avoid predictable patterns
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def generate_multiple_passwords(self, count=5, **kwargs):
        """Generate multiple passwords with the same criteria."""
        if count < 1 or count > 50:
            raise ValueError("Count must be between 1 and 50")
        
        passwords = []
        for _ in range(count):
            passwords.append(self.generate_password(**kwargs))
        return passwords
    
    def calculate_strength(self, password):
        """Calculate password strength score and category."""
        score = 0
        feedback = []
        
        # Length scoring
        length = len(password)
        if length >= 16:
            score += 30
            feedback.append("Excellent length")
        elif length >= 12:
            score += 25
            feedback.append("Good length")
        elif length >= 8:
            score += 15
            feedback.append("Adequate length")
        else:
            score += 5
            feedback.append("Too short")
        
        # Character variety scoring
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        
        char_types = sum([has_lower, has_upper, has_digit, has_symbol])
        score += char_types * 15
        
        if char_types >= 4:
            feedback.append("Excellent variety")
        elif char_types >= 3:
            feedback.append("Good variety")
        elif char_types >= 2:
            feedback.append("Fair variety")
        else:
            feedback.append("Poor variety")
        
        # Additional complexity bonuses
        if length >= 20:
            score += 10
        if char_types == 4:
            score += 5
        
        # No repeated characters bonus
        if len(set(password)) == len(password):
            score += 5
            feedback.append("No repeated characters")
        
        # Determine strength category
        if score >= 80:
            return {
                'score': min(score, 100),
                'category': 'Excellent',
                'color': '#22c55e',
                'feedback': feedback
            }
        elif score >= 60:
            return {
                'score': score,
                'category': 'Very Strong',
                'color': '#16a34a',
                'feedback': feedback
            }
        elif score >= 40:
            return {
                'score': score,
                'category': 'Strong',
                'color': '#eab308',
                'feedback': feedback
            }
        elif score >= 25:
            return {
                'score': score,
                'category': 'Medium',
                'color': '#f97316',
                'feedback': feedback
            }
        else:
            return {
                'score': score,
                'category': 'Weak',
                'color': '#ef4444',
                'feedback': feedback
            }
    
    def generate_passphrase(self, word_count=4, separator='-', capitalize=True):
        """Generate a memorable passphrase using common words."""
        # Simple word list for passphrases
        words = [
            'apple', 'brave', 'chair', 'dance', 'eagle', 'flame', 'grape', 'house',
            'island', 'jungle', 'knife', 'light', 'moon', 'night', 'ocean', 'paper',
            'queen', 'river', 'stone', 'tiger', 'uncle', 'voice', 'water', 'yellow',
            'zebra', 'magic', 'power', 'dream', 'cloud', 'storm', 'peace', 'happy',
            'strong', 'bright', 'quick', 'gentle', 'clever', 'silent', 'golden', 'silver'
        ]
        
        selected_words = []
        for _ in range(word_count):
            word = secrets.choice(words)
            if capitalize:
                word = word.capitalize()
            selected_words.append(word)
        
        # Add some numbers for extra security
        passphrase = separator.join(selected_words)
        passphrase += separator + str(secrets.randbelow(9999)).zfill(4)
        
        return passphrase

class WebPasswordHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the web interface."""
    
    def __init__(self, *args, **kwargs):
        self.password_gen = PasswordGenerator()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests - serve the main page or static content."""
        if self.path == '/' or self.path == '/index.html':
            self.serve_main_page()
        elif self.path == '/api/test':
            self.send_json_response({'status': 'OK', 'message': 'API is working'})
        else:
            self.send_error(404, "Page not found")
    
    def do_POST(self):
        """Handle POST requests - API endpoints."""
        if self.path == '/api/generate':
            self.handle_generate_api()
        elif self.path == '/api/bulk':
            self.handle_bulk_generate_api()
        elif self.path == '/api/passphrase':
            self.handle_passphrase_api()
        else:
            self.send_error(404, "API endpoint not found")
    
    def handle_generate_api(self):
        """Handle single password generation API."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters with defaults
            length = int(data.get('length', 12))
            include_lowercase = data.get('lowercase', True)
            include_uppercase = data.get('uppercase', True)
            include_numbers = data.get('numbers', True)
            include_symbols = data.get('symbols', True)
            exclude_similar = data.get('exclude_similar', False)
            
            # Generate password
            password = self.password_gen.generate_password(
                length=length,
                include_lowercase=include_lowercase,
                include_uppercase=include_uppercase,
                include_numbers=include_numbers,
                include_symbols=include_symbols,
                exclude_similar=exclude_similar
            )
            
            # Calculate strength
            strength = self.password_gen.calculate_strength(password)
            
            response = {
                'password': password,
                'strength': strength,
                'length': len(password)
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, status=400)
    
    def handle_bulk_generate_api(self):
        """Handle bulk password generation API."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            count = int(data.get('count', 5))
            
            # Generate multiple passwords
            passwords = self.password_gen.generate_multiple_passwords(
                count=count,
                length=int(data.get('length', 12)),
                include_lowercase=data.get('lowercase', True),
                include_uppercase=data.get('uppercase', True),
                include_numbers=data.get('numbers', True),
                include_symbols=data.get('symbols', True),
                exclude_similar=data.get('exclude_similar', False)
            )
            
            response = {'passwords': passwords}
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, status=400)
    
    def handle_passphrase_api(self):
        """Handle passphrase generation API."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            word_count = int(data.get('word_count', 4))
            separator = data.get('separator', '-')
            capitalize = data.get('capitalize', True)
            
            passphrase = self.password_gen.generate_passphrase(
                word_count=word_count,
                separator=separator,
                capitalize=capitalize
            )
            
            strength = self.password_gen.calculate_strength(passphrase)
            
            response = {
                'passphrase': passphrase,
                'strength': strength,
                'length': len(passphrase)
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, status=400)
    
    def send_json_response(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def serve_main_page(self):
        """Serve the main HTML page."""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Password Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            max-width: 700px;
            width: 100%;
            transition: transform 0.3s ease;
        }
        
        .container:hover { transform: translateY(-5px); }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .tab-container {
            display: flex;
            margin-bottom: 30px;
            background: #f1f3f4;
            border-radius: 12px;
            padding: 4px;
        }
        
        .tab {
            flex: 1;
            padding: 12px 20px;
            text-align: center;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        
        .tab.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        .form-group {
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        
        input[type="range"] {
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
            margin-bottom: 10px;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        }
        
        .length-display {
            text-align: center;
            font-size: 1.2em;
            color: #667eea;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .checkbox-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
        }
        
        .checkbox-item:hover {
            border-color: #667eea;
            transform: translateY(-2px);
        }
        
        .checkbox-item input {
            margin-right: 10px;
            transform: scale(1.2);
            accent-color: #667eea;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 15px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #28a745, #20c997);
        }
        
        .btn-secondary:hover {
            box-shadow: 0 10px 25px rgba(40, 167, 69, 0.4);
        }
        
        .output-section {
            margin-top: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 2px solid #e9ecef;
        }
        
        .password-display {
            font-family: 'Courier New', monospace;
            font-size: 1.2em;
            padding: 20px;
            background: white;
            border-radius: 8px;
            word-break: break-all;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .strength-meter {
            margin: 15px 0;
            text-align: center;
        }
        
        .strength-bar {
            height: 10px;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .strength-fill {
            height: 100%;
            transition: all 0.3s ease;
            border-radius: 5px;
        }
        
        .strength-text {
            font-weight: 600;
            margin-top: 10px;
        }
        
        .bulk-container {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 20px;
        }
        
        .bulk-item {
            font-family: 'Courier New', monospace;
            padding: 12px;
            background: white;
            margin-bottom: 8px;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s ease;
            border-left: 4px solid #667eea;
        }
        
        .bulk-item:hover { background: #f0f0f0; }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        @media (max-width: 768px) {
            .container { padding: 20px; }
            .checkbox-grid { grid-template-columns: 1fr; }
            h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Python Password Generator</h1>
        
        <div class="error-message" id="errorMessage"></div>
        
        <div class="tab-container">
            <div class="tab active" onclick="switchTab('password')">Password</div>
            <div class="tab" onclick="switchTab('bulk')">Bulk Generate</div>
            <div class="tab" onclick="switchTab('passphrase')">Passphrase</div>
        </div>
        
        <!-- Password Tab -->
        <div id="password-tab" class="tab-content active">
            <div class="form-group">
                <label for="length">Password Length:</label>
                <input type="range" id="length" min="4" max="50" value="12">
                <div class="length-display" id="lengthDisplay">12 characters</div>
            </div>
            
            <div class="form-group">
                <label>Character Types:</label>
                <div class="checkbox-grid">
                    <div class="checkbox-item">
                        <input type="checkbox" id="lowercase" checked>
                        <label>Lowercase (a-z)</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="uppercase" checked>
                        <label>Uppercase (A-Z)</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="numbers" checked>
                        <label>Numbers (0-9)</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="symbols" checked>
                        <label>Symbols (!@#$%)</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="excludeSimilar">
                        <label>Exclude Similar (i,l,1,O,0)</label>
                    </div>
                </div>
            </div>
            
            <button class="btn" onclick="generatePassword()">Generate Password</button>
        </div>
        
        <!-- Bulk Generate Tab -->
        <div id="bulk-tab" class="tab-content">
            <div class="form-group">
                <label for="bulkCount">Number of Passwords:</label>
                <input type="range" id="bulkCount" min="2" max="20" value="5">
                <div class="length-display" id="bulkCountDisplay">5 passwords</div>
            </div>
            
            <div class="form-group">
                <label for="bulkLength">Password Length:</label>
                <input type="range" id="bulkLength" min="4" max="50" value="12">
                <div class="length-display" id="bulkLengthDisplay">12 characters</div>
            </div>
            
            <button class="btn" onclick="generateBulkPasswords()">Generate Multiple Passwords</button>
        </div>
        
        <!-- Passphrase Tab -->
        <div id="passphrase-tab" class="tab-content">
            <div class="form-group">
                <label for="wordCount">Number of Words:</label>
                <input type="range" id="wordCount" min="3" max="8" value="4">
                <div class="length-display" id="wordCountDisplay">4 words</div>
            </div>
            
            <div class="form-group">
                <label>Separator:</label>
                <div class="checkbox-grid">
                    <div class="checkbox-item">
                        <input type="radio" name="separator" value="-" checked>
                        <label>Dash (-)</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="radio" name="separator" value="_">
                        <label>Underscore (_)</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="radio" name="separator" value=" ">
                        <label>Space ( )</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="capitalize" checked>
                        <label>Capitalize Words</label>
                    </div>
                </div>
            </div>
            
            <button class="btn" onclick="generatePassphrase()">Generate Passphrase</button>
        </div>
        
        <!-- Output Section -->
        <div class="output-section" id="outputSection" style="display: none;">
            <div class="password-display" id="passwordDisplay"></div>
            
            <div class="strength-meter" id="strengthMeter">
                <div class="strength-bar">
                    <div class="strength-fill" id="strengthFill"></div>
                </div>
                <div class="strength-text" id="strengthText"></div>
            </div>
            
            <button class="btn btn-secondary" onclick="copyToClipboard()">📋 Copy to Clipboard</button>
            
            <div class="bulk-container" id="bulkContainer" style="display: none;"></div>
        </div>
    </div>
    
    <script>
        let currentPassword = '';
        let currentPasswords = [];
        
        // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
        }
        
        // Update displays
        document.getElementById('length').addEventListener('input', function() {
            document.getElementById('lengthDisplay').textContent = this.value + ' characters';
        });
        
        document.getElementById('bulkCount').addEventListener('input', function() {
            document.getElementById('bulkCountDisplay').textContent = this.value + ' passwords';
        });
        
        document.getElementById('bulkLength').addEventListener('input', function() {
            document.getElementById('bulkLengthDisplay').textContent = this.value + ' characters';
        });
        
        document.getElementById('wordCount').addEventListener('input', function() {
            document.getElementById('wordCountDisplay').textContent = this.value + ' words';
        });
        
        // API functions
        async function generatePassword() {
            const data = {
                length: parseInt(document.getElementById('length').value),
                lowercase: document.getElementById('lowercase').checked,
                uppercase: document.getElementById('uppercase').checked,
                numbers: document.getElementById('numbers').checked,
                symbols: document.getElementById('symbols').checked,
                exclude_similar: document.getElementById('excludeSimilar').checked
            };
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showError(result.error);
                } else {
                    displaySinglePassword(result);
                }
            } catch (error) {
                showError('Failed to generate password: ' + error.message);
            }
        }
        
        async function generateBulkPasswords() {
            const data = {
                count: parseInt(document.getElementById('bulkCount').value),
                length: parseInt(document.getElementById('bulkLength').value),
                lowercase: document.getElementById('lowercase')?.checked ?? true,
                uppercase: document.getElementById('uppercase')?.checked ?? true,
                numbers: document.getElementById('numbers')?.checked ?? true,
                symbols: document.getElementById('symbols')?.checked ?? true,
                exclude_similar: document.getElementById('excludeSimilar')?.checked ?? false
            };
            
            try {
                const response = await fetch('/api/bulk', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showError(result.error);
                } else {
                    displayBulkPasswords(result.passwords);
                }
            } catch (error) {
                showError('Failed to generate passwords: ' + error.message);
            }
        }
        
        async function generatePassphrase() {
            const separator = document.querySelector('input[name="separator"]:checked').value;
            const data = {
                word_count: parseInt(document.getElementById('wordCount').value),
                separator: separator,
                capitalize: document.getElementById('capitalize').checked
            };
            
            try {
                const response = await fetch('/api/passphrase', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showError(result.error);
                } else {
                    displaySinglePassword(result, true);
                }
            } catch (error) {
                showError('Failed to generate passphrase: ' + error.message);
            }
        }
        
        function displaySinglePassword(result, isPassphrase = false) {
            currentPassword = result.password || result.passphrase;
            currentPasswords = [];
            
            document.getElementById('passwordDisplay').textContent = currentPassword;
            updateStrengthMeter(result.strength);
            
            document.getElementById('outputSection').style.display = 'block';
            document.getElementById('bulkContainer').style.display = 'none';
        }
        
        function displayBulkPasswords(passwords) {
            currentPasswords = passwords;
            currentPassword = '';
            
            const container = document.getElementById('bulkContainer');
            container.innerHTML = '';
            
            passwords.forEach((password, index) => {
                const div = document.createElement('div');
                div.className = 'bulk-item';
                div.textContent = `${index + 1}. ${password}`;
                div.onclick = () => copyPasswordToClipboard(password);
                container.appendChild(div);
            });
            
            document.getElementById('passwordDisplay').textContent = `${passwords.length} passwords generated (click any to copy)`;
            document.getElementById('strengthMeter').style.display = 'none';
            document.getElementById('outputSection').style.display = 'block';
            document.getElementById('bulkContainer').style.display = 'block';
        }
        
        function updateStrengthMeter(strength) {
            const fill = document.getElementById('strengthFill');
            const text = document.getElementById('strengthText');
            
            fill.style.width = strength.score + '%';
            fill.style.backgroundColor = strength.color;
            text.textContent = `${strength.category} (${strength.score}/100)`;
            text.style.color = strength.color;
            
            document.getElementById('strengthMeter').style.display = 'block';
        }
        
        function copyToClipboard() {
            if (currentPassword) {
                copyPasswordToClipboard(currentPassword);
            } else if (currentPasswords.length > 0) {
                copyPasswordToClipboard(currentPasswords.join('\\n'));
            }
        }
        
        function copyPasswordToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showSuccess('Copied to clipboard!');
            }).catch(() => {
                showError('Failed to copy to clipboard');
            });
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
        
        function showSuccess(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.backgroundColor = '#d4edda';
            errorDiv.style.color = '#155724';
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
                errorDiv.style.backgroundColor = '#f8d7da';
                errorDiv.style.color = '#721c24';
            }, 2000);
        }
        
        // Generate initial password
        window.addEventListener('load', () => {
            generatePassword();
        });
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to reduce console output."""
        return

def run_command_line_interface():
    """Run the command-line interface for password generation."""
    password_gen = PasswordGenerator()
    
    print("🔐 Python Password Generator - Command Line Interface")
    print("=" * 60)
    
    while True:
        try:
            print("\nOptions:")
            print("1. Generate single password")
            print("2. Generate multiple passwords")
            print("3. Generate passphrase")
            print("4. Start web interface")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                # Single password generation
                length = int(input("Password length (4-100) [12]: ") or "12")
                
                print("\nCharacter types to include:")
                lowercase = input("Include lowercase letters? (y/n) [y]: ").lower() != 'n'
                uppercase = input("Include uppercase letters? (y/n) [y]: ").lower() != 'n'
                numbers = input("Include numbers? (y/n) [y]: ").lower() != 'n'
                symbols = input("Include symbols? (y/n) [y]: ").lower() != 'n'
                exclude_similar = input("Exclude similar characters (i,l,1,O,0)? (y/n) [n]: ").lower() == 'y'
                
                password = password_gen.generate_password(
                    length=length,
                    include_lowercase=lowercase,
                    include_uppercase=uppercase,
                    include_numbers=numbers,
                    include_symbols=symbols,
                    exclude_similar=exclude_similar
                )
                
                strength = password_gen.calculate_strength(password)
                
                print(f"\n{'='*60}")
                print(f"Generated Password: {password}")
                print(f"Length: {len(password)} characters")
                print(f"Strength: {strength['category']} ({strength['score']}/100)")
                print(f"Feedback: {', '.join(strength['feedback'])}")
                print(f"{'='*60}")
                
            elif choice == '2':
                # Multiple password generation
                count = int(input("Number of passwords (1-50) [5]: ") or "5")
                length = int(input("Password length (4-100) [12]: ") or "12")
                
                passwords = password_gen.generate_multiple_passwords(
                    count=count,
                    length=length,
                    include_lowercase=True,
                    include_uppercase=True,
                    include_numbers=True,
                    include_symbols=True
                )
                
                print(f"\n{'='*60}")
                print(f"Generated {count} Passwords:")
                for i, pwd in enumerate(passwords, 1):
                    print(f"{i:2d}. {pwd}")
                print(f"{'='*60}")
                
            elif choice == '3':
                # Passphrase generation
                word_count = int(input("Number of words (3-8) [4]: ") or "4")
                separator = input("Separator (-, _, space) [-]: ") or "-"
                capitalize = input("Capitalize words? (y/n) [y]: ").lower() != 'n'
                
                passphrase = password_gen.generate_passphrase(
                    word_count=word_count,
                    separator=separator,
                    capitalize=capitalize
                )
                
                strength = password_gen.calculate_strength(passphrase)
                
                print(f"\n{'='*60}")
                print(f"Generated Passphrase: {passphrase}")
                print(f"Length: {len(passphrase)} characters")
                print(f"Strength: {strength['category']} ({strength['score']}/100)")
                print(f"{'='*60}")
                
            elif choice == '4':
                # Start web interface
                start_web_server()
                break
                
            elif choice == '5':
                print("Thank you for using Python Password Generator!")
                break
                
            else:
                print("Invalid choice. Please enter 1-5.")
                
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

def start_web_server(port=8080):
    """Start the web server."""
    try:
        server = HTTPServer(('localhost', port), WebPasswordHandler)
        print(f"🌐 Starting web server at http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Open browser automatically
        def open_browser():
            time.sleep(1)  # Wait for server to start
            webbrowser.open(f'http://localhost:{port}')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        server.serve_forever()
        
    except OSError as e:
        if e.errno == 48:  # Port already in use
            print(f"Port {port} is already in use. Trying port {port + 1}...")
            start_web_server(port + 1)
        else:
            print(f"Error starting server: {e}")
    except KeyboardInterrupt:
        print("\n\nShutting down web server...")
        server.shutdown()

def main():
    """Main entry point."""
    print("🔐 Python Password Generator")
    print("A secure password generator with web interface")
    print("Author: Advanced Password Generator v2.0")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Command line arguments provided
        if sys.argv[1] == '--web':
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
            start_web_server(port)
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python password_generator.py          # Interactive CLI")
            print("  python password_generator.py --web    # Start web server on port 8080")
            print("  python password_generator.py --web 9000  # Start web server on port 9000")
            print("  python password_generator.py --help   # Show this help")
        else:
            print("Unknown argument. Use --help for usage information.")
    else:
        # No arguments, run CLI
        run_command_line_interface()

if __name__ == "__main__":
    main()
