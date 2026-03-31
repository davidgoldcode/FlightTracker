#!/usr/bin/env python3
"""
LED Panel Viewer - interactive browser-based animation previewer.

Run: python led_viewer.py
Open: http://localhost:5555
"""
import json
import os
import re
import signal
import socket
import socketserver
import subprocess
import sys
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = 5555
WS_PORT = 5556
ANIMATION_PROCESS = None
PIXEL_LOCK = threading.Lock()
PIXEL_DATA = None  # flat list of [r,g,b,...] for 64x32

# discover animations from test_animation.py
def get_animations():
    animations = {}
    test_file = Path(__file__).parent / "test_animation.py"
    content = test_file.read_text()

    # extract ANIMATIONS dict entries
    for match in re.finditer(r"'(\w+)':\s*'scenes\.\w+\.\w+'", content):
        name = match.group(1)
        animations[name] = name

    # categorize
    holidays = [
        "valentines", "stpatricks", "easter", "independence",
        "halloween", "thanksgiving", "chanukah", "christmas",
        "newyear", "chinesenewyear"
    ]
    events = ["birthday", "anniversary"]
    ambient = [
        "heartbeat", "lovemessages", "starfield", "oceanwaves",
        "fallingsnow", "aurora", "fireplace", "candlelight",
        "moonrise", "rain", "timeofday"
    ]
    info = ["clock", "weather", "date", "planeintro"]

    return {
        "holidays": [a for a in holidays if a in animations],
        "events": [a for a in events if a in animations],
        "ambient": [a for a in ambient if a in animations],
        "info": [a for a in info if a in animations],
    }

# holiday dates for the date picker
HOLIDAY_DATES = {
    "valentines": "02-14",
    "stpatricks": "03-17",
    "easter": "04-20",
    "independence": "07-04",
    "halloween": "10-31",
    "thanksgiving": "11-27",
    "chanukah": "12-14",
    "christmas": "12-25",
    "newyear": "12-31",
    "chinesenewyear": "01-29",
}


def stop_animation():
    global ANIMATION_PROCESS
    if ANIMATION_PROCESS and ANIMATION_PROCESS.poll() is None:
        ANIMATION_PROCESS.terminate()
        try:
            ANIMATION_PROCESS.wait(timeout=3)
        except subprocess.TimeoutExpired:
            ANIMATION_PROCESS.kill()
    ANIMATION_PROCESS = None


def start_animation(name, scenario=None, name_arg=None, brightness=None):
    global ANIMATION_PROCESS
    stop_animation()

    cmd = [sys.executable, "test_animation.py", name]
    if scenario:
        cmd.append(f"--scenario={scenario}")
    if name_arg:
        cmd.append(f"--name={name_arg}")
    if brightness:
        cmd.append(f"--brightness={brightness}")

    env = os.environ.copy()
    env["LED_VIEWER"] = "1"

    ANIMATION_PROCESS = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LED Panel Viewer</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    background: #111;
    color: #ccc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    font-size: 14px;
    height: 100vh;
    display: flex;
}

/* sidebar */
.sidebar {
    width: 260px;
    min-width: 260px;
    background: #1a1a1a;
    border-right: 1px solid #333;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.sidebar h1 {
    font-size: 16px;
    color: #fff;
    font-weight: 600;
}

.sidebar h2 {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #666;
    margin-bottom: 6px;
}

.group { display: flex; flex-direction: column; gap: 2px; }

.anim-btn {
    background: transparent;
    border: 1px solid transparent;
    color: #aaa;
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    font-size: 13px;
    transition: all 0.15s;
}
.anim-btn:hover { background: #252525; color: #fff; }
.anim-btn.active { background: #2a2a3a; border-color: #4a4a6a; color: #fff; }

/* controls panel */
.controls {
    background: #1e1e2e;
    border-radius: 8px;
    padding: 12px;
    display: none;
    flex-direction: column;
    gap: 10px;
}
.controls.visible { display: flex; }

.controls label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #888;
}

.controls input, .controls select {
    background: #252535;
    border: 1px solid #3a3a4a;
    color: #ddd;
    padding: 6px 8px;
    border-radius: 4px;
    font-size: 13px;
    width: 100%;
}

.controls input:focus, .controls select:focus {
    outline: none;
    border-color: #5a5a8a;
}

.apply-btn {
    background: #3a3a6a;
    border: none;
    color: #ddd;
    padding: 8px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
}
.apply-btn:hover { background: #4a4a8a; }

/* main display */
.main {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
}

.panel-wrapper {
    background: #0a0a0a;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 0 40px rgba(0,0,0,0.5);
}

canvas {
    display: block;
    image-rendering: pixelated;
    border-radius: 4px;
}

/* stop button */
.stop-btn {
    background: #3a2020;
    border: 1px solid #5a3030;
    color: #ccc;
    padding: 8px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    width: 100%;
}
.stop-btn:hover { background: #4a2a2a; }

/* status */
.status {
    font-size: 11px;
    color: #555;
    text-align: center;
}
</style>
</head>
<body>

<div class="sidebar">
    <h1>LED Panel Viewer</h1>

    <div class="controls" id="dateControls">
        <label>Simulate Date (MM-DD)</label>
        <input type="text" id="dateInput" placeholder="e.g. 12-25" pattern="\\d{2}-\\d{2}">
        <div style="display:flex; flex-wrap:wrap; gap:4px;">
            <button class="anim-btn" style="font-size:11px; padding:3px 6px;" onclick="setDate('')">clear</button>
            <button class="anim-btn" style="font-size:11px; padding:3px 6px;" onclick="setDate('02-14')">val</button>
            <button class="anim-btn" style="font-size:11px; padding:3px 6px;" onclick="setDate('03-17')">stpat</button>
            <button class="anim-btn" style="font-size:11px; padding:3px 6px;" onclick="setDate('07-04')">july4</button>
            <button class="anim-btn" style="font-size:11px; padding:3px 6px;" onclick="setDate('10-31')">hween</button>
            <button class="anim-btn" style="font-size:11px; padding:3px 6px;" onclick="setDate('12-25')">xmas</button>
            <button class="anim-btn" style="font-size:11px; padding:3px 6px;" onclick="setDate('12-31')">nye</button>
        </div>
    </div>

    <div class="controls" id="scenarioControls">
        <label>Scenario</label>
        <select id="scenarioSelect">
            <option value="">default (demo)</option>
            <option value="day-of">day of</option>
            <option value="countdown:5">5 days out</option>
            <option value="countdown:3">3 days out</option>
            <option value="countdown:1">1 day out</option>
        </select>
        <label>Name</label>
        <input type="text" id="nameInput" placeholder="e.g. Taylor">
        <button class="apply-btn" onclick="relaunchCurrent()">apply</button>
    </div>

    <div id="animList"></div>

    <button class="stop-btn" onclick="stopAnim()">stop</button>
    <div class="status" id="status">not running</div>
</div>

<div class="main">
    <div class="panel-wrapper">
        <canvas id="led" width="640" height="320"></canvas>
    </div>
</div>

<script>
const LED_W = 64, LED_H = 32;
const PIXEL_SIZE = 10;
const PIXEL_GAP = 0;
const canvas = document.getElementById('led');
const ctx = canvas.getContext('2d');

canvas.width = LED_W * PIXEL_SIZE;
canvas.height = LED_H * PIXEL_SIZE;

let currentAnim = null;
let ws = null;

function drawLEDs(pixels) {
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const radius = (PIXEL_SIZE - PIXEL_GAP) / 2;

    for (let y = 0; y < LED_H; y++) {
        for (let x = 0; x < LED_W; x++) {
            const i = (y * LED_W + x) * 3;
            const r = pixels[i], g = pixels[i+1], b = pixels[i+2];

            if (r === 0 && g === 0 && b === 0) {
                // dim dot for off pixels
                ctx.fillStyle = '#151515';
                ctx.beginPath();
                ctx.arc(
                    x * PIXEL_SIZE + radius,
                    y * PIXEL_SIZE + radius,
                    radius * 0.4, 0, Math.PI * 2
                );
                ctx.fill();
                continue;
            }

            // glow effect
            const cx = x * PIXEL_SIZE + radius;
            const cy = y * PIXEL_SIZE + radius;
            const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius * 1.2);
            grad.addColorStop(0, `rgba(${r},${g},${b},1)`);
            grad.addColorStop(0.5, `rgba(${r},${g},${b},0.4)`);
            grad.addColorStop(1, `rgba(${r},${g},${b},0)`);

            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(cx, cy, radius * 1.2, 0, Math.PI * 2);
            ctx.fill();

            // bright core
            ctx.fillStyle = `rgb(${r},${g},${b})`;
            ctx.beginPath();
            ctx.arc(cx, cy, radius * 0.5, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}

// initial blank display
drawLEDs(new Uint8Array(LED_W * LED_H * 3));

function connectWS() {
    if (ws) ws.close();
    ws = new WebSocket(`ws://${location.hostname}:5556`);
    ws.binaryType = 'arraybuffer';
    ws.onmessage = (e) => {
        drawLEDs(new Uint8Array(e.data));
    };
    ws.onclose = () => {
        setTimeout(connectWS, 1000);
    };
}
connectWS();

function selectAnim(name) {
    document.querySelectorAll('.anim-btn[data-anim]').forEach(b => b.classList.remove('active'));
    const btn = document.querySelector(`.anim-btn[data-anim="${name}"]`);
    if (btn) btn.classList.add('active');
    currentAnim = name;

    // show/hide controls
    const hasScenario = ['birthday', 'anniversary'].includes(name);
    document.getElementById('scenarioControls').classList.toggle('visible', hasScenario);

    const scenario = document.getElementById('scenarioSelect').value || undefined;
    const nameArg = document.getElementById('nameInput').value || undefined;

    fetch('/api/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, scenario: hasScenario ? scenario : undefined, nameArg: hasScenario ? nameArg : undefined})
    });
    document.getElementById('status').textContent = name;
}

function relaunchCurrent() {
    if (currentAnim) selectAnim(currentAnim);
}

function stopAnim() {
    fetch('/api/stop', {method: 'POST'});
    document.querySelectorAll('.anim-btn[data-anim]').forEach(b => b.classList.remove('active'));
    currentAnim = null;
    document.getElementById('status').textContent = 'not running';
    drawLEDs(new Uint8Array(LED_W * LED_H * 3));
}

function setDate(d) {
    document.getElementById('dateInput').value = d;
    fetch('/api/date', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({date: d})
    }).then(() => {
        if (currentAnim) selectAnim(currentAnim);
    });
}

// build animation list
fetch('/api/animations').then(r => r.json()).then(data => {
    const container = document.getElementById('animList');
    const labels = {holidays: 'Holidays', events: 'Events', ambient: 'Ambient', info: 'Info'};

    for (const [group, anims] of Object.entries(data)) {
        const h = document.createElement('h2');
        h.textContent = labels[group] || group;
        container.appendChild(h);

        const div = document.createElement('div');
        div.className = 'group';
        for (const name of anims) {
            const btn = document.createElement('button');
            btn.className = 'anim-btn';
            btn.dataset.anim = name;
            btn.textContent = name;
            btn.onclick = () => selectAnim(name);
            div.appendChild(btn);
        }
        container.appendChild(div);
    }

    // show date controls
    document.getElementById('dateControls').classList.add('visible');
});
</script>
</body>
</html>
"""


class ViewerHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the viewer API and UI."""

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        elif self.path == "/api/animations":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(get_animations()).encode())
        else:
            self.send_error(404)

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_len)) if content_len else {}

        if self.path == "/api/start":
            start_animation(
                body.get("name", "heartbeat"),
                scenario=body.get("scenario"),
                name_arg=body.get("nameArg"),
                brightness=body.get("brightness"),
            )
            self._json_ok()
        elif self.path == "/api/stop":
            stop_animation()
            self._json_ok()
        elif self.path == "/api/date":
            # write DEBUG_DATE to a temp config overlay
            date_val = body.get("date", "")
            _set_debug_date(date_val)
            self._json_ok()
        else:
            self.send_error(404)

    def _json_ok(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, format, *args):
        pass  # suppress request logs


def _set_debug_date(date_str):
    """Write DEBUG_DATE to the viewer's config overlay."""
    overlay_path = Path(__file__).parent / "_viewer_config.py"
    if date_str:
        overlay_path.write_text(f'DEBUG_DATE = "{date_str}"\n')
    else:
        if overlay_path.exists():
            overlay_path.unlink()


def run_pixel_bridge():
    """WebSocket server that streams pixel data from the bridge file to browsers."""
    import asyncio

    bridge_path = Path(__file__).parent / "_pixel_bridge.bin"
    clients = set()

    async def handle_client(websocket):
        """Send pixel frames to a single client until it disconnects."""
        clients.add(websocket)
        try:
            while True:
                try:
                    if bridge_path.exists():
                        data = bridge_path.read_bytes()
                        if len(data) == 64 * 32 * 3:
                            await websocket.send(data)
                except (FileNotFoundError, OSError):
                    pass
                await asyncio.sleep(0.05)
        except Exception:
            pass
        finally:
            clients.discard(websocket)

    async def main_ws():
        import websockets
        async with websockets.serve(handle_client, "0.0.0.0", WS_PORT):
            await asyncio.Future()  # run forever

    asyncio.run(main_ws())


def main():
    print(f"\n  LED Panel Viewer")
    print(f"  http://localhost:{PORT}\n")

    # check for websockets
    try:
        import websockets  # noqa: F401
    except ImportError:
        print("  Installing websockets...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets", "-q"])

    # start WebSocket pixel bridge in background
    ws_thread = threading.Thread(target=run_pixel_bridge, daemon=True)
    ws_thread.start()

    # start HTTP server with SO_REUSEADDR
    class ReusableHTTPServer(HTTPServer):
        allow_reuse_address = True
    server = ReusableHTTPServer(("0.0.0.0", PORT), ViewerHandler)

    def cleanup():
        stop_animation()
        _set_debug_date("")
        bridge = Path(__file__).parent / "_pixel_bridge.bin"
        if bridge.exists():
            bridge.unlink()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
        server.server_close()
        print("\nstopped")


if __name__ == "__main__":
    main()
