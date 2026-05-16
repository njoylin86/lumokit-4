"""
premium_features.py
LumoKit premium-komponenter för Älvsjö Tandvård.

Innehåller:
  - build_fear_matcher()   — interaktivt trygghetsmatchningsverktyg (4 ja/nej-frågor → 3 personas)

Designprinciper:
  - DS-tokens (var(--blush-300), --ink-700, etc.) ärvs från klientens globala styles.css
  - Vanilla JS (ingen React) — collapse() i build_bundle plattar whitespace
  - JS-kommentarer alltid /* */ aldrig // (collapse() tar bort radbrytningar)
  - Visuellt språk efterliknar befintlig triage-widget (premium-badge, formulärkort, two-column)

Notera: alla copy-strings är PLACEHOLDERS — verifieras med kliniken före lansering.
Disclaimer "ev. implementationskostnader" visas i UI nära Premium-badgen.
"""

from __future__ import annotations


def _collapse(html: str) -> str:
    return " ".join(html.split())


# ---------------------------------------------------------------------------
# PREMIUM_TOOLTIPS — single source of truth för "Varför Premium?"-bubblorna.
# Innehållet visas både på badge-tooltipen på sektionen och i premium-tour-popup.
# Vill du ändra texten i en bubbla — ändra här, push:a de drabbade komponenterna.
# ---------------------------------------------------------------------------
PREMIUM_TOOLTIPS = {
    "symptom-triage": {
        "bullets": [
            "Patienten får hjälp att avgöra hur akut situationen är",
            "Färre samtal och frågemail till receptionen",
            "Rätt bokningar — ingen som ringer i onödan",
            "Sparar tid för både patient och personal",
        ],
        "note": "Innehållet anpassas helt efter er kliniks önskemål.",
    },
    "prismatris": {
        "bullets": [
            "Patienten ser snabbt vad behandlingen kostar per månad vid räntefri delbetalning",
            "Färre frågor till receptionen om priser",
            "Fler väljer att boka när de ser att det är överkomligt",
            "Sparar tid för både patient och personal",
        ],
        "note": "Belopp och intervall anpassas efter klinikens prisbild.",
    },
    "trygghetsmatchning": {
        "bullets": [
            "Patienter med tandvårdsrädsla får ett tryggt första steg",
            "Personifierad rekommendation — utan att de behöver ringa",
            "Färre avhopp — fler vågar boka konsultation",
            "Visar att kliniken förstår just deras situation",
        ],
        "note": "Frågor och paket anpassas helt efter er klinik.",
    },
    "behandlingsstepper": {
        "bullets": [
            "Patienten ser hela behandlingsförloppet i en överblick",
            "Tydlighet minskar oro och frågor inför första besöket",
            "Skapar förtroende för komplexa behandlingar som implantat",
            "Färre &quot;vad händer härnäst?&quot;-samtal till receptionen",
        ],
        "note": "Steg och innehåll anpassas per behandling.",
    },
    "prisoversikt": {
        "bullets": [
            "Patienter ser exakta priser innan de bokar — bygger förtroende",
            "Färre samtal till receptionen om &quot;vad kostar...?&quot;",
            "Sätter er tandvård i kontext mot räntefri delbetalning &amp; statligt stöd",
            "Sticker ut mot konkurrenter som döljer priser",
        ],
        "note": "Behandlingar och prisspann anpassas helt efter kliniken.",
    },
}


def lumo_tooltip(key: str) -> str:
    """Returnerar HTML för badge-tooltipen som ligger på själva premium-sektionen.
    Klasserna är .lumo-tooltip / .lumo-tt-* (definierade i LAYOUT_CSS)."""
    tt = PREMIUM_TOOLTIPS[key]
    bullets = "".join(f"<li>{b}</li>" for b in tt["bullets"])
    return (
        '<div class="lumo-tooltip">'
        '<div class="lumo-tt-title">Varför Premium?</div>'
        f'<ul class="lumo-tt-list">{bullets}</ul>'
        f'<div class="lumo-tt-note">{tt["note"]}</div>'
        '</div>'
    )


def lpt_card_tooltip(key: str) -> str:
    """Returnerar HTML för kort-tooltipen i premium-tour-popupen.
    Klasserna är .lpt-card-tt / .lpt-card-tt-* (i PREMIUM_TOUR_CSS)."""
    tt = PREMIUM_TOOLTIPS[key]
    bullets = "".join(f"<li>{b}</li>" for b in tt["bullets"])
    return (
        '<div class="lpt-card-tt">'
        '<div class="lpt-card-tt-title">Varför Premium?</div>'
        f'<ul>{bullets}</ul>'
        f'<div class="lpt-card-tt-note">{tt["note"]}</div>'
        '</div>'
    )


# ---------------------------------------------------------------------------
# Fear Matcher — trygghetsmatchning för tandvårdsrädsla
# ---------------------------------------------------------------------------

FEAR_MATCHER_CSS = """
.fm-section { background: var(--bg-soft); padding: var(--space-9) 0; border-top:1px solid var(--border); border-bottom:1px solid var(--border); scroll-margin-top: -78px; }
.fm-header { display:grid; grid-template-columns:1fr auto; align-items:end; gap:32px; margin-bottom:48px; padding-bottom:28px; border-bottom:1px solid var(--border); }
.fm-eyebrow-row { display:flex; align-items:center; flex-wrap:wrap; gap:6px 0; margin-bottom:12px; }
.fm-header-meta { max-width:36ch; text-align:right; margin:0; color:var(--fg-muted); }
.fm-grid { display:grid; grid-template-columns:1fr 1.15fr; gap:80px; align-items:start; }
.fm-left { position:sticky; top:120px; }
.fm-left-lead { color:var(--ink-500); font-size:var(--fs-lead); line-height:1.55; margin-bottom:var(--space-6); max-width:40ch; }
.fm-trust { display:flex; flex-direction:column; gap:var(--space-3); margin-bottom:var(--space-6); }
.fm-trust-item { display:flex; align-items:flex-start; gap:var(--space-3); }
.fm-trust-dot { width:6px; height:6px; border-radius:50%; background:var(--blush-400); flex-shrink:0; margin-top:6px; }
.fm-trust-title { font-size:var(--fs-small); font-weight:500; color:var(--fg-strong); margin-bottom:2px; }
.fm-trust-desc { font-size:var(--fs-tiny); color:var(--fg-subtle); }
.fm-card { background:var(--white); border:1px solid var(--border); box-shadow:var(--shadow-md); padding:clamp(28px, 4vw, 44px); }
.fm-progress { margin-bottom:var(--space-6); }
.fm-progress-meta { display:flex; justify-content:space-between; margin-bottom:var(--space-2); }
.fm-progress-track { height:2px; background:var(--border); }
.fm-progress-fill { height:100%; background:var(--blush-400); transition:width .4s var(--ease-standard); }
.fm-q-title { font-family:var(--font-serif); font-weight:400; font-size:var(--fs-h3); letter-spacing:var(--tracking-tight); color:var(--fg-strong); margin-bottom:var(--space-3); line-height:1.2; }
.fm-q-sub { color:var(--fg-muted); font-size:var(--fs-small); margin-bottom:var(--space-5); }
.fm-yn { display:grid; grid-template-columns:1fr 1fr; gap:var(--space-3); margin-bottom:var(--space-5); }
.fm-yn-btn { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; padding:var(--space-5) var(--space-4); background:var(--white); border:1px solid var(--border); cursor:pointer; font-family:var(--font-sans); transition:all var(--dur-fast) var(--ease-standard); min-height:96px; }
.fm-yn-btn:hover { border-color:var(--blush-400); background:var(--blush-50); }
.fm-yn-btn.is-sel { border-color:var(--ink-700); background:var(--ink-700); color:var(--white); }
.fm-yn-icon { width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:1.5px solid var(--border-strong); color:var(--fg-muted); transition:all var(--dur-fast) var(--ease-standard); }
.fm-yn-btn.is-sel .fm-yn-icon { border-color:var(--white); background:var(--white); color:var(--ink-700); }
.fm-yn-label { font-size:15px; font-weight:500; letter-spacing:.02em; }
.fm-yn-sub { font-size:11px; color:var(--fg-subtle); letter-spacing:.04em; }
.fm-yn-btn.is-sel .fm-yn-sub { color:rgba(255,255,255,.65); }
.fm-next-btn { width:100%; justify-content:center; }
.fm-next-btn.is-disabled { background:var(--blush-100); color:var(--blush-300); cursor:not-allowed; border-color:transparent; }
.fm-card-footer { display:flex; justify-content:space-between; align-items:center; padding-top:var(--space-4); border-top:1px solid var(--border); margin-top:var(--space-5); }
.fm-link-btn { background:none; border:none; padding:0; font-family:var(--font-sans); font-size:var(--fs-tiny); color:var(--fg-subtle); cursor:pointer; letter-spacing:.04em; transition:color var(--dur-fast) var(--ease-standard); }
.fm-link-btn:hover:not(:disabled) { color:var(--fg-muted); }
.fm-link-btn:disabled { color:var(--ink-100); cursor:not-allowed; }
.fm-result-eyebrow-row { display:flex; align-items:center; gap:12px; margin-bottom:var(--space-3); }
.fm-result-eyebrow { font-size:var(--fs-eyebrow); text-transform:uppercase; letter-spacing:var(--tracking-eyebrow); font-weight:500; color:var(--blush-600); }
.fm-result-divider { flex:1; height:1px; background:var(--border); }
.fm-result-title { font-family:var(--font-serif); font-weight:400; font-size:32px; line-height:1.15; letter-spacing:-.02em; color:var(--fg-strong); margin-bottom:var(--space-3); }
.fm-result-lead { color:var(--ink-500); font-size:var(--fs-lead); line-height:1.55; margin-bottom:var(--space-5); }
.fm-package { background:var(--blush-50); border:1px solid var(--blush-200); padding:var(--space-5); margin-bottom:var(--space-5); }
.fm-package-label { font-size:9px; font-weight:600; letter-spacing:.22em; text-transform:uppercase; color:var(--blush-600); margin-bottom:var(--space-3); }
.fm-package-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:var(--space-3); }
.fm-package-list li { display:flex; gap:10px; align-items:flex-start; font-size:14px; line-height:1.5; color:var(--ink-500); }
.fm-package-check { width:18px; height:18px; border-radius:50%; background:var(--blush-300); flex-shrink:0; margin-top:2px; display:flex; align-items:center; justify-content:center; }
.fm-actions { display:flex; flex-direction:column; gap:var(--space-2); }
.fm-actions .btn { width:100%; justify-content:center; }
.fm-restart-row { margin-top:var(--space-5); padding-top:var(--space-5); border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; }
.fm-analyzing { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:var(--space-9) 0; gap:var(--space-5); }
.fm-dots { display:flex; gap:7px; }
.fm-dots span { width:6px; height:6px; border-radius:50%; background:var(--blush-400); animation:fm-dot-bounce 1.2s ease-in-out infinite; }
.fm-dots span:nth-child(2) { animation-delay:.16s; }
.fm-dots span:nth-child(3) { animation-delay:.32s; }
@keyframes fm-dot-bounce { 0%,80%,100% { transform:translateY(0); opacity:.25; } 40% { transform:translateY(-5px); opacity:1; } }
@keyframes fm-q-enter { from { opacity:0; transform:translateX(18px); } to { opacity:1; transform:translateX(0); } }
@keyframes fm-result-enter { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
.fm-q-slide { animation:fm-q-enter .28s var(--ease-standard) both; }
.fm-result-reveal { animation:fm-result-enter .36s var(--ease-standard) both; }
.fm-premium-note { font-size:10px; color:var(--fg-subtle); font-style:italic; letter-spacing:.02em; line-height:1.4; flex-basis:100%; margin:6px 0 0 0; }
@media (max-width:900px) {
  .fm-header { grid-template-columns:1fr; align-items:start; gap:16px; margin-bottom:0; padding-bottom:0; border-bottom:0; }
  .fm-header-meta { display:none; }
  .fm-grid { margin-top:24px; }
  .fm-grid { grid-template-columns:1fr; gap:40px; }
  .fm-left { position:static; }
  .fm-yn { grid-template-columns:1fr; }
}
"""


FEAR_MATCHER_JS = r"""
(function(){
  /* Fear Matcher — vanilla JS state-machine. Inga // kommentarer. */
  var root = document.querySelector('[data-fear-matcher]');
  if (!root) return;
  if (root.dataset.fmReady === '1') return;
  root.dataset.fmReady = '1';

  var cfgEl = root.querySelector('script[type="application/json"][data-fm-config]');
  if (!cfgEl) return;
  var CFG;
  try { CFG = JSON.parse(cfgEl.textContent); } catch (e) { return; }
  var QUESTIONS = CFG.questions || [];
  var PERSONAS  = CFG.personas  || {};
  var ANALYSING_LABEL = CFG.analysing_label || 'Matchar dig med rätt paket';
  var CAVEAT_TEXT = CFG.caveat || '';
  var MATCH_RULES = CFG.match_rules || 'aterstart>=3|anxiolytika>=2|stegforsteg>=2|anxiolytika>=1';
  var DEFAULT_PERSONA = CFG.default_persona || 'stegforsteg';

  var state = { step: 0, answers: {}, selected: null, analysing: false, result: null };
  var section = root.closest('.fm-section') || root;

  function getHeaderOffset() {
    var candidates = ['.site-header', 'header.site-header', '#site-header', '.lumo-header', 'header[role="banner"]', 'body > header'];
    for (var i = 0; i < candidates.length; i++) {
      var el = document.querySelector(candidates[i]);
      if (!el) continue;
      var cs = window.getComputedStyle(el);
      if (cs.position === 'fixed' || cs.position === 'sticky') {
        return el.getBoundingClientRect().height;
      }
    }
    return 0;
  }

  function centerWidget() {
    var isMobile = window.matchMedia('(max-width: 900px)').matches;
    var target = (state.result || isMobile) ? root : section;
    var rect = target.getBoundingClientRect();
    var vh = window.innerHeight || document.documentElement.clientHeight;
    var pageY = window.pageYOffset || document.documentElement.scrollTop || 0;
    var headerH = getHeaderOffset();
    var gap = 16;
    var snapAdjust = 50;
    var top;
    if (isMobile) {
      top = pageY + rect.top - headerH - gap + snapAdjust;
    } else {
      var avail = vh - headerH;
      top = pageY + rect.top - headerH - Math.max(gap, (avail - rect.height) / 2) + snapAdjust;
    }
    top = Math.max(0, top);
    try {
      window.scrollTo({ top: top, behavior: 'smooth' });
    } catch (e) {
      window.scrollTo(0, top);
    }
  }

  root.addEventListener('click', function(){
    /* defer one frame so re-rendered DOM is measured */
    requestAnimationFrame(function(){ centerWidget(); });
  });

  function matchPersona(answers) {
    var scores = {};
    Object.keys(PERSONAS).forEach(function(k){ scores[k] = 0; });
    QUESTIONS.forEach(function(q){
      if (answers[q.id] !== 'yes') return;
      Object.keys(q.weights || {}).forEach(function(k){
        scores[k] = (scores[k] || 0) + q.weights[k];
      });
    });
    var rules = MATCH_RULES.split('|');
    for (var i = 0; i < rules.length; i++) {
      var m = rules[i].match(/^(\w+)\s*>=\s*(\d+)$/);
      if (!m) continue;
      if ((scores[m[1]] || 0) >= parseInt(m[2], 10)) return m[1];
    }
    return DEFAULT_PERSONA || Object.keys(PERSONAS)[0];
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function render() {
    var totalSteps = QUESTIONS.length;

    if (state.analysing) {
      root.innerHTML = '<div class="fm-analyzing">'
        + '<div class="fm-dots"><span></span><span></span><span></span></div>'
        + '<p class="tiny" style="letter-spacing:0.1em;">' + esc(ANALYSING_LABEL) + '</p>'
        + '</div>';
      return;
    }

    if (state.result) {
      var p = PERSONAS[state.result];
      if (!p) { state.result = null; state.step = 0; render(); return; }
      var listItems = (p.list || []).map(function(t){
        return '<li><div class="fm-package-check">'
          + '<svg width="9" height="7" viewBox="0 0 9 7" fill="none">'
          + '<path d="M1 3.5L3 5.5L8 1" stroke="white" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
          + '</svg></div>' + esc(t) + '</li>';
      }).join('');

      var html = '<div class="fm-result-reveal">'
        + '<div class="fm-result-eyebrow-row">'
        + '<span class="fm-result-eyebrow">' + esc(p.eyebrow) + '</span>'
        + '<div class="fm-result-divider"></div>'
        + '</div>'
        + '<h3 class="fm-result-title">' + esc(p.title) + '</h3>'
        + '<p class="fm-result-lead">' + esc(p.lead) + '</p>'
        + '<div class="fm-package">'
        + '<div class="fm-package-label">' + esc(p.list_label) + '</div>'
        + '<ul class="fm-package-list">' + listItems + '</ul>'
        + '</div>'
        + '<div class="fm-actions">'
        + '<a href="' + esc(p.cta_primary_link) + '" class="btn btn-sm btn-primary">' + esc(p.cta_primary_text) + '</a>'
        + '<a href="' + esc(p.cta_secondary_link) + '" class="btn btn-sm btn-ghost">' + esc(p.cta_secondary_text) + '</a>'
        + '</div>'
        + '<div class="fm-restart-row">'
        + '<p class="tiny" style="color:var(--fg-subtle);max-width:26ch;">' + esc(CAVEAT_TEXT) + '</p>'
        + '<button class="fm-link-btn" data-fm-restart>← Gör om matchningen</button>'
        + '</div>'
        + '</div>';
      root.innerHTML = html;
      bindResult();
      return;
    }

    var q = QUESTIONS[state.step];
    var pct = Math.round((state.step / totalSteps) * 100);
    var isLast = state.step === totalSteps - 1;
    var canNext = state.selected !== null;

    var yn = ['yes', 'no'].map(function(v){
      var label = v === 'yes' ? 'Ja' : 'Nej';
      var sub = v === 'yes' ? 'stämmer in på mig' : 'stämmer inte';
      var icon = v === 'yes'
        ? '<svg width="14" height="11" viewBox="0 0 14 11" fill="none"><path d="M1.5 5.5L5 9L12.5 1.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        : '<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 2L12 12M12 2L2 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
      var sel = state.selected === v ? ' is-sel' : '';
      return '<button class="fm-yn-btn' + sel + '" data-fm-answer="' + v + '">'
        + '<div class="fm-yn-icon">' + icon + '</div>'
        + '<div class="fm-yn-label">' + label + '</div>'
        + '<div class="fm-yn-sub">' + sub + '</div>'
        + '</button>';
    }).join('');

    root.innerHTML = '<div class="fm-progress">'
      + '<div class="fm-progress-meta">'
      + '<span class="tiny">Fråga ' + (state.step + 1) + ' av ' + totalSteps + '</span>'
      + '<span class="tiny">' + pct + '%</span>'
      + '</div>'
      + '<div class="fm-progress-track">'
      + '<div class="fm-progress-fill" style="width:' + pct + '%;"></div>'
      + '</div>'
      + '</div>'
      + '<div class="fm-q-slide" data-fm-step="' + state.step + '">'
      + '<h3 class="fm-q-title">' + esc(q.text) + '</h3>'
      + '<p class="fm-q-sub">' + esc(q.sub) + '</p>'
      + '<div class="fm-yn">' + yn + '</div>'
      + '<button class="btn btn-sm fm-next-btn ' + (canNext ? 'btn-primary' : 'is-disabled') + '" data-fm-next>'
      + (isLast ? 'Se min matchning' : 'Nästa fråga')
      + '</button>'
      + '<div class="fm-card-footer">'
      + '<button class="fm-link-btn" data-fm-back ' + (state.step === 0 ? 'disabled' : '') + '>← Föregående fråga</button>'
      + '<button class="fm-link-btn" data-fm-restart ' + (state.step === 0 ? 'disabled' : '') + '>Börja om</button>'
      + '</div>'
      + '</div>';
    bindQuestion();
  }

  function bindQuestion() {
    root.querySelectorAll('[data-fm-answer]').forEach(function(btn){
      btn.addEventListener('click', function(){
        state.selected = btn.getAttribute('data-fm-answer');
        render();
      });
    });
    var nextBtn = root.querySelector('[data-fm-next]');
    if (nextBtn) nextBtn.addEventListener('click', function(){
      if (state.selected == null) return;
      var q = QUESTIONS[state.step];
      state.answers[q.id] = state.selected;
      if (state.step === QUESTIONS.length - 1) {
        state.analysing = true;
        render();
        setTimeout(function(){
          state.analysing = false;
          state.result = matchPersona(state.answers);
          render();
        }, 1100);
      } else {
        state.step++;
        state.selected = null;
        render();
      }
    });
    var backBtn = root.querySelector('[data-fm-back]');
    if (backBtn) backBtn.addEventListener('click', function(){
      if (state.step === 0) return;
      state.step--;
      var prevQ = QUESTIONS[state.step];
      state.selected = state.answers[prevQ.id] || null;
      render();
    });
    var restartBtn = root.querySelector('[data-fm-restart]');
    if (restartBtn) restartBtn.addEventListener('click', resetState);
  }

  function bindResult() {
    var restartBtn = root.querySelector('[data-fm-restart]');
    if (restartBtn) restartBtn.addEventListener('click', resetState);
  }

  function resetState() {
    state = { step: 0, answers: {}, selected: null, analysing: false, result: null };
    render();
  }

  render();
})();
"""


def build_fear_matcher() -> dict:
    """Trygghetsmatchning för tandvårdsrädsla — 4 ja/nej-frågor matchar mot 3 personas."""
    html = (
        '<section id="trygghetsmatchning" class="fm-section">'
        '<style>' + FEAR_MATCHER_CSS + '</style>'
        '<div class="container-wide">'
        '<div class="fm-header">'
        '<div>'
        '<div class="fm-eyebrow-row">'
        '<span class="eyebrow">{{eyebrow}}</span>'
        '<span class="lumo-premium-badge" onclick="lumoToggle(this)">'
        '<span class="lumo-premium-dot"></span>'
        '<span class="lumo-mode-lbl">Premium</span>'
        + lumo_tooltip("trygghetsmatchning") +
        '</span>'
        '<span class="fm-premium-note">{{disclaimer_note}}</span>'
        '</div>'
        '<h2 style="max-width:22ch;">{{heading}}</h2>'
        '</div>'
        '<p class="fm-header-meta">{{subtext}}</p>'
        '</div>'
        '<div class="fm-grid">'
        '<div class="fm-left">'
        '<p class="fm-left-lead">{{lead}}</p>'
        '<div class="fm-trust">'
        '<div class="fm-trust-item"><div class="fm-trust-dot"></div><div>'
        '<div class="fm-trust-title">{{trust_1_title}}</div>'
        '<div class="fm-trust-desc">{{trust_1_desc}}</div>'
        '</div></div>'
        '<div class="fm-trust-item"><div class="fm-trust-dot"></div><div>'
        '<div class="fm-trust-title">{{trust_2_title}}</div>'
        '<div class="fm-trust-desc">{{trust_2_desc}}</div>'
        '</div></div>'
        '<div class="fm-trust-item"><div class="fm-trust-dot"></div><div>'
        '<div class="fm-trust-title">{{trust_3_title}}</div>'
        '<div class="fm-trust-desc">{{trust_3_desc}}</div>'
        '</div></div>'
        '</div>'
        '</div>'
        '<div class="fm-card" data-fear-matcher>'
        '<script type="application/json" data-fm-config>'
        '{"analysing_label":"{{analysing_label}}",'
        '"caveat":"{{matching_caveat}}",'
        '"default_persona":"stegforsteg",'
        '"match_rules":"aterstart>=3|anxiolytika>=2|stegforsteg>=2|anxiolytika>=1",'
        '"questions":['
        '{"id":"needles","text":"{{q1_text}}","sub":"{{q1_sub}}","weights":{"anxiolytika":2}},'
        '{"id":"drill","text":"{{q2_text}}","sub":"{{q2_sub}}","weights":{"anxiolytika":1}},'
        '{"id":"control","text":"{{q3_text}}","sub":"{{q3_sub}}","weights":{"stegforsteg":2}},'
        '{"id":"longtime","text":"{{q4_text}}","sub":"{{q4_sub}}","weights":{"aterstart":3}}'
        '],'
        '"personas":{'
        '"anxiolytika":{"eyebrow":"{{p1_eyebrow}}","title":"{{p1_title}}","lead":"{{p1_lead}}",'
        '"list_label":"{{p1_list_label}}","list":["{{p1_item_1}}","{{p1_item_2}}","{{p1_item_3}}","{{p1_item_4}}"],'
        '"cta_primary_text":"{{p1_cta_primary_text}}","cta_primary_link":"{{p1_cta_primary_link}}",'
        '"cta_secondary_text":"{{p1_cta_secondary_text}}","cta_secondary_link":"{{p1_cta_secondary_link}}"},'
        '"stegforsteg":{"eyebrow":"{{p2_eyebrow}}","title":"{{p2_title}}","lead":"{{p2_lead}}",'
        '"list_label":"{{p2_list_label}}","list":["{{p2_item_1}}","{{p2_item_2}}","{{p2_item_3}}","{{p2_item_4}}"],'
        '"cta_primary_text":"{{p2_cta_primary_text}}","cta_primary_link":"{{p2_cta_primary_link}}",'
        '"cta_secondary_text":"{{p2_cta_secondary_text}}","cta_secondary_link":"{{p2_cta_secondary_link}}"},'
        '"aterstart":{"eyebrow":"{{p3_eyebrow}}","title":"{{p3_title}}","lead":"{{p3_lead}}",'
        '"list_label":"{{p3_list_label}}","list":["{{p3_item_1}}","{{p3_item_2}}","{{p3_item_3}}","{{p3_item_4}}"],'
        '"cta_primary_text":"{{p3_cta_primary_text}}","cta_primary_link":"{{p3_cta_primary_link}}",'
        '"cta_secondary_text":"{{p3_cta_secondary_text}}","cta_secondary_link":"{{p3_cta_secondary_link}}"}'
        '}}'
        '</script>'
        '</div>'
        '</div>'
        '</div>'
        '<script>' + FEAR_MATCHER_JS + '</script>'
        '</section>'
    )

    schema = [
        {"name": "eyebrow",          "type": "text",     "label": "Etikett",           "default": "Trygghetsmatchning"},
        {"name": "disclaimer_note",  "type": "text",     "label": "Disclaimer vid Premium-badge", "default": "* ev. implementationskostnader kan förekomma"},
        {"name": "heading",          "type": "text",     "label": "Rubrik",            "default": "Hitta rätt sätt att börja igen."},
        {"name": "subtext",          "type": "textarea", "label": "Undertext",         "default": "Fyra frågor om vad som känns svårt — så föreslår vi det paket som passar dig bäst."},
        {"name": "lead",             "type": "textarea", "label": "Lead-text vänsterspalt", "default": "Vi möter dagligen patienter med tandvårdsrädsla — från mild oro till svår fobi. Beroende på vad som triggar din rädsla finns olika vägar in: lugnande medicin, steg-för-steg-bemötande eller ett återstart-besök helt utan ingrepp."},
        {"name": "trust_1_title",    "type": "text",     "label": "Trust-punkt 1 rubrik", "default": "Inga rätt eller fel svar"},
        {"name": "trust_1_desc",     "type": "text",     "label": "Trust-punkt 1 text",   "default": "Det här är en guide, inte en diagnos."},
        {"name": "trust_2_title",    "type": "text",     "label": "Trust-punkt 2 rubrik", "default": "Du bestämmer takten"},
        {"name": "trust_2_desc",     "type": "text",     "label": "Trust-punkt 2 text",   "default": "Du kan alltid byta paket eller pausa."},
        {"name": "trust_3_title",    "type": "text",     "label": "Trust-punkt 3 rubrik", "default": "Sparas inte"},
        {"name": "trust_3_desc",     "type": "text",     "label": "Trust-punkt 3 text",   "default": "Dina svar lämnar inte din webbläsare."},
        {"name": "analysing_label",  "type": "text",     "label": "Text under matchning",  "default": "Matchar dig med rätt paket"},
        {"name": "matching_caveat",  "type": "textarea", "label": "Disclaimer under resultat", "default": "Matchningen är en vägledning — alla är välkomna oavsett resultat."},

        {"name": "q1_text", "type": "text", "label": "Fråga 1", "default": "Är du rädd för sprutor eller bedövningsnålar?"},
        {"name": "q1_sub",  "type": "text", "label": "Fråga 1 underrubrik", "default": "Många upplever obehag av nålar — du är inte ensam."},
        {"name": "q2_text", "type": "text", "label": "Fråga 2", "default": "Är ljud eller känsla av borr ett stort problem?"},
        {"name": "q2_sub",  "type": "text", "label": "Fråga 2 underrubrik", "default": "Borrljudet är en av de vanligaste anledningarna till tandvårdsrädsla."},
        {"name": "q3_text", "type": "text", "label": "Fråga 3", "default": "Vill du veta exakt vad som händer hela tiden?"},
        {"name": "q3_sub",  "type": "text", "label": "Fråga 3 underrubrik", "default": "Vissa känner trygghet av att förstå varje steg — andra vill bara att det är över."},
        {"name": "q4_text", "type": "text", "label": "Fråga 4", "default": "Har du undvikit tandläkaren i mer än två år?"},
        {"name": "q4_sub",  "type": "text", "label": "Fråga 4 underrubrik", "default": "Det är vanligare än du tror — och vi möter dig där du är."},

        {"name": "p1_eyebrow", "type": "text", "label": "Persona 1 etikett", "default": "Rekommenderat paket"},
        {"name": "p1_title", "type": "text", "label": "Persona 1 titel", "default": "Lugnande medicin vid besöket"},
        {"name": "p1_lead", "type": "textarea", "label": "Persona 1 lead", "default": "Du beskriver klassiska tecken på behandlingsrädsla där anxiolytika (lugnande läkemedel) kan göra verklig skillnad. Vi diskuterar alltid alternativen i förväg — du vet exakt vad medicinen gör och hur lång tid den verkar."},
        {"name": "p1_list_label", "type": "text", "label": "Persona 1 listrubrik", "default": "Vad det innebär"},
        {"name": "p1_item_1", "type": "text", "label": "Persona 1 punkt 1", "default": "Tabletter du tar 30–60 min innan besöket — verkar lugnande utan att söva."},
        {"name": "p1_item_2", "type": "text", "label": "Persona 1 punkt 2", "default": "Diskuteras alltid med tandläkaren i förväg — inget överraskar dig."},
        {"name": "p1_item_3", "type": "text", "label": "Persona 1 punkt 3", "default": "Kombineras gärna med extra noggrann topical-bedövning innan injektion."},
        {"name": "p1_item_4", "type": "text", "label": "Persona 1 punkt 4", "default": "Du behöver sällskap hem — påverkan finns kvar några timmar."},
        {"name": "p1_cta_primary_text", "type": "text", "label": "Persona 1 primär CTA", "default": "Boka konsultation"},
        {"name": "p1_cta_primary_link", "type": "url", "label": "Persona 1 primär länk", "default": "#tdl-booking-widget"},
        {"name": "p1_cta_secondary_text", "type": "text", "label": "Persona 1 sekundär CTA", "default": "Läs om vårt arbetssätt"},
        {"name": "p1_cta_secondary_link", "type": "url", "label": "Persona 1 sekundär länk", "default": "/tandvardsradsla/"},

        {"name": "p2_eyebrow", "type": "text", "label": "Persona 2 etikett", "default": "Rekommenderat paket"},
        {"name": "p2_title", "type": "text", "label": "Persona 2 titel", "default": "Steg-för-steg-tandläkare"},
        {"name": "p2_lead", "type": "textarea", "label": "Persona 2 lead", "default": "Du vill ha kontroll och förstå exakt vad som händer. Hos oss träffar du en tandläkare som tar tid att förklara varje moment innan vi gör det — och stannar upp så fort du behöver paus eller frågar."},
        {"name": "p2_list_label", "type": "text", "label": "Persona 2 listrubrik", "default": "Vad det innebär"},
        {"name": "p2_item_1", "type": "text", "label": "Persona 2 punkt 1", "default": "Genomgång av allt som ska göras innan vi börjar."},
        {"name": "p2_item_2", "type": "text", "label": "Persona 2 punkt 2", "default": "'Stop-handen' — du höjer handen, vi stannar direkt."},
        {"name": "p2_item_3", "type": "text", "label": "Persona 2 punkt 3", "default": "Ingen säljpress — du bestämmer när och hur snabbt."},
        {"name": "p2_item_4", "type": "text", "label": "Persona 2 punkt 4", "default": "Längre tid avsatt än vanlig undersökning."},
        {"name": "p2_cta_primary_text", "type": "text", "label": "Persona 2 primär CTA", "default": "Boka konsultation utan ingrepp"},
        {"name": "p2_cta_primary_link", "type": "url", "label": "Persona 2 primär länk", "default": "#tdl-booking-widget"},
        {"name": "p2_cta_secondary_text", "type": "text", "label": "Persona 2 sekundär CTA", "default": "Läs om vår metod"},
        {"name": "p2_cta_secondary_link", "type": "url", "label": "Persona 2 sekundär länk", "default": "/tandvardsradsla/"},

        {"name": "p3_eyebrow", "type": "text", "label": "Persona 3 etikett", "default": "Rekommenderat paket"},
        {"name": "p3_title", "type": "text", "label": "Persona 3 titel", "default": "Återstart — utan behandling första gången"},
        {"name": "p3_lead", "type": "textarea", "label": "Persona 3 lead", "default": "Att inte ha gått på flera år är ingenting att skämmas för — det är där vi är specialiserade. Första besöket är samtal och en mjuk undersökning utan ingrepp. Inga föreläsningar, ingen skam — bara en plan framåt."},
        {"name": "p3_list_label", "type": "text", "label": "Persona 3 listrubrik", "default": "Vad det innebär"},
        {"name": "p3_item_1", "type": "text", "label": "Persona 3 punkt 1", "default": "Första besöket: bara samtal och ev. en titt — inget mer."},
        {"name": "p3_item_2", "type": "text", "label": "Persona 3 punkt 2", "default": "Du bestämmer takten på all kommande behandling."},
        {"name": "p3_item_3", "type": "text", "label": "Persona 3 punkt 3", "default": "Vi börjar med det enklaste, inte det svåraste."},
        {"name": "p3_item_4", "type": "text", "label": "Persona 3 punkt 4", "default": "Vi avsätter extra tid — ingen tidsstress vid första besöket."},
        {"name": "p3_cta_primary_text", "type": "text", "label": "Persona 3 primär CTA", "default": "Boka återstart-besök"},
        {"name": "p3_cta_primary_link", "type": "url", "label": "Persona 3 primär länk", "default": "#tdl-booking-widget"},
        {"name": "p3_cta_secondary_text", "type": "text", "label": "Persona 3 sekundär CTA", "default": "Läs hur vi jobbar"},
        {"name": "p3_cta_secondary_link", "type": "url", "label": "Persona 3 sekundär länk", "default": "/tandvardsradsla/"},
    ]

    return {
        "block_name": "lumo/fear-matcher",
        "title": "Trygghetsmatchning (premium)",
        "html_template": _collapse(html),
        "schema": schema,
    }


# ---------------------------------------------------------------------------
# Treatment Stepper — 5-stegs behandlingsflöde (för implantat-sidan)
# ---------------------------------------------------------------------------

TREATMENT_STEPPER_CSS = """
.ts-section { background: var(--bg-soft); padding: var(--space-9) 0; border-top:1px solid var(--border); border-bottom:1px solid var(--border); scroll-margin-top: -78px; }
.ts-header { display:grid; grid-template-columns:1fr auto; align-items:end; gap:32px; margin-bottom:48px; padding-bottom:28px; border-bottom:1px solid var(--border); }
.ts-eyebrow-row { display:flex; align-items:center; flex-wrap:wrap; gap:6px 0; margin-bottom:12px; }
.ts-header-meta { max-width:34ch; text-align:right; margin:0; color:var(--fg-muted); }
.ts-premium-note { font-size:10px; color:var(--fg-subtle); font-style:italic; letter-spacing:.02em; line-height:1.4; flex-basis:100%; margin:6px 0 0 0; }

.ts-rail { display:grid; grid-template-columns:repeat(5,1fr); gap:0; position:relative; margin-bottom:var(--space-8); }
.ts-rail::before { content:''; position:absolute; left:10%; right:10%; top:24px; height:1px; background:var(--border); z-index:0; }
.ts-step { display:flex; flex-direction:column; align-items:center; gap:10px; cursor:pointer; position:relative; z-index:1; background:var(--bg-soft); padding:0 6px; }
.ts-step-circle { width:48px; height:48px; border-radius:50%; background:var(--white); border:1px solid var(--border); display:flex; align-items:center; justify-content:center; font-family:var(--font-sans); font-size:15px; font-weight:500; color:var(--fg-muted); transition:all var(--dur-fast) var(--ease-standard); }
.ts-step.is-active .ts-step-circle { background:var(--ink-700); border-color:var(--ink-700); color:var(--white); }
.ts-step.is-done .ts-step-circle { background:var(--white); border-color:var(--ink-700); color:var(--ink-700); }
.ts-step:hover:not(.is-active) .ts-step-circle { border-color:var(--ink-500); }
.ts-step-label { font-size:14px; font-weight:500; color:var(--fg-strong); text-align:center; }
.ts-step.is-active .ts-step-label { color:var(--ink-700); }
.ts-step-meta { font-size:10px; letter-spacing:.18em; text-transform:uppercase; color:var(--fg-subtle); }

.ts-card { background:var(--white); border:1px solid var(--border); box-shadow:var(--shadow-md); display:grid; grid-template-columns:1fr 1.6fr; gap:0; overflow:hidden; }
.ts-card-left { padding:clamp(28px, 3.5vw, 44px); border-right:1px solid var(--border); display:flex; flex-direction:column; gap:var(--space-3); }
.ts-card-number { font-family:var(--font-serif); font-size:64px; line-height:1; color:var(--blush-400); font-style:italic; font-weight:400; }
.ts-card-eyebrow { font-size:var(--fs-eyebrow); text-transform:uppercase; letter-spacing:var(--tracking-eyebrow); font-weight:500; color:var(--fg-muted); margin-top:var(--space-3); }
.ts-card-title { font-family:var(--font-serif); font-weight:400; font-size:24px; line-height:1.2; color:var(--fg-strong); margin:0; }
.ts-card-pill { display:inline-flex; align-items:center; gap:6px; padding:5px 10px; background:var(--blush-50); border:1px solid var(--blush-200); border-radius:999px; color:var(--blush-600); font-size:10px; font-weight:600; letter-spacing:.16em; text-transform:uppercase; align-self:flex-start; margin-top:var(--space-3); }
.ts-card-pill::before { content:'+'; font-weight:700; }
.ts-card-right { padding:clamp(28px, 3.5vw, 44px); display:flex; flex-direction:column; gap:var(--space-5); }
.ts-card-lead { color:var(--ink-500); font-size:var(--fs-lead); line-height:1.6; margin:0; }
.ts-card-cols { display:grid; grid-template-columns:1fr 1fr; gap:var(--space-6); padding-top:var(--space-3); border-top:1px solid var(--border); }
.ts-card-col-label { font-size:9px; font-weight:600; letter-spacing:.22em; text-transform:uppercase; color:var(--blush-600); margin-bottom:var(--space-3); }
.ts-card-col-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:10px; }
.ts-card-col-list li { font-size:13px; line-height:1.5; color:var(--ink-500); padding-left:14px; position:relative; }
.ts-card-col-list li::before { content:'—'; position:absolute; left:0; color:var(--blush-400); }
.ts-card-footer { grid-column:1 / -1; border-top:1px solid var(--border); padding:var(--space-4) clamp(28px, 3.5vw, 44px); display:flex; justify-content:space-between; align-items:center; }
.ts-nav-btn { background:none; border:none; padding:0; font-family:var(--font-sans); font-size:13px; color:var(--fg-muted); cursor:pointer; letter-spacing:.02em; transition:color var(--dur-fast) var(--ease-standard); }
.ts-nav-btn:hover:not(:disabled) { color:var(--fg-strong); }
.ts-nav-btn:disabled { color:var(--ink-100); cursor:not-allowed; }

.ts-mobile { display:none; flex-direction:column; gap:8px; }
.ts-acc { background:var(--white); border:1px solid var(--border); overflow:hidden; }
.ts-acc-head { width:100%; display:grid; grid-template-columns:auto 1fr auto; gap:14px; align-items:center; padding:14px 16px; background:none; border:none; cursor:pointer; text-align:left; font-family:var(--font-sans); }
.ts-acc-num { width:32px; height:32px; border-radius:50%; background:var(--white); border:1px solid var(--border); display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:500; color:var(--fg-muted); }
.ts-acc.is-open .ts-acc-num { background:var(--ink-700); border-color:var(--ink-700); color:var(--white); }
.ts-acc-titles { display:flex; flex-direction:column; gap:2px; min-width:0; }
.ts-acc-title { font-size:14px; font-weight:500; color:var(--fg-strong); line-height:1.3; }
.ts-acc-meta { font-size:10px; letter-spacing:.16em; text-transform:uppercase; color:var(--fg-subtle); }
.ts-acc-chev { width:16px; height:16px; color:var(--fg-subtle); transition:transform var(--dur-fast) var(--ease-standard); flex-shrink:0; }
.ts-acc.is-open .ts-acc-chev { transform:rotate(180deg); }
.ts-acc-body { display:none; padding:0 16px 18px 16px; border-top:1px solid var(--border); }
.ts-acc.is-open .ts-acc-body { display:block; }
.ts-acc-lead { color:var(--ink-500); font-size:14px; line-height:1.6; margin:14px 0 var(--space-4) 0; }
.ts-acc-col { margin-bottom:var(--space-4); }
.ts-acc-col:last-child { margin-bottom:0; }

.ts-bottom { margin-top:var(--space-7); padding-top:var(--space-5); border-top:1px solid var(--border); display:grid; grid-template-columns:1fr auto; gap:var(--space-5); align-items:center; }
.ts-bottom-text { max-width:48ch; color:var(--fg-muted); font-size:14px; margin:0; }
.ts-bottom-ctas { display:flex; gap:var(--space-2); }

@media (max-width:900px) {
  .ts-header { grid-template-columns:1fr; align-items:start; gap:14px; margin-bottom:0; padding-bottom:0; border-bottom:0; }
  .ts-header-meta { display:none; }
  .ts-rail, .ts-card { display:none; }
  .ts-mobile { display:flex; margin-top:24px; }
  .ts-bottom { grid-template-columns:1fr; }
  .ts-bottom-ctas { flex-direction:column; }
  .ts-bottom-ctas .btn { width:100%; justify-content:center; }
}
"""


TREATMENT_STEPPER_JS = r"""
(function(){
  /* Treatment Stepper — vanilla JS. Inga // kommentarer. */
  var root = document.querySelector('[data-treatment-stepper]');
  if (!root) return;
  if (root.dataset.tsReady === '1') return;
  root.dataset.tsReady = '1';

  var cfgEl = root.querySelector('script[type="application/json"][data-ts-config]');
  if (!cfgEl) return;
  var CFG;
  try { CFG = JSON.parse(cfgEl.textContent); } catch (e) { return; }
  var STEPS = CFG.steps || [];
  if (!STEPS.length) return;

  var section = root.closest('.ts-section') || root;
  var rail    = root.querySelector('[data-ts-rail]');
  var card    = root.querySelector('[data-ts-card]');
  var mobile  = root.querySelector('[data-ts-mobile]');

  var state = { active: 0, mobileCollapsed: false };

  function getHeaderOffset() {
    var el = document.querySelector('.site-header');
    if (!el) return 0;
    var cs = window.getComputedStyle(el);
    if (cs.position === 'fixed' || cs.position === 'sticky') {
      return el.getBoundingClientRect().height;
    }
    return 0;
  }

  function centerWidget() {
    var isMobile = window.matchMedia('(max-width: 900px)').matches;
    var openRow = mobile && mobile.children[state.active];
    var target = isMobile ? (openRow || mobile) : section;
    var rect = target.getBoundingClientRect();
    var vh = window.innerHeight || document.documentElement.clientHeight;
    var pageY = window.pageYOffset || document.documentElement.scrollTop || 0;
    var headerH = getHeaderOffset();
    var gap = 16;
    var top;
    if (isMobile) {
      top = pageY + rect.top - headerH - gap;
    } else {
      var avail = vh - headerH;
      var snapAdjust = 50;
      top = pageY + rect.top - headerH - Math.max(gap, (avail - rect.height) / 2) + snapAdjust;
    }
    top = Math.max(0, top);
    try { window.scrollTo({ top: top, behavior: 'smooth' }); }
    catch (e) { window.scrollTo(0, top); }
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function pad2(n) { return n < 10 ? '0' + n : '' + n; }

  function renderRail() {
    if (!rail) return;
    rail.innerHTML = STEPS.map(function(s, i){
      var cls = 'ts-step';
      if (i === state.active) cls += ' is-active';
      else if (i < state.active) cls += ' is-done';
      return '<button type="button" class="' + cls + '" data-ts-goto="' + i + '">'
        + '<div class="ts-step-circle">' + (i + 1) + '</div>'
        + '<div class="ts-step-label">' + esc(s.label) + '</div>'
        + '<div class="ts-step-meta">' + esc(s.duration) + '</div>'
        + '</button>';
    }).join('');
  }

  function renderListItems(items) {
    return (items || []).map(function(t){ return '<li>' + esc(t) + '</li>'; }).join('');
  }

  function renderCard() {
    if (!card) return;
    var s = STEPS[state.active];
    var idx = state.active;
    var isLast  = idx === STEPS.length - 1;
    var isFirst = idx === 0;
    card.innerHTML =
      '<div class="ts-card-left">'
      + '<div class="ts-card-number">' + pad2(idx + 1) + '</div>'
      + '<div class="ts-card-eyebrow">' + esc(s.eyebrow) + '</div>'
      + '<h3 class="ts-card-title">' + esc(s.title) + '</h3>'
      + '<span class="ts-card-pill">' + esc(s.durationFull) + '</span>'
      + '</div>'
      + '<div class="ts-card-right">'
      + '<p class="ts-card-lead">' + esc(s.desc) + '</p>'
      + '<div class="ts-card-cols">'
      + '<div><div class="ts-card-col-label">' + esc(s.leftLabel) + '</div>'
      + '<ul class="ts-card-col-list">' + renderListItems(s.leftItems) + '</ul></div>'
      + '<div><div class="ts-card-col-label">' + esc(s.rightLabel) + '</div>'
      + '<ul class="ts-card-col-list">' + renderListItems(s.rightItems) + '</ul></div>'
      + '</div></div>'
      + '<div class="ts-card-footer">'
      + '<button type="button" class="ts-nav-btn" data-ts-prev ' + (isFirst ? 'disabled' : '') + '>← Föregående steg</button>'
      + '<button type="button" class="ts-nav-btn" data-ts-next ' + (isLast ? 'disabled' : '') + '>' + (isLast ? 'Klart' : 'Nästa steg →') + '</button>'
      + '</div>';
  }

  function renderMobile() {
    if (!mobile) return;
    mobile.innerHTML = STEPS.map(function(s, i){
      var open = i === state.active && !state.mobileCollapsed;
      var cls = 'ts-acc' + (open ? ' is-open' : '');
      var body = open
        ? '<div class="ts-acc-body">'
          + '<p class="ts-acc-lead">' + esc(s.desc) + '</p>'
          + '<div class="ts-acc-col"><div class="ts-card-col-label">' + esc(s.leftLabel) + '</div>'
          + '<ul class="ts-card-col-list">' + renderListItems(s.leftItems) + '</ul></div>'
          + '<div class="ts-acc-col"><div class="ts-card-col-label">' + esc(s.rightLabel) + '</div>'
          + '<ul class="ts-card-col-list">' + renderListItems(s.rightItems) + '</ul></div>'
          + '</div>'
        : '';
      return '<div class="' + cls + '">'
        + '<button type="button" class="ts-acc-head" data-ts-goto="' + i + '">'
        + '<div class="ts-acc-num">' + (i + 1) + '</div>'
        + '<div class="ts-acc-titles">'
        + '<div class="ts-acc-title">' + esc(s.title) + '</div>'
        + '<div class="ts-acc-meta">' + esc(s.durationFull) + '</div>'
        + '</div>'
        + '<svg class="ts-acc-chev" viewBox="0 0 16 16" fill="none"><path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        + '</button>'
        + body
        + '</div>';
    }).join('');
  }

  function setActive(i) {
    if (i < 0 || i >= STEPS.length) return;
    state.active = i;
    renderRail();
    renderCard();
    renderMobile();
  }

  function onClick(e) {
    var goto = e.target.closest('[data-ts-goto]');
    if (goto) {
      var idx = parseInt(goto.getAttribute('data-ts-goto'), 10);
      var isMobile = window.matchMedia('(max-width: 900px)').matches;
      if (isMobile && idx === state.active) {
        state.mobileCollapsed = !state.mobileCollapsed;
        renderMobile();
        if (!state.mobileCollapsed) requestAnimationFrame(centerWidget);
      } else {
        state.mobileCollapsed = false;
        setActive(idx);
        requestAnimationFrame(centerWidget);
      }
      return;
    }
    if (e.target.closest('[data-ts-next]')) { state.mobileCollapsed = false; setActive(state.active + 1); requestAnimationFrame(centerWidget); return; }
    if (e.target.closest('[data-ts-prev]')) { state.mobileCollapsed = false; setActive(state.active - 1); requestAnimationFrame(centerWidget); return; }
  }

  root.addEventListener('click', onClick);
  renderRail();
  renderCard();
  renderMobile();
})();
"""


def build_treatment_stepper() -> dict:
    """5-stegs behandlingsstepper för implantat-sidan (premium)."""
    html = (
        '<section id="behandlingsstepper" class="ts-section">'
        '<style>' + TREATMENT_STEPPER_CSS + '</style>'
        '<div class="container-wide">'
        '<div class="ts-header">'
        '<div>'
        '<div class="ts-eyebrow-row">'
        '<span class="eyebrow">{{eyebrow}}</span>'
        '<span class="lumo-premium-badge" onclick="lumoToggle(this)">'
        '<span class="lumo-premium-dot"></span>'
        '<span class="lumo-mode-lbl">Premium</span>'
        + lumo_tooltip("behandlingsstepper") +
        '</span>'
        '<span class="ts-premium-note">{{disclaimer_note}}</span>'
        '</div>'
        '<h2 style="max-width:22ch;">{{heading}}</h2>'
        '</div>'
        '<p class="ts-header-meta">{{subtext}}</p>'
        '</div>'
        '<div data-treatment-stepper>'
        '<div class="ts-rail" data-ts-rail></div>'
        '<div class="ts-card" data-ts-card></div>'
        '<div class="ts-mobile" data-ts-mobile></div>'
        '<script type="application/json" data-ts-config>'
        '{"steps":['
        + ",".join([
            '{'
            f'"label":"{{{{s{n}_label}}}}",'
            f'"duration":"{{{{s{n}_duration}}}}",'
            f'"durationFull":"{{{{s{n}_duration_full}}}}",'
            f'"eyebrow":"{{{{s{n}_eyebrow}}}}",'
            f'"title":"{{{{s{n}_title}}}}",'
            f'"desc":"{{{{s{n}_desc}}}}",'
            f'"leftLabel":"{{{{s{n}_left_label}}}}",'
            f'"leftItems":["{{{{s{n}_left_1}}}}","{{{{s{n}_left_2}}}}","{{{{s{n}_left_3}}}}"],'
            f'"rightLabel":"{{{{s{n}_right_label}}}}",'
            f'"rightItems":["{{{{s{n}_right_1}}}}","{{{{s{n}_right_2}}}}","{{{{s{n}_right_3}}}}"]'
            '}'
            for n in range(1, 6)
        ])
        + ']}'
        '</script>'
        '</div>'
        '<div class="ts-bottom">'
        '<p class="ts-bottom-text">{{bottom_text}}</p>'
        '<div class="ts-bottom-ctas">'
        '<a href="{{cta_1_link}}" class="btn btn-ghost btn-sm">{{cta_1_text}}</a>'
        '<a href="{{cta_2_link}}" class="btn btn-primary btn-sm">{{cta_2_text}}</a>'
        '</div>'
        '</div>'
        '</div>'
        '<script>' + TREATMENT_STEPPER_JS + '</script>'
        '</section>'
    )

    steps_data = [
        {
            "label": "Konsultation", "duration": "45–60 min", "duration_full": "Ca 45–60 minuter",
            "eyebrow": "Steg 01 — Bedömning", "title": "Konsultation & 3D-röntgen",
            "desc": "Du träffar vårt erfarna specialistteam med hundratals genomförda implantat. Vi tar 3D/CBCT-röntgen på plats — utan remiss till röntgenklinik — som visar käkbenets struktur i tre dimensioner. Så vi kan planera placeringen med precision och säkerhet.",
            "left_label": "Du upplever",
            "left_1": "Ca 45–60 minuter avsatt tid.",
            "left_2": "Smärtfri 3D-röntgen — ingen bedövning behövs.",
            "left_3": "Tid för dina frågor — inga dumma frågor.",
            "right_label": "Vi gör",
            "right_1": "Kartlägger benstruktur och tandhälsa.",
            "right_2": "Bedömer förutsättningar för implantat.",
            "right_3": "Diskuterar tidsplan och förväntningar.",
        },
        {
            "label": "Behandlingsplan", "duration": "1 vecka", "duration_full": "Inom 1 vecka",
            "eyebrow": "Steg 02 — Plan & offert", "title": "Detaljerad plan, offert & finansiering",
            "desc": "Du får en skriftlig behandlingsplan med exakt prisuppgift, tidsplan och alla alternativ. Vi går igenom planen tillsammans och svarar på alla frågor. Räntefri delbetalning erbjuds vid behov.",
            "left_label": "Du upplever",
            "left_1": "Skriftlig behandlingsplan med pris.",
            "left_2": "Lugn betänketid — ingen säljpress.",
            "left_3": "Räntefri finansiering om du vill.",
            "right_label": "Vi gör",
            "right_1": "Skräddarsyr planen efter ditt fall.",
            "right_2": "Förbereder material och team.",
            "right_3": "Bokar tid som passar dig.",
        },
        {
            "label": "Operation", "duration": "60–90 min", "duration_full": "Ca 60–90 minuter",
            "eyebrow": "Steg 03 — Implantatoperation", "title": "Implantatet sätts in",
            "desc": "Under lokalbedövning placeras en titanskruv i käkbenet. Operationen är väl beprövad och utförs av specialister med lång erfarenhet. De flesta beskriver det som lugnt och smärtfritt — mild ömhet och svullnad kan förekomma 1–3 dagar, men de flesta är tillbaka på jobbet dagen efter.",
            "left_label": "Du upplever",
            "left_1": "Lokalbedövning — du är vaken men känner ingenting.",
            "left_2": "Lugnande medicin kan diskuteras vid behov.",
            "left_3": "Hem samma dag — vila resten av dagen.",
            "right_label": "Vi gör",
            "right_1": "Placerar titanskruven med digital precision.",
            "right_2": "Eftervårdsanvisningar muntligt och skriftligt.",
            "right_3": "Bokar uppföljningskontroller under läkningen.",
        },
        {
            "label": "Läkning", "duration": "3–6 mån", "duration_full": "3 till 6 månader",
            "eyebrow": "Steg 04 — Osseointegration", "title": "Käkbenet växer fast runt implantatet",
            "desc": "Under läkningsperioden växer benvävnaden ihop med titanskruven — en process som kallas osseointegration. Du har en tillfällig provisorisk lösning så du aldrig är utan tänder. Vi följer upp med kontroller.",
            "left_label": "Du upplever",
            "left_1": "Tillfällig krona eller protes under tiden.",
            "left_2": "Vanlig tandborstning — som vanligt.",
            "left_3": "Inga ingrepp under läkningsperioden.",
            "right_label": "Vi gör",
            "right_1": "Regelbundna uppföljningskontroller under läkningen.",
            "right_2": "Bevakar att osseointegrationen fortskrider.",
            "right_3": "Förbereder den slutliga kronan.",
        },
        {
            "label": "Slutlig krona", "duration": "Ca 30 min", "duration_full": "Cirka 30 minuter",
            "eyebrow": "Steg 05 — Färdig behandling", "title": "Den slutliga kronan sätts på",
            "desc": "När implantatet är fullt integrerat fäster vi den permanenta kronan — specialtillverkad efter dina egna tänder i färg och form. Du går ut med en helt naturlig tand som du kan tugga, le och tala med precis som vanligt.",
            "left_label": "Du upplever",
            "left_1": "Ca 30 minuter — snabbt och smärtfritt.",
            "left_2": "Naturligt utseende — matchar dina egna tänder.",
            "left_3": "Full funktion direkt.",
            "right_label": "Vi gör",
            "right_1": "Färgmatchning mot dina andra tänder.",
            "right_2": "Bett-justering för optimal funktion.",
            "right_3": "Bokar in årlig kontroll.",
        },
    ]

    schema = [
        {"name": "eyebrow",         "type": "text",     "label": "Etikett",          "default": "Behandlingsplan"},
        {"name": "disclaimer_note", "type": "text",     "label": "Disclaimer vid Premium-badge", "default": "* ev. implementationskostnader kan förekomma"},
        {"name": "heading",         "type": "text",     "label": "Rubrik",           "default": "Så går implantat till hos oss."},
        {"name": "subtext",         "type": "textarea", "label": "Undertext (höger)", "default": "Fem steg över 3–6 månader. Du vet exakt vad som händer, när — och varför."},
        {"name": "bottom_text",     "type": "textarea", "label": "Bottom CTA-text",  "default": "Osäker på om implantat är rätt för dig? Boka konsultation från 199 kr — vi tar 3D-röntgen och går igenom dina förutsättningar utan förpliktelser till fortsatt behandling."},
        {"name": "cta_1_text",      "type": "text",     "label": "Bottom CTA 1 text", "default": "Ring kliniken"},
        {"name": "cta_1_link",      "type": "url",      "label": "Bottom CTA 1 länk", "default": "tel:0812854555"},
        {"name": "cta_2_text",      "type": "text",     "label": "Bottom CTA 2 text", "default": "Boka konsultation"},
        {"name": "cta_2_link",      "type": "url",      "label": "Bottom CTA 2 länk", "default": "#tdl-booking-widget"},
    ]

    for i, s in enumerate(steps_data, start=1):
        schema.extend([
            {"name": f"s{i}_label",         "type": "text",     "label": f"Steg {i} – kort label",   "default": s["label"]},
            {"name": f"s{i}_duration",      "type": "text",     "label": f"Steg {i} – tid kort",     "default": s["duration"]},
            {"name": f"s{i}_duration_full", "type": "text",     "label": f"Steg {i} – tid lång",     "default": s["duration_full"]},
            {"name": f"s{i}_eyebrow",       "type": "text",     "label": f"Steg {i} – eyebrow",      "default": s["eyebrow"]},
            {"name": f"s{i}_title",         "type": "text",     "label": f"Steg {i} – titel",        "default": s["title"]},
            {"name": f"s{i}_desc",          "type": "textarea", "label": f"Steg {i} – beskrivning",  "default": s["desc"]},
            {"name": f"s{i}_left_label",    "type": "text",     "label": f"Steg {i} – vänster rubrik", "default": s["left_label"]},
            {"name": f"s{i}_left_1",        "type": "text",     "label": f"Steg {i} – vänster pkt 1", "default": s["left_1"]},
            {"name": f"s{i}_left_2",        "type": "text",     "label": f"Steg {i} – vänster pkt 2", "default": s["left_2"]},
            {"name": f"s{i}_left_3",        "type": "text",     "label": f"Steg {i} – vänster pkt 3", "default": s["left_3"]},
            {"name": f"s{i}_right_label",   "type": "text",     "label": f"Steg {i} – höger rubrik",  "default": s["right_label"]},
            {"name": f"s{i}_right_1",       "type": "text",     "label": f"Steg {i} – höger pkt 1",   "default": s["right_1"]},
            {"name": f"s{i}_right_2",       "type": "text",     "label": f"Steg {i} – höger pkt 2",   "default": s["right_2"]},
            {"name": f"s{i}_right_3",       "type": "text",     "label": f"Steg {i} – höger pkt 3",   "default": s["right_3"]},
        ])

    return {
        "block_name": "lumo/treatment-stepper",
        "title": "Behandlingssteg (premium)",
        "html_template": _collapse(html),
        "schema": schema,
    }


# ---------------------------------------------------------------------------
# Premium Tour — auto-popup som listar alla premium-features (för demo/review)
# ---------------------------------------------------------------------------

PREMIUM_TOUR_CSS = """
.lpt-trigger { position:fixed; bottom:24px; right:24px; z-index:9998; display:inline-flex; align-items:center; gap:8px; padding:10px 16px 10px 12px; background:rgba(10,10,10,.92); color:#c9a14a; border:1px solid rgba(201,161,74,.6); border-radius:999px; font-family:var(--font-sans, system-ui); font-size:11px; font-weight:600; letter-spacing:.16em; text-transform:uppercase; cursor:pointer; box-shadow:0 8px 24px rgba(0,0,0,.25); backdrop-filter:blur(6px); transition:transform .2s ease, box-shadow .2s ease; }
.lpt-trigger:hover { transform:translateY(-2px); box-shadow:0 12px 28px rgba(0,0,0,.32); }
.lpt-trigger-star { width:14px; height:14px; fill:#c9a14a; }
.lpt-trigger::before { content:''; position:absolute; inset:-4px; border-radius:999px; border:1.5px solid rgba(201,161,74,.5); animation:lpt-ring 2.4s ease-out infinite; pointer-events:none; }
@keyframes lpt-ring { 0% { transform:scale(1); opacity:.7; } 100% { transform:scale(1.25); opacity:0; } }
.admin-bar .lpt-trigger { bottom:56px; }

.lpt-overlay { position:fixed; inset:0; z-index:9999; background:rgba(10,10,10,.6); backdrop-filter:blur(4px); display:none; padding:24px 0; opacity:0; transition:opacity .25s ease; overflow-y:auto; }
.lpt-overlay.is-open { display:block; opacity:1; }
.lpt-modal { background:#fff; max-width:680px; width:100%; border-radius:8px; box-shadow:0 32px 80px rgba(0,0,0,.4); position:relative; transform:translateY(20px); transition:transform .3s ease; overflow:visible; margin:24px auto; }
.lpt-overlay.is-open .lpt-modal { transform:translateY(0); }
.lpt-close { position:absolute; top:14px; right:14px; width:32px; height:32px; border-radius:50%; background:transparent; border:none; cursor:pointer; color:#6e6e6e; display:flex; align-items:center; justify-content:center; transition:background .15s ease; }
.lpt-close:hover { background:#f0f0f0; }
.lpt-header { padding:32px 36px 20px 36px; border-bottom:1px solid #ececec; }
.lpt-eyebrow-row { display:flex; align-items:center; gap:10px; margin-bottom:12px; }
.lpt-eyebrow { font-size:10px; font-weight:600; letter-spacing:.22em; text-transform:uppercase; color:#6e6e6e; }
.lpt-badge { display:inline-flex; align-items:center; gap:6px; padding:3px 8px; background:rgba(10,10,10,.92); border:1px solid rgba(201,161,74,.6); border-radius:4px; color:#c9a14a; font-size:8px; font-weight:600; letter-spacing:.2em; text-transform:uppercase; }
.lpt-badge-dot { width:4px; height:4px; border-radius:50%; background:#c9a14a; }
.lpt-title { font-family:'Cormorant Garamond', Georgia, serif; font-weight:400; font-size:30px; line-height:1.15; color:#1f1f1f; margin:0 0 8px 0; letter-spacing:-.01em; }
.lpt-lead { font-size:14px; line-height:1.55; color:#4a4a4a; margin:0; max-width:52ch; }
.lpt-list { list-style:none; padding:16px 20px; margin:0; display:flex; flex-direction:column; gap:4px; }
.lpt-item { display:block; }
.lpt-card { display:grid; grid-template-columns:auto 1fr auto; gap:18px; align-items:center; padding:18px; border-radius:6px; text-decoration:none; color:inherit; transition:background .15s ease; position:relative; }
.lpt-card-tt { position:absolute; top:calc(100% + 8px); left:18px; right:18px; background:#0a0a0a; color:#fff; padding:18px 22px; border-radius:6px; box-shadow:0 16px 40px rgba(0,0,0,.55); transform:translateY(-6px); opacity:0; pointer-events:none; transition:opacity .2s ease, transform .2s ease; z-index:10010; }
.lpt-card-tt::after { content:''; position:absolute; bottom:100%; left:38px; border:6px solid transparent; border-bottom-color:#0a0a0a; }
.lpt-card:hover .lpt-card-tt { opacity:1; transform:translateY(0); }
.lpt-card-tt-title { font-size:9px; font-weight:700; letter-spacing:.22em; text-transform:uppercase; color:rgba(255,255,255,.5); margin-bottom:10px; }
.lpt-card-tt ul { list-style:none; padding:0; margin:0 0 10px; display:flex; flex-direction:column; gap:7px; }
.lpt-card-tt li { font-size:12px; line-height:1.45; padding-left:16px; position:relative; color:rgba(255,255,255,.9); }
.lpt-card-tt li::before { content:'✓'; position:absolute; left:0; color:#22c55e; font-size:10px; top:1px; }
.lpt-card-tt-note { font-size:10px; color:rgba(255,255,255,.45); border-top:1px solid rgba(255,255,255,.12); padding-top:9px; line-height:1.4; font-style:italic; }
@media (hover: none) { .lpt-card-tt { display:none; } }
.lpt-card:hover { background:#f7f7f7; }
.lpt-card-icon { width:44px; height:44px; border-radius:8px; background:#f0f9fc; display:flex; align-items:center; justify-content:center; color:#1e7596; flex-shrink:0; }
.lpt-card-icon svg { width:22px; height:22px; }
.lpt-card-body { min-width:0; }
.lpt-card-title-row { display:flex; align-items:center; gap:10px; margin-bottom:3px; flex-wrap:wrap; }
.lpt-card-title { font-size:15px; font-weight:600; color:#1f1f1f; letter-spacing:-.01em; }
.lpt-card-badge { display:inline-flex; align-items:center; gap:5px; padding:3px 7px; background:rgba(10,10,10,.92); border:1px solid rgba(201,161,74,.6); border-radius:3px; color:#c9a14a; font-size:8px; font-weight:600; letter-spacing:.2em; text-transform:uppercase; }
.lpt-card-badge-dot { width:4px; height:4px; border-radius:50%; background:#c9a14a; }
.lpt-card-desc { font-size:13px; line-height:1.45; color:#6e6e6e; }
.lpt-card-loc { font-size:10px; letter-spacing:.18em; text-transform:uppercase; color:#a8a8a8; margin-top:6px; }
.lpt-card-arrow { width:22px; height:22px; border-radius:50%; background:transparent; border:1px solid #d6d6d6; display:flex; align-items:center; justify-content:center; color:#6e6e6e; flex-shrink:0; transition:all .15s ease; }
.lpt-card:hover .lpt-card-arrow { background:#1f1f1f; border-color:#1f1f1f; color:#fff; transform:translateX(3px); }
.lpt-footer { padding:16px 36px 24px 36px; border-top:1px solid #ececec; display:flex; justify-content:space-between; align-items:center; gap:16px; }
.lpt-footer-note { font-size:11px; color:#a8a8a8; font-style:italic; line-height:1.4; }
.lpt-footer-btn { background:transparent; border:none; padding:6px 0; font-family:inherit; font-size:12px; color:#6e6e6e; cursor:pointer; letter-spacing:.04em; }
.lpt-footer-btn:hover { color:#1f1f1f; }
@media (max-width:640px) {
  .lpt-modal { max-height:92vh; border-radius:8px 8px 0 0; }
  .lpt-header { padding:24px 22px 16px 22px; }
  .lpt-title { font-size:24px; }
  .lpt-list { padding:10px; }
  .lpt-card { grid-template-columns:auto 1fr auto; gap:12px; padding:14px; }
  .lpt-footer { padding:14px 22px 20px 22px; flex-direction:column; align-items:flex-start; }
  .lpt-trigger { bottom:16px; right:16px; font-size:10px; padding:9px 14px 9px 11px; }
}
"""


PREMIUM_TOUR_JS = r"""
(function(){
  if (window.__lptInit) return;
  window.__lptInit = true;
  var STORAGE_KEY = 'lumo_premium_tour_seen_v1';

  function open()  { var o = document.getElementById('lpt-overlay'); if (o) o.classList.add('is-open'); document.body.style.overflow = 'hidden'; }
  function close() { var o = document.getElementById('lpt-overlay'); if (o) o.classList.remove('is-open'); document.body.style.overflow = ''; try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {} }

  function init() {
    var trigger = document.getElementById('lpt-trigger');
    var overlay = document.getElementById('lpt-overlay');
    var closeBtn = document.querySelectorAll('[data-lpt-close]');
    if (!trigger || !overlay) return;
    trigger.addEventListener('click', open);
    overlay.addEventListener('click', function(e){ if (e.target === overlay) close(); });
    closeBtn.forEach(function(b){ b.addEventListener('click', close); });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape') close(); });
    overlay.querySelectorAll('a.lpt-card').forEach(function(a){
      a.addEventListener('click', function(){ close(); });
    });

    var seen = false;
    try { seen = localStorage.getItem(STORAGE_KEY) === '1'; } catch (e) {}
    if (!seen) { setTimeout(open, 900); }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
"""


# ---------------------------------------------------------------------------
# Cost Calculator — transparent prismatris (9 behandlingar × 3 prismodeller)
# ---------------------------------------------------------------------------

COST_CALCULATOR_CSS = """
.cc-section { background:var(--bg-soft); padding:var(--space-9) 0; border-top:1px solid var(--border); border-bottom:1px solid var(--border); scroll-margin-top:-78px; }
.cc-header { display:grid; grid-template-columns:1fr auto; align-items:end; gap:32px; margin-bottom:48px; padding-bottom:28px; border-bottom:1px solid var(--border); }
.cc-eyebrow-row { display:flex; align-items:center; flex-wrap:wrap; gap:6px 0; margin-bottom:12px; }
.cc-header-meta { max-width:36ch; text-align:right; margin:0; color:var(--fg-muted); }

.cc-grid { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,2.1fr); gap:32px; align-items:start; }
.cc-list-label { font-size:10px; font-weight:600; letter-spacing:.22em; text-transform:uppercase; color:var(--fg-muted); margin-bottom:var(--space-3); }
.cc-list { display:flex; flex-direction:column; gap:6px; }
.cc-list-btn { display:grid; grid-template-columns:auto 1fr auto; gap:14px; align-items:center; padding:14px 16px; background:var(--white); border:1px solid var(--border); cursor:pointer; text-align:left; font-family:inherit; transition:all var(--dur-fast) var(--ease-standard); }
.cc-list-btn:hover { border-color:var(--ink-300); }
.cc-list-btn.is-active { background:var(--ink-700); border-color:var(--ink-700); }
.cc-list-num { font-family:var(--font-serif); font-style:italic; font-size:13px; color:var(--fg-subtle); min-width:24px; }
.cc-list-btn.is-active .cc-list-num { color:var(--blush-300); }
.cc-list-body { min-width:0; display:flex; flex-direction:column; gap:2px; }
.cc-list-name { font-size:14px; font-weight:500; color:var(--fg-strong); display:block; }
.cc-list-meta { font-size:11px; color:var(--fg-subtle); letter-spacing:.02em; display:block; }
.cc-list-btn.is-active .cc-list-name { color:var(--white); }
.cc-list-btn.is-active .cc-list-meta { color:rgba(255,255,255,.55); }
.cc-list-arrow { width:18px; height:18px; color:var(--fg-subtle); opacity:0; transform:translateX(-4px); transition:all var(--dur-fast) var(--ease-standard); }
.cc-list-btn.is-active .cc-list-arrow { color:var(--white); opacity:1; transform:translateX(0); }

.cc-card { background:var(--white); border:1px solid var(--border); box-shadow:var(--shadow-md); padding:clamp(28px, 3.5vw, 44px); position:sticky; top:120px; align-self:start; max-height:calc(100vh - 140px); overflow-x:hidden; overflow-y:auto; min-width:0; }
.cc-card-eyebrow { font-size:var(--fs-eyebrow); text-transform:uppercase; letter-spacing:var(--tracking-eyebrow); font-weight:500; color:var(--blush-600); margin-bottom:var(--space-3); }
.cc-card-title { font-family:var(--font-serif); font-weight:400; font-size:32px; line-height:1.15; color:var(--fg-strong); letter-spacing:-.02em; margin:0 0 var(--space-3) 0; }
.cc-card-desc { color:var(--ink-500); font-size:var(--fs-lead); line-height:1.55; margin:0 0 var(--space-3) 0; }
.cc-card-readmore { display:inline-flex; align-items:center; gap:6px; color:var(--blush-600); font-size:13px; font-weight:500; text-decoration:none; margin-bottom:var(--space-6); border-bottom:1px solid transparent; transition:border-color .15s ease; }
.cc-card-readmore:hover { border-bottom-color:var(--blush-600); }
.cc-prices { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin-bottom:var(--space-4); }
.cc-price { background:var(--blush-50); border:1px solid var(--blush-100); padding:18px; position:relative; display:flex; flex-direction:column; gap:8px; min-width:0; overflow-wrap:anywhere; word-break:break-word; }
.cc-price-label { font-size:9px; font-weight:600; letter-spacing:.22em; text-transform:uppercase; color:var(--blush-600); }
.cc-price-amount { font-family:var(--font-serif); font-weight:400; font-size:22px; line-height:1.15; color:var(--fg-strong); letter-spacing:-.01em; }
.cc-price-unit { font-family:var(--font-sans); font-size:11px; color:var(--fg-subtle); margin-left:4px; }
.cc-price-note { font-size:11px; line-height:1.5; color:var(--fg-muted); flex:1; }
.cc-boka { margin-bottom:var(--space-5); padding:22px 26px; background:var(--ink-700); color:#fff; display:flex; align-items:center; justify-content:space-between; gap:20px; flex-wrap:wrap; }
.cc-boka-text { display:flex; flex-direction:column; gap:4px; min-width:0; }
.cc-boka-eyebrow { font-size:10px; font-weight:600; letter-spacing:.22em; text-transform:uppercase; color:rgba(255,255,255,.55); }
.cc-boka-name { font-family:var(--font-serif); font-weight:400; font-size:20px; line-height:1.2; color:#fff; letter-spacing:-.01em; }
.cc-boka-actions { display:flex; gap:10px; flex-wrap:wrap; }
.cc-boka-btn { display:inline-flex; align-items:center; gap:6px; padding:10px 20px; font-size:13px; font-weight:500; text-decoration:none; transition:background .15s ease, color .15s ease; }
.cc-boka-btn.is-primary { background:#fff; color:var(--ink-700); }
.cc-boka-btn.is-primary:hover { background:var(--blush-50); }
.cc-boka-btn.is-ghost { background:transparent; color:#fff; border:1px solid rgba(255,255,255,.35); }
.cc-boka-btn.is-ghost:hover { border-color:#fff; background:rgba(255,255,255,.08); }
@media(max-width:700px){
  .cc-boka { flex-direction:column; align-items:stretch; padding:20px; }
  .cc-boka-actions { width:100%; }
  .cc-boka-btn { flex:1; justify-content:center; }
}
.cc-disclaimer { font-size:11px; color:var(--fg-subtle); line-height:1.5; padding-top:var(--space-3); border-top:1px solid var(--border); margin-bottom:var(--space-4); }
.cc-card-cta { display:flex; gap:var(--space-2); justify-content:flex-end; }

@media (max-width:900px) {
  .cc-header { grid-template-columns:1fr; align-items:start; gap:14px; margin-bottom:0; padding-bottom:0; border-bottom:0; }
  .cc-header-meta { display:none; }
  .cc-grid { margin-top:24px; }
  .cc-grid { grid-template-columns:1fr; gap:24px; }
  .cc-prices { grid-template-columns:1fr; }
  .cc-card { position:static; max-height:none; overflow:visible; }
  .cc-card-title { font-size:24px; }
  .cc-card-cta { flex-direction:column; }
  .cc-card-cta .btn { width:100%; justify-content:center; }
}
"""


COST_CALCULATOR_JS = r"""
(function(){
  /* Cost Calculator — vanilla JS. Inga // kommentarer. */
  var root = document.querySelector('[data-cost-calc]');
  if (!root) return;
  if (root.dataset.ccReady === '1') return;
  root.dataset.ccReady = '1';

  var cfgEl = root.querySelector('script[type="application/json"][data-cc-config]');
  if (!cfgEl) return;
  var CFG;
  try { CFG = JSON.parse(cfgEl.textContent); } catch (e) { return; }
  var TREATMENTS = CFG.treatments || [];
  if (!TREATMENTS.length) return;

  var section = root.closest('.cc-section') || root;
  var listEl = root.querySelector('[data-cc-list]');
  var cardEl = root.querySelector('[data-cc-card]');

  var state = { active: 0 };

  function getHeaderOffset() {
    var el = document.querySelector('.site-header');
    if (!el) return 0;
    var cs = window.getComputedStyle(el);
    if (cs.position === 'fixed' || cs.position === 'sticky') {
      return el.getBoundingClientRect().height;
    }
    return 0;
  }

  function centerWidget() {
    var target = cardEl;
    if (!target) return;
    var rect = target.getBoundingClientRect();
    var vh = window.innerHeight || document.documentElement.clientHeight;
    var pageY = window.pageYOffset || document.documentElement.scrollTop || 0;
    var headerH = getHeaderOffset();
    var avail = vh - headerH;
    /* Centrera kortet vertikalt i tillgängligt utrymme under headern */
    var top = pageY + rect.top - headerH - Math.max(0, (avail - rect.height) / 2);
    top = Math.max(0, top);
    try { window.scrollTo({ top: top, behavior: 'smooth' }); }
    catch (e) { window.scrollTo(0, top); }
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function pad2(n) { return n < 10 ? '0' + n : '' + n; }

  function renderList() {
    if (!listEl) return;
    listEl.innerHTML = TREATMENTS.map(function(t, i){
      var cls = 'cc-list-btn' + (i === state.active ? ' is-active' : '');
      return '<button type="button" class="' + cls + '" data-cc-goto="' + i + '">'
        + '<span class="cc-list-num">' + pad2(i + 1) + '</span>'
        + '<span class="cc-list-body">'
        + '<span class="cc-list-name">' + esc(t.name) + '</span>'
        + '<span class="cc-list-meta">' + esc(t.meta) + '</span>'
        + '</span>'
        + '<svg class="cc-list-arrow" viewBox="0 0 18 18" fill="none"><path d="M4 9h10M10 4l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        + '</button>';
    }).join('');
  }

  function priceCard(label, p) {
    if (!p) return '';
    var amount = String(p.amount || '');
    var match = amount.match(/^(.+?)(\s*kr)$/);
    var amountHtml = match
      ? esc(match[1]) + '<span class="cc-price-unit">' + esc(match[2].trim()) + '</span>'
      : esc(amount);
    return '<div class="cc-price">'
      + '<div class="cc-price-label">' + esc(label) + '</div>'
      + '<div class="cc-price-amount">' + amountHtml + '</div>'
      + '<div class="cc-price-note">' + esc(p.note) + '</div>'
      + '</div>';
  }

  function renderCard() {
    if (!cardEl) return;
    var t = TREATMENTS[state.active];
    cardEl.innerHTML =
      '<div class="cc-card-eyebrow">' + esc(t.eyebrow) + '</div>'
      + '<h3 class="cc-card-title">' + esc(t.name) + '</h3>'
      + '<p class="cc-card-desc">' + esc(t.desc) + '</p>'
      + (t.link ? '<a class="cc-card-readmore" href="' + esc(t.link) + '">Läs mer <svg width="11" height="11" viewBox="0 0 11 11" fill="none"><path d="M1 5.5h9M6 1l4.5 4.5L6 10" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg></a>' : '')
      + '<div class="cc-prices">'
      + priceCard(CFG.label_kontant || 'Kontant', t.kontant)
      + priceCard(CFG.label_frisktandvard || 'Frisktandvård', t.frisktandvard)
      + priceCard(CFG.label_tandvardsstod || 'Tandvårdsstöd', t.tandvardsstod)
      + '</div>'
      + '<div class="cc-boka">'
      + '<div class="cc-boka-text">'
      + '<div class="cc-boka-eyebrow">' + esc(CFG.boka_eyebrow || 'Klar att boka?') + '</div>'
      + '<div class="cc-boka-name">' + esc(t.name) + '</div>'
      + '</div>'
      + '<div class="cc-boka-actions">'
      + '<a href="' + esc(CFG.cta_1_link || '') + '" class="cc-boka-btn is-ghost">' + esc(CFG.cta_1_text || '') + '</a>'
      + '<a href="' + esc(CFG.cta_2_link || '') + '" class="cc-boka-btn is-primary">' + esc(CFG.cta_2_text || '') + ' <svg width="11" height="11" viewBox="0 0 11 11" fill="none"><path d="M1 5.5h9M6 1l4.5 4.5L6 10" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg></a>'
      + '</div>'
      + '</div>'
      + '<p class="cc-disclaimer">' + esc(CFG.disclaimer || '') + '</p>';
  }

  function setActive(i) {
    if (i < 0 || i >= TREATMENTS.length) return;
    state.active = i;
    renderList();
    renderCard();
  }

  root.addEventListener('click', function(e){
    var goto = e.target.closest('[data-cc-goto]');
    if (goto) {
      setActive(parseInt(goto.getAttribute('data-cc-goto'), 10));
      requestAnimationFrame(centerWidget);
    }
  });

  renderList();
  renderCard();
})();
"""


def build_cost_calculator() -> dict:
    """Transparent prismatris för 9 behandlingar × 3 prismodeller (premium)."""

    treatments_data = [
        {"slug":"undersokning","name":"Undersökning + röntgen","meta":"Bastandvård · 30–45 min","eyebrow":"N° 01 · Undersökning",
         "desc":"Helhetskoll av tänder och tandkött, intraoral röntgen och en mjuk hygienistgenomgång. Det här är grunden — alla nya patienter börjar här.",
         "link":"/akut-tandvard/",
         "k_amount":"1 080 kr","k_note":"Pris före tandvårdsbidrag. Akut undersökning: 575 kr (nya patienter 440 kr).","k_rec":False,
         "f_amount":"Ej aktuellt","f_note":"Enkelbesök betalas direkt vid besöket.","f_rec":False,
         "s_amount":"Från ~780 kr","s_note":"Efter Allmänt tandvårdsbidrag (ATB 600 kr/år för 24–29 år & 65+, övriga 300 kr).","s_rec":True},
        {"slug":"tandsten","name":"Tandsten & hygienist","meta":"Tandhygienist · 45–60 min","eyebrow":"N° 02 · Hygienistbesök",
         "desc":"Skonsam borttagning av tandsten och beläggningar, polering och personliga råd om hemvård. Förebygger karies och tandköttsbesvär.",
         "link":"/tandsten-tandhygienist/",
         "k_amount":"Från 845 kr","k_note":"Pris varierar med tandstensmängd och behandlingsomfattning.","k_rec":True,
         "f_amount":"Vid större paket","f_note":"Vid omfattande hygienistpaket: räntefri delbetalning upp till 12 månader.","f_rec":False,
         "s_amount":"Via ATB","s_note":"Allmänt tandvårdsbidrag kan användas mot besöket.","s_rec":False},
        {"slug":"karies","name":"Lagning (karies)","meta":"Allmäntandvård · per yta","eyebrow":"N° 03 · Karies-behandling",
         "desc":"Modern komposit-lagning som matchas i färg mot din egen tand. Smärtfri behandling under lokalbedövning.",
         "link":"/karies-hal-i-tanden/",
         "k_amount":"Enligt prislista","k_note":"Vi följer Folktandvårdens prislista. Pris per tand-yta — varierar med lagningens storlek och placering.","k_rec":True,
         "f_amount":"Vid större paket","f_note":"Vid omfattande behandlingsplan: räntefri delbetalning upp till 12 månader.","f_rec":False,
         "s_amount":"Vid större behandling","s_note":"Högkostnadsskyddet (50 % efter 3 000 kr) träder in om du har mer tandvård samma 12-månadersperiod.","s_rec":False},
        {"slug":"akut","name":"Akut tandvärk","meta":"Akut · samma dag","eyebrow":"N° 04 · Akutbesök",
         "desc":"Du får tid samma dag vid akut värk eller skada. Vi gör smärtlindring direkt och planerar fortsatt behandling.",
         "link":"/akut-tandvard/",
         "k_amount":"575 kr","k_note":"Akut undersökning. Nya patienter: 440 kr. Eventuell behandling enligt Folktandvårdens prislista.","k_rec":True,
         "f_amount":"Vid större paket","f_note":"Vid större eftervård (rotbehandling, krona): räntefri delbetalning upp till 12 månader.","f_rec":False,
         "s_amount":"Vid större behandling","s_note":"Vid omfattande akutvård kan högkostnadsskyddet träda in.","s_rec":False},
        {"slug":"tandblekning","name":"Tandblekning","meta":"Estetik · klinikbehandling","eyebrow":"N° 05 · Estetisk tandvård",
         "desc":"Professionell klinikblekning med skonsamma metoder. Konsultation och undersökning krävs innan behandling.",
         "link":"/tandblekning/",
         "k_amount":"3 500 kr","k_note":"Klinikblekning. Konsultation: 300 kr. Föregås av undersökning för att säkerställa att tänderna är friska.","k_rec":True,
         "f_amount":"Räntefri delbetalning","f_note":"Räntefri delbetalning upp till 12 månader med Resurs Bank (godkänd kreditprövning).","f_rec":False,
         "s_amount":"Ingår ej","s_note":"Estetisk tandvård omfattas inte av statligt tandvårdsstöd.","s_rec":False},
        {"slug":"veneers","name":"Tandfasader (veneers)","meta":"Estetik · per tand","eyebrow":"N° 06 · Tandfasader",
         "desc":"Tunna porslinsfasader som transformerar ditt leende. Skräddarsys efter dina egna tänder i färg och form.",
         "link":"/tandfasader-veneers/",
         "k_amount":"Pris efter konsultation","k_note":"Skräddarsys per tand. Exakt pris ges efter konsultation och bedömning av antal tänder.","k_rec":True,
         "f_amount":"Räntefri delbetalning","f_note":"Räntefri delbetalning upp till 12 månader med Resurs Bank (godkänd kreditprövning).","f_rec":False,
         "s_amount":"Ingår ej","s_note":"Veneers räknas som estetisk tandvård utan statligt stöd.","s_rec":False},
        {"slug":"tandreglering","name":"Tandreglering (Invisalign)","meta":"Ortodonti · 6–18 mån","eyebrow":"N° 07 · Tandreglering",
         "desc":"Osynliga skenor som rätar dina tänder utan brackets. Resultatet kommer gradvis och syns knappt under behandlingen.",
         "link":"/tandreglering-stockholm/",
         "k_amount":"Pris efter konsultation","k_note":"Total kostnad beror på komplexitet och behandlingslängd — bedöms vid konsultation.","k_rec":False,
         "f_amount":"Räntefri delbetalning","f_note":"Räntefri delbetalning upp till 12 månader med Resurs Bank (godkänd kreditprövning).","f_rec":True,
         "s_amount":"Ingår ej för vuxna","s_note":"Statligt stöd finns endast för barn och unga i särskilda fall.","s_rec":False},
        {"slug":"tandvardsradsla","name":"Tandvårdsrädsla-paket","meta":"Trygghet · lustgas, samtal","eyebrow":"N° 08 · Tandvårdsrädsla",
         "desc":"Lugn miljö, extra tid och lustgas vid behov. Vi har också en psykoterapeut på kliniken för samtalsterapi.",
         "link":"/tandvardsradsla/",
         "k_amount":"Pris efter besök","k_note":"Behandlingspris enligt Folktandvårdens prislista. Samtalsterapi: 800 kr per 60 min. Lustgas och förlängd tid kan tillkomma.","k_rec":True,
         "f_amount":"Vid större paket","f_note":"Vid större behandlingsplan: räntefri delbetalning upp till 12 månader.","f_rec":False,
         "s_amount":"Vid F-tandvård","s_note":"Vid sjukdomstillstånd som ger rätt till F-tandvård betalar du sjukvårdsavgift istället (50–400 kr per besök).","s_rec":False},
        {"slug":"implantat","name":"Implantat","meta":"Kirurgi · per tand · 4–6 mån","eyebrow":"N° 09 · Implantat",
         "desc":"Komplett ersättning för förlorad tand — titanrot + krona. Funktion och utseende identiskt med en egen tand.",
         "link":"/implantat/",
         "k_amount":"Pris efter konsultation","k_note":"Konsultation och kontroll: 199 kr. Total kostnad bedöms efter CBCT-röntgen och behandlingsplan.","k_rec":False,
         "f_amount":"Räntefri delbetalning","f_note":"Räntefri delbetalning upp till 12 månader med Resurs Bank (godkänd kreditprövning).","f_rec":False,
         "s_amount":"Stöd via högkostnadsskyddet","s_note":"Implantat omfattas av statligt tandvårdsstöd — 50 % på 3 000–15 000 kr och 85 % över 15 000 kr av TLV:s referenspris.","s_rec":True},
    ]

    def treatment_json(i: int) -> str:
        return (
            '{'
            f'"slug":"{{{{t{i}_slug}}}}",'
            f'"name":"{{{{t{i}_name}}}}",'
            f'"meta":"{{{{t{i}_meta}}}}",'
            f'"eyebrow":"{{{{t{i}_eyebrow}}}}",'
            f'"desc":"{{{{t{i}_desc}}}}",'
            f'"link":"{{{{t{i}_link}}}}",'
            f'"kontant":{{"amount":"{{{{t{i}_k_amount}}}}","note":"{{{{t{i}_k_note}}}}","recommended":{{{{t{i}_k_rec}}}},"cta_text":"Boka","cta_link":"#tdl-booking-widget"}},'
            f'"frisktandvard":{{"amount":"{{{{t{i}_f_amount}}}}","note":"{{{{t{i}_f_note}}}}","recommended":{{{{t{i}_f_rec}}}},"cta_text":"Läs mer","cta_link":"/rantefritt/"}},'
            f'"tandvardsstod":{{"amount":"{{{{t{i}_s_amount}}}}","note":"{{{{t{i}_s_note}}}}","recommended":{{{{t{i}_s_rec}}}},"cta_text":"Läs om tandvårdsstöd","cta_link":"/om-oss/#tandvardsstod"}}'
            '}'
        )

    treatments_json = ",".join(treatment_json(i) for i in range(1, len(treatments_data) + 1))

    html = (
        '<section id="prisoversikt" class="cc-section">'
        '<style>' + COST_CALCULATOR_CSS + '</style>'
        '<div class="container-wide">'
        '<div class="cc-header">'
        '<div>'
        '<div class="cc-eyebrow-row">'
        '<span class="eyebrow">{{eyebrow}}</span>'
        '<span class="lumo-premium-badge" onclick="lumoToggle(this)">'
        '<span class="lumo-premium-dot"></span>'
        '<span class="lumo-mode-lbl">Premium</span>'
        + lumo_tooltip("prisoversikt") +
        '</span>'
        '</div>'
        '<h2 style="max-width:22ch;">{{heading}}</h2>'
        '</div>'
        '<p class="cc-header-meta">{{subtext}}</p>'
        '</div>'
        '<div data-cost-calc>'
        '<div class="cc-grid">'
        '<div>'
        '<div class="cc-list-label">{{list_label}}</div>'
        '<div class="cc-list" data-cc-list></div>'
        '</div>'
        '<div class="cc-card" data-cc-card></div>'
        '</div>'
        '<script type="application/json" data-cc-config>'
        '{"label_kontant":"{{label_kontant}}",'
        '"label_frisktandvard":"{{label_frisktandvard}}",'
        '"label_tandvardsstod":"{{label_tandvardsstod}}",'
        '"disclaimer":"{{disclaimer}}",'
        '"boka_eyebrow":"{{boka_eyebrow}}",'
        '"cta_1_text":"{{cta_1_text}}","cta_1_link":"{{cta_1_link}}",'
        '"cta_2_text":"{{cta_2_text}}","cta_2_link":"{{cta_2_link}}",'
        '"treatments":[' + treatments_json + ']'
        '}'
        '</script>'
        '</div>'
        '</div>'
        '<script>' + COST_CALCULATOR_JS + '</script>'
        '</section>'
    )

    schema = [
        {"name":"eyebrow","type":"text","label":"Etikett","default":"Prisöversikt"},
        {"name":"heading","type":"text","label":"Rubrik","default":"Transparenta priser — vi följer Folktandvårdens prislista."},
        {"name":"subtext","type":"textarea","label":"Undertext (höger)","default":"Jämför direktbetalning, räntefri delbetalning eller efter statligt tandvårdsstöd. Vi följer Folktandvårdens prislista och är knutna till Försäkringskassan — högkostnadsskydd och tandvårdsbidrag dras automatiskt vid besöket."},
        {"name":"list_label","type":"text","label":"Lista-rubrik","default":"Välj behandling"},
        {"name":"label_kontant","type":"text","label":"Kolumn 1 – etikett","default":"Direktbetalning"},
        {"name":"label_frisktandvard","type":"text","label":"Kolumn 2 – etikett","default":"Räntefri (12 mån)"},
        {"name":"label_tandvardsstod","type":"text","label":"Kolumn 3 – etikett","default":"Tandvårdsstöd"},
        {"name":"disclaimer","type":"textarea","label":"Disclaimer under priserna","default":"Vi följer Folktandvårdens prislista. Listade priser är riktvärden — exakt pris får du efter undersökning och behandlingsplan, utan kostnad och utan förpliktelser. Räntefri delbetalning sker via Resurs Bank (godkänd kreditprövning). Subventionsbelopp baseras på Tandvårds- och läkemedelsförmånsverkets (TLV) referenspriser."},
        {"name":"boka_eyebrow","type":"text","label":"Boka-block – eyebrow","default":"Klar att boka?"},
        {"name":"cta_1_text","type":"text","label":"CTA 1 text","default":"Ring kliniken"},
        {"name":"cta_1_link","type":"url","label":"CTA 1 länk","default":"tel:0812854555"},
        {"name":"cta_2_text","type":"text","label":"CTA 2 text","default":"Boka tid"},
        {"name":"cta_2_link","type":"url","label":"CTA 2 länk","default":"#tdl-booking-widget"},
    ]

    for i, t in enumerate(treatments_data, start=1):
        schema.extend([
            {"name":f"t{i}_slug","type":"text","label":f"Behandling {i} – slug","default":t["slug"]},
            {"name":f"t{i}_name","type":"text","label":f"Behandling {i} – namn","default":t["name"]},
            {"name":f"t{i}_meta","type":"text","label":f"Behandling {i} – meta","default":t["meta"]},
            {"name":f"t{i}_eyebrow","type":"text","label":f"Behandling {i} – eyebrow","default":t["eyebrow"]},
            {"name":f"t{i}_desc","type":"textarea","label":f"Behandling {i} – beskrivning","default":t["desc"]},
            {"name":f"t{i}_link","type":"url","label":f"Behandling {i} – läs mer-länk","default":t["link"]},
            {"name":f"t{i}_k_amount","type":"text","label":f"Behandling {i} – Direktbetalning pris","default":t["k_amount"]},
            {"name":f"t{i}_k_note","type":"textarea","label":f"Behandling {i} – Direktbetalning info","default":t["k_note"]},
            {"name":f"t{i}_k_rec","type":"text","label":f"Behandling {i} – Direktbetalning bäst värde (true/false)","default":"true" if t["k_rec"] else "false"},
            {"name":f"t{i}_f_amount","type":"text","label":f"Behandling {i} – Frisktandvård pris","default":t["f_amount"]},
            {"name":f"t{i}_f_note","type":"textarea","label":f"Behandling {i} – Frisktandvård info","default":t["f_note"]},
            {"name":f"t{i}_f_rec","type":"text","label":f"Behandling {i} – Frisktandvård bäst värde","default":"true" if t["f_rec"] else "false"},
            {"name":f"t{i}_s_amount","type":"text","label":f"Behandling {i} – Tandvårdsstöd pris","default":t["s_amount"]},
            {"name":f"t{i}_s_note","type":"textarea","label":f"Behandling {i} – Tandvårdsstöd info","default":t["s_note"]},
            {"name":f"t{i}_s_rec","type":"text","label":f"Behandling {i} – Tandvårdsstöd bäst värde","default":"true" if t["s_rec"] else "false"},
        ])

    return {
        "block_name": "lumo/cost-calculator",
        "title": "Prisöversikt (premium)",
        "html_template": _collapse(html),
        "schema": schema,
    }


def build_premium_tour_html() -> str:
    """Returnerar färdig HTML+CSS+JS-snippet för premium-tour popup.
    Injectas i site-footer html_template så den renderas på varje sida."""

    features = [
        {
            "key": "symptom-triage",
            "title": "Symptom-triage",
            "desc": "Interaktiv guide för akuta tandbesvär — användaren svarar på frågor och får skräddarsydd rekommendation.",
            "loc": "Akut tandvård",
            "href": "/akut-tandvard/#symptom-triage",
            "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v6M12 16v6M2 12h6M16 12h6"/><circle cx="12" cy="12" r="3"/></svg>',
        },
        {
            "key": "prisoversikt",
            "title": "Prisöversikt",
            "desc": "Patienten ser snabbt vad behandlingar kostar — direktbetalning, räntefri delbetalning eller efter tandvårdsstöd.",
            "loc": "Startsida",
            "href": "/#prisoversikt",
            "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h8M8 15h5"/></svg>',
        },
        {
            "key": "behandlingsstepper",
            "title": "Behandlingsstepper",
            "desc": "5-stegs interaktivt flöde som visar implantatresan från konsultation till färdig krona — klickbart per steg.",
            "loc": "Implantat",
            "href": "/implantat/#behandlingsstepper",
            "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/><path d="M7 12h3M14 12h3"/></svg>',
        },
        {
            "key": "trygghetsmatchning",
            "title": "Trygghetsmatchning",
            "desc": "Fyra frågor matchar patienter med tandvårdsrädsla mot rätt vårdpaket — lugnande medicin, steg-för-steg eller återstart.",
            "loc": "Tandvårdsrädsla",
            "href": "/tandvardsradsla/#trygghetsmatchning",
            "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
        },
        {
            "key": "prismatris",
            "title": "Transparent prismatris",
            "desc": "9 behandlingar × 3 prismodeller (direktbetalning, räntefri delbetalning, statligt stöd) — patienten ser exakt vad det kostar för deras situation.",
            "loc": "Priser",
            "href": "/implantat/#prismatris",
            "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1v22M17 5H9.5a3.5 3.5 0 1 0 0 7h5a3.5 3.5 0 1 1 0 7H6"/></svg>',
        },
    ]

    cards_html = "".join([
        f'<a class="lpt-card" href="{f["href"]}">'
        f'<div class="lpt-card-icon">{f["icon"]}</div>'
        f'<div class="lpt-card-body">'
        f'<div class="lpt-card-title-row">'
        f'<span class="lpt-card-title">{f["title"]}</span>'
        f'<span class="lpt-card-badge"><span class="lpt-card-badge-dot"></span>Premium</span>'
        f'</div>'
        f'<div class="lpt-card-desc">{f["desc"]}</div>'
        f'<div class="lpt-card-loc">{f["loc"]}</div>'
        f'</div>'
        f'<div class="lpt-card-arrow">'
        f'<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><path d="M1 5.5h9M6 1l4.5 4.5L6 10" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        f'</div>'
        f'{lpt_card_tooltip(f["key"])}'
        f'</a>'
        for f in features
    ])

    html = (
        '<style>' + PREMIUM_TOUR_CSS + '</style>'
        '<button id="lpt-trigger" class="lpt-trigger" type="button" aria-label="Visa premium-features">'
        '<svg class="lpt-trigger-star" viewBox="0 0 24 24"><path d="M12 2l2.39 7.36H22l-6.18 4.49L18.18 21 12 16.52 5.82 21l2.36-7.15L2 9.36h7.61L12 2z"/></svg>'
        'Premium-features'
        '</button>'
        '<div id="lpt-overlay" class="lpt-overlay" role="dialog" aria-modal="true" aria-labelledby="lpt-title">'
        '<div class="lpt-modal">'
        '<button class="lpt-close" data-lpt-close aria-label="Stäng">'
        '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
        '</button>'
        '<div class="lpt-header">'
        '<div class="lpt-eyebrow-row">'
        '<span class="lpt-eyebrow">Översikt</span>'
        '<span class="lpt-badge"><span class="lpt-badge-dot"></span>Premium</span>'
        '</div>'
        '<h2 id="lpt-title" class="lpt-title">Fem interaktiva premium-funktioner på sajten.</h2>'
        '<p class="lpt-lead">De ligger utspridda i flödet där de gör mest nytta — här är en genväg så du kan testa varje och avgöra vilka som ska aktiveras.</p>'
        '</div>'
        '<div class="lpt-list">' + cards_html + '</div>'
        '<div class="lpt-footer">'
        '<p class="lpt-footer-note">* Eventuella implementationskostnader kan tillkomma per funktion.</p>'
        '<button class="lpt-footer-btn" data-lpt-close>Stäng</button>'
        '</div>'
        '</div>'
        '</div>'
        '<script>' + PREMIUM_TOUR_JS + '</script>'
    )
    return " ".join(html.split())
