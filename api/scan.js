// api/scan.js
// Excelligence Anti-Pattern Scanner
// Vercel serverless function
// Reads live ANT entries from /api/excelligence.json
// Calls Anthropic API with governed registry context
// Returns findings: id, name, severity, finding, governed_alternative, entry_url

export const config = { runtime: 'edge' };

const ANTHROPIC_API = 'https://api.anthropic.com/v1/messages';
const REGISTRY_URL = 'https://excelligence.dev/api/excelligence.json';

// ── Load ANT entries from live registry ──────────────
async function loadANTEntries() {
  const res = await fetch(REGISTRY_URL);
  if (!res.ok) throw new Error('Registry fetch failed');
  const data = await res.json();
  return data.entries.filter(e => e.type === 'ANT');
}

// ── Build system prompt with registry context ─────────
function buildSystemPrompt(antEntries) {
  const entryBlock = antEntries.map(e => `
ENTRY: ${e.id}
Name: ${e.name}
What it does: ${e.what_it_does}
Intent: ${e.intent}
Failure modes: ${e.failure_modes}
Governance notes: ${e.governance_notes}
Severity: ${e.difficulty_score <= 1 ? 'High' : e.difficulty_score <= 2 ? 'Medium' : 'Low'}
`.trim()).join('\n\n---\n\n');

  return `You are the Excelligence Anti-Pattern Scanner — a governed diagnostic tool powered by the Excelligence Excel knowledge graph.

Your job: analyze the user's input (a formula, a workbook description, or a problem they're experiencing) and identify which governed anti-patterns from the registry apply.

REGISTRY CONTEXT — ${antEntries.length} ANT entries:

${entryBlock}

RULES:
1. Only cite anti-patterns from the registry above. Never invent anti-patterns.
2. For each finding, cite the exact entry ID (e.g. ANT-0009).
3. Be specific about WHERE in the user's input the anti-pattern appears.
4. Always provide the governed alternative from the registry entry.
5. If no anti-patterns are detected, say so clearly and explain why the input looks governed.
6. Maximum 5 findings. If more apply, cite the most severe ones.
7. Be direct. No hedging. This is a diagnostic tool, not a chatbot.

COVERAGE NOTE: This scanner currently checks for ${antEntries.length} governed anti-patterns from the Excelligence registry. Registry coverage grows as new ANT entries are added.

OUTPUT FORMAT — respond with valid JSON only, no markdown, no explanation outside the JSON:
{
  "findings": [
    {
      "id": "ANT-XXXX",
      "name": "entry name",
      "severity": "High|Medium|Low",
      "finding": "specific description of the anti-pattern in the user's input",
      "governed_alternative": "what to do instead, from the registry",
      "governance_note": "key governance principle from the entry"
    }
  ],
  "clean": false,
  "coverage": ${antEntries.length},
  "summary": "one sentence summary of the diagnosis"
}

If no anti-patterns found:
{
  "findings": [],
  "clean": true,
  "coverage": ${antEntries.length},
  "summary": "one sentence explaining why this looks governed"
}`;
}

// ── Handler ───────────────────────────────────────────
export default async function handler(req) {
  // CORS
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': 'https://excelligence.dev',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers });
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers });
  }

  try {
    const body = await req.json();
    const input = (body.input || '').trim();

    if (!input) {
      return new Response(JSON.stringify({ error: 'No input provided' }), { status: 400, headers });
    }

    if (input.length > 3000) {
      return new Response(JSON.stringify({ error: 'Input too long. Max 3000 characters.' }), { status: 400, headers });
    }

    // Load live registry
    const antEntries = await loadANTEntries();
    const systemPrompt = buildSystemPrompt(antEntries);

    // Call Anthropic
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) throw new Error('API key not configured');

    const response = await fetch(ANTHROPIC_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1024,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: `Analyze this for Excel anti-patterns:\n\n${input}`
          }
        ]
      })
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`Anthropic API error: ${response.status}`);
    }

    const data = await response.json();
    const text = data.content?.[0]?.text || '{}';

    // Parse JSON response
    let result;
    try {
      result = JSON.parse(text);
    } catch {
      // Try to extract JSON if wrapped in anything
      const match = text.match(/\{[\s\S]*\}/);
      result = match ? JSON.parse(match[0]) : { error: 'Parse failed', raw: text };
    }

    return new Response(JSON.stringify(result), { status: 200, headers });

  } catch (err) {
    console.error('Scanner error:', err);
    return new Response(
      JSON.stringify({ error: err.message || 'Scanner failed' }),
      { status: 500, headers }
    );
  }
}
