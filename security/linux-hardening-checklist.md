# Linux Hardening Checklist

A practical, step-by-step security hardening checklist for production Linux instances.

---

## 1. System Updates & Package Management

- [ ] **Apply latest patches:** Update system packages immediately after installation:
  ```bash
  sudo apt update && sudo apt dist-upgrade -y  # Debian/Ubuntu
  sudo dnf upgrade -y                         # RHEL/CentOS/Rocky
  ```
- [ ] **Enable Unattended Upgrades:** Configure automatic security updates:
  ```bash
  sudo apt install unattended-upgrades
  sudo dpkg-reconfigure --priority=low unattended-upgrades
  ```
- [ ] **Remove unused packages & services:**
  ```bash
  sudo apt autoremove --purge
  ```

---

## 2. SSH Hardening (`/etc/ssh/sshd_config`)

- [ ] **Disable Root Login:**
  ```ini
  PermitRootLogin no
  ```
- [ ] **Disable Password Authentication (Enforce SSH Keys):**
  ```ini
  PasswordAuthentication no
  PubkeyAuthentication yes
  ```
- [ ] **Change default SSH port (Optional but recommended):**
  ```ini
  Port 2222
  ```
- [ ] **Restrict Max Auth Attempts:**
  ```ini
  MaxAuthTries 3
  ```
- [ ] **Use modern Ciphers and MACs:**
  ```ini
  KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group16-sha512
  Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
  ```
- [ ] **Restart SSH daemon:**
  ```bash
  sudo systemctl restart sshd
  ```

---

## 3. Account & Password Policy

- [ ] **Audit Sudo Users:** Ensure only authorized users are in the `sudo` / `wheel` group:
  ```bash
  getent group sudo
  getent group wheel
  ```
- [ ] **Enforce Password Complexity (PAM):** Ensure minimum password length and complexity rules.
- [ ] **Lock Expired/Inactive Accounts:** Set account expiration policies using `chage`.

---

## 4. Network & Firewall

- [ ] **Enable Firewall (UFW / firewalld):**
  ```bash
  # UFW (Ubuntu)
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw allow 22/tcp  # or custom SSH port
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw enable
  ```
- [ ] **Install Fail2ban:** Protect against brute-force attacks:
  ```bash
  sudo apt install fail2ban
  sudo systemctl enable --now fail2ban
  ```
- [ ] **Disable Unused Protocols:** Disable IPv6 if not in use, disable DCCP, SCTP in kernel.

---

## 5. Filesystem & Permissions

- [ ] **Audit SUID/SGID Files:**
  ```bash
  find / -perm -4000 -o -perm -2000 -type f 2>/dev/null
  ```
- [ ] **Secure World-Writable Files:**
  ```bash
  find / -xdev -type f -perm -0002 -exec ls -l {} +
  ```
- [ ] **Mount `/tmp` and `/var/tmp` with `noexec,nosuid,nodev`** options in `/etc/fstab`.

---

## 6. Logging & Auditing

- [ ] **Enable `auditd`:** Track access to sensitive system files:
  ```bash
  sudo apt install auditd
  sudo systemctl enable --now auditd
  ```
- [ ] **Centralize Logs:** Ship logs to a central server (Loki, Elasticsearch, CloudWatch).
- [ ] **Monitor Disk Usage for `/var/log`** to prevent log exhaustion attacks.

---

[← Back to Security](README.md)
