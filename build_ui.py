import builtins
import time

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Asteroid Defence — Start</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:wght@100..900&family=Public+Sans:ital,wght@0,100..900;1,100..900&family=Space+Grotesk:wght@300..700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0c0c0e; --card: rgba(30,30,34,0.9); --card-border: rgba(255,255,255,0.06);
      --accent: #ff5e3a; --text: #f0f0f5; --muted: #777;
      --font-body: 'DM Mono', monospace; --font-sub: 'Public Sans', sans-serif;
      --font-head: 'Inter', sans-serif; --font-title: 'Space Grotesk', sans-serif;
      --success: #4fc3f7; --fail: #ff3333; --pass: #66bb6a;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; cursor: none !important; }

    #custom-cursor {
      position: fixed; width: 36px; height: 36px;
      background: url('/cursor/asteroid.png') center/contain no-repeat;
      pointer-events: none; z-index: 99999; transform: translate(-50%, -50%);
    }

    html, body { width: 100%; height: 100%; font-family: var(--font-body); background: var(--bg); color: var(--text); overflow: hidden; }

    /* Nav */
    .top-nav {
      position: fixed; top: 16px; left: 50%; transform: translateX(-50%);
      width: calc(100% - 40px); max-width: 960px; height: 52px;
      background: rgba(22, 22, 22, 0.88); backdrop-filter: blur(14px);
      border-radius: 32px; z-index: 100; display: flex; align-items: center; justify-content: space-between;
      padding: 0 8px 0 22px; border: 1px solid var(--card-border);
      box-shadow: 0 6px 30px rgba(0,0,0,0.5);
    }
    .nav-l { display: flex; align-items: center; gap: 8px; font-family: var(--font-title); font-weight: 700; font-size: 0.95rem; color: #fff; letter-spacing: 0.06em; }
    .nav-l .dot { width: 13px; height: 13px; background: var(--accent); border-radius: 3px; transform: rotate(45deg); }
    .nav-r a { background: #f4f4f4; color: #000; padding: 9px 20px; border-radius: 22px; text-decoration: none; font-family: var(--font-head); font-weight: 600; font-size: 0.82rem; transition: opacity 0.3s; }
    
    .env-tags {
      position: fixed; top: 80px; left: 50%; transform: translateX(-50%);
      display: flex; gap: 12px; z-index: 90;
    }
    .env-tag {
      background: rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px;
      padding: 5px 12px; font-family: var(--font-mono); font-size: 0.7rem; color: #aaa;
    }

    #intro, #transition { display: flex; position: fixed; inset: 0; background: #000; z-index: 60; align-items: center; justify-content: center; transition: all 0.7s;}
    #transition { display: none; flex-direction: column; gap: 24px; }
    
    .circle-wrap { position: relative; width: 340px; height: 340px; }
    .circle-wrap svg { width: 100%; height: 100%; }
    .spin-g { animation: sp 10s linear infinite; transform-origin: 200px 200px; }
    @keyframes sp { to { transform: rotate(360deg); } }
    .play-circle { position: absolute; top: 50%; left: 50%; width: 90px; height: 90px; border-radius: 50%; background: rgba(255,255,255,0.07); transform: translate(-50%,-50%); border: 1px solid rgba(255,255,255,0.12); display: flex; justify-content: center; align-items: center; transition: 0.3s;}
    .play-circle:hover { background: rgba(255,255,255,0.14); transform: translate(-50%,-50%) scale(1.08); }
    .play-circle svg { width: 24px; height: 24px; fill: #fff; margin-left: 3px; }

    #dash { width: 100vw; height: 100vh; display: none; flex-direction: column; }
    .grid { flex: 1; display: grid; grid-template-columns: 1fr; grid-template-rows: auto 1fr; gap: 16px; padding: 120px 20px 24px 20px; overflow: hidden; }

    .pipeline-nav { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 5px; scrollbar-width: none; flex-wrap: nowrap; }
    .pipe-step { background: rgba(30, 30, 34, 0.5); border: 1px solid var(--card-border); border-radius: 20px; padding: 10px 20px; font-family: var(--font-head); font-size: 0.9rem; font-weight: 500; color: var(--muted); flex-shrink: 0; transition: all 0.3s; cursor: pointer !important; }
    .pipe-step.active { background: var(--accent); color: #fff; border-color: var(--accent); }
    .pipe-step.done { background: rgba(102, 187, 106, 0.15); border-color: var(--pass); color: var(--pass); }

    .main-view { border-radius: 28px; background: var(--card); border: 1px solid var(--card-border); padding: 30px; display: flex; gap: 20px; height: 100%; overflow: hidden;}
    .left-panel { flex: 2; border-right: 1px solid rgba(255,255,255,0.05); padding-right: 20px; display: flex; flex-direction: column; overflow-y: auto; position: relative;}
    .right-panel { flex: 1; padding-left: 20px; display: flex; flex-direction: column; overflow-y: auto;}

    .btn-run { background: var(--accent); color: #fff; padding: 15px 30px; border-radius: 30px; border: none; margin-top: 30px; font-weight: 600; cursor: pointer !important; transition: 0.3s;}
    .btn-run:disabled { opacity: 0.5; pointer-events: none;}
    
    .concept-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;}
    .tag { font-family: var(--font-mono); font-size: 0.75rem; color: #888; border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 12px; }
    .tag.glow { border-color: var(--success); color: var(--success); background: rgba(79, 195, 247, 0.05); box-shadow: 0 0 10px rgba(79, 195, 247, 0.3);}
    .tag.tsp { border-color: #ba68c8; color: #ba68c8; background: rgba(186, 104, 200, 0.05); box-shadow: 0 0 10px rgba(186, 104, 200, 0.3);}

    .vis-area { flex: 1; background: #000; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); margin-top: 20px; overflow: hidden; display: flex; position: relative; min-height: 480px; padding: 20px;}
    .viz-container { width: 100%; height: 100%; display: none; flex-direction: column; position: relative; }
    .viz-container.active { display: flex; }

    /* Step 0 */
    .scenario-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;}
    .scenario-card { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 20px; cursor: pointer !important; transition: 0.2s;}
    .scenario-card.selected { border-color: var(--accent); }
    .s-row { display: flex; justify-content: space-between; font-size: 0.85rem; color: #aaa; margin-top:8px;}

    .edi-label { display:block; font-family:var(--font-mono); font-size:0.75rem; color:#aaa; margin-bottom:5px;}
    .edi-input { width:100%; border:1px solid #444; background:#111; color:#fff; padding:8px 12px; border-radius:6px; font-family:var(--font-mono); font-size:0.9rem; outline:none; transition:0.3s;}
    .edi-input:focus { border-color:var(--accent); box-shadow:0 0 10px rgba(255,94,58,0.2);}

    /* Step 1 */
    .formulation-box { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; margin-bottom: 12px; opacity: 0; transform: translateY(10px); transition: 0.5s;}
    .formulation-box.show { opacity: 1; transform: translateY(0); }
    .tsp-box { position: absolute; bottom: 20px; right: 20px; border: 1px dashed #ba68c8; padding: 10px; border-radius: 8px; color: #ba68c8; font-size: 0.75rem; text-align: center; opacity: 0;}

    /* Step 2 Search */
    .search-modes { position: absolute; right: 20px; top: 20px; display: flex; gap: 5px; z-index: 10;}
    .btn-sm { background: #222; border: 1px solid #444; color: #aaa; padding: 5px 10px; border-radius: 4px; font-family: var(--font-mono); font-size: 0.7rem; cursor: pointer !important;}
    .btn-sm.active { background: var(--success); color: #000; border-color: var(--success);}

    .frontier-panel { position: absolute; left: 20px; top: 20px; width: 140px; background: rgba(0,0,0,0.8); border: 1px solid #444; border-radius: 8px; padding: 10px; font-family: var(--font-mono); font-size: 0.7rem; color: #fff; z-index: 10;}
    
    .node { position: absolute; padding: 10px; background: #1a1a1e; border: 2px solid #333; border-radius: 8px; font-size: 0.8rem; text-align: center; transform: translate(-50%, -50%) scale(0); opacity: 0; transition: all 0.4s; z-index: 2;}
    .node.expand { transform: translate(-50%, -50%) scale(1); opacity: 1; border-color: var(--success);}
    .node.goal { border-color: var(--pass); box-shadow: 0 0 15px rgba(102, 187, 106, 0.4);}
    .node .f-val { position: absolute; top: -20px; left: 50%; transform: translateX(-50%); color: var(--success); font-size: 0.65rem; white-space: nowrap; display: none;}
    .node.show-f .f-val { display: block;}
    
    .edge { position: absolute; height: 2px; background: #333; transform-origin: left center; z-index: 1; opacity: 0; transition: 0.4s;}
    .edge.show { opacity: 1; }
    .edge.active { background: var(--success); }

    /* Step 3 CSP */
    .csp-grid { width: 100%; display: flex; flex-direction: column; gap: 15px; position:relative; z-index:2;}
    .csp-card { display: flex; justify-content: space-between; background: #1a1a1e; padding: 15px; border-radius: 12px; border: 1px solid #333; opacity: 0; transform: translateX(-20px); transition: 0.5s;}
    .csp-card.show { opacity: 1; transform: translateX(0); }
    .csp-card.rejected { opacity: 0.4; text-decoration: line-through; border-color: var(--fail);}
    .c-badge { padding: 4px 8px; font-size: 0.7rem; border-radius: 4px; background: #333;}
    .c-badge.pass { background: rgba(102, 187, 106, 0.2); color: var(--pass);}
    .c-badge.fail { background: rgba(255, 51, 51, 0.2); color: var(--fail);}
    .csp-gate { position: absolute; bottom: 60px; left: 50%; width:80%; transform: translateX(-50%); padding: 10px 20px; border: 2px dashed #666; color: #888; font-family: var(--font-head); font-weight: bold; border-radius: 12px; text-align:center; z-index:1; background: rgba(0,0,0,0.5);}
    .csp-gate.active { border-color: var(--success); color: var(--success); box-shadow: 0 0 20px rgba(79,195,247,0.3);}
    .csp-matrix { 
      position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); 
      width: 90%; background: rgba(255,255,255,0.05); border-radius: 12px; padding: 12px;
      font-size: 0.75rem; color: #aaa; text-align: center; opacity: 0; transition: 0.5s;
      border: 1px solid rgba(255,255,255,0.1);
    }
    .csp-matrix.show { opacity: 1; transform: translateX(-50%) translateY(-10px); }

    /* Step 4 MM */
    .adv-head { font-family: var(--font-mono); font-size: 0.8rem; color: #888; position: absolute; left: 20px; padding:4px 8px; border:1px solid #333; border-radius:4px; background:#111;}
    .prune-line { position: absolute; width: 40px; height: 2px; background: var(--fail); transform: rotate(-45deg); z-index: 3;}
    .ab-panel { position: absolute; right: 20px; top: 120px; background: rgba(0,0,0,0.8); border: 1px dashed var(--fail); border-radius: 8px; padding: 10px; font-family: var(--font-mono); font-size: 0.75rem; color: #fff; z-index: 10;}
    .eval-text { position: absolute; color: var(--accent); font-size: 0.65rem; font-family: var(--font-mono); opacity: 0; transition: 0.3s; transform: translate(-50%, -100%); white-space: nowrap; top: -10px; left: 50%; z-index: 10; background: rgba(0,0,0,0.9); padding: 4px 8px; border-radius: 4px; border: 1px solid rgba(255,94,58,0.5); pointer-events:none;}
    .eval-text.show { opacity: 1; transform: translate(-50%, -150%);}
    
    /* Step 5 KB */
    .kb-panel { width: 100%; display: flex; flex-direction: column; gap: 15px;}
    .kb-rule { padding: 12px; background: rgba(255,255,255,0.03); border: 1px solid transparent; border-radius: 8px; font-size: 0.8rem; opacity: 0;}
    .kb-rule.fire { border-color: var(--accent); background: rgba(255, 94, 58, 0.1); color: #fff;}

    .step-content { display: none; flex-direction: column; width: 100%; height: 100%;}
    .step-content.active { display: flex; }
    
    .log-box { flex: 1; background: rgba(0,0,0,0.5); padding: 15px; border-radius: 12px; font-size: 0.8rem; overflow-y: auto; display: flex; flex-direction: column; gap: 8px;}
    .log-entry { border-left: 2px solid var(--accent); padding-left: 8px; opacity: 0; animation: fadeIn 0.3s forwards;}
    @keyframes fadeIn { to { opacity: 1; } from { opacity: 0; } }

  </style>
</head>
<body>
  <div id="custom-cursor"></div>

  <nav class="top-nav">
    <div class="nav-l"><div class="dot"></div><span>AI Asteroid Defence</span></div>
    <div class="nav-r"><a href="/" id="home-btn">Home</a></div>
  </nav>

  <div class="env-tags">
    <span class="env-tag">Single-Agent</span>
    <span class="env-tag">Deterministic</span>
    <span class="env-tag">Known State Space</span>
  </div>

  <div id="intro">
    <div class="circle-wrap"><svg viewBox="0 0 400 400"><defs><path id="cp" d="M200,200 m-160,0 a160,160 0 1,0 320,0 a160,160 0 1,0 -320,0" fill="none"/></defs><g class="spin-g"><text fill="white" font-size="20"><textPath href="#cp" startOffset="0%">— AstroPath AI Mission Planner №⁜※ — AstroPath AI Mission Planner №⁜※</textPath></text></g></svg><div class="play-circle" id="play-btn"><svg viewBox="0 0 24 24"><polygon points="7,4 20,12 7,20"/></svg></div></div>
  </div>

  <div id="transition">
    <div style="font-family: var(--font-title); font-size: 1.4rem; color: #fff;">Initializing Autonomous Systems</div>
  </div>

  <div id="dash">
    <div class="grid">
      <div class="pipeline-nav" id="pipeline-nav-bar">
        <div class="pipe-step active" id="ps-0">0. Scenario Selection</div>
        <div class="pipe-step" id="ps-1">1. Formulate Problem</div>
        <div class="pipe-step" id="ps-2">2. Search (Strategies)</div>
        <div class="pipe-step" id="ps-3">3. CSP (Constraints)</div>
        <div class="pipe-step" id="ps-4">4. Adversarial (Minimax)</div>
        <div class="pipe-step" id="ps-5">5. Rule Base (Logic)</div>
        <div class="pipe-step" id="ps-6">6. Final Decision</div>
      </div>

      <div class="main-view">
        <div class="left-panel">
          
          <div class="step-content active" id="step-0">
            <h2 style="font-family: var(--font-title); font-size: 2.2rem; margin-bottom: 20px;">Select Threat Scenario</h2>
            <div class="concept-tags">
              <span class="tag glow">Environment</span><span class="tag glow">Frames Representation</span>
            </div>
            <div class="scenario-grid" id="scenario-grid"></div>

            <div class="editor-panel" id="editor-panel" style="display:none; margin-top:20px; background:rgba(0,0,0,0.5); border:1px solid #333; padding:20px; border-radius:12px;">
              <h3 style="color:var(--accent); margin-bottom:15px; font-family:var(--font-head); font-size:1.1rem;">Override Mission Constraints</h3>
              <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                <div>
                  <label class="edi-label">Diameter (m)</label>
                  <input type="number" class="edi-input" id="edit-diam">
                </div>
                <div>
                  <label class="edi-label">Mass (e.g. 1e7)</label>
                  <div style="display:flex; align-items:center; gap:5px;">
                    <input type="text" class="edi-input" id="edit-mass" style="flex:1;">
                    <span style="color:#888; font-size:0.8rem;">kg</span>
                  </div>
                </div>
                <div>
                  <label class="edi-label">Time to Impact (days)</label>
                  <input type="number" class="edi-input" id="edit-time">
                </div>
                <div>
                  <label class="edi-label">Risk Level</label>
                  <select class="edi-input" id="edit-risk">
                    <option value="Moderate">Moderate</option>
                    <option value="High">High</option>
                    <option value="Critical">Critical</option>
                  </select>
                </div>
                <div>
                  <label class="edi-label">Global Budget Limit (Billion $)</label>
                  <input type="number" step="0.1" class="edi-input" id="edit-budget" value="2.0">
                </div>
              </div>
            </div>

            <button class="btn-run" id="btn-run-ai" disabled>Deploy Intelligent Agent</button>
          </div>

          <div class="step-content" id="step-vp">
            <h2 id="st-head" style="font-family: var(--font-title); font-size: 1.8rem; margin-bottom: 10px;">...</h2>
            <div class="concept-tags" id="active-concepts"></div>

            <div class="vis-area" id="vis-box">
              
              <div class="viz-container" id="viz-1">
                <div class="formulation-box" id="f-init"><h4>Initial State s₀</h4><p id="t-init-state">...</p></div>
                <div class="formulation-box" id="f-goal"><h4>Goal State g</h4><p>Earth safe, impact avoided.</p></div>
                <div class="formulation-box" id="f-actions"><h4>Actions A(s)</h4><p>Deploy: [Kinetic, Nuclear, Tractor, Sail]</p></div>
                <div class="tsp-box" id="tsp-box">TSP Analogy:<br>Optimal Path through<br>Action Space</div>
              </div>

              <div class="viz-container" id="viz-2">
                <div class="search-modes" id="search-mode-btns" style="display:none;">
                  <button class="btn-sm" onclick="runSearchMode('BFS')">BFS</button>
                  <button class="btn-sm" onclick="runSearchMode('DFS')">DFS</button>
                  <button class="btn-sm" onclick="runSearchMode('UCS')">UCS</button>
                  <button class="btn-sm" onclick="runSearchMode('A*')">A*</button>
                </div>
                <div class="frontier-panel">
                  <div style="color:var(--accent); border-bottom:1px solid #444; margin-bottom: 5px; padding-bottom:3px;">Open List (Frontier)</div>
                  <div id="frontier-list" style="display:flex; flex-direction:column; gap:4px;"></div>
                </div>
                <div id="tree-canvas" style="position: absolute; inset:0;"></div>
              </div>

              <div class="viz-container" id="viz-3">
                <div class="csp-grid" id="csp-list"></div>
                <div class="csp-gate" id="csp-gate">CONSTRAINT SATISFACTION CHECK GATE</div>
                <div class="csp-matrix" id="csp-matrix"><b>CSP Analysis</b><br><span id="csp-summary">Evaluating domains...</span></div>
              </div>

              <div class="viz-container" id="viz-4">
                <div class="adv-head" style="top:20px;">MAX Level (Planner)</div>
                <div class="adv-head" style="top:150px;">MIN Level (Nature: worst-case failure probs)</div>
                <div class="ab-panel" id="ab-panel">
                  <div style="color:var(--accent); border-bottom:1px dashed #444; margin-bottom: 5px; padding-bottom:3px;">Pruning Bounds</div>
                  <div id="ab-val">α = -∞<br>β = +∞</div>
                </div>
                <div id="adv-canvas" style="position: absolute; inset:0; margin-top:30px;"></div>
              </div>

              <div class="viz-container" id="viz-5">
                <div class="kb-panel">
                  <div class="kb-rule" id="kr-facts" style="border-left: 3px solid var(--success);"></div>
                  <div class="kb-rule" id="kr-p"><b>(Propositional Rule):</b> IF Risk=Critical ∧ Time_Short THEN ImmediateHighDeltaV</div>
                  <div class="kb-rule" id="kr-pr"><b>(Predicate Rule):</b> ∀a: Asteroid(a) ∧ Time_Window(a, short) → Choose(KineticImpact, a)</div>
                  <div class="kb-rule" id="kr-concl" style="border-left: 3px solid var(--pass); font-weight:bold;">CONCLUSION: ...</div>
                </div>
              </div>

              <div class="viz-container" id="viz-6" style="justify-content:center; align-items:center;">
                <div style="text-align:center; max-width: 400px; line-height:1.6;">
                  <h2 style="font-family:var(--font-title); font-size:2rem; margin-bottom:20px;">Agent Execution Output</h2>
                  <h3 id="final-strat-name" style="color:var(--accent); margin-bottom:20px;">Kinetic Impactor</h3>
                  <p id="final-explanation" style="font-size:0.95rem; color:#aaa;"></p>
                  <p id="final-logs" style="font-size:0.8rem; color:#66bb6a; margin-top:15px; background:rgba(102,187,106,0.1); border:1px solid #66bb6a; padding:10px; border-radius:8px;"></p>
                  <button class="btn-run" onclick="location.reload()" style="margin-top:20px; padding:10px 20px; font-size:0.9rem;">Reset Agent / New Scenario</button>
                </div>
              </div>

            </div>
          </div>
        </div>

        <div class="right-panel">
           <div class="details">
             <h3 id="panel-title">Agent Status</h3>
             <p id="panel-desc">Awaiting initialization... Select a target frame.</p>
             <h3 style="margin-top: 20px; font-size: 1.1rem;">Pipeline Log</h3>
             <div class="log-box" id="action-log"><div class="log-entry">System online. Evaluating problem types...</div></div>
           </div>
        </div>
      </div>
      <footer style="padding: 15px 40px; border-top: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.4); display: flex; justify-content: space-between; align-items: center; font-family: var(--font-mono); font-size: 0.72rem; color: #555; z-index: 10;">
        <div>AI Asteroid Defence — Final Mission Deployment</div>
        <div style="display: flex; gap: 25px;">
          <span>Unit 2: Search (A*)</span>
          <span>Unit 3: CSP (Constraints)</span>
          <span>Unit 4: Adversarial (Minimax)</span>
          <span>Unit 5: Logic (Rule Base)</span>
        </div>
      </footer>
    </div>
  </div>

  <script>
    const cur = document.getElementById('custom-cursor');
    document.addEventListener('mousemove', e => { cur.style.left = e.clientX+'px'; cur.style.top = e.clientY+'px'; });

    const scenarios = [
      { id: 's1', name: "Chelyabinsk", diameter: 20, mass: "1e7 kg", speed: "19.1 km/s", prob: "100%", timeDays: 14, risk: "Moderate" },
      { id: 's2', name: "2019 OK", diameter: 130, mass: "5e8 kg", speed: "24.0 km/s", prob: "95%", timeDays: 14, risk: "High" },
      { id: 's3', name: "Apophis", diameter: 340, mass: "4e10 kg", speed: "30.7 km/s", prob: "8.5%", timeDays: 730, risk: "Critical" },
    ];
    const strats = [
      { id: 'st1', name: 'Nuclear', type: 'Deflect', cost: 4.5, time: 2, isNuclear: true },
      { id: 'st2', name: 'Kinetic', type: 'Deflect', cost: 1.2, time: 7, isNuclear: false },
      { id: 'st3', name: 'Tractor', type: 'Mitigate', cost: 0.8, time: 365, isNuclear: false },
      { id: 'st4', name: 'Sail', type: 'Mitigate', cost: 0.5, time: 730, isNuclear: false }
    ];

    let sel = null; let pr = false;
    window.globalBudget = 2.0;

    const logBox = document.getElementById('action-log');
    function logAction(msg, isConcept=false) {
      const d = document.createElement('div'); d.className = 'log-entry'+(isConcept?' concept':'');
      d.innerHTML = `> ${msg}`; logBox.appendChild(d);
      setTimeout(() => logBox.scrollTop = logBox.scrollHeight, 50);
    }
    const delay = ms => new Promise(res => setTimeout(res, ms));

    const gridEl = document.getElementById('scenario-grid');
    scenarios.forEach(sc => {
      const c = document.createElement('div'); c.className = 'scenario-card';
      c.innerHTML = `<div style="font-family:var(--font-mono); color:var(--success); font-size:0.75rem; margin-bottom:10px;">Frame: Asteroid_Data</div><h3>${sc.name}</h3>
        <div class="s-row"><span>Diameter:</span><span style="color:#fff">${sc.diameter} m</span></div>
        <div class="s-row"><span>Mass:</span><span style="color:#fff">${sc.mass}</span></div>
        <div class="s-row"><span>Risk Level:</span><span style="color:${sc.risk==='Critical'?'var(--fail)':'#f0a020'}">${sc.risk}</span></div>`;
      c.addEventListener('click', () => {
        if(pr) return;
        document.querySelectorAll('.scenario-card').forEach(x => x.classList.remove('selected'));
        c.classList.add('selected'); sel = sc;
        document.getElementById('btn-run-ai').removeAttribute('disabled');
        logAction(`Loaded <span style="color:var(--success);">Frame: ${sc.name}</span>`);
        
        // Show Editor Panel
        document.getElementById('editor-panel').style.display='block';
        document.getElementById('edit-diam').value = sel.diameter;
        document.getElementById('edit-mass').value = sel.mass.replace(' kg','');
        document.getElementById('edit-time').value = sel.timeDays;
        document.getElementById('edit-risk').value = sel.risk;
      });
      gridEl.appendChild(c);
    });

    document.getElementById('play-btn').addEventListener('click', () => {
      document.getElementById('intro').style.display='none';
      document.getElementById('transition').style.display='flex';
      setTimeout(() => { document.getElementById('transition').style.display='none'; document.getElementById('dash').style.display='flex'; }, 1000);
    });
    document.getElementById('home-btn').addEventListener('click', e => { e.preventDefault(); location.href = '/'; });

    document.getElementById('btn-run-ai').addEventListener('click', async () => {
        if(pr) return; pr = true;
        
        // Save Editor State
        sel.diameter = document.getElementById('edit-diam').value;
        sel.mass = document.getElementById('edit-mass').value + ' kg';
        sel.timeDays = parseInt(document.getElementById('edit-time').value);
        sel.risk = document.getElementById('edit-risk').value;
        window.globalBudget = parseFloat(document.getElementById('edit-budget').value);
        logAction(`Applied Overrides: Time=${sel.timeDays}d, Risk=${sel.risk}, Budget=${window.globalBudget}B`);

        document.getElementById('step-0').classList.remove('active');
        document.getElementById('step-vp').classList.add('active');
        await runPipeline();
        pr = false;
        // make nodes clickable manually
        document.getElementById('search-mode-btns').style.display='flex';
    });

    document.querySelectorAll('.pipe-step').forEach(el => {
      el.addEventListener('click', () => {
         if(!sel || pr) return;
         let id = parseInt(el.id.split('-')[1]);
         if(id === 0) {
            document.getElementById('step-vp').classList.remove('active');
            document.getElementById('step-0').classList.add('active');
            document.querySelectorAll('.pipe-step').forEach(e => e.classList.remove('active'));
            el.classList.add('active');
         } else if(el.classList.contains('done')) {
            document.getElementById('step-0').classList.remove('active');
            document.getElementById('step-vp').classList.add('active');
            setStage(id, document.getElementById('st-head').textContent.substring(3), "", document.getElementById('active-concepts').innerHTML, 'viz-'+id);
         }
      });
    });

    function setStage(id, title, desc, tagsHtml, viz) {
      document.querySelectorAll('.pipe-step').forEach(e => e.classList.remove('active'));
      document.getElementById('ps-'+id).classList.add('active');
      document.getElementById('st-head').textContent = `${id}. ${title}`;
      document.getElementById('panel-title').textContent = title;
      if(desc) document.getElementById('panel-desc').textContent = desc;
      if(tagsHtml) document.getElementById('active-concepts').innerHTML = tagsHtml;
      document.querySelectorAll('.viz-container').forEach(e => e.classList.remove('active'));
      document.getElementById(viz).classList.add('active');
    }

    async function runPipeline() {
      // Step 1
      setStage(1, "Problem Formulation", "Mapping frames to State Space. Agent identifies initial and goal states.", `<span class="tag glow">State Space</span><span class="tag glow">Initial State</span><span class="tag glow">Goal State</span><span class="tag tsp">Travelling Salesman Problem (TSP Reference)</span>`, 'viz-1');
      document.getElementById('t-init-state').textContent = `Asteroid: ${sel.name}, Risk: ${sel.risk}, Chosen Strategy: None`;
      logAction("Formulating State Space parameters...", true);
      await delay(800); document.getElementById('f-init').classList.add('show');
      await delay(800); document.getElementById('f-goal').classList.add('show');
      await delay(800); document.getElementById('f-actions').classList.add('show');
      await delay(1000); document.getElementById('tsp-box').style.opacity=1;
      logAction("Note: In the same way TSP finds an optimal tour among cities, here the agent finds an optimal node amongst strategy states.");
      document.getElementById('ps-1').classList.add('done');
      await delay(1500);

      // Step 2
      setStage(2, "Problem Space Search", "Animating search through the strategy tree.", `<span class="tag glow">Trees/Graphs</span><span class="tag glow">General Search</span>`, 'viz-2');
      logAction("Initializing generic search visualization.");
      await window.runSearchMode('A*', true); // auto run A* to show
      document.getElementById('search-mode-btns').style.display='flex';
      document.getElementById('ps-2').classList.add('done');
      await delay(1500);

      // Step 3
      setStage(3, "Constraint Satisfaction Problem", "Strategies filtered by Domain Constraints.", `<span class="tag glow">Variables</span><span class="tag glow">Domains</span><span class="tag glow">Constraints</span>`, 'viz-3');
      const cg = document.getElementById('csp-list'); cg.innerHTML='';
      document.getElementById('csp-gate').classList.add('active');
      document.getElementById('csp-matrix').classList.remove('show');
      logAction(`Checking actions against dynamic CSP thresholds: Time ≤ ${sel.timeDays}d, Budget ≤ $${window.globalBudget}B.`);
      
      let finalStrats = [];
      for(let s of strats) {
        let isTimeOk = (s.time <= sel.timeDays);
        let isBudgOk = (s.cost <= window.globalBudget);
        if(sel.risk === 'Critical' && s.isNuclear) isBudgOk = true;

        let pass = isTimeOk && isBudgOk;
        if(pass) finalStrats.push(s);

        let c = document.createElement('div');
        c.className = `csp-card ${pass?'':'rejected'}`;
        c.innerHTML = `<span style="font-family:var(--font-mono); color:#fff; font-size:1rem;">${s.name}</span>
          <div><span class="c-badge ${isBudgOk?'pass':'fail'}">Budget:${s.cost}B</span>
          <span class="c-badge ${isTimeOk?'pass':'fail'}">Time:${s.time}d</span></div>`;
        cg.appendChild(c);
        await delay(600); c.classList.add('show');
        logAction(`CSP Filter [${s.name}]: ${pass?'PASS':'FAIL'}`);
      }

      // CSP Explanation Summary
      let matrixText = "";
      if(finalStrats.length === 0) matrixText = "0 Solutions: EARTH AT RISK. Requirements impossible to meet.";
      else if(finalStrats.length === 1) matrixText = "1 Solution: Unique deployment path found. Optimization trivial.";
      else matrixText = `${finalStrats.length} Solutions: MULTIPLE candidate paths. Transitioning to Search/Logic for optimization.`;
      
      document.getElementById('csp-summary').textContent = matrixText;
      document.getElementById('csp-matrix').classList.add('show');
      
      document.getElementById('ps-3').classList.add('done');
      await delay(1500);

      // Step 4
      setStage(4, "Adversarial Search (Games)", "Planner vs Nature. Modeling worst-case probabilities.", `<span class="tag glow">Minimax</span><span class="tag glow">Alpha-Beta Pruning</span><span class="tag glow">Game Tree</span>`, 'viz-4');
      const ac = document.getElementById('adv-canvas'); ac.innerHTML='';
      function makeN(x,y,t,id) {let n=document.createElement('div'); n.className='node'; n.id=id; n.style.left=x+'%'; n.style.top=y+'%'; n.innerHTML=t; ac.appendChild(n); return n;}
      function makeE(x1,y1,x2,y2,id) {let e=document.createElement('div'); e.className='edge'; e.id=id; ac.appendChild(e); setTimeout(()=>{let p=ac.getBoundingClientRect(); let cx1=x1/100*p.width,cy1=y1/100*p.height,cx2=x2/100*p.width,cy2=y2/100*p.height; let dx=cx2-cx1,dy=cy2-cy1,dist=Math.sqrt(dx*dx+dy*dy),ang=Math.atan2(dy,dx)*180/Math.PI; e.style.width=dist+'px'; e.style.left=cx1+'px'; e.style.top=cy1+'px'; e.style.transform=`rotate(${ang}deg)`; },10); return e;}
      function showEval(node, text) { let d=document.createElement('div'); d.className='eval-text'; d.textContent=text; node.appendChild(d); setTimeout(()=>d.classList.add('show'),10);}

      // Dynamic Minimax values based on Risk
      let p1 = 40, p2 = 0, p3 = 20, p4 = -10;
      if (sel.risk === 'Critical') { p1 = 90; p2 = -20; p3 = 40; p4 = -99; }
      if (sel.risk === 'High') { p1 = 60; p2 = -10; p3 = 30; p4 = -50; }

      let mx = makeN(50,5,'MAX Planner', 'm-0'); await delay(500); mx.classList.add('expand');
      let mn1 = makeN(30,40,'MIN Nature','m-1'); let mn2 = makeN(70,40,'MIN Nature','m-2');
      makeE(50,5,30,40,'e-1').classList.add('show'); makeE(50,5,70,40,'e-2').classList.add('show');
      await delay(500); mn1.classList.add('expand'); mn2.classList.add('expand');
      
      let l1=makeN(20,80,'+'+p1,'l-1'); let l2=makeN(40,80,p2,'l-2'); let l3=makeN(60,80,'+'+p3,'l-3'); let l4=makeN(80,80,p4,'l-4');
      makeE(30,40,20,80,'').classList.add('show'); makeE(30,40,40,80,'').classList.add('show');
      makeE(70,40,60,80,'').classList.add('show'); makeE(70,40,80,80,'').classList.add('show');

      await delay(800); l1.classList.add('expand'); showEval(l1,`Payoff=${p1}`);
      await delay(600); l2.classList.add('expand'); showEval(l2,`Payoff=${p2}`);
      await delay(600); mn1.textContent=p2; showEval(mn1,`min(${p1},${p2})`);
      document.getElementById('ab-val').innerHTML = `α = ${p2} (MAX updated)<br>β = +∞`;
      logAction(`ALPHA set to ${p2} based on worst-case payoff.`);

      await delay(800); l3.classList.add('expand'); showEval(l3,`Payoff=${p3}`);
      if (p3 > p2) {
        await delay(600); showEval(mn2,`${p3} > α, PRUNING!`);
        let prn = document.createElement('div'); prn.className='prune-line'; prn.style.left='73%'; prn.style.top='62%'; ac.appendChild(prn);
        l4.classList.add('expand'); l4.classList.add('fail');
        document.getElementById('ab-val').innerHTML = "<span style='color:var(--fail)'>Subtree pruned by α,β</span>";
        logAction("Alpha-Beta pruning: branch discarded as suboptimal for MAX.", true);
      } else {
        await delay(600); l4.classList.add('expand'); showEval(l4,`Payoff=${p4}`);
        mn2.textContent = Math.min(p3, p4); logAction("Branch explored completely (no pruning trigger).");
      }
      
      await delay(1200); mx.textContent=(p3>p2?p3:p2); showEval(mx,`max(${p2},${p3})`); mn2.classList.add('goal');
      logAction(`Minimax algorithm complete. Optimal payoff expected: ${p3 > p2 ? p3 : p2}`);
      document.getElementById('ps-4').classList.add('done');
      await delay(1500);

      // Step 5
      setStage(5, "Logical Inference", "Mapping frames to logic symbols and applying rule inference.", `<span class="tag glow">Propositional Logic</span><span class="tag glow">Predicate Logic</span><span class="tag glow">Rule-based System</span>`, 'viz-5');
      document.getElementById('kr-facts').innerHTML = `<b>Fact Extraction:</b> (Risk==${sel.risk}) ∧ (TimeDays==${sel.timeDays})`;
      document.getElementById('kr-facts').style.opacity=1;
      await delay(1000); document.getElementById('kr-p').style.opacity=1;
      await delay(1000); document.getElementById('kr-pr').style.opacity=1;

      let rFired = '';
      if(sel.risk === 'Critical') {
        document.getElementById('kr-p').classList.add('fire');
        logAction("Propositional Rule 1 Fired!"); rFired = "Nuclear";
      } else {
        document.getElementById('kr-pr').classList.add('fire');
        logAction("Predicate Rule 2 Fired!"); rFired = "Kinetic Impactor";
      }
      await delay(1000); document.getElementById('kr-concl').textContent = `CONCLUSION: Agent action output := Deploy ${rFired}`;
      document.getElementById('kr-concl').style.opacity=1;
      document.getElementById('ps-5').classList.add('done');
      await delay(1500);

      // Step 6
      setStage(6, "Mission Deployed", "Utility-Based Rational agent locks final decision.", `<span class="tag glow">Rational Agent</span><span class="tag glow">Utility-Based Agent</span>`, 'viz-6');
      document.getElementById('final-strat-name').textContent = rFired;
      
      let explain = "";
      if (finalStrats.length === 1) {
        explain = `The AI filtered the domain through the CSP gate and found that ONLY the ${rFired} satisfied the mandatory constraints of Time and Budget. No further search optimization was strictly required, but the agent verified the result through Logical Inference.`;
      } else if (finalStrats.length > 1) {
        explain = `The AI found multiple viable strategies (${finalStrats.length}) passing the CSP gate. It then used Minimax and A* to optimize for the highest safety payoff. Based on the Knowledge Base rules and expected utility, ${rFired} was selected as the optimal rational choice.`;
      } else {
        explain = `CRITICAL WARNING: The CSP gate rejected ALL known strategies based on your input constraints. An Intelligent Agent in a "No-Solution" state recommended the ${rFired} as a last-resort heuristic to minimize damage, despite the constraint failure.`;
      }

      document.getElementById('final-explanation').textContent = explain;
      document.getElementById('final-logs').innerHTML = `CSP Result Set: ${finalStrats.length} | Logic Rules Fired: 1 | Strategy Type: ${rFired==='Nuclear'?'Aggressive':'Precision'}`;
      
      logAction("All stages complete. Final decision rendered accurately.");
      document.getElementById('ps-6').classList.add('done');
    }

    window.runSearchMode = async function(mode, isAuto=false) {
      if(!isAuto && pr) return;
      document.querySelectorAll('.btn-sm').forEach(b => {
        b.classList.remove('active');
        if(b.textContent === mode) b.classList.add('active');
      });
      document.getElementById('active-concepts').innerHTML = `<span class="tag glow">Search Space</span><span class="tag glow">${mode==='A*'?'Informed Search':'Uninformed Search'}</span><span class="tag glow">${mode} Mode active</span>`;

      const tc = document.getElementById('tree-canvas'); tc.innerHTML='';
      const fl = document.getElementById('frontier-list'); fl.innerHTML='';
      
      function makeN(x,y,t,id,fstr="") {let n=document.createElement('div'); n.className='node'; n.id=id; n.style.left=x+'%'; n.style.top=y+'%'; n.innerHTML=`${t}<div class="f-val">${fstr}</div>`; tc.appendChild(n); return n;}
      function makeE(x1,y1,x2,y2) {let e=document.createElement('div'); e.className='edge'; tc.appendChild(e); setTimeout(()=>{let p=tc.getBoundingClientRect(); let cx1=x1/100*p.width,cy1=y1/100*p.height,cx2=x2/100*p.width,cy2=y2/100*p.height; let dx=cx2-cx1,dy=cy2-cy1,dist=Math.sqrt(dx*dx+dy*dy),ang=Math.atan2(dy,dx)*180/Math.PI; e.style.width=dist+'px'; e.style.left=cx1+'px'; e.style.top=cy1+'px'; e.style.transform=`rotate(${ang}deg)`; },10); return e;}

      let nodes = {
        S0: {x:50,y:10, text:'S0 (Start)', cid:'ns0', f:'f=0'},
        D1: {x:30,y:40, text:'Deflect', cid:'ns1', f:'g=1'},
        M2: {x:70,y:40, text:'Mitigate', cid:'ns2', f:'g=5'},
        N3: {x:20,y:75, text:'Nuclear', cid:'ns3', f:'f(x)=2'},
        K4: {x:40,y:75, text:'Kinetic', cid:'ns4', f:'f(x)=3'},
        T5: {x:60,y:75, text:'Tractor', cid:'ns5', f:'f(x)=9'},
        S6: {x:80,y:75, text:'Sail', cid:'ns6', f:'f(x)=11'}
      };
      
      Object.keys(nodes).forEach(k => { nodes[k].el = makeN(nodes[k].x, nodes[k].y, nodes[k].text, nodes[k].cid, nodes[k].f); });
      let e1 = makeE(50,10,30,40); let e2 = makeE(50,10,70,40);
      let e3 = makeE(30,40,20,75); let e4 = makeE(30,40,40,75);
      let e5 = makeE(70,40,60,75); let e6 = makeE(70,40,80,75);
      
      if(mode === 'A*') document.querySelectorAll('.node').forEach(n => n.classList.add('show-f'));
      
      let target = (sel.risk === 'Critical') ? 'N3' : 'K4';
      let order = [];
      if(mode === 'BFS') order = ['S0','D1','M2','N3','K4','T5','S6'];
      else if(mode === 'DFS') order = ['S0','D1','N3','K4','M2','T5','S6'];
      else if(mode === 'UCS') order = ['S0','D1','N3','K4','M2','T5','S6']; 
      else if(mode === 'A*') order = ['S0','D1', target]; 
      
      if(!isAuto) logAction(`User requested mode: ${mode}`);
      logAction(`[${mode}] Expanding Frontier...`);
      for(let k of order) {
        let fhtml = ''; for(let j of order) { if(order.indexOf(j)>=order.indexOf(k)) fhtml+=`<div style='opacity:0.6'>[${j}] wait</div>`; }
        fl.innerHTML = fhtml;
        await delay(isAuto ? 600 : 400); 
        nodes[k].el.classList.add('expand');
        if(k==='D1' || k==='M2') { e1.classList.add('show'); e2.classList.add('show'); }
        if(k==='N3' || k==='K4') { e3.classList.add('show'); e4.classList.add('show'); }
        if(k==='T5' || k==='S6') { e5.classList.add('show'); e6.classList.add('show'); }
        if(mode === 'A*' && k===target) { 
          nodes[k].el.classList.add('goal'); 
          if(target === 'N3') e3.classList.add('active');
          if(target === 'K4') e4.classList.add('active');
          break;
        }
      }
      fl.innerHTML = "<div style='color:var(--pass)'>[Path Resolved]</div>";
    };

  </script>
</body>
</html>
"""

with open("/home/pranjay/workspace/Projects/no copy/public/working-soon.html", "w") as f:
    f.write(html_content)

print("HTML file successfully rewritten!")
