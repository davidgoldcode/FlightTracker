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


def start_animation(name):
    """Start an animation by name."""
    global current_process, current_animation

    stop_animation()

    # start test_animation.py in a new process group
    cmd = [sys.executable, 'test_animation.py', name]
    current_process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )
    current_animation = name
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
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        h1 {
            text-align: center;
            margin-bottom: 10px;
            color: #fff;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .current {
            background: #16213e;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .current-label { color: #888; font-size: 12px; }
        .current-name {
            font-size: 24px;
            font-weight: bold;
            color: #0f0;
            margin-top: 5px;
        }
        .current-name.none { color: #666; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 12px;
        }
        .animation-btn {
            background: #16213e;
            border: 2px solid #0f3460;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
        }
        .animation-btn:hover {
            background: #1a1a4e;
            border-color: #e94560;
            transform: translateY(-2px);
        }
        .animation-btn.active {
            background: #0f3460;
            border-color: #0f0;
        }
        .animation-btn .name {
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 4px;
        }
        .animation-btn .key {
            display: inline-block;
            background: #0f3460;
            color: #aaa;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-family: monospace;
        }
        .animation-btn.active .key {
            background: #0f0;
            color: #000;
        }
        .controls {
            margin-top: 20px;
            text-align: center;
        }
        .stop-btn {
            background: #e94560;
            border: none;
            color: white;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }
        .stop-btn:hover { background: #ff6b6b; }
        .help {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
        .led-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #e94560;
            text-decoration: none;
        }
        .led-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Animation Selector</h1>
        <p class="subtitle">FlightTracker LED Panel Emulator</p>

        <div class="current">
            <div class="current-label">NOW PLAYING</div>
            <div class="current-name {{ 'none' if not current else '' }}" id="current">
                {{ current or 'None' }}
            </div>
        </div>

        <div class="grid" id="animations">
            {% for i, (name, path) in enumerate(animations.items()) %}
            <div class="animation-btn {{ 'active' if name == current else '' }}"
                 data-name="{{ name }}"
                 onclick="selectAnimation('{{ name }}')">
                <div class="name">{{ name }}</div>
                <span class="key">{{ i + 1 if i < 9 else '' }}</span>
            </div>
            {% endfor %}
        </div>

        <div class="controls">
            <button class="stop-btn" onclick="stopAnimation()">⏹ Stop (Esc)</button>
        </div>

        <a href="http://localhost:8888" target="_blank" class="led-link">
            Open LED Display →
        </a>

        <div class="help">
            Press 1-9 to select animation • Esc to stop • Arrows to navigate
        </div>
    </div>

    <script>
        const animations = {{ animations_json | safe }};
        const animationNames = Object.keys(animations);
        let currentIndex = animationNames.indexOf('{{ current }}');

        function selectAnimation(name) {
            fetch('/api/start/' + name, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        updateUI(name);
                        currentIndex = animationNames.indexOf(name);
                    }
                });
        }

        function stopAnimation() {
            fetch('/api/stop', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        updateUI(null);
                        currentIndex = -1;
                    }
                });
        }

        function updateUI(current) {
            document.getElementById('current').textContent = current || 'None';
            document.getElementById('current').className =
                'current-name' + (current ? '' : ' none');

            document.querySelectorAll('.animation-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.name === current);
            });
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                stopAnimation();
            } else if (e.key >= '1' && e.key <= '9') {
                const idx = parseInt(e.key) - 1;
                if (idx < animationNames.length) {
                    selectAnimation(animationNames[idx]);
                }
            } else if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                currentIndex = (currentIndex + 1) % animationNames.length;
                selectAnimation(animationNames[currentIndex]);
            } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                currentIndex = (currentIndex - 1 + animationNames.length) % animationNames.length;
                selectAnimation(animationNames[currentIndex]);
            }
        });

        // poll for status updates
        setInterval(() => {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => updateUI(data.current));
        }, 2000);
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
        enumerate=enumerate
    )


@app.route('/api/animations')
def api_animations():
    return jsonify(discover_animations())


@app.route('/api/status')
def api_status():
    return jsonify({
        'current': current_animation,
        'running': current_process is not None and current_process.poll() is None
    })


@app.route('/api/start/<name>', methods=['POST'])
def api_start(name):
    animations = discover_animations()
    if name not in animations:
        return jsonify({'success': False, 'error': 'Unknown animation'}), 404

    success = start_animation(name)
    return jsonify({'success': success, 'current': current_animation})


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
