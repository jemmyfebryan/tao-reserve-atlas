module.exports = {
  apps: [{
    name: 'atlas',
    script: 'run_bot.py',
    interpreter: 'python3',
    cwd: '/home/jemmy/projects/bittensor_project/taoreserve_bot',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/atlas-error.log',
    out_file: './logs/atlas-out.log',
    log_file: './logs/atlas-combined.log',
    time: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s'
  }]
};
