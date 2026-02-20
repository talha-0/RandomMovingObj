# streamlit_app.py
import streamlit as st

# Page config
st.set_page_config(layout="wide", page_title="Random Dot (Hero)")

# Outer CSS: remove Streamlit paddings and force the iframe to fill the viewport.
st.markdown(
    """
    <style>
    /* make Streamlit outer containers full-viewport and remove scrollbars */
    html, body, .reportview-container, .main, .block-container {
      height: 100%;
      margin: 0;
      padding: 0;
      overflow: hidden;
      background: #2b2b2b;
    }
    header, footer { display: none !important; } /* hide Streamlit chrome */

    /* Force the iframe created by st.components.v1.html to be full viewport */
    .stIFrame {
      position: fixed !important;
      inset: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      border: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
      z-index: 9998;
      background: transparent !important;
    }

    /* Ensure main app containers don't introduce scroll or extra space */
    .stApp, .stAppViewContainer, .stMain {
      height: 100vh !important;
      overflow: hidden !important;
      background: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Hero HTML + JS (p5.js). This is the inner page that will run inside the iframe.
html = r'''
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Random Dot (Hero)</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.6.0/p5.min.js"></script>
    <style>
      /* full viewport fixed canvas inside the iframe */
      html,body { height:100%; margin:0; background:#2b2b2b; }
      #sketch-holder {
        position: fixed; inset: 0;
        width: 100vw; height: 100vh;
        background: #2b2b2b; z-index: 1;
      }

      /* transparent glass controls (auto-hide) */
      .controls {
        position: fixed;
        right: 18px;
        top: 18px;
        width: 300px;
        max-width: 40vw;
        z-index: 9999;
        padding: 12px;
        border-radius: 12px;
        background: rgba(255,255,255,0.03); /* very transparent */
        color: white;
        box-shadow: 0 8px 30px rgba(0,0,0,0.45);
        backdrop-filter: blur(6px) saturate(120%);
        -webkit-backdrop-filter: blur(6px) saturate(120%);
        font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        transition: opacity 300ms ease, transform 300ms ease;
        opacity: 1;
        pointer-events: auto;
      }

      /* hidden state (auto-hide) */
      .controls.hidden {
        opacity: 0;
        transform: translateY(-8px);
        pointer-events: none;
      }

      .controls h3 { margin: 0 0 8px 0; font-size: 18px; color: #e9eef8; }
      .control-row { display: flex; gap: 8px; align-items:center; margin: 8px 0; }
      .control-row label { min-width: 90px; font-size: 13px; color:#d7e6ff; }
      .control-row input[type="range"] { width: 100%; }
      .btn-row { display:flex; gap:8px; margin-top:6px; }
      button, select { border-radius:8px; padding:8px 10px; border: none; background: rgba(255,255,255,0.06); color: #eaf2ff; cursor:pointer; }
      button.primary { background: linear-gradient(90deg,#27e58a,#0fb39b); color: #052018; font-weight:700; }
      .small { font-size: 12px; padding:6px 8px; }
      .checkbox-row { display:flex; align-items:center; gap:8px; color:#cfe8ff; font-size:13px; }
      .footer-note { margin-top:8px; font-size:12px; color:#9fbfe6; opacity:0.9; }

      input[type="range"]::-webkit-slider-runnable-track { background: rgba(255,255,255,0.12); height:8px; border-radius:6px; }
      input[type="range"]::-webkit-slider-thumb { -webkit-appearance:none; width:14px; height:14px; border-radius:50%; background:#fff; box-shadow:0 0 6px rgba(0,0,0,0.6); margin-top:-3px; }

      /* make sure body does not scroll inside iframe */
      body { overflow: hidden; }
    </style>
  </head>

  <body>
    <div id="sketch-holder"></div>

    <div class="controls" id="controls" role="region" aria-label="Controls">
      <h3>Controls</h3>
      <div class="control-row">
        <label>Animation</label>
        <div style="display:flex; gap:8px;">
          <button id="startBtn" class="small primary" aria-label="Start">Start</button>
          <button id="stopBtn" class="small" aria-label="Stop">Stop</button>
          <button id="resetBtn" class="small" aria-label="Reset">Reset</button>
        </div>
      </div>

      <div class="control-row">
        <label for="speedRange">Speed</label>
        <input id="speedRange" type="range" min="0.5" max="20" step="0.1" value="3" aria-label="Speed">
      </div>

      <div class="control-row">
        <label for="sizeRange">Dot Size</label>
        <input id="sizeRange" type="range" min="4" max="48" step="1" value="12" aria-label="Dot Size">
      </div>

      <div class="control-row">
        <label for="pauseRange">Pause (ms)</label>
        <input id="pauseRange" type="range" min="0" max="2000" step="10" value="350" aria-label="Pause Duration">
      </div>

      <div class="control-row">
        <label for="colorSelect">Color</label>
        <select id="colorSelect" aria-label="Color">
          <option value="cyan">Cyan</option>
          <option value="#ff5555">Red</option>
          <option value="#50fa8b">Green</option>
          <option value="#f1fa8c">Yellow</option>
          <option value="white">White</option>
        </select>
      </div>

      <div class="control-row checkbox-row">
        <input id="showBoundary" type="checkbox" checked aria-label="Show Boundary">
        <label for="showBoundary">Show boundary</label>
      </div>

      <div class="footer-note">Tip: When the dot reaches the edge it pauses, then continues in a random direction.</div>
    </div>

    <script>
      // ---- sketch config & state ----
      let config = {
        speed: 3,
        dot_size: 12,
        pause_ms: 350,
        color: 'cyan',
        show_boundary: true
      };

      let dot = { x:0, y:0, angle:0, remaining:0, pausedUntil:0 };
      let running = false;
      let margin = 15;
      let canvasW = 800, canvasH = 600;

      function setup() {
        const holder = document.getElementById('sketch-holder');
        canvasW = holder.clientWidth || window.innerWidth;
        canvasH = holder.clientHeight || window.innerHeight;
        let cnv = createCanvas(canvasW, canvasH);
        cnv.parent('sketch-holder');
        frameRate(60);
        resetDotCenter();
        pickNewMovement();
      }

      function windowResized() {
        const holder = document.getElementById('sketch-holder');
        canvasW = holder.clientWidth || window.innerWidth;
        canvasH = holder.clientHeight || window.innerHeight;
        resizeCanvas(canvasW, canvasH);
        clampDotPosition();
      }

      function resetDotCenter() {
        dot.x = canvasW/2;
        dot.y = canvasH/2;
        dot.remaining = 0;
        dot.pausedUntil = 0;
      }

      function pickNewMovement() {
        dot.angle = random(0, TWO_PI);
        const diag = sqrt(sq(canvasW) + sq(canvasH));
        const dynMin = min(100, diag * 0.1);
        const dynMax = min(600, diag * 0.6);
        dot.remaining = random(dynMin, dynMax);
        dot.pausedUntil = millis() + config.pause_ms;
      }

      function clampDotPosition() {
        const maxX = canvasW/2 - margin;
        const maxY = canvasH/2 - margin;
        const centerX = canvasW/2, centerY = canvasH/2;
        let relX = dot.x - centerX;
        let relY = dot.y - centerY;
        if (relX > maxX) relX = maxX;
        if (relX < -maxX) relX = -maxX;
        if (relY > maxY) relY = maxY;
        if (relY < -maxY) relY = -maxY;
        dot.x = centerX + relX;
        dot.y = centerY + relY;
      }

      /* OLD bounce logic (commented out)
      function bounceIfNeeded() {
        ...
      }
      */

      function drawBoundary() {
        if (!config.show_boundary) return;
        push();
        stroke(255, 200);
        strokeWeight(1.5);
        noFill();
        const maxX = canvasW/2 - margin;
        const maxY = canvasH/2 - margin;
        rectMode(CENTER);
        rect(canvasW/2, canvasH/2, maxX*2, maxY*2, 6);
        pop();
      }

      function draw() {
        background('#2b2b2b');
        canvasW = windowWidth;
        canvasH = windowHeight;

        drawBoundary();

        // If paused until a later time, we still draw but don't move.
        if (millis() < dot.pausedUntil) {
          drawDot();
          return;
        }

        // Normal control flow: if not running, just draw
        if (!running) { drawDot(); return; }

        // If movement finished (remaining <= 0), pick a new heading+distance and pause (as before)
        if (dot.remaining <= 0) { pickNewMovement(); drawDot(); return; }

        // perform a step
        let step = min(config.speed, dot.remaining);
        dot.x += cos(dot.angle) * step;
        dot.y += sin(dot.angle) * step;
        dot.remaining -= step;

        // clamp to boundary and when hits an edge: pause then later pick a random new direction
        const maxX = canvasW/2 - margin;
        const maxY = canvasH/2 - margin;
        const centerX = canvasW/2, centerY = canvasH/2;
        let relX = dot.x - centerX;
        let relY = dot.y - centerY;

        let hitEdge = false;
        if (relX >= maxX) { relX = maxX; hitEdge = true; }
        if (relX <= -maxX) { relX = -maxX; hitEdge = true; }
        if (relY >= maxY) { relY = maxY; hitEdge = true; }
        if (relY <= -maxY) { relY = -maxY; hitEdge = true; }

        dot.x = centerX + relX;
        dot.y = centerY + relY;

        if (hitEdge) {
          // NEW BEHAVIOR:
          // - Do NOT stop the animation permanently.
          // - Set remaining=0 so the pickNewMovement() branch will run after the pause.
          // - Set pausedUntil so we wait for the configured pause_ms before moving again.
          dot.remaining = 0;
          dot.pausedUntil = millis() + config.pause_ms;
        }

        drawDot();
      }

      function drawDot() {
        push();
        noStroke();
        fill(config.color);
        const size = config.dot_size;
        ellipse(dot.x, dot.y, size, size);
        pop();
      }

      // ---- UI wiring & auto-hide logic ----
      document.addEventListener('DOMContentLoaded', () => {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const resetBtn = document.getElementById('resetBtn');
        const speedRange = document.getElementById('speedRange');
        const sizeRange = document.getElementById('sizeRange');
        const pauseRange = document.getElementById('pauseRange');
        const colorSelect = document.getElementById('colorSelect');
        const showBoundary = document.getElementById('showBoundary');
        const controlsEl = document.getElementById('controls');

        startBtn.onclick = () => { running = true; };
        stopBtn.onclick = () => { running = false; };
        resetBtn.onclick = () => { resetDotCenter(); pickNewMovement(); running = false; };

        speedRange.oninput = (e) => { config.speed = parseFloat(e.target.value); };
        sizeRange.oninput = (e) => { config.dot_size = parseInt(e.target.value); };
        pauseRange.oninput = (e) => { config.pause_ms = parseInt(e.target.value); };
        colorSelect.onchange = (e) => { config.color = e.target.value; };
        showBoundary.onchange = (e) => { config.show_boundary = e.target.checked; };

        // auto-hide controls after idle (2.2s) and re-show on mouse movement/touch
        let hideTimer = null;
        const hideDelay = 2200;

        function scheduleHide() {
          if (hideTimer) clearTimeout(hideTimer);
          controlsEl.classList.remove('hidden');
          hideTimer = setTimeout(() => {
            controlsEl.classList.add('hidden');
          }, hideDelay);
        }

        window.addEventListener('mousemove', scheduleHide);
        window.addEventListener('touchstart', scheduleHide);
        window.addEventListener('pointerdown', scheduleHide);

        // show initially then hide after delay
        scheduleHide();
      });

      // defaults
      config.speed = 3;
      config.dot_size = 12;
      config.pause_ms = 350;
      config.color = 'cyan';
      config.show_boundary = true;
    </script>
  </body>
</html>
'''

# Embed the HTML. height param is ignored by our CSS override, but required by Streamlit.
st.components.v1.html(html, height=900, scrolling=False)