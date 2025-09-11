import { useEffect, useState } from "react"

export default function AlertsList() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("http://localhost:4000/alerts")
    .then(res => res.json())
    .then(data => {
      setAlerts(data.alerts)
      setLoading(false)
    })
    .catch(err => {
      console.log("Error fetching alerts:", err)
      setLoading(false)
    })
  },[])

  return (
    <div>
      {loading && <p>Loading alerts...</p>}
      {!loading && (
        <>
          <h2>🚨 Alerts</h2>
          <ul>
            {alerts.length === 0 ? (
              <li>No alerts yet ✅</li>
            ) : (
              alerts.map((alert, idx) => (
                <li key={idx} style={{ marginBottom: "1rem", padding: "0.5rem", border: "1px solid #ccc", borderRadius: "8px" }}>
                  <p><strong>Product:</strong> {alert.product_id}</p>
                  <div style={{ padding: "0.5rem", marginTop: "0.5rem", backgroundColor: "#f9f9f9", borderRadius: "6px" }}>
                    <p><strong>Alert ID:</strong> {alert.alert_id}</p>
                    <p><strong>Total Sales (last 5 min):</strong> {alert.total_sales_last_5m}</p>
                    <p><strong>Threshold:</strong> {alert.threshold}</p>
                    <p><strong>Timestamp:</strong> {new Date(alert.timestamp).toLocaleString()}</p>
                  </div>
                </li>
              ))
            )}
          </ul>
        </>
      )}
    </div>
  )
}
