# Agent Instructions: LumoKit Project

You are operating within the **LumoKit** project, an automated, AI-driven factory for generating high-performance WordPress websites. 

## The LumoKit Architecture ("Spår 3")
We use a "Data-Driven Component Engine" to balance creative freedom with strict content management. 
- **Separation of Concerns:** Design/Structure is decoupled from Content.
- **The Flow:** You (the AI) design components locally. You generate a JSON payload containing `html_template` (Tailwind + mustache syntax like `{{title}}`) and an ACF `schema`. 
- **The Execution:** Python scripts push this JSON to a custom WordPress plugin ("LumoKit Bridge"). The plugin dynamically registers ACF fields and a Gutenberg block. The client edits content via ACF; the site renders raw, blazing-fast HTML without heavy page builders.

## The WAT Framework (Workflows, Agents, Tools)
You operate strictly within the WAT framework. Probabilistic AI (you) handles reasoning and design. Deterministic code (tools) handles execution.

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/` (or referenced below in this document).
- Read these to understand exactly how to design a component, what Tailwind classes are allowed, and how the ACF schemas should be formatted.

**Layer 2: Agents (The Decision-Maker - YOU)**
- Read the client brief and the relevant workflows.
- Make creative decisions (e.g., generating Tailwind layouts).
- Generate the JSON structure. 
- You do NOT push to WordPress directly. You call the tools to do it.

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the heavy lifting.
- `tools/compile_tailwind.py`: Compiles the JIT Tailwind CSS locally.
- `tools/push_to_wp.py`: Handles authentication and safely pushes JSON payloads to the WordPress REST API.
- `tools/pull_from_wp.py`: Fetches the current state of a component.

## Core Rules of Operation

**1. The "Pull Before Push" Rule (CRITICAL)**
Never overwrite a component on WordPress without pulling its current state first. The client might have local changes or specific content in the database. Always use `tools/pull_from_wp.py` before modifying an existing structure.

**2. Local Tailwind Compilation**
WordPress does not compile Tailwind. If you add new utility classes to an `html_template`, you must instruct the system to run `tools/compile_tailwind.py` to generate the updated `style.css` before pushing to the server.

**3. Sanitize and Secure**
When generating `html_template` strings, never include `<script>`, `<iframe>`, or potentially malicious injection vectors. Keep it strictly to semantic HTML5 and Tailwind CSS.

**4. Check Tools First**
Before writing new scripts, check `tools/` to see if a utility already exists for your task.

## The Self-Improvement Loop
When a tool fails or the WP REST API returns an error (e.g., a 400 Bad Request due to an unsupported ACF field type):
1. Read the error trace carefully.
2. Fix the payload or the Python tool.
3. Verify the fix works.
4. Document the constraint so you don't make the same mistake twice.

## File Structure
```text
.tmp/             # Disposable processing files (generated JSON payloads before pushing)
tools/            # Python scripts for deterministic execution (API pushes, Tailwind JIT)
workflows/        # Markdown SOPs defining design rules and ACF mapping logic
wp-plugin/        # PHP code for the "LumoKit Bridge" installed on the WordPress host
.env              # API keys and WP credentials (NEVER store secrets in code)
```

## Mission Statement
Your job is to read instructions, design beautiful Tailwind components, output precise JSON schemas, call the right tools to compile/push, and build bulletproof WordPress sites. Keep it reliable and structured.

---

# Baseline Workflow: Design Hero Section
*(Use this as your standard operating procedure when asked to create a Hero Section)*

## Objective
Design a Hero Section for a WordPress site and generate the required LumoKit JSON payload. The component must be built with Tailwind CSS and map directly to ACF fields.

## Rules & Constraints
1. **Design System:** Use Tailwind CSS utility classes exclusively. Assume a standard Tailwind configuration.
2. **Responsiveness:** Always ensure the design looks good on mobile (`default`), tablet (`md:`), and desktop (`lg:`).
3. **Semantic HTML:** Use proper tags (`<section>`, `<h1>`, `<p>`, `<a>`).
4. **Data Binding:** Use mustache syntax (e.g., `{{headline}}`) for any dynamic content. Do NOT hardcode text or image URLs in the HTML.
5. **Allowed ACF Field Types:** Restrict the schema to `text`, `textarea`, `image`, and `url`.

## Output Format
Your output must be a valid JSON object saved to `.tmp/hero_payload.json`.

### JSON Structure Template:
```json
{
  "block_name": "lumo/hero-section",
  "title": "Hero Section",
  "html_template": "<section class=\"relative bg-gray-900 flex items-center justify-center min-h-screen\">\n  <div class=\"z-10 text-center px-4\">\n    <h1 class=\"text-5xl md:text-7xl font-bold text-white mb-6\">{{headline}}</h1>\n    <p class=\"text-lg md:text-2xl text-gray-300 mb-8 max-w-2xl mx-auto\">{{subheadline}}</p>\n    <a href=\"{{cta_link}}\" class=\"bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-full transition\">{{cta_text}}</a>\n  </div>\n  <div class=\"absolute inset-0 z-0\">\n    <img src=\"{{background_image}}\" alt=\"Background\" class=\"w-full h-full object-cover opacity-40\">\n  </div>\n</section>",
  "schema": [
    {
      "name": "headline",
      "type": "text",
      "label": "Huvudrubrik"
    },
    {
      "name": "subheadline",
      "type": "textarea",
      "label": "Underrubrik"
    },
    {
      "name": "cta_text",
      "type": "text",
      "label": "Knapptext"
    },
    {
      "name": "cta_link",
      "type": "url",
      "label": "Knapplänk"
    },
    {
      "name": "background_image",
      "type": "image",
      "label": "Bakgrundsbild"
    }
  ]
}
```

## Execution Steps for Agent
1. Analyze the client brief to determine the vibe/style of the hero section.
2. Draft the Tailwind HTML structure.
3. Replace all hardcoded content with `{{variable_names}}`.
4. Define the ACF schema mapping those variables.
5. Save the JSON to `.tmp/[client_name]_hero.json`.
6. Call the tool to compile Tailwind (if applicable) and the tool to push to WordPress.