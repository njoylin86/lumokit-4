# LumoKit — Refactoring Underlag

Identifierade svagheter och förbättringsområden. Används som underlag för `refactor/deterministic-pipeline`.

---

## 1. AI är en opålitlig fabriksarbetare

**Problem:** Fabriken bygger på att en språkmodell följer workflows konsekvent. AI har inget verkligt minne mellan sessioner, kan misstolka instruktioner, och kan producera subtilt fel HTML som ser rätt ut men har brister.

**Mål:** Flytta mer ansvar till deterministisk kod. AI ska fatta beslut — inte exekvera dem.

---

## 2. Kvalitetskontroll är cirkulär

**Problem:** Självgranskning via screenshot innebär att AI bedömer sitt eget arbete. Systematiska fel kan passera oupptäckta varje gång.

**Mål:** Separera design-steget från valideringssteget. Validering bör ha objektiva, kodade kriterier (t.ex. kontrastkrav, obligatoriska fält, HTML-validering).

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

## 6. WordPress-beroendet är en ouppackad flaskhals

**Problem:** All deploy går via REST API och SFTP till en specifik WP-instans. Om servern är nere, API:et ändras, eller ACF uppdateras och bryter schema-formatet — stannar hela fabriken utan tydlig felhantering.

**Mål:** Lägg till explicit felhantering och retry-logik i `push_to_wp.py`. Separera "build" (lokal) från "deploy" (nätverksberoende) tydligare så att en misslyckad deploy inte förstör en lyckad build.

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
