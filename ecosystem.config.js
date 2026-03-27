module.exports = {
	apps: [
		{
			name: "Glu-Stock-Engine",
			script: "main.py",
			cwd: "c:/Users/MP2NE93D/Documents/PLWEP/Glu-Stock",
			interpreter: "c:/Users/MP2NE93D/miniconda3/python.exe",
			cron_restart: "0 9 * * 1-5", // Every weekday at 09:00 AM
			autorestart: false, // Let cron manage the scheduled starts
			max_memory_restart: "500M", // Safe memory limit
			env: {
				PYTHONPATH: ".",
				PYTHONUNBUFFERED: "1",
				NODE_ENV: "production",
			},
			error_file: "logs/pm2_error.log",
			out_file: "logs/pm2_out.log",
			log_date_format: "YYYY-MM-DD HH:mm:ss",
		},
	],
};
