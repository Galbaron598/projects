import { useEffect, useState } from "react";


function App() {
  const [tasks, setTasks] = useState([])
  const [text, setText] = useState('')

  useEffect(() => {
    fetch(`http://localhost:3001/tasks`, {
      method: 'GET',
      headers: {'Content-Type': 'application/json'},
    })
    .then(res => res.json())
    .then(data => setTasks(data))
    .catch(err => console.log(err))
  },[])

  const addTask = () => {
    fetch(`http://localhost:3001/tasks`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    })
    .then(res => res.json())
    .then(data => {
      setTasks([...tasks, data])
      setText('')
    })
    .catch(err => console.log(err))
  }

  const deleteAllTasks = () => {
    fetch(`http://localhost:3001/tasks`, {
      method: 'DELETE',
      headers: {'Content-Type': 'application/json'},
    })
    .then(res => res.json())
    .then(data => {
      setTasks([])
    })
    .catch(err => console.log(err))
  }

  const changeStatus = (id) => {
    fetch(`http://localhost:3001/tasks/${id}`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
    })
    .then(res => res.json())
    .then(updatedTask => {
      setTasks(tasks.map(task => task.id === id ? updatedTask : task))
        })
    .catch(err => console.log(err))
  }

    const deleteTask = (id) => {
      fetch(`http://localhost:3001/tasks/${id}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'},
      })
      .then(res => res.json())
      .then(() => {
        setTasks(tasks.filter(task => task.id !== id))
      })
      .catch(err => console.log(err))
    }
    
  return (
    <div>
      <h1>Tasks</h1>
      <form>
        <input type="text" placeholder="Add a task" onChange ={(e) => setText(e.target.value)} />
        <button type="submit"
        onClick ={() => addTask()}>Add Task</button>
      </form>
      <button
        onClick = {() => deleteAllTasks()}
        >Delete All Tasks
      </button>
      <table>
        <thead>
          <tr>
            <th>Id</th>
            <th>Data</th>
            <th>Status</th>
          </tr>
        </thead>
          <tbody> 
            {tasks.map((task) => (
            <tr key= {task.id}>
              <td> {task.id}</td>
              <td> {task.data}</td>
              <td>
                <button
                onClick = {() => changeStatus(task.id)}
                >{task.done ? 'Done' : 'Undone'}
                </button>
                {task.done ? 'Done' : 'Undone'}
              </td>
              <td>
                <button
                onClick = { () => deleteTask(task.id)}
                >delete Task
                </button>
              </td>
            </tr>
          ))}
          </tbody>
      </table>
    </div>
  )
}

export default App;