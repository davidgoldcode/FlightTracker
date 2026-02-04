#!/usr/bin/env python3
"""
Interactive Animation Selector for FlightTracker LED Panel.

Provides a web UI to browse and switch between animations.
Dynamically discovers animations from the scenes/ folder.

Usage:
    python animation_selector.py
    # Open http://localhost:8000 for controls
    # LED display at http://localhost:8888
"""
import os
import re
import signal
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# state
current_process = None
current_animation = None

# excluded scenes (not idle animations)
EXCLUDED_SCENES = {
    'clock', 'weather', 'date', 'day', 'flightdetails',
    'journey', 'loadingpulse', 'loadingled', 'planedetails'
}


def discover_animations():
    """Scan scenes/ folder for animation classes."""
    animations = {}
    scenes_dir = Path(__file__).parent / 'scenes'

    for file in scenes_dir.glob('*.py'):
        if file.name.startswith('_'):
            continue

        name = file.stem
        if name in EXCLUDED_SCENES:
            continue

        # read file to find class name
        content = file.read_text()
        match = re.search(r'class (\w+Scene)\(', content)
        if match:
            class_name = match.group(1)
            animations[name] = f'scenes.{name}.{class_name}'

    return dict(sorted(animations.items()))


def stop_animation():
    """Stop the currently running animation."""
    global current_process, current_animation
    if current_process:
        try:
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass
        current_process = None
        current_animation = None


current_scenario = None

# animations that support scenarios
SCENARIO_ANIMATIONS = {'birthday', 'anniversary'}


def start_animation(name, scenario=None):
    """Start an animation by name with optional scenario."""
    global current_process, current_animation, current_scenario

    stop_animation()

    # start test_animation.py in a new process group
    cmd = [sys.executable, 'test_animation.py', name]
    if scenario and name in SCENARIO_ANIMATIONS:
        cmd.append(f'--scenario={scenario}')

    current_process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )
    current_animation = name
    current_scenario = scenario if name in SCENARIO_ANIMATIONS else None
    return True


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FlightTracker Animation Selector</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .header {
            padding: 16px 20px;
            border-bottom: 1px solid #21262d;
            flex-shrink: 0;
        }
        .header h1 {
            font-size: 16px;
            font-weight: 500;
            color: #58a6ff;
            text-align: center;
        }

        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            padding: 16px 20px;
            max-width: 500px;
            margin: 0 auto;
            width: 100%;
        }

        /* Now playing status */
        .current-status {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-shrink: 0;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #6e7681;
            flex-shrink: 0;
        }
        .status-dot.active {
            background: #3fb950;
            box-shadow: 0 0 6px #3fb950;
        }
        .status-text { flex: 1; }
        .status-name {
            font-weight: 500;
            font-size: 14px;
            color: #c9d1d9;
        }
        .status-label {
            font-size: 10px;
            color: #6e7681;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Animation list - scrollable */
        .animation-list {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow-y: auto;
            flex: 1;
            min-height: 0;
        }
        .animation-item {
            padding: 10px 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid #21262d;
            transition: background 0.1s;
            font-size: 14px;
        }
        .animation-item:last-child { border-bottom: none; }
        .animation-item:hover { background: #21262d; }
        .animation-item.selected {
            background: #1f6feb30;
            border-left: 3px solid #58a6ff;
            padding-left: 11px;
        }
        .animation-item.active { background: #23863620; }
        .item-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #30363d;
            flex-shrink: 0;
        }
        .animation-item.active .item-dot { background: #3fb950; }
        .item-name { flex: 1; }

        /* Footer */
        .footer {
            padding: 12px 20px;
            border-top: 1px solid #21262d;
            flex-shrink: 0;
            text-align: center;
        }
        .hint {
            font-size: 11px;
            color: #6e7681;
            margin-bottom: 8px;
        }
        .hint kbd {
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 3px;
            padding: 1px 5px;
            font-family: monospace;
            font-size: 10px;
        }
        .led-link {
            color: #58a6ff;
            text-decoration: none;
            font-size: 12px;
        }
        .led-link:hover { text-decoration: underline; }

        /* Command palette overlay */
        .palette-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            z-index: 100;
            justify-content: center;
            padding-top: 80px;
        }
        .palette-overlay.active { display: flex; }
        .palette {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            width: 400px;
            max-height: 350px;
            overflow: hidden;
            box-shadow: 0 16px 32px rgba(0,0,0,0.5);
        }
        .palette-input {
            width: 100%;
            background: transparent;
            border: none;
            border-bottom: 1px solid #30363d;
            padding: 14px;
            font-size: 14px;
            color: #c9d1d9;
            outline: none;
        }
        .palette-input::placeholder { color: #6e7681; }
        .palette-results {
            max-height: 280px;
            overflow-y: auto;
        }
        .palette-item {
            padding: 10px 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            border-left: 3px solid transparent;
            font-size: 14px;
        }
        .palette-item:hover, .palette-item.selected {
            background: #21262d;
            border-left-color: #58a6ff;
        }
        .palette-item.active-anim { background: #1f6feb20; }
        .palette-icon {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #30363d;
        }
        .palette-item.active-anim .palette-icon {
            background: #3fb950;
            box-shadow: 0 0 6px #3fb950;
        }
        .palette-empty {
            padding: 16px;
            text-align: center;
            color: #6e7681;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Animation Selector</h1>
    </div>

    <div class="main">
        <div class="current-status">
            <div class="status-dot {{ 'active' if current else '' }}" id="statusDot"></div>
            <div class="status-text">
                <div class="status-label">Now Playing</div>
                <div class="status-name" id="statusName">{{ current or 'None' }}</div>
            </div>
        </div>

        <div class="animation-list" id="animationList">
            {% for name in animations.keys() %}
            <div class="animation-item {{ 'active' if name == current else '' }}"
                 data-name="{{ name }}"
                 onclick="selectAnimation('{{ name }}')">
                <div class="item-dot"></div>
                <div class="item-name">{{ name }}</div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="footer">
        <div class="hint">
            <kbd>↑</kbd> <kbd>↓</kbd> navigate |
            <kbd>Enter</kbd> watch |
            <kbd>⌘K</kbd> search |
            <kbd>Esc</kbd> stop
        </div>
        <a href="/display" class="led-link">Open LED Display →</a>
    </div>

    <!-- Command Palette -->
    <div class="palette-overlay" id="palette">
        <div class="palette">
            <input type="text" class="palette-input" id="paletteInput"
                   placeholder="Search animations..." autocomplete="off">
            <div class="palette-results" id="paletteResults"></div>
        </div>
    </div>

    <!-- Scenario Palette -->
    <div class="palette-overlay" id="scenarioPalette">
        <div class="palette">
            <div class="palette-input" style="padding: 14px; border-bottom: 1px solid #30363d;">
                <span style="color: #58a6ff;" id="scenarioAnimName"></span> - Select Scenario
            </div>
            <div class="palette-results" id="scenarioResults"></div>
            <div style="padding: 10px 14px; border-top: 1px solid #30363d; font-size: 11px; color: #6e7681; text-align: center;">
                <kbd>Esc</kbd> cancel | <kbd>↑↓</kbd> navigate | <kbd>Enter</kbd> select
            </div>
        </div>
    </div>

    <script>
        // animation data from server (trusted source)
        const animations = {{ animations_json | safe }};
        const animationNames = Object.keys(animations);
        const scenarioAnimations = new Set(['birthday', 'anniversary']);
        let selectedIndex = animationNames.indexOf('{{ current }}');
        if (selectedIndex < 0) selectedIndex = 0;
        let paletteIndex = 0;
        let filteredNames = [...animationNames];
        let pendingAnimation = null;
        let scenarioIndex = 0;
        let scenarios = [];

        async function selectAnimation(name, navigateAfter = false) {
            // check if this animation supports scenarios
            if (scenarioAnimations.has(name)) {
                pendingAnimation = { name, navigateAfter };
                await openScenarioPalette(name);
                return true;
            }

            return await startAnimation(name, null, navigateAfter);
        }

        async function startAnimation(name, scenario, navigateAfter = false) {
            const body = scenario ? JSON.stringify({ scenario }) : null;
            const response = await fetch('/api/start/' + encodeURIComponent(name), {
                method: 'POST',
                headers: scenario ? { 'Content-Type': 'application/json' } : {},
                body
            });
            const data = await response.json();
            if (data.success) {
                updateUI(name);
                selectedIndex = animationNames.indexOf(name);
                closePalette();
                closeScenarioPalette();
                if (navigateAfter) {
                    await new Promise(r => setTimeout(r, 500));
                    window.location.href = '/display';
                }
            }
            return data.success;
        }

        async function openScenarioPalette(name) {
            const response = await fetch('/api/scenarios/' + encodeURIComponent(name));
            const data = await response.json();
            scenarios = data.scenarios || [];
            scenarioIndex = 0;

            document.getElementById('scenarioAnimName').textContent = name;
            document.getElementById('scenarioPalette').classList.add('active');
            renderScenarioResults();
        }

        function closeScenarioPalette() {
            document.getElementById('scenarioPalette').classList.remove('active');
            pendingAnimation = null;
        }

        function renderScenarioResults() {
            const results = document.getElementById('scenarioResults');
            while (results.firstChild) {
                results.removeChild(results.firstChild);
            }

            scenarios.forEach((scenario, i) => {
                const item = document.createElement('div');
                item.className = 'palette-item' + (i === scenarioIndex ? ' selected' : '');
                item.onclick = () => selectScenario(scenario.id);

                const icon = document.createElement('div');
                icon.className = 'palette-icon';
                item.appendChild(icon);

                const text = document.createElement('div');
                text.textContent = scenario.label;
                item.appendChild(text);

                results.appendChild(item);
            });
        }

        async function selectScenario(scenarioId) {
            if (!pendingAnimation) return;
            const { name, navigateAfter } = pendingAnimation;
            await startAnimation(name, scenarioId, navigateAfter);
        }

        function stopAnimation() {
            fetch('/api/stop', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) updateUI(null);
                });
        }

        function updateUI(current) {
            document.getElementById('statusName').textContent = current || 'None';
            document.getElementById('statusDot').className =
                'status-dot' + (current ? ' active' : '');

            document.querySelectorAll('.animation-item').forEach((item, i) => {
                const isActive = item.dataset.name === current;
                const isSelected = i === selectedIndex;
                item.className = 'animation-item' +
                    (isActive ? ' active' : '') +
                    (isSelected ? ' selected' : '');
            });
        }

        function updateSelection(index) {
            selectedIndex = Math.max(0, Math.min(animationNames.length - 1, index));
            updateUI(document.getElementById('statusName').textContent === 'None' ?
                     null : document.getElementById('statusName').textContent);

            // scroll into view
            const items = document.querySelectorAll('.animation-item');
            if (items[selectedIndex]) {
                items[selectedIndex].scrollIntoView({ block: 'nearest' });
            }
        }

        // Command palette functions
        function openPalette() {
            document.getElementById('palette').classList.add('active');
            document.getElementById('paletteInput').value = '';
            document.getElementById('paletteInput').focus();
            filterPalette('');
        }

        function closePalette() {
            document.getElementById('palette').classList.remove('active');
        }

        function filterPalette(query) {
            query = query.toLowerCase();
            filteredNames = animationNames.filter(name =>
                name.toLowerCase().includes(query)
            );
            paletteIndex = 0;
            renderPaletteResults();
        }

        function renderPaletteResults() {
            const results = document.getElementById('paletteResults');
            const current = document.getElementById('statusName').textContent;

            // clear existing content safely
            while (results.firstChild) {
                results.removeChild(results.firstChild);
            }

            if (filteredNames.length === 0) {
                const empty = document.createElement('div');
                empty.className = 'palette-empty';
                empty.textContent = 'No animations found';
                results.appendChild(empty);
                return;
            }

            // build results using DOM methods (safe from XSS)
            filteredNames.forEach((name, i) => {
                const item = document.createElement('div');
                item.className = 'palette-item' +
                    (i === paletteIndex ? ' selected' : '') +
                    (name === current ? ' active-anim' : '');
                item.dataset.name = name;
                item.onclick = () => selectAnimation(name);

                const icon = document.createElement('div');
                icon.className = 'palette-icon';
                item.appendChild(icon);

                const text = document.createElement('div');
                text.textContent = name;
                item.appendChild(text);

                results.appendChild(item);
            });
        }

        document.getElementById('paletteInput').addEventListener('input', (e) => {
            filterPalette(e.target.value);
        });

        document.getElementById('palette').addEventListener('click', (e) => {
            if (e.target.id === 'palette') closePalette();
        });

        document.getElementById('scenarioPalette').addEventListener('click', (e) => {
            if (e.target.id === 'scenarioPalette') closeScenarioPalette();
        });

        document.addEventListener('keydown', (e) => {
            const paletteOpen = document.getElementById('palette').classList.contains('active');
            const scenarioPaletteOpen = document.getElementById('scenarioPalette').classList.contains('active');

            // Cmd+K or Ctrl+K to open palette
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                if (scenarioPaletteOpen) return;
                if (paletteOpen) closePalette();
                else openPalette();
                return;
            }

            if (e.key === 'Escape') {
                if (scenarioPaletteOpen) {
                    closeScenarioPalette();
                } else if (paletteOpen) {
                    closePalette();
                } else {
                    stopAnimation();
                }
                return;
            }

            // handle scenario palette navigation
            if (scenarioPaletteOpen) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    scenarioIndex = Math.min(scenarios.length - 1, scenarioIndex + 1);
                    renderScenarioResults();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    scenarioIndex = Math.max(0, scenarioIndex - 1);
                    renderScenarioResults();
                } else if (e.key === 'Enter' && scenarios.length > 0) {
                    e.preventDefault();
                    selectScenario(scenarios[scenarioIndex].id);
                }
                return;
            }

            if (paletteOpen) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    paletteIndex = Math.min(filteredNames.length - 1, paletteIndex + 1);
                    renderPaletteResults();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    paletteIndex = Math.max(0, paletteIndex - 1);
                    renderPaletteResults();
                } else if (e.key === 'Enter' && filteredNames.length > 0) {
                    e.preventDefault();
                    selectAnimation(filteredNames[paletteIndex]);
                }
            } else {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    updateSelection(selectedIndex + 1);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    updateSelection(selectedIndex - 1);
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    // start animation and go to display
                    selectAnimation(animationNames[selectedIndex], true);
                }
            }
        });

        // poll for status
        setInterval(() => {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    const statusName = document.getElementById('statusName');
                    if (statusName.textContent !== (data.current || 'None')) {
                        updateUI(data.current);
                    }
                });
        }, 2000);

        // initial selection highlight
        updateSelection(selectedIndex);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    animations = discover_animations()
    import json
    return render_template_string(
        HTML_TEMPLATE,
        animations=animations,
        animations_json=json.dumps(animations),
        current=current_animation,
    )


DISPLAY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FlightTracker LED Display</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #000;
            overflow: hidden;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        iframe {
            border: none;
            width: 100vw;
            height: 100vh;
        }
        iframe.hidden { display: none; }

        /* Loading state */
        .loading {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #6e7681;
            gap: 16px;
        }
        .loading.hidden { display: none; }
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 3px solid #21262d;
            border-top-color: #58a6ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Command palette overlay */
        .palette-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 100;
            justify-content: center;
            padding-top: 100px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .palette-overlay.active { display: flex; }

        .palette {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            width: 500px;
            max-height: 400px;
            overflow: hidden;
            box-shadow: 0 16px 32px rgba(0,0,0,0.5);
        }
        .palette-input {
            width: 100%;
            background: transparent;
            border: none;
            border-bottom: 1px solid #30363d;
            padding: 16px;
            font-size: 16px;
            color: #c9d1d9;
            outline: none;
        }
        .palette-input::placeholder { color: #6e7681; }
        .palette-results {
            max-height: 320px;
            overflow-y: auto;
        }
        .palette-item {
            padding: 12px 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            border-left: 3px solid transparent;
            color: #c9d1d9;
        }
        .palette-item:hover, .palette-item.selected {
            background: #21262d;
            border-left-color: #58a6ff;
        }
        .palette-item.active-anim {
            background: #1f6feb20;
        }
        .palette-icon {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #30363d;
        }
        .palette-item.active-anim .palette-icon {
            background: #3fb950;
            box-shadow: 0 0 8px #3fb950;
        }
        .palette-empty {
            padding: 20px;
            text-align: center;
            color: #6e7681;
        }
        .palette-back {
            padding: 12px 16px;
            border-top: 1px solid #30363d;
            color: #6e7681;
            font-size: 12px;
            text-align: center;
        }
        .palette-back kbd {
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 2px 6px;
            font-family: monospace;
            font-size: 11px;
        }

        /* Hint in corner */
        .hint {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(22, 27, 34, 0.9);
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 8px 12px;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 12px;
            color: #6e7681;
            z-index: 50;
        }
        .hint kbd {
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 2px 6px;
            font-family: monospace;
            font-size: 11px;
        }
        .hint.hidden { display: none; }
    </style>
</head>
<body>
    <div class="loading" id="loading">
        <div class="loading-spinner"></div>
        <div>Starting animation...</div>
    </div>
    <iframe id="ledFrame" class="hidden"></iframe>

    <div class="hint" id="hint">
        <kbd>⌘K</kbd> animations | <kbd>Esc</kbd> stop | <kbd>B</kbd> back
    </div>

    <!-- Command Palette -->
    <div class="palette-overlay" id="palette">
        <div class="palette">
            <input type="text" class="palette-input" id="paletteInput"
                   placeholder="Search animations..." autocomplete="off">
            <div class="palette-results" id="paletteResults"></div>
            <div class="palette-back">
                <kbd>Esc</kbd> close | <kbd>B</kbd> back to selector
            </div>
        </div>
    </div>

    <!-- Scenario Palette -->
    <div class="palette-overlay" id="scenarioPalette">
        <div class="palette">
            <div class="palette-input" style="padding: 16px; border-bottom: 1px solid #30363d;">
                <span style="color: #58a6ff;" id="scenarioAnimName"></span> - Select Scenario
            </div>
            <div class="palette-results" id="scenarioResults"></div>
            <div class="palette-back">
                <kbd>Esc</kbd> cancel | <kbd>↑↓</kbd> navigate | <kbd>Enter</kbd> select
            </div>
        </div>
    </div>

    <script>
        let animations = {};
        let animationNames = [];
        const scenarioAnimations = new Set(['birthday', 'anniversary']);
        let currentAnimation = null;
        let paletteIndex = 0;
        let filteredNames = [];
        let emulatorReady = false;
        let pendingAnimation = null;
        let scenarioIndex = 0;
        let scenarios = [];

        // load animations from API
        fetch('/api/animations')
            .then(r => r.json())
            .then(data => {
                animations = data;
                animationNames = Object.keys(data);
                filteredNames = [...animationNames];
            });

        // poll for current status
        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    currentAnimation = data.current;
                });
        }
        updateStatus();
        setInterval(updateStatus, 2000);

        // wait for emulator to be ready on port 8888
        async function waitForEmulator(maxRetries = 20) {
            for (let i = 0; i < maxRetries; i++) {
                try {
                    const response = await fetch('http://localhost:8888/', { mode: 'no-cors' });
                    return true;
                } catch (e) {
                    await new Promise(r => setTimeout(r, 250));
                }
            }
            return false;
        }

        async function loadEmulator() {
            const ready = await waitForEmulator();
            if (ready) {
                document.getElementById('loading').classList.add('hidden');
                const iframe = document.getElementById('ledFrame');
                iframe.src = 'http://localhost:8888';
                iframe.classList.remove('hidden');
                emulatorReady = true;
            } else {
                document.querySelector('.loading div:last-child').textContent =
                    'No animation running. Press ⌘K to select one.';
            }
        }

        loadEmulator();

        async function selectAnimation(name) {
            // check if this animation supports scenarios
            if (scenarioAnimations.has(name)) {
                pendingAnimation = name;
                await openScenarioPalette(name);
                return;
            }
            await startAnimation(name, null);
        }

        async function startAnimation(name, scenario) {
            const body = scenario ? JSON.stringify({ scenario }) : null;
            const response = await fetch('/api/start/' + encodeURIComponent(name), {
                method: 'POST',
                headers: scenario ? { 'Content-Type': 'application/json' } : {},
                body
            });
            const data = await response.json();
            if (data.success) {
                currentAnimation = name;
                closePalette();
                closeScenarioPalette();
                // reload emulator after animation change
                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('ledFrame').classList.add('hidden');
                loadEmulator();
            }
        }

        async function openScenarioPalette(name) {
            const response = await fetch('/api/scenarios/' + encodeURIComponent(name));
            const data = await response.json();
            scenarios = data.scenarios || [];
            scenarioIndex = 0;

            document.getElementById('scenarioAnimName').textContent = name;
            document.getElementById('scenarioPalette').classList.add('active');
            renderScenarioResults();
        }

        function closeScenarioPalette() {
            document.getElementById('scenarioPalette').classList.remove('active');
            pendingAnimation = null;
        }

        function renderScenarioResults() {
            const results = document.getElementById('scenarioResults');
            while (results.firstChild) {
                results.removeChild(results.firstChild);
            }

            scenarios.forEach((scenario, i) => {
                const item = document.createElement('div');
                item.className = 'palette-item' + (i === scenarioIndex ? ' selected' : '');
                item.onclick = () => selectScenario(scenario.id);

                const icon = document.createElement('div');
                icon.className = 'palette-icon';
                item.appendChild(icon);

                const text = document.createElement('div');
                text.textContent = scenario.label;
                item.appendChild(text);

                results.appendChild(item);
            });
        }

        async function selectScenario(scenarioId) {
            if (!pendingAnimation) return;
            await startAnimation(pendingAnimation, scenarioId);
        }

        function stopAnimation() {
            fetch('/api/stop', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) currentAnimation = null;
                });
        }

        function openPalette() {
            document.getElementById('palette').classList.add('active');
            document.getElementById('paletteInput').value = '';
            document.getElementById('paletteInput').focus();
            document.getElementById('hint').classList.add('hidden');
            filterPalette('');
        }

        function closePalette() {
            document.getElementById('palette').classList.remove('active');
            document.getElementById('hint').classList.remove('hidden');
        }

        function filterPalette(query) {
            query = query.toLowerCase();
            filteredNames = animationNames.filter(name =>
                name.toLowerCase().includes(query)
            );
            paletteIndex = 0;
            renderPaletteResults();
        }

        function renderPaletteResults() {
            const results = document.getElementById('paletteResults');

            while (results.firstChild) {
                results.removeChild(results.firstChild);
            }

            if (filteredNames.length === 0) {
                const empty = document.createElement('div');
                empty.className = 'palette-empty';
                empty.textContent = 'No animations found';
                results.appendChild(empty);
                return;
            }

            filteredNames.forEach((name, i) => {
                const item = document.createElement('div');
                item.className = 'palette-item' +
                    (i === paletteIndex ? ' selected' : '') +
                    (name === currentAnimation ? ' active-anim' : '');
                item.dataset.name = name;
                item.onclick = () => selectAnimation(name);

                const icon = document.createElement('div');
                icon.className = 'palette-icon';
                item.appendChild(icon);

                const text = document.createElement('div');
                text.textContent = name;
                item.appendChild(text);

                results.appendChild(item);
            });
        }

        document.getElementById('paletteInput').addEventListener('input', (e) => {
            filterPalette(e.target.value);
        });

        document.getElementById('palette').addEventListener('click', (e) => {
            if (e.target.id === 'palette') closePalette();
        });

        document.getElementById('scenarioPalette').addEventListener('click', (e) => {
            if (e.target.id === 'scenarioPalette') closeScenarioPalette();
        });

        document.addEventListener('keydown', (e) => {
            const paletteOpen = document.getElementById('palette').classList.contains('active');
            const scenarioPaletteOpen = document.getElementById('scenarioPalette').classList.contains('active');

            // Cmd+K or Ctrl+K to open palette
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                if (scenarioPaletteOpen) return;
                if (paletteOpen) closePalette();
                else openPalette();
                return;
            }

            // B to go back to selector
            if (e.key === 'b' || e.key === 'B') {
                if (!paletteOpen && !scenarioPaletteOpen) {
                    window.location.href = '/';
                    return;
                }
            }

            if (e.key === 'Escape') {
                if (scenarioPaletteOpen) {
                    closeScenarioPalette();
                } else if (paletteOpen) {
                    closePalette();
                } else {
                    stopAnimation();
                }
                return;
            }

            // handle scenario palette navigation
            if (scenarioPaletteOpen) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    scenarioIndex = Math.min(scenarios.length - 1, scenarioIndex + 1);
                    renderScenarioResults();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    scenarioIndex = Math.max(0, scenarioIndex - 1);
                    renderScenarioResults();
                } else if (e.key === 'Enter' && scenarios.length > 0) {
                    e.preventDefault();
                    selectScenario(scenarios[scenarioIndex].id);
                }
                return;
            }

            if (paletteOpen) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    paletteIndex = Math.min(filteredNames.length - 1, paletteIndex + 1);
                    renderPaletteResults();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    paletteIndex = Math.max(0, paletteIndex - 1);
                    renderPaletteResults();
                } else if (e.key === 'Enter' && filteredNames.length > 0) {
                    e.preventDefault();
                    selectAnimation(filteredNames[paletteIndex]);
                }
            }
        });
    </script>
</body>
</html>
"""


@app.route('/display')
def display():
    return render_template_string(DISPLAY_TEMPLATE)


@app.route('/api/animations')
def api_animations():
    return jsonify(discover_animations())


@app.route('/api/status')
def api_status():
    return jsonify({
        'current': current_animation,
        'scenario': current_scenario,
        'running': current_process is not None and current_process.poll() is None
    })


@app.route('/api/scenarios/<name>')
def api_scenarios(name):
    """Get available scenarios for an animation."""
    if name in SCENARIO_ANIMATIONS:
        return jsonify({
            'scenarios': [
                {'id': 'default', 'label': 'Default (countdown)'},
                {'id': 'day-of', 'label': 'Day of celebration'},
                {'id': 'countdown:1', 'label': '1 day countdown'},
                {'id': 'countdown:2', 'label': '2 days countdown'},
                {'id': 'countdown:3', 'label': '3 days countdown'},
                {'id': 'countdown:5', 'label': '5 days countdown'},
                {'id': 'countdown:7', 'label': '7 days countdown'},
            ]
        })
    return jsonify({'scenarios': []})


@app.route('/api/start/<name>', methods=['POST'])
def api_start(name):
    from flask import request
    animations = discover_animations()
    if name not in animations:
        return jsonify({'success': False, 'error': 'Unknown animation'}), 404

    # get optional scenario from request
    scenario = None
    if request.is_json:
        scenario = request.json.get('scenario')
    elif request.form:
        scenario = request.form.get('scenario')

    # 'default' means no scenario
    if scenario == 'default':
        scenario = None

    success = start_animation(name, scenario)
    return jsonify({'success': success, 'current': current_animation, 'scenario': current_scenario})


@app.route('/api/stop', methods=['POST'])
def api_stop():
    stop_animation()
    return jsonify({'success': True, 'current': None})


def cleanup(signum, frame):
    """Clean up on exit."""
    stop_animation()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("\n🎨 Animation Selector")
    print("   Controls: http://localhost:8000")
    print("   LED Display: http://localhost:8888")
    print("\nPress Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
