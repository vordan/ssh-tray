const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DATA_DIR = '/var/ssh-tray-sync';
const PORT = 9182;

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
	fs.mkdirSync(DATA_DIR, { recursive: true });
	console.log(`Created data directory: ${DATA_DIR}`);
}

const server = http.createServer((req, res) => {
	// Enable CORS for web requests
	res.setHeader('Access-Control-Allow-Origin', '*');
	res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
	res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-User-ID');
	
	// Handle OPTIONS preflight requests
	if (req.method === 'OPTIONS') {
		res.writeHead(200);
		res.end();
		return;
	}
	
	const timestamp = new Date().toISOString();
	console.log(`${timestamp} - ${req.method} ${req.url} from ${req.connection.remoteAddress}`);
	
	if (req.method === 'POST' && req.url === '/upload') {
		// Upload bookmark configuration
		const userId = req.headers['x-user-id'];
		if (!userId || !/^[a-f0-9]{16}$/.test(userId)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid or missing user ID');
			return;
		}
		
		let body = '';
		req.on('data', chunk => {
			body += chunk;
			// Prevent huge uploads (max 64KB for config files)
			if (body.length > 65536) {
				res.writeHead(413, {'Content-Type': 'text/plain'});
				res.end('File too large');
				req.destroy();
				return;
			}
		});
		
		req.on('end', () => {
			try {
				// Generate sync ID and create filename with user prefix
				const syncId = crypto.randomBytes(4).toString('hex');
				const fileName = `${userId}_${syncId}.txt`;
				const filePath = path.join(DATA_DIR, fileName);
				
				// Write the configuration file
				fs.writeFileSync(filePath, body, 'utf8');
				
				console.log(`Uploaded config for user ${userId}, sync ID: ${syncId}`);
				res.writeHead(200, {'Content-Type': 'text/plain'});
				res.end(syncId);
			} catch (error) {
				console.error('Upload error:', error);
				res.writeHead(500, {'Content-Type': 'text/plain'});
				res.end('Server error');
			}
		});
		
		req.on('error', (error) => {
			console.error('Request error:', error);
			res.writeHead(400);
			res.end('Bad request');
		});
	} 
	else if (req.method === 'GET' && req.url.startsWith('/download/')) {
		// Download bookmark configuration
		const urlParts = req.url.split('/');
		if (urlParts.length !== 3) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid URL format');
			return;
		}
		
		const syncId = urlParts[2];
		const userId = req.headers['x-user-id'];
		
		if (!userId || !/^[a-f0-9]{16}$/.test(userId)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid or missing user ID');
			return;
		}
		
		if (!/^[a-f0-9]{8}$/.test(syncId)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid sync ID format');
			return;
		}
		
		const fileName = `${userId}_${syncId}.txt`;
		const filePath = path.join(DATA_DIR, fileName);
		
		try {
			if (fs.existsSync(filePath)) {
				const content = fs.readFileSync(filePath, 'utf8');
				console.log(`Downloaded config for user ${userId}, sync ID: ${syncId}`);
				res.writeHead(200, {'Content-Type': 'text/plain'});
				res.end(content);
			} else {
				console.log(`Config not found for user ${userId}, sync ID: ${syncId}`);
				res.writeHead(404, {'Content-Type': 'text/plain'});
				res.end('Configuration not found');
			}
		} catch (error) {
			console.error('Download error:', error);
			res.writeHead(500, {'Content-Type': 'text/plain'});
			res.end('Server error');
		}
	}
	else if (req.method === 'GET' && req.url === '/status') {
		// Health check endpoint
		const fileCount = fs.readdirSync(DATA_DIR).length;
		res.writeHead(200, {'Content-Type': 'application/json'});
		res.end(JSON.stringify({
			status: 'online',
			port: PORT,
			files: fileCount,
			uptime: process.uptime()
		}));
	}
	else {
		res.writeHead(404, {'Content-Type': 'text/plain'});
		res.end('Endpoint not found');
	}
});

// Error handling
server.on('error', (error) => {
	console.error('Server error:', error);
});

// Graceful shutdown
process.on('SIGINT', () => {
	console.log('\nShutting down SSH Tray Sync service...');
	server.close(() => {
		console.log('Server closed.');
		process.exit(0);
	});
});

server.listen(PORT, '0.0.0.0', () => {
	console.log(`SSH Tray Sync service running on port ${PORT}`);
	console.log(`Data directory: ${DATA_DIR}`);
	console.log('Endpoints:');
	console.log('  POST /upload - Upload configuration');
	console.log('  GET /download/{syncId} - Download configuration');
	console.log('  GET /status - Service status');
});