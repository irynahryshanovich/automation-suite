import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";

// Get API base URL from environment variable or use default
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const normalizeLogData = (logEntry) => {
  if (!logEntry || !logEntry.data) {
    return null;
  }

  if (typeof logEntry.data === "string") {
    try {
      return JSON.parse(logEntry.data);
    } catch (error) {
      return null;
    }
  }

  return logEntry.data;
};

const Dashboard = () => {
  // States
  const [isLoading, setIsLoading] = useState(false);
  const [cadence, setCadence] = useState(30);
  const [selectedCity, setSelectedCity] = useState("Seattle");
  const [availableCities, setAvailableCities] = useState([]);
  const [lastRunTime, setLastRunTime] = useState("Never");
  const [weatherData, setWeatherData] = useState(null);
  const [sportsData, setSportsData] = useState(null);
  const [logs, setLogs] = useState([]);
  const [targets, setTargets] = useState([]);

  // Fetch all required data
  const fetchData = useCallback(async () => {
    try {
      // Fetch logs
      const logsResponse = await axios.get(`${API_URL}/logs`);
      setLogs(logsResponse.data);

      // Fetch social targets state
      const stateResponse = await axios.get(`${API_URL}/state`);
      setTargets(stateResponse.data);

      // Fetch settings including available cities
      const settingsResponse = await axios.get(`${API_URL}/settings`);
      if (settingsResponse.data.available_cities) {
        setAvailableCities(settingsResponse.data.available_cities);
        setSelectedCity(settingsResponse.data.city);
      }

      // Find latest weather and sports data
      const weatherLog = logsResponse.data.find(
        (log) => log.source === "weather"
      );
      const sportsLog = logsResponse.data.find(
        (log) => log.source === "sports"
      );

      if (weatherLog) {
        setWeatherData(normalizeLogData(weatherLog));
        setLastRunTime(new Date(weatherLog.timestamp).toLocaleString());
      }

      if (sportsLog) {
        setSportsData(normalizeLogData(sportsLog));
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  }, []);

  // Fetch data on component mount
  useEffect(() => {
    fetchData();

    // Refresh data every minute
    const intervalId = setInterval(fetchData, 60000);
    return () => clearInterval(intervalId);
  }, [fetchData]);

  // Run automation manually
  const handleRunNow = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/run`, { city: selectedCity });

      // Update state with new data
      setWeatherData(response.data.weather);
      setSportsData(response.data.sports);
      setTargets(response.data.states);
      setLastRunTime(new Date().toLocaleString());

      // Refresh logs
      const logsResponse = await axios.get(`${API_URL}/logs`);
      setLogs(logsResponse.data);
    } catch (error) {
      console.error("Error running automation:", error);
      alert("Failed to run automation");
    } finally {
      setIsLoading(false);
    }
  };

  // Update cadence
  const handleUpdateCadence = async () => {
    if (cadence < 5 || cadence > 1440) {
      alert(
        "Please enter a valid cadence between 5 and 1440 minutes, which is 24 hours."
      );
      return;
    }

    try {
      const response = await axios.put(`${API_URL}/cadence?minutes=${cadence}`);
      if (response.data && response.data.message) {
        alert(response.data.message);
      }
    } catch (error) {
      console.error("Error updating cadence:", error);
      alert("Failed to update cadence");
    }
  };

  // Toggle target state
  const handleToggleTarget = async (target, currentStatus) => {
    const newStatus = currentStatus === "active" ? "paused" : "active";

    try {
      await axios.put(`${API_URL}/state/${target}`, { status: newStatus });

      // Update local state
      setTargets((prevTargets) =>
        prevTargets.map((t) =>
          t.target === target
            ? {
                ...t,
                status: newStatus,
                last_updated: new Date().toLocaleString(),
              }
            : t
        )
      );
    } catch (error) {
      console.error(`Error toggling state for ${target}:`, error);
      alert(`Failed to update ${target} state`);
    }
  };

  // Filter logs to show only actions
  const actionLogs = logs.filter((log) => log.action_taken !== "None");
  const handleClearLogs = async () => {
    if (window.confirm("Are you sure you want to clear all logs?")) {
      try {
        await axios.delete(`${API_URL}/logs`);
        // Refresh data
        fetchData();
        alert("Logs cleared successfully");
      } catch (error) {
        console.error("Error clearing logs:", error);
        alert("Failed to clear logs");
      }
    }
  };

  // Convert from YYYY-MM-DD to M/D/YYYY
  const formattedDate = sportsData?.events?.[0]?.dateEvent
    ? new Date(sportsData.events[0].dateEvent).toLocaleDateString("en-US", {
        month: "numeric",
        day: "numeric",
        year: "numeric",
      })
    : "N/A";

  return (
    <div>
      {/* Controls Section */}
      <div className="card">
        <h2>Controls</h2>
        <div>
          <div style={{ marginBottom: "1rem" }}>
            <label htmlFor="city">City: </label>
            <select
              id="city"
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              style={{
                margin: "0 0.5rem",
                padding: "0.25rem",
                minWidth: "150px",
              }}
            >
              {availableCities.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>
          </div>

          <div style={{ marginTop: "1rem" }}>
            <label htmlFor="cadence">Run every</label>
            <input
              type="number"
              id="cadence"
              min="5"
              max="1440"
              value={cadence}
              onChange={(e) => setCadence(parseInt(e.target.value))}
              style={{ margin: "0 0.5rem" }}
            />
            <span>minutes</span>
            <button
              className="btn secondary"
              onClick={handleUpdateCadence}
              style={{ marginLeft: "0.5rem" }}
            >
              Update
            </button>

            <p style={{ marginBottom: "1rem" }}>Last run: {lastRunTime}</p>

            <button
              className="btn primary"
              onClick={handleRunNow}
              disabled={isLoading}
            >
              {isLoading ? "Running..." : "Run Now"}
            </button>
          </div>
        </div>
      </div>

      {/* Social Targets */}
      <div className="card">
        <h2>Social Targets</h2>
        <div className="grid">
          {targets.map((target) => (
            <div
              key={target.target}
              style={{
                border: "1px solid #eee",
                padding: "1rem",
                borderRadius: "4px",
              }}
            >
              <h3>{target.target}</h3>
              <p>
                Status:
                <span className={`status ${target.status}`}>
                  {target.status}
                </span>
              </p>
              <p>
                Last updated: {new Date(target.last_updated).toLocaleString()}
              </p>
              <button
                className="btn primary"
                onClick={() => handleToggleTarget(target.target, target.status)}
              >
                {target.status === "active" ? "Pause" : "Activate"}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Weather Data */}
      <div className="card">
        <h2>Weather Data</h2>
        {weatherData ? (
          <div>
            <div style={{ textAlign: "center", marginBottom: "1rem" }}>
              <h3 style={{ fontSize: "2rem" }}>
                {weatherData.main?.temp_c && weatherData.main?.temp_f
                  ? `${weatherData.main.temp_c}°C / ${weatherData.main.temp_f}°F`
                  : "N/A"}
              </h3>
              <p>{weatherData.weather?.[0]?.main || "Unknown"}</p>
            </div>

            <div>
              <p>
                <strong>Location:</strong> {weatherData.name || "Unknown"}
              </p>
              {weatherData.wind && (
                <p>
                  <strong>Wind:</strong>{" "}
                  {weatherData.wind.speed
                    ? `${weatherData.wind.speed} m/s`
                    : "N/A"}
                </p>
              )}
              <p>
                <strong>Updated:</strong>{" "}
                {weatherData.dt
                  ? new Date(weatherData.dt * 1000).toLocaleTimeString()
                  : "Unknown"}
              </p>
            </div>
          </div>
        ) : (
          <p>No weather data available</p>
        )}
      </div>

      {/* Sports Data */}
      <div className="card">
        <h2>Sports Data</h2>
        {sportsData && sportsData.events && sportsData.events.length > 0 ? (
          <div>
            <h3 style={{ textAlign: "center", marginBottom: "1rem" }}>
              Match Result
            </h3>

            <div
              style={{
                display: "flex",
                justifyContent: "center",
                marginBottom: "1rem",
              }}
            >
              <div style={{ textAlign: "right", marginRight: "1rem" }}>
                <p style={{ fontSize: "1rem" }}>
                  Away:{" "}
                  <span style={{ fontWeight: "bold" }}>
                    {sportsData.events[0].strAwayTeam || "Away"}
                  </span>
                </p>
                <p style={{ fontWeight: "bold", fontSize: "1.5rem" }}>
                  {sportsData.events[0].intAwayScore || "0"}
                </p>
              </div>
              <div style={{ textAlign: "center", alignSelf: "center" }}>
                <p style={{ fontSize: "1.5rem", marginTop: "1.2rem" }}>-</p>
              </div>
              <div style={{ textAlign: "left", marginLeft: "1rem" }}>
                <p style={{ fontSize: "1rem" }}>
                  Home:{" "}
                  <span style={{ fontWeight: "bold" }}>
                    {sportsData.events[0].strHomeTeam || "Home"}
                  </span>
                </p>
                <p style={{ fontWeight: "bold", fontSize: "1.5rem" }}>
                  {sportsData.events[0].intHomeScore || "0"}
                </p>
              </div>
            </div>

            <div>
              <p>
                <strong>Date:</strong> {formattedDate}
              </p>
              <p>
                <strong>Status:</strong>{" "}
                {sportsData.events[0].strStatus || "N/A"}
              </p>
            </div>
          </div>
        ) : (
          <p>No sports data available</p>
        )}
      </div>

      {/* Automation Rules */}
      <div className="card">
        <h2>Automation Rules</h2>
        <div>
          <div style={{ marginBottom: "1rem" }}>
            <h3>Temperature-based Rule (Twitter)</h3>
            <ul>
              <li>If temperature exceeds 86°F, Twitter ads are paused</li>
              <li>If temperature is below 86°F, Twitter ads are activated</li>
            </ul>
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <h3>Sports-based Rule (Facebook)</h3>
            <ul>
              <li>If the home team wins a match, Facebook ads are activated</li>
              <li>If the home team loses or ties, Facebook ads are paused</li>
            </ul>
          </div>

          <div>
            <h3>Time-based Rule (Instagram)</h3>
            <ul>
              <li>
                During prime hours (8 AM - 8 PM), Instagram ads are activated
              </li>
              <li>During off-hours, Instagram ads are paused</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Action Logs */}
      <div className="card">
        <h2>
          Action Logs
          <button
            className="btn danger"
            onClick={handleClearLogs}
            style={{
              float: "right",
              fontSize: "0.8rem",
              padding: "0.25rem 0.5rem",
            }}
          >
            Clear Logs
          </button>
        </h2>
        {actionLogs.length > 0 ? (
          <div style={{ maxHeight: "400px", overflow: "auto" }}>
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Source</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {actionLogs.map((log, index) => (
                  <tr key={index}>
                    <td>{new Date(log.timestamp).toLocaleString()}</td>
                    <td>{log.source}</td>
                    <td>{log.action_taken}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No action logs available</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
