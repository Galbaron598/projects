import { useEffect, useState } from "react"

export default function AlertsList() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("http://localhost:4000/alerts")
    .then(res => res.json())
    .then(data => setAlerts(data.alerts))
    .catch(err => console.log("Error fetching alerts:", err))
    setLoading(False)
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
                <li key={idx}>
                  <p><strong>Product:</strong> {alert.product_id}</p>
                  <p><strong>Message:</strong> {alert.message}</p>
                  <p>{new Date(alert.timestamp * 1000).toLocaleString()}</p>
                </li>
              ))
            )}
          </ul>
        </>
      )}
    </div>
  )
}
