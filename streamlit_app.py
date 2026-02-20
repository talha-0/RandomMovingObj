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
      html,body { height:100%; margin:0; background:#2b2b2b; transition: background 0.3s ease; }
      #sketch-holder {
        position: fixed; inset: 0;
        width: 100vw; height: 100vh;
        z-index: 1;
      }

      /* transparent glass controls (auto-hide) */
      .controls {
        position: fixed;
        right: 20px;
        top: 20px;
        width: 320px;
        max-width: 85vw;
        z-index: 9999;
        padding: 20px;
        border-radius: 16px;
        background: rgba(30, 30, 30, 0.4); /* Darker transparent base */
        border: 1px solid rgba(255, 255, 255, 0.1); /* Subtle border */
        color: white;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        transition: opacity 400ms ease, transform 400ms cubic-bezier(0.4, 0, 0.2, 1);
        opacity: 1;
        pointer-events: auto;
      }

      /* hidden state (auto-hide) */
      .controls.hidden {
        opacity: 0;
        transform: translateY(-10px) scale(0.98);
        pointer-events: none;
      }

      .controls h3 { margin: 0 0 16px 0; font-size: 20px; font-weight: 600; color: #ffffff; letter-spacing: 0.5px; }
      .control-row { display: flex; gap: 12px; align-items:center; margin: 12px 0; justify-content: space-between; }
      .control-row label { min-width: 95px; font-size: 14px; font-weight: 500; color:#cdd9ed; }
      .control-row input[type="range"] { flex-grow: 1; cursor: pointer; }
      
      .btn-row { display:flex; gap:8px; margin-bottom: 16px; }
      button { 
        flex: 1;
        border-radius:8px; 
        padding:10px 12px; 
        border: 1px solid rgba(255,255,255,0.1); 
        background: rgba(255,255,255,0.05); 
        color: #eaf2ff; 
        cursor:pointer; 
        font-weight: 500;
        transition: all 0.2s ease;
      }
      button:hover { background: rgba(255,255,255,0.15); transform: translateY(-1px); }
      button.primary { background: linear-gradient(135deg,#27e58a,#0fb39b); color: #052018; font-weight:700; border: none; }
      button.primary:hover { box-shadow: 0 4px 12px rgba(39, 229, 138, 0.3); }
      button.danger:hover { background: rgba(235, 87, 87, 0.8); color: white; border-color: transparent;}
      
      .checkbox-row { display:flex; align-items:center; justify-content: flex-start; gap:8px; color:#cfe8ff; font-size:14px; margin-top: 16px;}
      .checkbox-row input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; accent-color: #27e58a; }
      
      .footer-note { margin-top:16px; font-size:12px; color:#8fa8c7; opacity:0.8; line-height: 1.4; }

      /* Modern Range Slider */
      input[type="range"] { -webkit-appearance: none; background: transparent; }
      input[type="range"]::-webkit-slider-runnable-track { background: rgba(255,255,255,0.15); height:6px; border-radius:6px; }
      input[type="range"]::-webkit-slider-thumb { -webkit-appearance:none; width:16px; height:16px; border-radius:50%; background:#27e58a; box-shadow:0 0 8px rgba(0,0,0,0.4); margin-top:-5px; transition: transform 0.1s; }
      input[type="range"]::-webkit-slider-thumb:hover { transform: scale(1.2); }

      /* Sleek Color Picker */
      input[type="color"] {
        -webkit-appearance: none;
        border: none;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        cursor: pointer;
        padding: 0;
        background: transparent;
      }
      input[type="color"]::-webkit-color-swatch-wrapper { padding: 0; }
      input[type="color"]::-webkit-color-swatch {
        border: 2px solid rgba(255,255,255,0.2);
        border-radius: 8px;
        box-shadow: inset 0 0 4px rgba(0,0,0,0.2);
      }

      /* make sure body does not scroll inside iframe */
      body { overflow: hidden; }
    </style>
  </head>

  <body>
    <div id="sketch-holder"></div>

    <div class="controls" id="controls" role="region" aria-label="Controls">
      <h3>Animation Settings</h3>
      
      <div class="btn-row">
        <button id="startBtn" class="primary" aria-label="Start">Start</button>
        <button id="stopBtn" class="danger" aria-label="Stop">Stop</button>
        <button id="resetBtn" aria-label="Reset">Reset</button>
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
        <label for="dotColor">Dot Color</label>
        <input type="color" id="dotColor" value="#00ffff" aria-label="Dot Color">
      </div>
      
      <div class="control-row">
        <label for="bgColor">Background</label>
        <input type="color" id="bgColor" value="#2b2b2b" aria-label="Background Color">
      </div>

      <div class="control-row checkbox-row">
        <input id="showBoundary" type="checkbox" checked aria-label="Show Boundary">
        <label for="showBoundary">Show boundaries</label>
      </div>

      <div class="footer-note">Tip: The menu auto-hides. Move your mouse to reveal it. When the dot reaches the edge it pauses, then continues in a random direction.</div>
    </div>

    <script>
      // ---- sketch config & state ----
      let config = {
        speed: 3,
        dot_size: 12,
        pause_ms: 350,
        color: '#00ffff',
        bg_color: '#2b2b2b',
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

      function drawBoundary() {
        if (!config.show_boundary) return;
        push();
        stroke(255, 120);
        strokeWeight(1.5);
        noFill();
        const maxX = canvasW/2 - margin;
        const maxY = canvasH/2 - margin;
        rectMode(CENTER);
        rect(canvasW/2, canvasH/2, maxX*2, maxY*2, 6);
        pop();
      }

      function draw() {
        background(config.bg_color);
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
          // NEW BEHAVIOR: Set remaining=0 so the pickNewMovement() branch will run after the pause.
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
        const dotColorInput = document.getElementById('dotColor');
        const bgColorInput = document.getElementById('bgColor');
        const showBoundary = document.getElementById('showBoundary');
        const controlsEl = document.getElementById('controls');

        startBtn.onclick = () => { running = true; };
        stopBtn.onclick = () => { running = false; };
        resetBtn.onclick = () => { resetDotCenter(); pickNewMovement(); running = false; };

        speedRange.oninput = (e) => { config.speed = parseFloat(e.target.value); };
        sizeRange.oninput = (e) => { config.dot_size = parseInt(e.target.value); };
        pauseRange.oninput = (e) => { config.pause_ms = parseInt(e.target.value); };
        
        dotColorInput.oninput = (e) => { config.color = e.target.value; };
        bgColorInput.oninput = (e) => { 
            config.bg_color = e.target.value; 
            document.body.style.background = config.bg_color; // Sync HTML body color
        };
        
        showBoundary.onchange = (e) => { config.show_boundary = e.target.checked; };

        // auto-hide controls after idle (2.5s) and re-show on mouse movement/touch
        let hideTimer = null;
        const hideDelay = 2500;

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
    </script>
  </body>
</html>
'''

# Embed the HTML. height param is ignored by our CSS override, but required by Streamlit.
st.components.v1.html(html, height=900, scrolling=False)