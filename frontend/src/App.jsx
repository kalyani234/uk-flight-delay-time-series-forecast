import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function App() {
  const [airports, setAirports] = useState([]);
  const [airport, setAirport] = useState("");
  const [horizon, setHorizon] = useState(1);

  const [loadingAirports, setLoadingAirports] = useState(true);
  const [loadingForecast, setLoadingForecast] = useState(false);

  const [error, setError] = useState("");
  const [forecast, setForecast] = useState(null);

  const [forecastPlotUrl, setForecastPlotUrl] = useState("");
  const [reportFigures, setReportFigures] = useState([]);
  const [loadingFigures, setLoadingFigures] = useState(true);

  const horizonOptions = useMemo(() => [1, 2, 3], []);

  // Load airports
  useEffect(() => {
    let alive = true;
    setLoadingAirports(true);

    fetch(`${API}/airports`)
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load airports (${r.status})`);
        return r.json();
      })
      .then((d) => {
        if (!alive) return;
        const list = d?.airports || [];
        setAirports(list);
        setAirport((prev) => prev || list[0] || "");
        setError("");
      })
      .catch((e) => {
        if (!alive) return;
        setError(e.message || "Failed to load airports");
      })
      .finally(() => {
        if (!alive) return;
        setLoadingAirports(false);
      });

    return () => {
      alive = false;
    };
  }, []);

  // Load report figures (saved PNGs)
  useEffect(() => {
    let alive = true;
    setLoadingFigures(true);

    fetch(`${API}/report-figures`)
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load report figures (${r.status})`);
        return r.json();
      })
      .then((d) => {
        if (!alive) return;
        setReportFigures(d?.files || []);
      })
      .catch(() => {
        if (!alive) return;
        setReportFigures([]);
      })
      .finally(() => {
        if (!alive) return;
        setLoadingFigures(false);
      });

    return () => {
      alive = false;
    };
  }, []);

  async function getForecast() {
    if (!airport) return;

    setError("");
    setForecast(null);
    setForecastPlotUrl("");
    setLoadingForecast(true);

    try {
      const url = `${API}/forecast?airport=${encodeURIComponent(airport)}&horizon=${encodeURIComponent(
        horizon
      )}`;

      const r = await fetch(url);
      if (!r.ok) {
        const txt = await r.text();
        throw new Error(txt || `Forecast failed (${r.status})`);
      }

      const data = await r.json();
      setForecast(data);

      // Cache-buster so the browser doesn’t reuse old PNG
      const plotUrl = `${API}/plots?airport=${encodeURIComponent(airport)}&horizon=${encodeURIComponent(
        horizon
      )}&_t=${Date.now()}`;

      setForecastPlotUrl(plotUrl);
    } catch (e) {
      setError(e.message || "Forecast failed");
    } finally {
      setLoadingForecast(false);
    }
  }

  return (
    <div className="container">
      <h1 className="title">✈️ UK Flight Delay Forecast</h1>

      {/* Controls */}
      <div className="card">
        <h3 className="sectionTitle">Forecast Controls</h3>

        <div className="grid2">
          <div>
            <label className="label">Airport</label>
            <select
              value={airport}
              onChange={(e) => setAirport(e.target.value)}
              disabled={loadingAirports}
            >
              {loadingAirports ? (
                <option>Loading airports…</option>
              ) : (
                airports.map((a) => (
                  <option value={a} key={a}>
                    {a}
                  </option>
                ))
              )}
            </select>
          </div>

          <div>
            <label className="label">Months ahead</label>
            <select value={horizon} onChange={(e) => setHorizon(Number(e.target.value))}>
              {horizonOptions.map((n) => (
                <option value={n} key={n}>
                  {n}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button onClick={getForecast} disabled={!airport || loadingForecast}>
          {loadingForecast ? "Fetching…" : "Get Forecast"}
        </button>

        {error && <div className="noticeError">{error}</div>}

        {forecast && (
          <div className="resultCard" style={{ marginTop: 14 }}>
            <h3 className="sectionTitle">Forecast Result</h3>

            <div className="kv">
              <div className="k">Airport</div>
              <div className="v">{forecast.airport}</div>

              <div className="k">Last observed month</div>
              <div className="v">{forecast.last_observed_month}</div>

              <div className="k">Forecast month</div>
              <div className="v">{forecast.forecast_month}</div>

              <div className="k">Horizon</div>
              <div className="v">{forecast.horizon}</div>

              <div className="k">Predicted avg delay</div>
              <div className="v">{forecast.predicted_avg_delay_minutes} minutes</div>

              {typeof forecast.lower_95 !== "undefined" &&
                typeof forecast.upper_95 !== "undefined" && (
                  <>
                    <div className="k">95% CI</div>
                    <div className="v">
                      {forecast.lower_95} – {forecast.upper_95} minutes
                    </div>
                  </>
                )}

              {forecast.model_used && (
                <>
                  <div className="k">Model</div>
                  <div className="v">{forecast.model_used}</div>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Forecast Plot */}
      {forecastPlotUrl && (
        <div className="card">
          <h3 className="sectionTitle">Forecast Chart</h3>
          <img className="img" src={forecastPlotUrl} alt="Forecast plot" />
          <div className="footer" style={{ marginTop: 10 }}>
            Generated from <code>/plots</code>
          </div>
        </div>
      )}

      {/* Saved Report Figures */}
      <div className="card">
        <h3 className="sectionTitle">Project Report Charts</h3>

        {loadingFigures ? (
          <div className="footer">Loading report figures…</div>
        ) : reportFigures.length === 0 ? (
          <div className="footer">
            No saved figures found. Run: <code>python -m src.visualization.generate_all</code>
          </div>
        ) : (
          <div className="figGrid">
            {reportFigures.map((f) => (
              <figure className="figure" key={f}>
                <figcaption className="caption">{f}</figcaption>
                <img
                  className="img"
                  src={`${API}/reports/figures/${encodeURIComponent(f)}`}
                  alt={f}
                  loading="lazy"
                />
              </figure>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
