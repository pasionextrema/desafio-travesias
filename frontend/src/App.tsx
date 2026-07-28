function App() {
  const levels = [
    { name: "Explorador", color: "#4CAF50", gem: "Jade" },
    { name: "Navegante", color: "#2196F3", gem: "Zafiro" },
    { name: "Constructor", color: "#9C27B0", gem: "Amatista" },
    { name: "Estrella", color: "#FFD700", gem: "Diamante" },
  ]

  return (
    <div className="app">
      <header className="header">
        <h1>Desafio de Travesias</h1>
        <p className="subtitle">Plataforma gamificada de trivias educativas</p>
      </header>

      <main className="main">
        <section className="status-card">
          <h2>Fase 0 - Infraestructura</h2>
          <div className="status-grid">
            <div className="status-item">
              <span className="indicator green"></span>
              <span>Backend: FastAPI</span>
            </div>
            <div className="status-item">
              <span className="indicator green"></span>
              <span>Frontend: React + TypeScript</span>
            </div>
            <div className="status-item">
              <span className="indicator green"></span>
              <span>Base de Datos: PostgreSQL</span>
            </div>
            <div className="status-item">
              <span className="indicator yellow"></span>
              <span>Cache: Redis</span>
            </div>
            <div className="status-item">
              <span className="indicator yellow"></span>
              <span>Despliegue: Railway</span>
            </div>
          </div>
        </section>

        <section className="levels-section">
          <h2>Niveles de Participacion</h2>
          <div className="levels-grid">
            {levels.map((level) => (
              <div
                key={level.name}
                className="level-card"
                style={{ borderColor: level.color }}
              >
                <span
                  className="gem"
                  style={{ color: level.color, fontSize: "2rem" }}
                >
                  &#9670;
                </span>
                <h3 style={{ color: level.color }}>{level.name}</h3>
                <p>Gema {level.gem}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>Pasion Extrema &copy; 2026</p>
      </footer>
    </div>
  )
}

export default App
