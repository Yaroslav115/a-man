import "./styles.css";

export function App() {
  return (
    <main className="app-shell">
      <section className="welcome-card" aria-labelledby="demo-title">
        <p className="eyebrow">A-Man</p>
        <h1 id="demo-title">Voice Transcriber Demo</h1>
        <p className="summary">
          The demo frontend is running. Chat and voice widgets will be added in
          the next steps.
        </p>
        <span className="status">Frontend ready</span>
      </section>
    </main>
  );
}
