import { useEffect, useState } from "react";

export default function OutputViewer() {
  const [payload, setPayload] = useState(null);
  const [activeTab, setActiveTab] = useState("Config");

  const tabs = ["Intent", "Design", "Config", "Validation", "Execution"];

  useEffect(() => {
    function handleOutput(event) {
      setPayload(event.detail);
    }

    window.addEventListener("compiler:output", handleOutput);
    return () => window.removeEventListener("compiler:output", handleOutput);
  }, []);

  return (
    <section className="panel output">
      <div className="panel-header">
        <h2>Output</h2>
        <span className="status">JSON</span>
      </div>
      <div className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            className={tab === activeTab ? "tab active" : "tab"}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>
      <pre>
        {payload
          ? JSON.stringify(
              {
                Intent: payload.intent,
                Design: payload.design,
                Config: payload.config,
                Validation: payload.validation,
                Execution: payload.execution
              }[activeTab],
              null,
              2
            )
          : "No output yet."}
      </pre>
      <div className="assumptions">
        <h3>Assumptions</h3>
        {payload?.assumptions?.length ? (
          <ul>
            {payload.assumptions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="muted">No assumptions recorded.</p>
        )}
      </div>
      <div className="questions">
        <h3>Clarifying Questions</h3>
        {payload?.clarifying_questions?.length ? (
          <ul>
            {payload.clarifying_questions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="muted">No questions at this time.</p>
        )}
      </div>
      <div className="execution">
        <h3>Execution Summary</h3>
        {payload?.execution ? (
          <div className="exec-grid">
            <div>
              <p className="label">Executed</p>
              <p>{payload.execution.executed ? "Yes" : "No"}</p>
            </div>
            <div>
              <p className="label">Tables</p>
              <p>{payload.execution.tables_created.length}</p>
            </div>
            <div>
              <p className="label">Errors</p>
              <p>{payload.execution.errors.length}</p>
            </div>
          </div>
        ) : (
          <p className="muted">No execution report yet.</p>
        )}
        {payload?.execution?.errors?.length ? (
          <ul>
            {payload.execution.errors.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : null}
      </div>
      <div className="preview">
        <h3>UI Preview</h3>
        <div className="preview-grid">
          {payload?.config?.ui?.pages?.length ? (
            payload.config.ui.pages.map((page) => (
              <div className="preview-card" key={page.route}>
                <p className="preview-title">{page.name}</p>
                <p className="preview-meta">Route: {page.route}</p>
                <p className="preview-meta">Components: {page.components.length}</p>
                <p className="preview-meta">
                  Roles: {page.roles_allowed.length ? page.roles_allowed.join(", ") : "Public"}
                </p>
              </div>
            ))
          ) : (
            <p className="muted">No UI pages generated yet.</p>
          )}
        </div>
      </div>
    </section>
  );
}
