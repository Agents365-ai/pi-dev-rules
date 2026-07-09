# Pi — Security & Containerization

Source: https://pi.dev/docs/latest/security, /containerization

Pi is a **local coding agent**: it runs with the permissions of the user account that starts it and
treats files writable by that user as inside the same local trust boundary.

---

## 1. Project trust

Project trust controls whether Pi loads project-local settings, resources, packages, and extensions.
**It is not a sandbox** and does not restrict what the model can ask tools to do once you start
working in a directory.

### What requires trust

A project is treated as requiring trust when, from the current working directory, any of these
exist:

- `.pi/settings.json`
- `.pi/extensions`, `.pi/skills`, `.pi/prompts`, or `.pi/themes`
- `.pi/SYSTEM.md` or `.pi/APPEND_SYSTEM.md`
- project `.agents/skills` in the current dir or an ancestor

A bare `.pi` directory (no resources) does **not** count.

### Deciding trust

- On interactive start in a trust-requiring project with no saved decision (for the dir or a
  parent), Pi follows **`defaultProjectTrust`** (global setting): `"ask"` (default; prompts when a
  UI is available), `"always"`, or `"never"`.
- Saved decisions are stored **by canonical directory** in **`~/.pi/agent/trust.json`**; the closest
  saved decision on the current/parent path wins over the global default. Save with `/trust`.
- **Trusting** loads: `.pi/settings.json`, `.pi` resources (extensions/skills/prompts/themes/system
  prompt files), missing project packages configured via project settings, and project-local /
  project-package extensions.
- **Declining** skips those resources. `AGENTS.md`/`CLAUDE.md` context files load **regardless** of
  trust (unless context loading is disabled). Before trust resolves, Pi loads only context files,
  user/global extensions, and CLI `-e` extensions.
- User/global and CLI extensions can handle the **`project_trust` event**; the first extension that
  returns a yes/no decision owns it.
- **Non-interactive modes** (`-p`, `--mode json`, `--mode rpc`) show no prompt: with no applicable
  saved decision, `"ask"` and `"never"` ignore the resources while `"always"` trusts them. Override
  a single run with **`--approve`/`-a`** or **`--no-approve`/`-na`**.

## 2. No built-in sandbox

Pi ships **no built-in sandbox**. Built-in tools read/write/edit files and run shell commands with
the Pi process's permissions; extensions are TypeScript modules with the same permissions; package
installs, shell commands, language servers, and test commands run as ordinary local processes.

This is intentional — Pi is designed to operate on local source trees and integrate with the dev
environment. "Real isolation needs to come from the operating system or a virtualization/container
boundary." Project trust is only an **input-loading guard**; it does not make untrusted code,
prompts, or model output safe. **Prompt injection** from repository files, comments, docs, context
files, or build output is an expected local-agent risk and cannot be reliably prevented by Pi.

## 3. Running untrusted or unmonitored work

For untrusted repos, unmonitored generated code, or unattended automation, run Pi in a container,
VM, micro-VM, or policy-controlled sandbox with only the required files/credentials:

- run the whole `pi` process inside a container/sandbox, **or** run host Pi and route built-in tool
  execution into a Gondolin micro-VM;
- mount only the workspace paths the agent should access;
- **avoid mounting host `~/.pi/agent`** unless the container should reach host sessions, settings,
  and credentials (it exposes auth + session files);
- pass the minimum API keys, or short-lived credentials; restrict network access when unneeded;
- review diffs/outputs before copying results back to trusted systems. Bind-mounting a workspace
  read/write lets in-container writes modify host files — use read-only mounts or copy in/out for
  stronger protection.

### Reporting security issues

Follow the repo Security Policy; do not open a public issue. Out of scope (unless a real
privilege-boundary bypass is shown): expected local-agent behavior, the lack of a built-in sandbox,
prompt injection from untrusted content, behavior of user-installed extensions/skills.

---

## 4. Containerization patterns

| Pattern | What is isolated | Best for | Notes |
|---------|------------------|----------|-------|
| Gondolin extension | Built-in tools & `!` commands | Local micro-VM isolation, auth stays on host | `examples/extensions/gondolin/` |
| Plain Docker | Whole `pi` process | Simple local isolation | Provider API keys enter the container |
| OpenShell | Whole `pi` process | Local or remote managed sandbox | Requires an OpenShell gateway |

Extensions run wherever the `pi` process runs. With host Pi + a tool-routing extension, other
custom extension tools still run on the host unless they also delegate.

### Gondolin (local Linux micro-VM)

Repo `earendil-works/gondolin`, package `@earendil-works/gondolin`. Requires Node.js **≥ 23.6.0** and
**QEMU**.

```bash
cp -R packages/coding-agent/examples/extensions/gondolin ~/.pi/agent/extensions/gondolin
cd ~/.pi/agent/extensions/gondolin && npm install --ignore-scripts
cd /path/to/project
pi -e ~/.pi/agent/extensions/gondolin
```

Mounts host cwd at `/workspace`, overrides `read/write/edit/bash/grep/find/ls`, routes `!` commands
into the VM; writes under `/workspace` pass through to the host.

### Plain Docker

```dockerfile
# Dockerfile.pi
FROM node:24-bookworm-slim
RUN apt-get update \
  && apt-get install -y --no-install-recommends bash ca-certificates git ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN npm install -g --ignore-scripts @earendil-works/pi-coding-agent
WORKDIR /workspace
ENTRYPOINT ["pi"]
```

```bash
docker build -t pi-sandbox -f Dockerfile.pi .
docker run --rm -it \
  -e ANTHROPIC_API_KEY \
  -v "$PWD:/workspace" \
  -v pi-agent-home:/root/.pi/agent \
  pi-sandbox
```

`-v "$PWD:/workspace"` writes affect host files. Use a **named volume** for `/root/.pi/agent`
(container-local settings/sessions); mounting host `~/.pi/agent` exposes host auth/session files.

### NVIDIA OpenShell

Policy-controlled sandbox with filesystem, process, network, credential, and inference controls;
runs via a local gateway (Docker/Podman/VM) or a remote Kubernetes gateway. Every sandbox needs an
active gateway.

```bash
openshell gateway add <gateway-url> --name <name>
openshell gateway select <name>
openshell sandbox create --name pi-sandbox --from pi -- pi   # whole process runs inside
```

Remote gateways don't bind-mount project files — clone in the sandbox or transfer:

```bash
openshell sandbox upload   pi-sandbox ./repo /workspace
openshell sandbox download pi-sandbox /workspace/repo ./repo-out
```

**Credential/inference routing**: OpenShell can keep raw model API keys outside the sandbox — code
inside calls `https://inference.local` and the gateway injects provider credentials upstream.
Configure Pi to use the corresponding OpenAI-/Anthropic-compatible endpoint.
