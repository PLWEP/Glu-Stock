module.exports = {
	apps: [
		{
			name: "glu-stock-engine",
			script: "scheduler.py",
			args: "--loop",
			// interpreter: "c:/Users/MP2NE93D/miniconda3/python.exe", // Windows PATH
			// interpreter: "python", // Standard for Termux/Linux
			interpreter: "./glustock_venv/bin/python",
			instances: 1,
			autorestart: true,
			watch: false,
			max_memory_restart: "400M", // Guard against memory leaks in Termux
			exp_backoff_restart_delay: 5000, // Wait 5s before restart on failure
			env: {
				PYTHONUNBUFFERED: "1",
				TZ: "Asia/Jakarta",
			},
		},
		{
			name: "glu-stock-bot",
			script: "telegram_bot.py",
			// interpreter: "python",
			interpreter: "./glustock_venv/bin/python",
			autorestart: true,
			max_memory_restart: "200M",
			env: {
				PYTHONUNBUFFERED: "1",
			},
		},
	],
};
