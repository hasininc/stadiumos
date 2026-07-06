# Deployment & Infrastructure as Code (IaC)

This directory contains configurations and scripts to deploy StadiumOS:

## Directory Index
- `kubernetes/`: Kubernetes manifests, ingress configurations, and deployment definitions for GKE clusters.

## Core Guidelines
- Secure control plane endpoints by restricting access to authorized networks.
- Enforce network policies inside GKE to block unauthorized communication between namespaces.
- Inject secrets into container environments at runtime, keeping credentials out of image configurations or git repositories.
