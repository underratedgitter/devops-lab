# Kubernetes (kubectl) Cheatsheet

Quick reference for essential `kubectl` CLI commands.

---

## Configuration & Context

```bash
kubectl config get-contexts                        # List available contexts
kubectl config use-context my-cluster              # Switch context
kubectl config set-context --current --namespace=dev # Change default namespace
kubectl cluster-info                               # Display cluster endpoint & services
```

---

## Inspecting Resources

```bash
kubectl get pods -A                                # List pods in all namespaces
kubectl get pods -o wide                           # Show pod IPs and assigned node
kubectl get deployments -n staging                 # List deployments in namespace
kubectl get svc                                    # List services
kubectl describe pod <pod-name>                    # Detailed pod info + events
kubectl get pod <pod-name> -o yaml                 # Export pod spec as YAML
```

---

## Debugging & Operations

```bash
# Logs & Exec
kubectl logs -f <pod-name>                         # Follow pod logs
kubectl logs -f <pod-name> -c <container-name>     # Container-specific logs
kubectl exec -it <pod-name> -- /bin/sh             # Shell inside pod

# Resource Utilization
kubectl top node                                   # Node CPU/Memory usage
kubectl top pod                                    # Pod CPU/Memory usage

# Scaling & Updates
kubectl scale deployment/myapp --replicas=5        # Scale replicas
kubectl rollout status deployment/myapp            # Check deployment progress
kubectl rollout undo deployment/myapp              # Rollback deployment
```

---

## Port Forwarding & Secret Decoding

```bash
# Forward local port 8080 to service port 80
kubectl port-forward svc/myapp 8080:80

# Decode Base64 secret value
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 -d
```

---

[← Back to Cheatsheets](README.md)
