# LumoKit — Refactoring Underlag

Identifierade svagheter och förbättringsområden. Används som underlag för `refactor/deterministic-pipeline`.

---

## Vision: Fullständig Automation

**Långsiktigt mål:** LumoKit ska köras helt autonomt på en server — från brief till färdig WordPress-sajt — med minimal eller ingen mänsklig inblandning. Varje refactoring-beslut ska utvärderas mot detta mål: flyttar det systemet mot eller bort från självkörande drift?

Konkret innebär det:
- Deterministiska pipelines som kan triggas via API/webhook
- Felhantering som återhämtar sig utan manuell intervention
- Ingen manuell rensning, filhantering eller kommandokörning krävs av operatören
- AI fattar beslut, deterministisk kod exekverar dem — utan att en människa sitter mitt i loopen

---

## 1. AI är en opålitlig fabriksarbetare

**Problem:** Fabriken bygger på att en språkmodell följer workflows konsekvent. AI har inget verkligt minne mellan sessioner, kan misstolka instruktioner, och kan producera subtilt fel HTML som ser rätt ut men har brister.

**Mål:** Flytta mer ansvar till deterministisk kod. AI ska fatta beslut — inte exekvera dem.

---

## 2. Kvalitetskontroll är cirkulär ✅ ÅTGÄRDAT

**Lösning:** `tools/validate_bundle.py` körs automatiskt som pre-deploy-steg i `build_all.py`.
- **Fel (blockerar deploy):** mustache-variabel utan schema-fält, schema-fält utan mustache-variabel, `<script>`/`<iframe>`, saknade required-fält
- **Varningar (blockerar ej):** misstänkta låg-kontrast-kombinationer — flaggas men design-beslutet fattas av människa/AI
- `--strict`-flagga finns för den som vill att kontrast-varningar också blockerar

---

## 3. Workflows är läsbara men inte exekverbara

**Problem:** `workflows/*.md` är Markdown-instruktioner som AI:n tolkar fritt. Inget garanterar att varje build följer samma steg i samma ordning. Det finns inget CI-system som enforcar flödet.

**Mål:** Skapa en maskinläsbar pipeline-definition (t.ex. YAML eller JSON) som styr stegen deterministiskt. Markdown kan finnas kvar som dokumentation, men ska inte vara det enda som styr exekveringen.

---

## 4. `.tmp/`-livscykeln är manuell och opålitlig ✅ ÅTGÄRDAT

**Lösning:** Varje klient har nu en egen `clients/<name>/.tmp/`. CSS-kompilering skriver till klientens egna scratch-mapp automatiskt baserat på bundle-sökvägen. Ingen manuell rensning behövs.

---

## 5. En klient i taget — ingen parallellitet ✅ ÅTGÄRDAT

**Lösning:** `clients/<name>/.tmp/` är helt isolerade per klient. Alla tools (`compile_tailwind.py`, `build_design_html.py`, `upload_media.py`, `pull_from_wp.py`) stödjer nu `--client`-argument eller deriverar klientens scratch-dir från bundle-sökvägen.

---

## 6. WordPress-beroendet är en ouppackad flaskhals ✅ ÅTGÄRDAT

**Lösning:**
- `retry_post()` med exponential backoff (max 3 försök) i både `build_all.py` och `push_to_wp.py`
- `deploy_state.json` skrivs till `clients/<name>/.tmp/` efter varje komponent — håller reda på vad som lyckades/misslyckades
- `--resume`-flagga i `build_all.py` hoppar över komponenter med status `ok` i state-filen
- En kraschad halvdeploy kan återupptas exakt där den slutade

---

## 7. CLAUDE.md är okodad affärslogik

**Problem:** CLAUDE.md är kärnan i systemet men är inte versionerat på ett meningsfullt sätt, inte testat, och saknar edge case-specifikationer. Motstridiga regler fångas inte automatiskt.

**Mål:** Extrahera maskinvaliderbara regler ur CLAUDE.md till strukturerad form. CLAUDE.md ska vara ett index/översikt — inte den enda sanningskällan för exekveringslogik.

---

## Prioriteringsordning (förslag)

| Prio | Område | Värde | Komplexitet |
|------|--------|-------|-------------|
| 1 | `.tmp/`-isolering per klient (#5) | Hög | Låg |
| 2 | Obligatorisk rensning vid ny build (#4) | Hög | Låg |
| 3 | Felhantering i deploy-flöde (#6) | Hög | Medium |
| 4 | Maskinläsbar pipeline-definition (#3) | Medium | Hög |
| 5 | Objektiv valideringssteg (#2) | Medium | Hög |
| 6 | Extrahera regler ur CLAUDE.md (#7) | Medium | Hög |
