const http = require('http');
const fs = require('fs');
const path = require('path');

const port = process.env.PORT || 3000;
const publicDir = path.join(__dirname, 'public');

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

function getBotReply(message) {
  const normalized = message.trim().toLowerCase();

  if (!normalized) {
    return 'Say something so I can help you.';
  }

  if (['hi', 'hello', 'hey', 'hola'].some((word) => normalized.includes(word))) {
    return 'Hello! I am Nova, your friendly chat bot. How can I help you today?';
  }

  if (normalized.includes('your name')) {
    return 'I am Nova, a simple chat bot built with Node.js.';
  }

  if (normalized.includes('time')) {
    return `The current time is ${new Date().toLocaleTimeString()}.`;
  }

  if (normalized.includes('date')) {
    return `Today is ${new Date().toLocaleDateString()}.`;
  }

  if (normalized.includes('weather')) {
    return 'I cannot check live weather right now, but I can help you look up a forecast.';
  }

  if (normalized.includes('help')) {
    return 'You can ask me about greetings, my name, the time, the date, weather, or just say thanks.';
  }

  if (normalized.includes('thanks') || normalized.includes('thank you')) {
    return 'You are very welcome!';
  }

  return `You said: "${message}". I am still learning, but I can help with greetings, my name, the time, the date, weather, or general questions.`;
}

function serveStaticFile(res, filePath) {
  const ext = path.extname(filePath);
  const contentType = mimeTypes[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }

    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/api/chat') {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
    });

    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        const reply = getBotReply(payload.message || '');
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ reply }));
      } catch (error) {
        res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ error: 'Invalid JSON payload' }));
      }
    });
    return;
  }

  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ status: 'ok' }));
  }

  const requestedPath = req.url === '/' ? '/index.html' : req.url;
  const safePath = path.normalize(requestedPath).replace(/^\/+/, '');
  const filePath = path.join(publicDir, safePath);

  if (!filePath.startsWith(publicDir)) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Forbidden');
    return;
  }

  serveStaticFile(res, filePath);
});

server.listen(port, () => {
  console.log(`Chat bot server running at http://localhost:${port}`);
});
