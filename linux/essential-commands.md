# Linux Essential Commands

A practical reference of the most important Linux commands, organized by category with real-world examples.

---

## Table of Contents

- [File and Directory Operations](#file-and-directory-operations)
- [Text Processing](#text-processing)
- [System Information](#system-information)
- [Process Management](#process-management)
- [Disk and Storage](#disk-and-storage)
- [Networking](#networking)
- [User Management](#user-management)
- [Package Management](#package-management)
- [Compression and Archives](#compression-and-archives)
- [Search and Find](#search-and-find)

---

## File and Directory Operations

### Navigation

```bash
pwd                     # Print current directory
cd /var/log             # Change to absolute path
cd ..                   # Go up one directory
cd -                    # Go to previous directory
cd ~                    # Go to home directory
```

### Listing

```bash
ls -la                  # Long format, include hidden files
ls -lh                  # Human-readable file sizes
ls -lt                  # Sort by modification time (newest first)
ls -lS                  # Sort by file size (largest first)
ls -R                   # Recursive listing
tree -L 2               # Tree view, 2 levels deep
```

### File Operations

```bash
cp file.txt backup.txt          # Copy file
cp -r src/ dest/                # Copy directory recursively
cp -p file.txt backup.txt      # Preserve permissions and timestamps

mv old.txt new.txt              # Rename file
mv file.txt /tmp/               # Move file to another directory

rm file.txt                     # Delete file
rm -r directory/                # Delete directory recursively
rm -i file.txt                  # Prompt before deleting

mkdir -p path/to/dir            # Create nested directories
touch newfile.txt               # Create empty file or update timestamp

ln -s /path/to/target link      # Create symbolic link
ln /path/to/target hardlink     # Create hard link
```

### File Content

```bash
cat file.txt                    # Display entire file
head -n 20 file.txt             # First 20 lines
tail -n 20 file.txt             # Last 20 lines
tail -f /var/log/syslog         # Follow log file in real time
less file.txt                   # Paginated view (q to quit)
wc -l file.txt                  # Count lines
wc -w file.txt                  # Count words
diff file1.txt file2.txt        # Compare two files
```

---

## Text Processing

### grep — Pattern Matching

```bash
grep "error" /var/log/syslog            # Search for pattern
grep -i "error" file.txt                # Case-insensitive search
grep -r "TODO" ./src/                   # Recursive search in directory
grep -n "pattern" file.txt             # Show line numbers
grep -c "error" file.txt               # Count matching lines
grep -v "debug" file.txt               # Invert match (exclude pattern)
grep -E "error|warning" file.txt       # Extended regex (OR)
grep -l "pattern" *.txt                # List files containing pattern
```

### sed — Stream Editor

```bash
sed 's/old/new/' file.txt               # Replace first occurrence per line
sed 's/old/new/g' file.txt              # Replace all occurrences
sed -i 's/old/new/g' file.txt           # In-place replacement
sed -n '5,10p' file.txt                 # Print lines 5–10
sed '/^#/d' file.txt                    # Delete comment lines
sed '3d' file.txt                       # Delete line 3
```

### awk — Text Processing

```bash
awk '{print $1}' file.txt                      # Print first column
awk '{print $1, $3}' file.txt                  # Print columns 1 and 3
awk -F: '{print $1}' /etc/passwd               # Custom delimiter
awk '$3 > 100 {print $1, $3}' data.txt         # Conditional filter
awk '{sum += $1} END {print sum}' numbers.txt   # Sum a column
awk 'NR==5,NR==10' file.txt                    # Print lines 5–10
```

### Other Text Tools

```bash
sort file.txt                   # Sort alphabetically
sort -n file.txt                # Sort numerically
sort -r file.txt                # Reverse sort
sort -u file.txt                # Sort and remove duplicates

uniq file.txt                   # Remove adjacent duplicates
sort file.txt | uniq -c         # Count occurrences

cut -d: -f1 /etc/passwd         # Cut by delimiter, field 1
cut -c1-10 file.txt             # Cut by character position

tr 'a-z' 'A-Z' < file.txt      # Translate lowercase to uppercase
tr -d '\r' < file.txt           # Remove carriage returns

xargs                           # Build command lines from stdin
find . -name "*.log" | xargs rm # Delete all .log files
```

---

## System Information

```bash
uname -a                # Full system information
uname -r                # Kernel version
hostname                # System hostname
hostnamectl             # Detailed host info (systemd)

uptime                  # System uptime and load averages
date                    # Current date and time
timedatectl             # Timezone and NTP status

cat /etc/os-release     # OS distribution info
lsb_release -a          # Distribution details

free -h                 # Memory usage (human-readable)
lscpu                   # CPU architecture details
lsblk                   # Block device information
lspci                   # PCI devices
lsusb                   # USB devices

dmesg | tail -20        # Recent kernel messages
journalctl -xe          # Recent systemd journal entries
```

---

## Process Management

```bash
ps aux                          # All running processes
ps aux | grep nginx             # Find specific process
ps -ef --forest                 # Process tree

top                             # Interactive process monitor
htop                            # Enhanced process monitor (if installed)

kill PID                        # Send SIGTERM to process
kill -9 PID                     # Force kill (SIGKILL)
kill -HUP PID                   # Reload configuration (SIGHUP)
killall process_name            # Kill by name
pkill -f "pattern"              # Kill by pattern match

nohup command &                 # Run process immune to hangups
jobs                            # List background jobs
bg %1                           # Resume job 1 in background
fg %1                           # Bring job 1 to foreground

nice -n 10 command              # Start with lower priority
renice -n 5 -p PID              # Change priority of running process

strace -p PID                   # Trace system calls
lsof -p PID                     # List open files for process
lsof -i :80                     # What process is using port 80
```

---

## Disk and Storage

```bash
df -h                           # Disk space usage
df -i                           # Inode usage
du -sh /var/log/                # Size of a directory
du -sh * | sort -rh | head -10  # Top 10 largest items

fdisk -l                        # List disk partitions
blkid                           # Block device attributes
mount                           # List mounted filesystems
mount /dev/sdb1 /mnt            # Mount a device
umount /mnt                     # Unmount

lsblk -f                        # Filesystems on block devices

# Filesystem check (unmount first)
fsck /dev/sdb1

# Create filesystem
mkfs.ext4 /dev/sdb1
mkfs.xfs /dev/sdb1
```

---

## Networking

```bash
ip addr show                    # Show IP addresses
ip route show                   # Show routing table
ip link show                    # Show network interfaces

ping -c 4 google.com            # Test connectivity
traceroute google.com           # Trace packet route
mtr google.com                  # Combined ping + traceroute

curl -I https://example.com     # HTTP headers only
curl -o file.zip URL            # Download file
wget URL                        # Download file

ss -tuln                        # List listening ports
ss -tp                          # Show connections with process info
netstat -tuln                   # Legacy: list listening ports

dig example.com                 # DNS lookup
nslookup example.com            # DNS lookup (simple)
host example.com                # DNS lookup (compact)

nc -zv host 80                  # Test if port is open
nmap -sT host                   # Port scan

scp file.txt user@host:/path/   # Secure copy to remote
rsync -avz src/ user@host:dest/ # Sync files to remote
```

---

## User Management

```bash
whoami                          # Current user
id                              # Current user ID and groups
id username                     # Specific user's ID and groups

useradd -m -s /bin/bash user    # Create user with home dir
userdel -r user                 # Delete user and home dir
usermod -aG sudo user           # Add user to sudo group
usermod -aG docker user         # Add user to docker group

passwd username                 # Change password
chage -l username               # Password aging info

groups username                 # List user's groups
groupadd devops                 # Create group
groupdel devops                 # Delete group

su - username                   # Switch user
sudo command                    # Run as root
sudo -u user command            # Run as specific user
visudo                          # Edit sudoers safely

last                            # Login history
w                               # Who is logged in and what they're doing
who                             # Currently logged-in users
```

---

## Package Management

### Debian/Ubuntu (apt)

```bash
apt update                      # Update package index
apt upgrade                     # Upgrade installed packages
apt install package             # Install package
apt remove package              # Remove package
apt autoremove                  # Remove unused dependencies
apt search keyword              # Search for package
apt show package                # Package details
dpkg -l                         # List installed packages
dpkg -L package                 # List files in package
```

### RHEL/CentOS (yum/dnf)

```bash
yum update                      # Update all packages
yum install package             # Install package
yum remove package              # Remove package
yum search keyword              # Search for package
yum info package                # Package details
rpm -qa                         # List installed packages
rpm -ql package                 # List files in package

# dnf (modern replacement for yum)
dnf install package
dnf update
```

---

## Compression and Archives

```bash
# tar
tar -czf archive.tar.gz dir/    # Create gzip compressed archive
tar -cjf archive.tar.bz2 dir/  # Create bzip2 compressed archive
tar -xzf archive.tar.gz        # Extract gzip archive
tar -xzf archive.tar.gz -C /dest/  # Extract to specific directory
tar -tzf archive.tar.gz        # List contents without extracting

# zip
zip -r archive.zip dir/         # Create zip archive
unzip archive.zip               # Extract zip archive
unzip -l archive.zip            # List contents

# gzip
gzip file.txt                   # Compress (replaces original)
gunzip file.txt.gz              # Decompress
zcat file.txt.gz                # View without decompressing
```

---

## Search and Find

### find

```bash
find / -name "nginx.conf"                   # Find by exact name
find . -name "*.log"                         # Find by pattern
find . -type f -name "*.py"                  # Find files only
find . -type d -name "config"               # Find directories only
find . -mtime -7                             # Modified in last 7 days
find . -size +100M                           # Files larger than 100MB
find . -perm 777                             # Files with specific permissions
find . -user root -type f                    # Files owned by root
find . -empty                                # Empty files and directories

# Find and execute
find . -name "*.tmp" -delete                 # Find and delete
find . -name "*.sh" -exec chmod +x {} \;     # Find and make executable
find . -name "*.log" -exec grep -l "error" {} \;  # Find logs containing "error"
```

### locate and which

```bash
locate filename                  # Fast file search (uses database)
updatedb                         # Update locate database

which python3                    # Find command location
whereis nginx                    # Find binary, source, man page
type command                     # Show how command is interpreted
```

---

## Quick Tips

| Task | Command |
|------|---------|
| Repeat last command | `!!` |
| Repeat last command with sudo | `sudo !!` |
| Search command history | `Ctrl+R` then type |
| Clear terminal | `Ctrl+L` or `clear` |
| Cancel current command | `Ctrl+C` |
| Send to background | `Ctrl+Z` then `bg` |
| Redirect stdout and stderr | `command > out.log 2>&1` |
| Append to file | `command >> file.txt` |
| Pipe output | `command1 \| command2` |
| Run if previous succeeded | `cmd1 && cmd2` |
| Run if previous failed | `cmd1 \|\| cmd2` |

---

[← Back to Linux](README.md) | [→ Permissions Guide](permissions-guide.md)
