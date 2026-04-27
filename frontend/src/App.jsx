import PromptInput from "./components/PromptInput.jsx";
import OutputViewer from "./components/OutputViewer.jsx";

export default function App() {
  return (
    <div className="page">
      <header className="hero">
        <div className="hero-top">
          <p className="eyebrow">App Compiler</p>
          <span className="pill">Deterministic pipeline</span>
        </div>
        <h1>Generate validated app configs from plain language.</h1>
        <p className="subhead">Enter a prompt, then review the compiled JSON and validation status.</p>
      </header>
      <main className="stack">
        <PromptInput />
        <OutputViewer />
      </main>
    </div>
  );
}
