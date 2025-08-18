const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

let tasks=[];

app.get('/tasks',(req,res) => {
    res.json(tasks)
})

// app.get('/favicon.ico', (req, res) => res.status(204));

app.post('/tasks',(req,res) => {
    const task = {id: Date.now(), data: req.body.text, done: false};
    tasks.push(task);
    res.status(201).json(task);
});

app.patch('/tasks/:id', (req,res) => {
    const task = tasks.find(t=> t.id === parseInt(req.params.id))
    if (!task) {
        return res.status(404).json({message:'Task not found'})
    }
    task.done = !task.done;
    res.json(task);

})

app.delete('/tasks/:id',(req,res) => {
    const task = tasks.find(t => t.id === parseInt(req.params.id));
    if (!task) {
    return res.status(404).json({message: 'Task not found'});
    }
    tasks = tasks.filter(t=> t.id !== task.id);
    res.status(200).json({ message: 'Task deleted', id: taskId });
});

app.delete('/tasks',(req,res) => {
    tasks= [];
    res.status(200).json({message: 'All tasks deleted'});
});

app.use((req,res) => {
    return res.status(404).json({message: 'Page not found'})
})

app.listen(3001, () => console.log('Server running on port 3001'));

