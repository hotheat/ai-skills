---
name: clash-verge-proxy-manager
description: Use when configuring or maintaining Clash Verge Rev on macOS, especially MyProxy/MyLocal profiles, whitelist proxy rules, default DIRECT routing, proxy credentials, or verifying whether Clash Verge rule and proxy changes are active.
---

# Clash Verge Proxy Manager

## Purpose

Maintain the user's Clash Verge Rev setup with a conservative routing policy:

- `MyProxy` is the only custom outbound proxy.
- `Proxy` is a selector group containing `MyProxy` and `DIRECT`.
- Explicit whitelist rules go to `Proxy`.
- The final fallback remains `MATCH,DIRECT`.

## Canonical Files

Keep these files synchronized:

```text
$HOME/.clash-verge/my-local.yaml
$HOME/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/profiles/Lj28jGfzuySk.yaml
$HOME/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml
$HOME/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge-check.yaml
$HOME/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/profiles.yaml
```

`profiles.yaml` should contain:

```yaml
current: Lj28jGfzuySk
```

If runtime shows `Bitz Net`, Clash is using `SocketProxy2`, not `MyLocal`.

## Proxy Shape

Keep this shape unless the user gives a new proxy:

```yaml
proxies:
- name: MyProxy
  type: http
  server: <proxy-host>
  port: <proxy-port>
  username: <proxy-username>
  password: <proxy-password>
proxy-groups:
- name: Proxy
  type: select
  proxies:
  - MyProxy
  - DIRECT
```

When given `host:port:user:pass`, test protocol first:

```bash
curl -sS --connect-timeout 8 --max-time 15 -x "http://USER:PASS@HOST:PORT" https://ipinfo.io/json
curl -sS --connect-timeout 8 --max-time 15 -x "socks5h://USER:PASS@HOST:PORT" https://ipinfo.io/json
```

Use the working type in YAML. For the current Miya proxy, `http` is correct.

## Add Rules

For domain requests, use `DOMAIN-SUFFIX,<domain>,Proxy` unless an exact `DOMAIN` rule is clearly needed.

Use the bundled script:

```bash
ruby "${SKILL_DIR}/scripts/add_rules.rb" \
  DOMAIN-SUFFIX,wipo.int,Proxy \
  DOMAIN-SUFFIX,pubmed.ncbi.nlm.nih.gov,Proxy
```

The script backs up files, inserts new proxy rules before direct/fallback rules, keeps `MATCH,DIRECT`, and sets `current: Lj28jGfzuySk`.

Keep direct exceptions near the end:

```yaml
- GEOIP,CN,DIRECT
- DOMAIN-SUFFIX,miyaip.com,DIRECT
- DOMAIN-SUFFIX,miyaip.online,DIRECT
- MATCH,DIRECT
```

## Apply

Validate:

```bash
"/Applications/Clash Verge.app/Contents/MacOS/verge-mihomo" -t \
  -d "$HOME/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev" \
  -f "$HOME/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml"
```

Try hot reload:

```bash
config="$HOME/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml"
curl --unix-socket /tmp/verge/verge-mihomo.sock -sS -o /tmp/clash-reload.out -w '%{http_code}\n' \
  -X PUT -H 'Authorization: Bearer set-your-secret' -H 'Content-Type: application/json' \
  --data "{\"path\":\"$config\",\"force\":true}" http://unix/configs
```

If `/rules` still shows old rule count or old targets after `204`, restart Clash Verge:

```bash
pkill -TERM -f '/Applications/Clash Verge.app/Contents/MacOS/clash-verge' || true
sleep 2
open -a 'Clash Verge'
```

## Verify

Check runtime proxies:

```bash
curl --unix-socket /tmp/verge/verge-mihomo.sock -sS \
  -H 'Authorization: Bearer set-your-secret' http://unix/proxies
```

Expected:

- `Proxy.now == MyProxy`
- `MyProxy.type == Http`
- `MyProxy.alive == true`
- `Bitz Net` absent

Check runtime rules:

```bash
curl --unix-socket /tmp/verge/verge-mihomo.sock -sS \
  -H 'Authorization: Bearer set-your-secret' http://unix/rules
```

Expected:

- New requested domains point to `Proxy`.
- Tail ends with `miyaip.com -> DIRECT`, `miyaip.online -> DIRECT`, `Match -> DIRECT`.

Test through Clash:

```bash
curl -I -L --connect-timeout 8 --max-time 20 -x http://127.0.0.1:7897 https://example.com/
```

## Rule Categories Already Maintained

When expanding existing lists, keep these categories in `Proxy`: AI/search tools, OpenAI/ChatGPT, Google/GitHub/YouTube/Twitter/X/Telegram, Jina/Brave/Perplexity/Monica, WIPO/patent sites, PubMed/NCBI/ClinicalTrials, FDA/EMA/PMDA, publishers and literature databases, bio/drug databases, and major pharma company sites.

## Pitfalls

- `DIRECT` does not fail over to `Proxy`; add explicit proxy rules for failing sites.
- `mixed-port` in the source local file may be `7890`; runtime is usually `7897`. Verify with `/configs` or `scutil --proxy`.
- Hot reload can return `204` while runtime rules remain stale. Trust `/rules`, then restart when stale.
