export default function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <header className="brand">
          <div className="brand-mark">🚚</div>
          <div>
            <h1 className="brand-name">Driftline</h1>
            <p className="brand-tagline">Weather-aware truck routing</p>
          </div>
        </header>
      </aside>

      <main className="map-area"></main>
    </div>
  )
}