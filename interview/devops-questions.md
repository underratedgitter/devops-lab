# DevOps & SRE Interview Questions

A collection of high-yield technical and scenario questions for DevOps and Site Reliability Engineering interviews.

---

## 1. Linux & Systems

### Q1: What is the difference between a Process and a Thread?
**Answer:**
- A **Process** is an executing instance of a program with its own dedicated memory space (virtual memory, file descriptors, stack, heap). Processes are isolated from each other.
- A **Thread** is the smallest unit of execution within a process. Multiple threads within the same process share the process's memory space, open files, and resources, but have their own execution stack and registers.

### Q2: What happens under the hood when you type `curl https://example.com` and press Enter?
**Answer:**
1. **DNS Resolution:** Client queries local cache → `/etc/hosts` → DNS recursive resolver → Root → TLD → Authoritative DNS to resolve `example.com` to an IP.
2. **TCP Handshake:** Client sends `SYN` to port 443 → Server responds with `SYN-ACK` → Client sends `ACK`.
3. **TLS Handshake:** Client & Server negotiate TLS version, cipher suite, verify certificate chain, and exchange key material (e.g. ECDHE).
4. **HTTP Request:** Client sends encrypted `GET / HTTP/1.1` request.
5. **Server Processing & Response:** Server processes request (reverse proxy → app server → database) and returns HTTP 200 OK with HTML content.
6. **Connection Termination / Reuse:** Connection is kept alive or closed via TCP FIN/ACK.

### Q3: What is the difference between Load Average and CPU Utilization?
**Answer:**
- **CPU Utilization** measures the percentage of time the CPU was actively executing instructions over a period (user, system, wait).
- **Load Average** represents the average number of processes that are either in a runnable state (using or waiting for CPU) or in an uninterruptible sleep state (waiting for I/O). A load average higher than the total CPU core count indicates queuing/saturation.

---

## 2. Docker & Containerization

### Q4: How do Docker containers differ from Virtual Machines?
**Answer:**
- **VMs** run a full guest operating system on virtualized hardware via a hypervisor (Type 1 or Type 2). They have heavy resource overhead, take minutes to boot, and provide hardware-level isolation.
- **Containers** share the host operating system kernel and isolate processes using Linux kernel features (`namespaces` for isolation, `cgroups` for resource limits). They are lightweight, start in milliseconds, and use fewer resources.

### Q5: What are Linux Namespaces and Cgroups?
**Answer:**
- **Namespaces** provide *isolation* by giving containers their own workspace view (PID, NET, MNT, IPC, UTS, USER).
- **Cgroups (Control Groups)** provide *resource limiting and accounting* (limiting CPU, Memory, Disk I/O, Network bandwidth).

---

## 3. Kubernetes

### Q6: What is the difference between a Deployment and a StatefulSet?
**Answer:**
- **Deployment:** Used for stateless applications. Pods are interchangeable, have random generated hashes in their names (`web-7d4b4598-xyz`), and can be replaced or scaled in any order. Storage is typically ephemeral.
- **StatefulSet:** Used for stateful applications (databases, Kafka). Pods have persistent ordinal identifiers (`redis-0`, `redis-1`), deterministic startup/shutdown order, stable network identities (DNS), and persistent volume claim bindings.

### Q7: What is the difference between a Liveness Probe and a Readiness Probe?
**Answer:**
- **Liveness Probe:** Checks if the container is alive. If it fails, Kubernetes kills the container and restarts it according to the restart policy.
- **Readiness Probe:** Checks if the container is ready to accept network traffic. If it fails, Kubernetes removes the pod's IP from the Service endpoints, preventing traffic from being routed to it until it recovers.

---

## 4. CI/CD & Terraform

### Q8: How does Terraform track state, and why is remote state locking important?
**Answer:**
- Terraform uses a `terraform.tfstate` file to map declared code resources to real-world infrastructure objects.
- **Remote State Locking** (e.g. using AWS S3 + DynamoDB) prevents concurrent `terraform apply` executions by multiple engineers or CI/CD pipelines, avoiding state corruption or race conditions.

---

## 5. SRE Scenarios

### Q9: A service's CPU usage spikes to 100% and response latency triples. How do you troubleshoot?
**Answer:**
1. **Identify affected instances:** Check metrics dashboard (Grafana/CloudWatch) to see if it's across all nodes or specific ones.
2. **Inspect top processes:** SSH/exec into host/container and run `top` or `htop` to identify the specific PID consuming CPU.
3. **Check application logs:** Look for error bursts, unexpected traffic spikes, or infinite loops.
4. **Analyze thread/heap dump or trace:** Take a thread dump (Java/Go/Python profile) to identify hot methods.
5. **Mitigate:** Scale out replicas (HPA/Auto Scaling) to alleviate load, or roll back if triggered by a recent deployment.

---

[← Back to Interview Prep](README.md)
