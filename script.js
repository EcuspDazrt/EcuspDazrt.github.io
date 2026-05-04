'use strict';

/* ─── OSCILLOSCOPE ──────────────────────────────────────────── */
(function () {
  const canvas = document.getElementById('osc-canvas');
  const ctx    = canvas.getContext('2d');
  let phase    = 0;
  let W = 0, H = 0;

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }

  function draw() {
    if (!W || !H) { requestAnimationFrame(draw); return; }

    ctx.fillStyle = 'rgba(20,22,26,0.18)';
    ctx.fillRect(0, 0, W, H);

    ctx.save();
    ctx.strokeStyle = 'rgba(48,52,63,0.75)';
    ctx.lineWidth   = 0.5;
    const rows = 8, cols = 12;
    for (let r = 1; r < rows; r++) {
      const y = (H / rows) * r;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
    for (let c = 1; c < cols; c++) {
      const x = (W / cols) * c;
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    ctx.restore();

    const midY = H * 0.5;
    const amp  = H * 0.165;
    const env  = 0.82 + 0.18 * Math.sin(phase * 0.08);

    function signal(x, phaseOffset) {
      const t = (x / W) * Math.PI * 10 + phase + phaseOffset;
      return midY + env * amp * (
          0.52 * Math.sin(t)
        + 0.27 * Math.sin(t * 2.13 + 0.7)
        + 0.13 * Math.sin(t * 5.41 + 1.4)
        + 0.06 * Math.sin(t * 11.3 + 2.2)
      );
    }

    /* Ghost trace */
    ctx.save();
    ctx.beginPath();
    ctx.lineWidth   = 0.8;
    ctx.strokeStyle = 'rgba(47, 204, 149, 0.14)';
    for (let x = 0; x <= W; x++) {
      const y = signal(x, -0.22) + (Math.random() - 0.5) * amp * 0.03;
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();

    /* Primary trace */
    ctx.save();
    ctx.beginPath();
    ctx.lineWidth    = 1.5;
    ctx.strokeStyle  = '#2fcc95';
    ctx.shadowColor  = '#2fcc95';
    ctx.shadowBlur   = 7;
    for (let x = 0; x <= W; x++) {
      const noise = (Math.random() - 0.5) * amp * 0.045;
      const y     = signal(x, 0) + noise;
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();

    phase += 0.021;
    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
  draw();
})();


/* ─── RAIL ACTIVE STATE ─────────────────────────────────────── */
(function () {
  const items    = document.querySelectorAll('.rail-item');
  const sections = document.querySelectorAll('section[id]');

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        items.forEach(i => i.classList.remove('active'));
        const match = document.querySelector(`.rail-item[data-target="${entry.target.id}"]`);
        if (match) match.classList.add('active');
      }
    });
  }, { threshold: 0.35 });

  sections.forEach(s => observer.observe(s));
})();


/* ─── SCROLL REVEAL ─────────────────────────────────────────── */
(function () {
  const targets = document.querySelectorAll('.reveal, .reveal-stagger, .project-article');

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.07 });

  targets.forEach(t => observer.observe(t));
})();


/* ─── FOOTER YEAR ───────────────────────────────────────────── */
document.getElementById('footer-year').textContent =
  `Ecusp Dazrt — ${new Date().getFullYear()}`;


/* ─── 15-PUZZLE ─────────────────────────────────────────────── */
let puzzleBoard = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0];

function onDisableSolver() {
  setPuzzleStatus('Puzzle board disabled');
}

if (window.disableSolver) {
  onDisableSolver();
}

window.addEventListener('disableSolverChanged', () => {
  if (window.disableSolver) {
    onDisableSolver();
  }
});

function drawPuzzle() {
  const el = document.getElementById('puzzle-board');
  if (!el) return;
  el.innerHTML = '';
  puzzleBoard.forEach(n => {
    const tile = document.createElement('div');
    tile.className   = 'p-tile' + (n === 0 ? ' p-empty' : '');
    tile.textContent = n === 0 ? '' : n;
    tile.setAttribute('role', 'gridcell');
    el.appendChild(tile);
  });
}

function swapTiles(a, b) {
  [puzzleBoard[a], puzzleBoard[b]] = [puzzleBoard[b], puzzleBoard[a]];
}

function applyMove(dir) {
  const idx = puzzleBoard.indexOf(0);
  const row = Math.floor(idx / 4), col = idx % 4;
  if (dir === 'U' && row < 3) swapTiles(idx, idx + 4);
  if (dir === 'D' && row > 0) swapTiles(idx, idx - 4);
  if (dir === 'L' && col < 3) swapTiles(idx, idx + 1);
  if (dir === 'R' && col > 0) swapTiles(idx, idx - 1);
}

function animateSolution(moves) {
  let i = 0;
  const iv = setInterval(() => {
    if (i >= moves.length) { clearInterval(iv); return; }
    applyMove(moves[i++]);
    drawPuzzle();
  }, 60);
}

function setPuzzleStatus(msg, state) {
  const el = document.getElementById('puzzle-status');
  el.textContent = msg;
  el.className   = 'd-status' + (state ? ' ' + state : '');
}

async function requestSolve() {
  if (window.disableSolver) return;

  setPuzzleStatus('Computing optimal path…', 'busy');
  try {
    pyodide.globals.set("board_dict", pyodide.toPy({ board: puzzleBoard }));
    const moves = await pyodide.runPythonAsync(`solve(board_dict)`)

    animateSolution(moves);
    setPuzzleStatus(`Solved — ${moves.length} moves`, 'ok' )
  } catch {
    setPuzzleStatus('Error: was not able to generate solution', 'err');
  }
}

async function requestShuffle() {
  if (window.disableSolver) return;

  setPuzzleStatus('Generating solvable board state…', 'busy');
  try {
      const currBoard = await pyodide.runPythonAsync(`init_board()`);
      puzzleBoard = currBoard.toJs().flat();
      drawPuzzle();
      setPuzzleStatus('Shuffled — click Solve', '');
    } catch(err) {
      setPuzzleStatus('Error: was not able to generate board', 'err');
      console.log(err)
    }
}

drawPuzzle();

/* ─── DIGIT RECOGNIZER ──────────────────────────────────────── */
function onDisableDigitRec() {
  disableDigitRecFunc();
}

if (window.disableDigitRec) {
  onDisableDigitRec();
}

window.addEventListener('disableDigitRecChanged', () => {
  if (window.disableDigitRec) {
    onDisableDigitRec();
  }
});

(function () {
  const canvas = document.getElementById('digit-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  canvas.width  = 28;
  canvas.height = 28;

  ctx.lineWidth   = 2;
  ctx.lineCap     = 'round';
  ctx.lineJoin    = 'round';
  ctx.strokeStyle = '#ffffff';

  let drawing = false;

  function getScaledPos(e) {
    const rect = canvas.getBoundingClientRect();
    const src  = e.touches ? e.touches[0] : e;
    return {
      x: (src.clientX - rect.left) * (canvas.width  / rect.width),
      y: (src.clientY - rect.top)  * (canvas.height / rect.height)
    };
  }

  canvas.addEventListener('mousedown', e => {
    drawing = true;
    const p = getScaledPos(e);
    ctx.beginPath(); ctx.moveTo(p.x, p.y);
  });
  canvas.addEventListener('mousemove', e => {
    if (!drawing) return;
    const p = getScaledPos(e);
    ctx.lineTo(p.x, p.y); ctx.stroke();
  });
  canvas.addEventListener('mouseup',    () => { drawing = false; });
  canvas.addEventListener('mouseleave', () => { drawing = false; });

  canvas.addEventListener('touchstart', e => {
    e.preventDefault();
    drawing = true;
    const p = getScaledPos(e);
    ctx.beginPath(); ctx.moveTo(p.x, p.y);
  }, { passive: false });

  canvas.addEventListener('touchmove', e => {
    e.preventDefault();
    if (!drawing) return;
    const p = getScaledPos(e);
    ctx.lineTo(p.x, p.y); ctx.stroke();
  }, { passive: false });

  canvas.addEventListener('touchend', e => {
    e.preventDefault();
    drawing = false;
  }, { passive: false });
})();

function disableDigitRecFunc() {
  const r = document.getElementById('digit-result');
  r.textContent = 'Digit Recognizer Disabled'
  r.className = 'd-status disabled'
}

function clearDigit() {
  const canvas = document.getElementById('digit-canvas');
  const ctx    = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!disableDigitRec) {
  const r      = document.getElementById('digit-result');
  r.textContent = 'Draw a digit, then predict';
  r.className   = 'd-status';
  } 
}

async function predictDigit() {
  if (disableDigitRec) return;

  const canvas = document.getElementById('digit-canvas');
  const r      = document.getElementById('digit-result');
  r.textContent = 'Running inference…';
  r.className   = 'd-status busy';

  try {
    pyodide.globals.set('image', pyodide.toPy(canvas.toDataURL('image/png')))
    const raw = await pyodide.runPythonAsync(`predict({'image': image})`)
    const data = raw.toJs()

    r.textContent = `Prediction: ${data.digit} — ${(data.confidence * 100).toFixed(1)}% confidence`;
    r.className = `d-status ok`;
  } catch {
    r.textContent = 'Error: could not predict digit';
    r.className = 'd-status err';
  }
}