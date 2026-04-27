# =====================================================================================
# Day 4 — Paramiko: SSH & SFTP Operations in Python
# =====================================================================================
# Paramiko is a third-party Python library for SSH2 protocol (remote server communication).
# It enables two key DevOps capabilities:
#   1. SSH  — Execute shell commands on remote servers programmatically.
#   2. SFTP — Securely transfer files (push/pull) to/from remote servers.
# Install it via: pip install paramiko
# =====================================================================================

import paramiko  # Import the paramiko library for SSH/SFTP operations

# =====================================================================================
# SECTION 1: SSH — REMOTE COMMAND EXECUTION
# =====================================================================================
# Run shell commands on remote servers without spawning subprocess calls.
# This is commonly used in DevOps for restarting services, checking status,
# deploying code, and running maintenance tasks on remote machines.

# paramiko.SSHClient() — Creates an SSH client instance.
# This object manages the SSH connection lifecycle (connect → execute → close).
client = paramiko.SSHClient()

# set_missing_host_key_policy() — Defines how to handle unknown SSH host keys.
# paramiko.AutoAddPolicy() — Automatically adds the server's host key without prompting.
# WARNING: In production, use paramiko.RejectPolicy() or load known hosts with
# client.load_host_keys() or client.load_system_host_keys() for security.
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# client.connect() — Establishes an SSH connection to the remote server.
# Parameters:
#   hostname     — IP address or domain of the remote server ('10.0.0.5')
#   username     — SSH login username ('devops')
#   key_filename — Path to the private key file for key-based authentication ('id_rsa')
# You can also use password='...' for password-based auth (less secure).
client.connect('10.0.0.5', username='devops', key_filename='id_rsa')

# client.exec_command() — Executes a command on the remote server.
# Returns three file-like objects:
#   stdin  — Standard input stream (for sending input to the command)
#   stdout — Standard output stream (command's normal output)
#   stderr — Standard error stream (command's error output)
stdin, stdout, stderr = client.exec_command('systemctl restart nginx')

# stdout.read() — Reads the command's output as bytes.
# .decode() — Converts bytes to a UTF-8 string for readable printing.
print(stdout.read().decode())

# client.close() — Closes the SSH connection and frees resources.
# Always close connections to avoid resource leaks.
client.close()

# =====================================================================================
# SECTION 2: SFTP — SECURE FILE TRANSFER
# =====================================================================================
# Push/pull configuration files, logs, artifacts, backups.
# SFTP (SSH File Transfer Protocol) provides encrypted file transfers over SSH.
# Useful for deploying config files, pulling logs, and syncing backups.

# paramiko.Transport() — Creates a low-level transport layer for SSH communication.
# Takes a tuple of (hostname, port). Default SSH port is 22.
transport = paramiko.Transport(('10.0.0.5', 22))

# transport.connect() — Authenticates the transport connection.
# paramiko.RSAKey.from_private_key_file() — Loads the RSA private key from a file.
# This is used instead of client.connect() because SFTP needs a Transport object.
transport.connect(username='devops', pkey=paramiko.RSAKey.from_private_key_file('id_rsa'))

# paramiko.SFTPClient.from_transport() — Creates an SFTP client from the transport.
# This SFTP client provides methods for file operations (put, get, listdir, etc.).
sftp = paramiko.SFTPClient.from_transport(transport)

# sftp.put(local_path, remote_path) — Uploads a file from local to remote server.
# sftp.get(remote_path, local_path) — Downloads a file from remote to local (not shown).
sftp.put('/local/app.conf', '/remote/app.conf')

# Always close both the SFTP client and the transport to release resources.
sftp.close()       # Close the SFTP session
transport.close()  # Close the underlying SSH transport connection