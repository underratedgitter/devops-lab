# Linux Permissions Guide

A deep dive into Linux file permissions, ownership, special permission bits, and Access Control Lists (ACLs).

---

## Table of Contents

- [Understanding Permission Basics](#understanding-permission-basics)
- [Reading Permissions](#reading-permissions)
- [Changing Permissions (chmod)](#changing-permissions-chmod)
- [Changing Ownership (chown, chgrp)](#changing-ownership-chown-chgrp)
- [Default Permissions (umask)](#default-permissions-umask)
- [Special Permission Bits](#special-permission-bits)
- [Access Control Lists (ACLs)](#access-control-lists-acls)
- [Common Permission Patterns](#common-permission-patterns)
- [Troubleshooting](#troubleshooting)

---

## Understanding Permission Basics

Every file and directory in Linux has three sets of permissions for three categories of users:

```
Owner (u)  →  The user who owns the file
Group (g)  →  The group that owns the file
Others (o) →  Everyone else
```

Each category can have three types of permissions:

| Permission | File Effect | Directory Effect | Numeric |
|-----------|-------------|-----------------|---------|
| `r` (read) | View contents | List contents | 4 |
| `w` (write) | Modify contents | Create/delete files inside | 2 |
| `x` (execute) | Run as program | Enter directory (`cd`) | 1 |

---

## Reading Permissions

```bash
ls -la
```

Output example:

```
-rwxr-xr--  1  suraj  devops  4096  Jul 20 10:30  deploy.sh
drwxr-x---  5  suraj  devops  4096  Jul 20 10:30  scripts/
lrwxrwxrwx  1  suraj  devops    15  Jul 20 10:30  latest -> v2.1/
```

Breaking down `-rwxr-xr--`:

```
-    rwx    r-x    r--
│    │      │      │
│    │      │      └── Others: read only
│    │      └── Group: read + execute
│    └── Owner: read + write + execute
└── File type: - regular, d directory, l symlink
```

Numeric equivalent: `rwx` = 4+2+1 = **7**, `r-x` = 4+0+1 = **5**, `r--` = 4+0+0 = **4** → **754**

---

## Changing Permissions (chmod)

### Symbolic Mode

```bash
# Add execute for owner
chmod u+x script.sh

# Remove write for group and others
chmod go-w file.txt

# Set exact permissions
chmod u=rwx,g=rx,o=r file.txt

# Add execute for everyone
chmod a+x script.sh

# Remove all permissions for others
chmod o= file.txt

# Recursive
chmod -R u+rw directory/
```

### Numeric (Octal) Mode

```bash
chmod 755 script.sh     # rwxr-xr-x  (common for scripts)
chmod 644 file.txt      # rw-r--r--  (common for files)
chmod 700 private/      # rwx------  (owner only)
chmod 600 secrets.key   # rw-------  (sensitive files)
chmod 777 file.txt      # rwxrwxrwx  (AVOID — security risk!)
chmod 750 directory/    # rwxr-x---  (team directory)
chmod 440 sudoers       # r--r-----  (read-only config)
```

### Common Permission Reference

| Octal | Symbolic | Use Case |
|-------|----------|----------|
| `755` | `rwxr-xr-x` | Executable scripts, public directories |
| `644` | `rw-r--r--` | Regular files, documentation |
| `700` | `rwx------` | Private directories, home dirs |
| `600` | `rw-------` | SSH keys, sensitive config files |
| `750` | `rwxr-x---` | Shared team directories |
| `440` | `r--r-----` | Sudoers, read-only configs |
| `664` | `rw-rw-r--` | Shared files in a group |

---

## Changing Ownership (chown, chgrp)

```bash
# Change owner
chown user file.txt
chown user:group file.txt

# Change group only
chgrp devops file.txt
chown :devops file.txt

# Recursive ownership change
chown -R www-data:www-data /var/www/

# Change only if current owner matches
chown --from=olduser newuser file.txt
```

---

## Default Permissions (umask)

The `umask` determines default permissions for newly created files and directories.

```bash
umask                   # Show current umask
umask 022               # Set umask
```

### How umask Works

```
Default file permissions:    666 (rw-rw-rw-)
Default directory permissions: 777 (rwxrwxrwx)

With umask 022:
  Files:       666 - 022 = 644 (rw-r--r--)
  Directories: 777 - 022 = 755 (rwxr-xr-x)

With umask 077:
  Files:       666 - 077 = 600 (rw-------)
  Directories: 777 - 077 = 700 (rwx------)
```

### Setting Persistent umask

```bash
# Add to ~/.bashrc or ~/.profile
echo "umask 027" >> ~/.bashrc

# System-wide: /etc/profile or /etc/login.defs
```

---

## Special Permission Bits

### SUID (Set User ID) — Octal: 4000

When set on an executable, the process runs with the **file owner's** permissions instead of the user who runs it.

```bash
# Set SUID
chmod u+s program
chmod 4755 program

# Identify SUID files
ls -la /usr/bin/passwd
# -rwsr-xr-x  ← 's' in owner execute position

# Find all SUID files on system (security audit)
find / -perm -4000 -type f 2>/dev/null
```

**Example:** `/usr/bin/passwd` has SUID so regular users can change their own password (which requires writing to `/etc/shadow`, owned by root).

### SGID (Set Group ID) — Octal: 2000

- **On files:** Process runs with file's group permissions.
- **On directories:** New files inherit the directory's group (not the creator's primary group).

```bash
# Set SGID on directory (team collaboration)
chmod g+s /shared/project/
chmod 2775 /shared/project/

# Identify SGID
ls -la
# drwxrwsr-x  ← 's' in group execute position

# Find all SGID files
find / -perm -2000 -type f 2>/dev/null
```

**Use case:** Team directories where all files should belong to the same group.

### Sticky Bit — Octal: 1000

On directories, only the file owner (or root) can delete or rename files — even if others have write permission.

```bash
# Set sticky bit
chmod +t /tmp/
chmod 1777 /tmp/

# Identify sticky bit
ls -ld /tmp/
# drwxrwxrwt  ← 't' in others execute position

# Find directories with sticky bit
find / -perm -1000 -type d 2>/dev/null
```

**Example:** `/tmp` has the sticky bit so users can create files but can't delete each other's files.

### Summary of Special Bits

| Bit | Octal | Symbol | Effect |
|-----|-------|--------|--------|
| SUID | 4000 | `s` in user execute | Process runs as file owner |
| SGID | 2000 | `s` in group execute | Files: runs as file group. Dirs: new files inherit group |
| Sticky | 1000 | `t` in others execute | Only owner can delete files in directory |

---

## Access Control Lists (ACLs)

ACLs provide fine-grained permissions beyond the standard owner/group/others model.

### Prerequisites

```bash
# Install ACL tools (if not present)
# Debian/Ubuntu
apt install acl

# RHEL/CentOS
yum install acl

# Verify filesystem supports ACLs
mount | grep acl
```

### Viewing ACLs

```bash
getfacl file.txt
```

Output:

```
# file: file.txt
# owner: suraj
# group: devops
user::rw-
user:alice:r--          # Specific user ACL
group::r--
group:qa:rw-            # Specific group ACL
mask::rw-
other::---
```

### Setting ACLs

```bash
# Grant read to specific user
setfacl -m u:alice:r file.txt

# Grant read-write to specific group
setfacl -m g:qa:rw file.txt

# Set default ACL on directory (inherited by new files)
setfacl -d -m g:devops:rwx /shared/project/

# Remove specific ACL entry
setfacl -x u:alice file.txt

# Remove all ACLs
setfacl -b file.txt

# Recursive ACL
setfacl -R -m g:devops:rx /shared/project/
```

### ACL + Files Indicator

When a file has ACLs, `ls -l` shows a `+` sign:

```bash
ls -la file.txt
# -rw-r--r--+  ← the '+' indicates ACLs are set
```

---

## Common Permission Patterns

### Web Server Files

```bash
# Web root owned by www-data
chown -R www-data:www-data /var/www/html/
chmod -R 755 /var/www/html/          # Directories
find /var/www/html -type f -exec chmod 644 {} \;  # Files

# Writable upload directory
chmod 775 /var/www/html/uploads/
chown www-data:www-data /var/www/html/uploads/
```

### SSH Keys

```bash
chmod 700 ~/.ssh/
chmod 600 ~/.ssh/id_rsa              # Private key
chmod 644 ~/.ssh/id_rsa.pub          # Public key
chmod 600 ~/.ssh/authorized_keys
chmod 644 ~/.ssh/known_hosts
chmod 600 ~/.ssh/config
```

### Shared Team Directory

```bash
mkdir /shared/project
chown root:devops /shared/project
chmod 2775 /shared/project           # SGID so files inherit group
```

### Secrets and Config Files

```bash
chmod 600 /etc/ssl/private/*.key     # SSL private keys
chmod 640 /etc/app/config.yml        # App config (owner rw, group r)
chmod 400 /root/.aws/credentials     # AWS credentials (owner read only)
```

---

## Troubleshooting

### "Permission denied" Checklist

1. **Check file permissions:** `ls -la file`
2. **Check directory permissions:** You need `x` on every directory in the path
3. **Check ownership:** `ls -la file` — are you the owner or in the group?
4. **Check ACLs:** `getfacl file`
5. **Check for immutable flag:** `lsattr file` (remove with `chattr -i file`)
6. **Check SELinux/AppArmor:** `ls -Z file` (SELinux), `aa-status` (AppArmor)
7. **Check mount options:** `mount | grep partition` — is it mounted `ro` or `noexec`?

### Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| `chmod 777` on everything | Major security risk | Use least privilege (644/755) |
| Forgetting `x` on directories | Can't `cd` into directory | `chmod +x dir/` |
| Wrong web server permissions | 403 Forbidden errors | Ensure `www-data` can read |
| SSH key too open | "Permissions are too open" error | `chmod 600 ~/.ssh/id_rsa` |
| Missing group membership | Can't access shared files | `usermod -aG group user` + re-login |

---

[← Back to Linux](README.md) | [← Essential Commands](essential-commands.md)
