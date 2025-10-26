import { useState, useEffect, useMemo } from 'react'
import './App.css'
import BarGraph from './components/BarGraph'

function App() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [sortOrder, setSortdOrder] = useState("asc")
  const [sortedData, setSortedData] =useState(false)

  const fetchData = () => {
    setLoading(true)
    fetch('http://127.0.0.1:8000/api/capacity')
    .then(res => res.json())
    .then(data => setData(data))
    .catch(err=> console.log(err))
    .finally(() =>setLoading(false))
    setSortedData(false)
  }

  useEffect(() =>{
    fetchData()
  },[])

  const sortData = useMemo(() => {
    if (!data) return
    if (!sortedData) return data
    const newData = [...data].sort((a,b) => 
      sortOrder === "asc" ? a.capacity - b.capacity : b.capacity - a.capacity)
    return newData
  },[data, sortOrder, sortedData])


  if (loading || !data) return <p>Loding</p>

  return (
    <div>
      <h2>Capcity Dashboard</h2>
      <button
      onClick={fetchData}
      disabled={loading}
      >
        {loading ? "Loading" : "Reload Data"}
      </button>
      <button
        onClick={() => {
          setSortedData(true)
          setSortdOrder((prev) => (prev === "asc" ? "desc" : "asc"))
        }}
      >
        Sort by capacity ({sortOrder === "asc" ? "arrow_up" : "arrow_down"})
      
      </button>
      <BarGraph data={sortData} />
    </div>
  )
}

export default App
