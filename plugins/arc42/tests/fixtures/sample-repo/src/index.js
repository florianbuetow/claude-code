const express = require('express');
const taskRouter = require('./handlers/tasks');

const app = express();
app.use(express.json());
app.use('/tasks', taskRouter);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`task-api listening on port ${PORT}`);
});

module.exports = app;
