const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

app.use(bodyParser.json());
app.use(express.static('public'));

// Dummy session for login
let isLoggedIn = false;
let userData = {}; // Mock user data (you can use a real database here)

// Load data from a JSON file (or a database)
function loadData() {
  try {
    return JSON.parse(fs.readFileSync(path.join(__dirname, 'data.json')));
  } catch (err) {
    return {};
  }
}

// Save data to a JSON file (or a database)
function saveData(data) {
  fs.writeFileSync(path.join(__dirname, 'data.json'), JSON.stringify(data, null, 2));
}

// Endpoint for user login
app.post('/login', (req, res) => {
  const { username, password } = req.body;

  // Dummy login check
  if (username === 'user' && password === 'password') {
    isLoggedIn = true;
    return res.json({ message: 'Logged in successfully' });
  }

  return res.status(401).json({ message: 'Invalid credentials' });
});

// Endpoint for user logout
app.post('/logout', (req, res) => {
  isLoggedIn = false;
  res.json({ message: 'Logged out successfully' });
});

// Endpoint to get diet data
app.get('/diet-data', (req, res) => {
  if (!isLoggedIn) return res.status(403).json({ message: 'You must be logged in' });

  const data = loadData();
  res.json(data);
});

// Endpoint to add diet data
app.post('/diet-data', (req, res) => {
  if (!isLoggedIn) return res.status(403).json({ message: 'You must be logged in' });

  const { date, food, calories, notes } = req.body;

  const data = loadData();
  if (!data[date]) {
    data[date] = { food, calories, notes };
  }

  saveData(data);
  res.json({ message: 'Diet data added successfully' });
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
