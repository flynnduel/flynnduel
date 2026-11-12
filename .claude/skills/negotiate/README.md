# Negotiation Skill — AI-Powered Negotiation Assistant

> Prepare, analyze, practice, and evaluate negotiations using the 7 Elements methodology.

Built by [Club de Negociación](https://clubdenegociacion.com) — the first live negotiation practice platform with AI analysis.

## What It Does

This skill turns your AI coding assistant into a negotiation coach. It provides six commands:

| Command | Description |
|---------|-------------|
| `/negotiate:prepare` | Prepare for a negotiation with a structured 7 Elements analysis |
| `/negotiate:analyze` | Analyze a negotiation transcript or email thread |
| `/negotiate:options` | Generate creative options for mutual gain |
| `/negotiate:maan` | Calculate your MAAN (Best Alternative to a Negotiated Agreement) |
| `/negotiate:practice` | Practice negotiating with an AI counterpart |
| `/negotiate:evaluate` | Evaluate a proposed agreement against the 7 Elements |

### Methodology

- **Collaborative, interest-based negotiation** (not competitive/positional)
- **7 Elements framework**: Interests, MAAN, Options, Legitimacy, Commitments, Communication, Relationship
- **Guiding principle**: "Ser incondicionalmente constructivo" — be unconditionally constructive
- **Bilingual**: Works in both English and Spanish (detects language from your input)

## Installation

### Claude Code

```bash
# Global install (available in all projects)
npx @clubdenegociacion/negotiation-skill --global

# Or clone manually
git clone https://github.com/clubdenegociacion/negotiation-skill.git
cp -r negotiation-skill ~/.claude/skills/negotiate/
```

### Cursor

Add to your `.cursor/skills/` directory:

```bash
mkdir -p .cursor/skills/negotiate
cp -r negotiation-skill/* .cursor/skills/negotiate/
```

### Gemini CLI

```bash
mkdir -p ~/.gemini/skills/negotiate
cp -r negotiation-skill/* ~/.gemini/skills/negotiate/
```

## Usage Examples

### Prepare for a negotiation

```
/negotiate:prepare

I need to negotiate a software development contract with a new client.
They want a custom CRM, budget is around $50k, timeline is 3 months.
My company typically charges $80k for this scope.
```

### Analyze a transcript

```
/negotiate:analyze

[paste email thread or meeting transcript]
```

### Generate options

```
/negotiate:options

We're negotiating a partnership where we provide technology
and they provide distribution. They want exclusivity,
we want flexibility. Both want revenue growth.
```

### Calculate your MAAN

```
/negotiate:maan

I'm negotiating my salary at a new company.
They offered $120k. I currently make $110k.
```

### Practice a negotiation

```
/negotiate:practice

I need to practice asking my landlord for a rent reduction.
Current rent is $2,500/month. Market rate for similar
apartments is $2,200. My lease expires in 2 months.
```

### Evaluate a deal

```
/negotiate:evaluate

We're being offered: 3-year contract, $45k/year,
exclusive in our region, 90-day termination clause,
annual price review tied to CPI.
```

## Included References

The skill includes deep reference materials:

- `references/seven-elements.md` — Comprehensive guide to the 7 Elements (2000+ words)
- `references/maan-guide.md` — MAAN calculation with correct/incorrect examples
- `references/collaborative-framework.md` — Why collaborative beats competitive
- `assets/preparation-template.md` — Ready-to-use preparation template

## About Club de Negociación

[Club de Negociación](https://clubdenegociacion.com) is the first online platform for live negotiation practice. Members negotiate structured cases with real professionals via video, receive AI-powered analysis of their performance across the 7 Elements, and participate in weekly expert debriefs.

- Live practice with real humans (not simulations)
- AI-powered analysis with 7 Elements scoring
- Weekly sessions from $0/month
- 100% in Spanish

**Contact**: contacto@clubdenegociacion.com | [WhatsApp +595 974 205000](https://wa.me/595974205000)

## License

MIT License

Copyright (c) 2026 Club de Negociación — Consultoría Francisco Gutiérrez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
