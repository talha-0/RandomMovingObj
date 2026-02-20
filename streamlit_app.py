"""
Streamlit application that embeds a full-viewport p5.js animation.
Features randomly moving shapes with dynamic rotations, a visual shape selector, 
and a modern glassmorphism control panel with native fullscreen support.
"""

import streamlit as st

# Configure Streamlit page layout
st.set_page_config(layout="wide", page_title="Random Shape (Hero)")

# Inject CSS to remove Streamlit paddings and force the iframe to fill the viewport
st.markdown(
    """
    <style>
    html, body, .reportview-container, .main, .block-container {
      height: 100%;
      margin: 0;
      padding: 0;
      overflow: hidden;
      background: #2b2b2b;
    }
    
    header, footer { display: none !important; }

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

    .stApp, .stAppViewContainer, .stMain {
      height: 100vh !important;
      overflow: hidden !important;
      background: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Core HTML, CSS, and p5.js logic injected into the Streamlit iframe
html = r'''
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Random Shape (Hero)</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.6.0/p5.min.js"></script>
    <style>
      /* Base and Canvas Setup */
      html, body { height: 100%; margin: 0; background: #2b2b2b; transition: background 0.3s ease; overflow: hidden; }
      #sketch-holder {
        position: fixed; inset: 0;
        width: 100vw; height: 100vh;
        z-index: 1;
      }

      /* Glassmorphism Control Panel */
      .controls {
        position: fixed;
        right: 20px;
        top: 20px;
        width: 330px;
        max-width: 85vw;
        z-index: 9999;
        padding: 20px;
        border-radius: 16px;
        background: rgba(30, 30, 30, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        transition: opacity 400ms ease, transform 400ms cubic-bezier(0.4, 0, 0.2, 1);
        opacity: 1;
        pointer-events: auto;
      }

      .controls.hidden {
        opacity: 0;
        transform: translateY(-10px) scale(0.98);
        pointer-events: none;
      }

      /* Typography and Layout Constraints */
      .controls h3 { margin: 0 0 16px 0; font-size: 20px; font-weight: 600; color: #ffffff; letter-spacing: 0.5px; }
      .control-row { display: flex; gap: 12px; align-items:center; margin: 12px 0; justify-content: space-between; }
      .control-col { display: flex; flex-direction: column; width: 100%; gap: 8px; margin: 16px 0; }
      .control-row label, .control-col label { min-width: 95px; font-size: 14px; font-weight: 500; color:#cdd9ed; }
      .control-row input[type="range"] { flex-grow: 1; cursor: pointer; }
      .btn-row { display:flex; gap:8px; margin-bottom: 8px; }
      .footer-note { margin-top:16px; font-size:12px; color:#8fa8c7; opacity:0.8; line-height: 1.4; }
      
      /* Visual Shape Selector Grid */
      .shape-grid { display: flex; gap: 8px; flex-wrap: wrap; width: 100%; }
      .shape-btn { 
        flex: 1; min-width: 38px; height: 38px; padding: 0; display: flex; align-items: center; justify-content: center; 
        font-size: 18px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); 
        border-radius: 8px; color: #fff; cursor: pointer; transition: 0.2s; 
      }
      .shape-btn:hover { background: rgba(255,255,255,0.15); transform: translateY(-2px); }
      .shape-btn.active { 
        background: rgba(39, 229, 138, 0.2); border-color: #27e58a; color: #27e58a; 
        box-shadow: 0 0 8px rgba(39, 229, 138, 0.3); 
      }

      /* Standard Buttons Styling */
      button.std-btn { 
        flex: 1; border-radius:8px; padding:10px 12px; border: 1px solid rgba(255,255,255,0.1); 
        background: rgba(255,255,255,0.05); color: #eaf2ff; cursor:pointer; font-weight: 500; transition: all 0.2s ease;
      }
      button.std-btn:hover { background: rgba(255,255,255,0.15); transform: translateY(-1px); }
      button.primary { background: linear-gradient(135deg,#27e58a,#0fb39b); color: #052018; font-weight:700; border: none; }
      button.primary:hover { box-shadow: 0 4px 12px rgba(39, 229, 138, 0.3); }
      button.danger:hover { background: rgba(235, 87, 87, 0.8); color: white; border-color: transparent;}
      button.fullscreen-btn { width: 100%; margin-top: 4px; background: rgba(255,255,255,0.1); }
      
      .checkbox-row { display:flex; align-items:center; justify-content: flex-start; gap:8px; color:#cfe8ff; font-size:14px; margin-top: 16px;}
      .checkbox-row input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; accent-color: #27e58a; }

      input[type="range"] { -webkit-appearance: none; background: transparent; }
      input[type="range"]::-webkit-slider-runnable-track { background: rgba(255,255,255,0.15); height:6px; border-radius:6px; }
      input[type="range"]::-webkit-slider-thumb { -webkit-appearance:none; width:16px; height:16px; border-radius:50%; background:#27e58a; box-shadow:0 0 8px rgba(0,0,0,0.4); margin-top:-5px; transition: transform 0.1s; }
      input[type="range"]::-webkit-slider-thumb:hover { transform: scale(1.2); }

      input[type="color"] { -webkit-appearance: none; border: none; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; padding: 0; background: transparent; }
      input[type="color"]::-webkit-color-swatch-wrapper { padding: 0; }
      input[type="color"]::-webkit-color-swatch { border: 2px solid rgba(255,255,255,0.2); border-radius: 8px; box-shadow: inset 0 0 4px rgba(0,0,0,0.2); }
    </style>
  </head>

  <body>
    <div id="sketch-holder"></div>

    <div class="controls" id="controls" role="region" aria-label="Controls">
      <h3>Animation Settings</h3>
      
      <div class="btn-row">
        <button id="startBtn" class="std-btn primary" aria-label="Start">Start</button>
        <button id="stopBtn" class="std-btn danger" aria-label="Stop">Stop</button>
        <button id="resetBtn" class="std-btn" aria-label="Reset">Reset</button>
      </div>
      <button id="fullscreenBtn" class="std-btn fullscreen-btn" aria-label="Toggle Fullscreen">⛶ Toggle Fullscreen</button>

      <div class="control-col">
        <label>Shape</label>
        <div class="shape-grid">
          <button class="shape-btn active" data-shape="circle" title="Circle">●</button>
          <button class="shape-btn" data-shape="glow" title="Neon Glow">🔅</button>
          <button class="shape-btn" data-shape="square" title="Square">■</button>
          <button class="shape-btn" data-shape="triangle" title="Arrow">➤</button>
          <button class="shape-btn" data-shape="star" title="Star">★</button>
          <button class="shape-btn" data-shape="heart" title="Heart">♥</button>
          <button class="shape-btn" data-shape="ring" title="Ring">◎</button>
        </div>
      </div>

      <div class="control-row">
        <label for="speedRange">Speed</label>
        <input id="speedRange" type="range" min="0.5" max="20" step="0.1" value="3" aria-label="Speed">
      </div>

      <div class="control-row">
        <label for="sizeRange">Size</label>
        <input id="sizeRange" type="range" min="8" max="100" step="1" value="24" aria-label="Shape Size">
      </div>

      <div class="control-row">
        <label for="pauseRange">Pause (ms)</label>
        <input id="pauseRange" type="range" min="0" max="2000" step="10" value="350" aria-label="Pause Duration">
      </div>

      <div class="control-row">
        <label for="dotColor">Object Color</label>
        <input type="color" id="dotColor" value="#00ffff" aria-label="Object Color">
      </div>
      
      <div class="control-row">
        <label for="bgColor">Background</label>
        <input type="color" id="bgColor" value="#2b2b2b" aria-label="Background Color">
      </div>

      <div class="control-row checkbox-row">
        <input id="showBoundary" type="checkbox" checked aria-label="Show Boundary">
        <label for="showBoundary">Show boundaries</label>
      </div>

      <div class="footer-note">Tip: The menu and cursor auto-hide after 2 seconds. Move your mouse to reveal them.</div>
    </div>

    <script>
      let config = {
        speed: 3,
        dot_size: 24,
        pause_ms: 350,
        color: '#00ffff',
        bg_color: '#2b2b2b',
        shape: 'circle',
        show_boundary: true
      };

      let dot = { x: 0, y: 0, angle: 0, remaining: 0, pausedUntil: 0 };
      let running = false;
      let margin = 15;
      let canvasW = 800, canvasH = 600;

      /**
       * Initializes the canvas, sets frame rate, and prepares the first movement.
       */
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

      /**
       * Dynamically resizes the canvas and recalculates bounds if the window changes size.
       */
      function windowResized() {
        const holder = document.getElementById('sketch-holder');
        canvasW = holder.clientWidth || window.innerWidth;
        canvasH = holder.clientHeight || window.innerHeight;
        resizeCanvas(canvasW, canvasH);
        clampDotPosition();
      }

      /**
       * Centers the shape on the canvas and clears its movement state.
       */
      function resetDotCenter() {
        dot.x = canvasW / 2;
        dot.y = canvasH / 2;
        dot.remaining = 0;
        dot.pausedUntil = 0;
      }

      /**
       * Assigns a random trajectory angle and travel distance based on screen proportions.
       */
      function pickNewMovement() {
        dot.angle = random(0, TWO_PI);
        const diag = sqrt(sq(canvasW) + sq(canvasH));
        const dynMin = min(100, diag * 0.1);
        const dynMax = min(600, diag * 0.6);
        dot.remaining = random(dynMin, dynMax);
        dot.pausedUntil = millis() + config.pause_ms;
      }

      /**
       * Enforces boundaries by snapping the shape back inside the margin limits dynamically based on size.
       */
      function clampDotPosition() {
        const offset = margin + (config.dot_size / 2);
        const maxX = canvasW / 2 - offset;
        const maxY = canvasH / 2 - offset;
        const centerX = canvasW / 2, centerY = canvasH / 2;
        
        let relX = dot.x - centerX;
        let relY = dot.y - centerY;
        
        if (relX > maxX) relX = maxX;
        if (relX < -maxX) relX = -maxX;
        if (relY > maxY) relY = maxY;
        if (relY < -maxY) relY = -maxY;
        
        dot.x = centerX + relX;
        dot.y = centerY + relY;
      }

      /**
       * Renders the faint rectangular bounding box limit on the canvas.
       */
      function drawBoundary() {
        if (!config.show_boundary) return;
        push();
        stroke(255, 120);
        strokeWeight(1.5);
        noFill();
        const offset = margin + (config.dot_size / 2);
        const maxX = canvasW / 2 - offset;
        const maxY = canvasH / 2 - offset;
        rectMode(CENTER);
        rect(canvasW / 2, canvasH / 2, maxX * 2, maxY * 2, 6);
        pop();
      }

      /**
       * Helper function to draw a multi-pointed star.
       */
      function drawStar(x, y, radius1, radius2, npoints) {
        let angle = TWO_PI / npoints;
        let halfAngle = angle / 2.0;
        beginShape();
        for (let a = -PI / 2; a < TWO_PI - PI / 2; a += angle) {
          let sx = x + cos(a) * radius2;
          let sy = y + sin(a) * radius2;
          vertex(sx, sy);
          sx = x + cos(a + halfAngle) * radius1;
          sy = y + sin(a + halfAngle) * radius1;
          vertex(sx, sy);
        }
        endShape(CLOSE);
      }

      /**
       * Helper function to draw a mathematically perfect heart using parametric equations.
       */
      function drawHeart(x, y, size) {
        push();
        translate(x, y - size * 0.15);
        beginShape();
        for (let a = 0; a < TWO_PI; a += 0.05) {
          let hx = 16 * pow(sin(a), 3);
          let hy = -(13 * cos(a) - 5 * cos(2 * a) - 2 * cos(3 * a) - cos(4 * a));
          vertex(hx * size * 0.03, hy * size * 0.03);
        }
        endShape(CLOSE);
        pop();
      }

      /**
       * Draws the selected geometry onto the canvas, applying dynamic rotations and shadow effects.
       */
      function drawDot() {
        push();
        translate(dot.x, dot.y);
        noStroke();
        fill(config.color);
        const size = config.dot_size;

        if (config.shape === 'circle') {
          ellipse(0, 0, size, size);
        } else if (config.shape === 'glow') {
          drawingContext.shadowBlur = size * 1.5;
          drawingContext.shadowColor = config.color;
          ellipse(0, 0, size, size);
        } else if (config.shape === 'square') {
          rotate(millis() / 1500.0); // Continuous tumbling
          rectMode(CENTER);
          rect(0, 0, size, size, size * 0.25); 
        } else if (config.shape === 'triangle') {
          rotate(dot.angle); // Strictly rotate to point in the current travel direction
          triangle(size / 2, 0, -size / 2, -size / 2.5, -size / 2, size / 2.5);
        } else if (config.shape === 'star') {
          rotate(millis() / 1000.0); // Continuous tumbling
          drawStar(0, 0, size / 2.5, size, 5);
        } else if (config.shape === 'heart') {
          drawHeart(0, 0, size);
        } else if (config.shape === 'ring') {
          noFill();
          stroke(config.color);
          strokeWeight(size * 0.2);
          ellipse(0, 0, size, size);
        }
        
        pop();
      }

      /**
       * Main p5 render loop executing every frame to update positions and draw objects.
       */
      function draw() {
        background(config.bg_color);
        canvasW = windowWidth;
        canvasH = windowHeight;

        drawBoundary();

        if (millis() < dot.pausedUntil || !running) {
          drawDot();
          return;
        }

        if (dot.remaining <= 0) { 
          pickNewMovement(); 
          drawDot(); 
          return; 
        }

        let step = min(config.speed, dot.remaining);
        dot.x += cos(dot.angle) * step;
        dot.y += sin(dot.angle) * step;
        dot.remaining -= step;

        const offset = margin + (config.dot_size / 2);
        const maxX = canvasW / 2 - offset;
        const maxY = canvasH / 2 - offset;
        const centerX = canvasW / 2, centerY = canvasH / 2;
        
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
          dot.remaining = 0;
          dot.pausedUntil = millis() + config.pause_ms;
        }

        drawDot();
      }

      // UI Control Bindings
      document.addEventListener('DOMContentLoaded', () => {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const resetBtn = document.getElementById('resetBtn');
        const fullscreenBtn = document.getElementById('fullscreenBtn');
        const shapeBtns = document.querySelectorAll('.shape-btn');
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

        // Handle native browser Fullscreen toggling
        fullscreenBtn.onclick = () => {
          if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch((err) => {
              console.log(`Error attempting to enable fullscreen: ${err.message}`);
            });
          } else {
            document.exitFullscreen();
          }
        };

        // Handle visual shape selection
        shapeBtns.forEach(btn => {
          btn.addEventListener('click', () => {
            shapeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            config.shape = btn.dataset.shape;
          });
        });

        speedRange.oninput = (e) => { config.speed = parseFloat(e.target.value); };
        sizeRange.oninput = (e) => { config.dot_size = parseInt(e.target.value); };
        pauseRange.oninput = (e) => { config.pause_ms = parseInt(e.target.value); };
        
        dotColorInput.oninput = (e) => { config.color = e.target.value; };
        bgColorInput.oninput = (e) => { 
            config.bg_color = e.target.value; 
            document.body.style.background = config.bg_color;
        };
        showBoundary.onchange = (e) => { config.show_boundary = e.target.checked; };

        // Auto-Hide Logic
        let hideTimer = null;
        const hideDelay = 2000;

        /**
         * Resets the inactivity timer, bringing back the controls and mouse cursor.
         */
        function scheduleHide() {
          if (hideTimer) clearTimeout(hideTimer);
          controlsEl.classList.remove('hidden');
          document.body.style.cursor = 'default';
          
          hideTimer = setTimeout(() => {
            controlsEl.classList.add('hidden');
            document.body.style.cursor = 'none';
          }, hideDelay);
        }

        window.addEventListener('mousemove', scheduleHide);
        window.addEventListener('touchstart', scheduleHide);
        window.addEventListener('pointerdown', scheduleHide);

        scheduleHide();
      });
    </script>
  </body>
</html>
'''

# Embed the HTML within Streamlit
st.components.v1.html(html, height=900, scrolling=False)