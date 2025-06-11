const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const DATA_DIR = '/var/ssh-tray-sync';
const PORT = 9182;
const MAX_VERSIONS = 5;

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
	fs.mkdirSync(DATA_DIR, { recursive: true });
	console.log(`Created data directory: ${DATA_DIR}`);
}

// Get system ID (username@hostname)
function getSystemId() {
	try {
		const username = execSync('whoami').toString().trim();
		const hostname = execSync('hostname').toString().trim();
		return `${username}@${hostname}`;
	} catch (error) {
		console.error('Error getting system ID:', error);
		return 'unknown-system';
	}
}

// Validate slug format (alphanumeric, hyphens, underscores, 3-32 chars)
function isValidSlug(slug) {
	return /^[a-zA-Z0-9-_]{3,32}$/.test(slug);
}

// Validate password (at least 4 chars, no spaces)
function isValidPassword(password) {
	return password && password.length >= 4 && !password.includes(' ');
}

// Get all versions of a configuration
function getConfigVersions(userId) {
	const versions = [];
	const files = fs.readdirSync(DATA_DIR);

	for (const file of files) {
		if (file.startsWith(`${userId}_`) && file.endsWith('.json')) {
			const parts = file.slice(0, -5).split('_');
			if (parts.length >= 3) {
				versions.push({
					file: file,
					timestamp: parts[2],
					systemId: parts[1]
				});
			}
		}
	}

	return versions.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
}

// Clean up old versions
function cleanupOldVersions(userId) {
	const versions = getConfigVersions(userId);
	if (versions.length > MAX_VERSIONS) {
		for (let i = MAX_VERSIONS; i < versions.length; i++) {
			const filePath = path.join(DATA_DIR, versions[i].file);
			try {
				fs.unlinkSync(filePath);
				console.log(`Deleted old version: ${versions[i].file}`);
			} catch (error) {
				console.error(`Error deleting old version ${versions[i].file}:`, error);
			}
		}
	}
}

const server = http.createServer((req, res) => {
	// Enable CORS for web requests
	res.setHeader('Access-Control-Allow-Origin', '*');
	res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
	res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-User-ID, X-Timestamp, X-Password, X-System-ID');

	// Handle OPTIONS preflight requests
	if (req.method === 'OPTIONS') {
		res.writeHead(200);
		res.end();
		return;
	}

	const timestamp = new Date().toISOString();
	console.log(`${timestamp} - ${req.method} ${req.url} from ${req.connection.remoteAddress}`);

	if (req.method === 'POST' && req.url === '/check-slug') {
		// Check if slug exists and validate password
		const userId = req.headers['x-user-id'];
		const password = req.headers['x-password'];

		if (!userId || !isValidSlug(userId)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid or missing user ID. Must be 3-32 characters, alphanumeric with hyphens and underscores.');
			return;
		}

		if (!password || !isValidPassword(password)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid password. Must be at least 4 characters long and contain no spaces.');
			return;
		}

		// Check all versions for password match
		const versions = getConfigVersions(userId);
		let exists = false;
		let authorized = false;

		for (const version of versions) {
			try {
				const data = JSON.parse(fs.readFileSync(path.join(DATA_DIR, version.file), 'utf8'));
				if (data.password === password) {
					exists = true;
					authorized = true;
					break;
				}
			} catch (error) {
				console.error(`Error reading version ${version.file}:`, error);
			}
		}

		res.writeHead(200, {'Content-Type': 'application/json'});
		res.end(JSON.stringify({
			exists,
			authorized
		}));
	}
	else if (req.method === 'POST' && req.url === '/upload') {
		// Upload bookmark configuration
		const userId = req.headers['x-user-id'];
		const clientTimestamp = req.headers['x-timestamp'];
		const password = req.headers['x-password'];
		const systemId = req.headers['x-system-id'] || getSystemId();

		if (!userId || !isValidSlug(userId)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid or missing user ID. Must be 3-32 characters, alphanumeric with hyphens and underscores.');
			return;
		}

		if (!password || !isValidPassword(password)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid password. Must be at least 4 characters long and contain no spaces.');
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
				const versions = getConfigVersions(userId);
				let serverData = null;

				// Find the latest version
				if (versions.length > 0) {
					try {
						serverData = JSON.parse(fs.readFileSync(path.join(DATA_DIR, versions[0].file), 'utf8'));
						// Verify password
						if (serverData.password !== password) {
							res.writeHead(401, {'Content-Type': 'text/plain'});
							res.end('Invalid password');
							return;
						}
					} catch (error) {
						console.error('Error reading latest version:', error);
					}
				}

				const clientData = JSON.parse(body);
				const serverTimestamp = serverData ? serverData.timestamp : null;

				// If timestamps differ, there's a conflict
				if (serverTimestamp && clientTimestamp && serverTimestamp !== clientTimestamp) {
					res.writeHead(409, {'Content-Type': 'application/json'});
					res.end(JSON.stringify({
						conflict: true,
						serverTimestamp,
						clientTimestamp,
						serverData: serverData.data,
						serverSystemId: versions[0].systemId
					}));
					return;
				}

				// Create new version with timestamp and system ID
				const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
				const fileName = `${userId}_${systemId}_${timestamp}.json`;
				const filePath = path.join(DATA_DIR, fileName);

				// Write the configuration file with timestamp and password
				const data = {
					timestamp: timestamp,
					password: password,
					data: clientData
				};

				fs.writeFileSync(filePath, JSON.stringify(data), 'utf8');

				// Clean up old versions
				cleanupOldVersions(userId);

				console.log(`Uploaded config for user ${userId} from ${systemId}`);
				res.writeHead(200, {'Content-Type': 'application/json'});
				res.end(JSON.stringify({ timestamp: data.timestamp }));
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
	else if (req.method === 'POST' && req.url === '/change-password') {
		// Change password for existing configuration
		const userId = req.headers['x-user-id'];
		const oldPassword = req.headers['x-password'];
		const newPassword = req.headers['x-new-password'];
		const systemId = req.headers['x-system-id'] || getSystemId();

		if (!userId || !isValidSlug(userId)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid or missing user ID');
			return;
		}

		if (!oldPassword || !isValidPassword(oldPassword) || !newPassword || !isValidPassword(newPassword)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid password format');
			return;
		}

		const versions = getConfigVersions(userId);
		if (versions.length === 0) {
			res.writeHead(404, {'Content-Type': 'text/plain'});
			res.end('Configuration not found');
			return;
		}

		try {
			// Verify old password
			const latestVersion = versions[0];
			const data = JSON.parse(fs.readFileSync(path.join(DATA_DIR, latestVersion.file), 'utf8'));
			if (data.password !== oldPassword) {
				res.writeHead(401, {'Content-Type': 'text/plain'});
				res.end('Invalid current password');
				return;
			}

			// Create new version with updated password
			const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
			const fileName = `${userId}_${systemId}_${timestamp}.json`;
			const filePath = path.join(DATA_DIR, fileName);

			data.password = newPassword;
			data.timestamp = timestamp;

			fs.writeFileSync(filePath, JSON.stringify(data), 'utf8');

			// Clean up old versions
			cleanupOldVersions(userId);

			res.writeHead(200, {'Content-Type': 'application/json'});
			res.end(JSON.stringify({ success: true }));
		} catch (error) {
			console.error('Password change error:', error);
			res.writeHead(500, {'Content-Type': 'text/plain'});
			res.end('Server error');
		}
	}
	else if (req.method === 'GET' && req.url.startsWith('/download/')) {
		// Download bookmark configuration
		const urlParts = req.url.split('/');
		if (urlParts.length !== 3) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid URL format');
			return;
		}

		const userId = urlParts[2];
		if (!isValidSlug(userId)) {
			res.writeHead(400, {'Content-Type': 'text/plain'});
			res.end('Invalid user ID format');
			return;
		}

		const versions = getConfigVersions(userId);
		if (versions.length === 0) {
			res.writeHead(404, {'Content-Type': 'text/plain'});
			res.end('Configuration not found');
			return;
		}

		try {
			const latestVersion = versions[0];
			const content = fs.readFileSync(path.join(DATA_DIR, latestVersion.file), 'utf8');
			console.log(`Downloaded config for user ${userId} from ${latestVersion.systemId}`);
			res.writeHead(200, {'Content-Type': 'application/json'});
			res.end(content);
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
	console.log('  POST /check-slug - Check if slug exists and validate password');
	console.log('  POST /upload - Upload configuration');
	console.log('  POST /change-password - Change configuration password');
	console.log('  GET /download/{userId} - Download configuration');
	console.log('  GET /status - Service status');
});
