import { useState } from "react";

const DEFAULT_PROMPT =
  "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.";

export default function PromptInput() {
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const [status, setStatus] = useState("Idle");
  const [result, setResult] = useState(null);

  async function handleGenerate() {
    setStatus("Compiling...");
    const response = await fetch("https://app-compiler.onrender.com/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });
    const data = await response.json();
    setResult(data);
    setStatus("Done");
    window.dispatchEvent(new CustomEvent("compiler:output", { detail: data }));
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Prompt</h2>
        <span className="status">{status}</span>
      </div>
      <textarea
        value={prompt}
        className="input"
        placeholder="Describe the app you want to generate..."
        onChange={(event) => setPrompt(event.target.value)}
        rows={12}
      />
      <button className="primary" onClick={handleGenerate}>Generate</button>
      {result && (
        <div className="quick-stats">
          <div>
            <p className="label">Valid</p>
            <p>{result.validation.valid ? "Yes" : "No"}</p>
          </div>
          <div>
            <p className="label">Repairs</p>
            <p>{result.validation.repairs.length}</p>
          </div>
          <div>
            <p className="label">Retries</p>
            <p>{result.validation.retries}</p>
          </div>
        </div>
      )}
    </section>
  );
}
