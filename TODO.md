# Yapılacaklar / TODO

**Son Güncelleme:** 2026-06-11

---

## 🗺️ Paralel Akış Şeması (Agentic)

```
Faz 0 (Foundation)
  │
  ├──────┬──────────┬──────────────┬──────────────┐
  │      │          │              │              │
  ▼      ▼          ▼              ▼              ▼
Faz 1A  Faz 1B    Faz 1C        Faz 1D        Faz 2C
(MCP +  (Telegram (Çoklu Model)  (Auth +       (MCP Client
 Panel)   Bot)                    Cron +         + Dış
                                  Memory)        Araçlar)
  │      │          │              │              │
  ├──────┼──────────┼──────────────┼──────────────┘
  │      │          │              │
  ▼      ▼          ▼              ▼
Faz 2A  Faz 2B (Agent Yetenekleri)
(Task   (Tool Sistemi + Skill +    ← 1C + 1D'nin çıktılarını kullanır
 Queue + Chain-of-Thought)
 Logging)
  │      │
  └──────┘
     │
     ▼
Faz 3A  Faz 3B
(Prod.  (Ekosistem)
 Hardening)
```

---

## Faz 0 — Foundation (ÖNCE BUNU YAP)
*Her şeyin temeli. Python Core iskeleti.*

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 0.1 | Python Core iskeleti (FastAPI + uvicorn + SQLite) | - | 🔴 Kritik |
| 0.2 | State store (SQLAlchemy modelleri: agents, tasks, providers, sessions, cron) | AgentGPT Prisma şeması referans | 🔴 Kritik |
| 0.3 | BaseAgent (abstract) + AgentStatus enum + AgentRegistry | agentclaw agent yapısı | 🔴 Kritik |
| 0.4 | BaseProvider (abstract) + OpenAI Provider (ilk provider) | **lobe-chat** `providers/` pattern'i | 🔴 Kritik |
| 0.5 | LLM Router (provider yönlendirme, stream, fallback chain) | **lobe-chat** multi-provider routing | 🔴 Kritik |
| 0.6 | CLI: `agentmanager {start,stop,status,create}` | Auto-GPT CLI argüman pattern'i | 🔴 Kritik |
| 0.7 | WebSocket manager (temel bağlantı yönetimi) | - | 🟡 Yüksek |
| 0.8 | REST API schemas (Pydantic) | - | 🟡 Yüksek |
| 0.9 | VCR test framework kurulumu (record & replay) | **aider** test pattern'i | 🟡 Yüksek |

---

## Faz 1A — MCP + Platform Eklentileri (Track A)
*Faz 0 biter bitmez başlar. 1B/1C/1D/2C ile paralel.*

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 1A.1 | MCP Server: list_agents, get_agent_detail | agentclaw MCP pattern | 🔴 Kritik |
| 1A.2 | MCP Server: assign_task, pause_agent, resume_agent | Project_Plan.md | 🔴 Kritik |
| 1A.3 | MCP Server: create/delete agent, change_role, change_model | - | 🔴 Kritik |
| 1A.4 | MCP Server: list/register providers | appflowy PluginSandbox | 🟡 Yüksek |
| 1A.5 | VS Code Extension iskeleti (TypeScript, activation) | - | 🔴 Kritik |
| 1A.6 | VS Code Webview: React panel entegrasyonu | **lobe-chat** UI pattern'leri | 🔴 Kritik |
| 1A.7 | Web Panel: Agent Dashboard (kart listesi + durum) | **lobe-chat** agent market UI | 🔴 Kritik |
| 1A.8 | Web Panel: Provider Manager (ekleme/düzenleme) | - | 🟡 Yüksek |
| 1A.9 | Web Panel: Agent Creator (rol + model seçimi) | - | 🟡 Yüksek |

---

## Faz 1B — Telegram Bot + Bildirimler (Track B)
*Faz 0 biter bitmez başlar. 1A/1C/1D/2C ile paralel.*

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 1B.1 | Telegram bot (python-telegram-bot ile) | agentclaw Ch.1 | 🔴 Kritik |
| 1B.2 | `/status` — tüm ajanların durum özeti | 💡 Yeni fikir | 🔴 Kritik |
| 1B.3 | `/agent <isim>` — tek ajan detayı + canlı log | 💡 Yeni fikir | 🔴 Kritik |
| 1B.4 | `/tasks` — bekleyen/tamamlanan görevler | **AgentGPT** task list pattern | 🟡 Yüksek |
| 1B.5 | `/pause <isim>` / `/resume <isim>` — ajan kontrolü | 💡 Yeni fikir | 🟡 Yüksek |
| 1B.6 | Access control (allowlist, bot'a kimler yazabilir) | agentclaw Ch.1 | 🔴 Kritik |
| 1B.7 | Zamanlanmış rapor motoru (cron tabanlı) | agentclaw Ch.5 | 🔴 Kritik |
| 1B.8 | Sabah raporu (09:00: dün ne yapıldı, bugün ne yapılacak) | 💡 Yeni fikir | 🟡 Yüksek |
| 1B.9 | Akşam raporu (18:00: tamamlanan görevler) | 💡 Yeni fikir | 🟡 Yüksek |
| 1B.10 | Tüm ajanlar boşta kalınca bildirim | 💡 Yeni fikir | 🟡 Yüksek |
| 1B.11 | Hata anında anlık uyarı (WebSocket → Telegram) | 💡 Yeni fikir | 🟡 Yüksek |
| 1B.12 | Dosya gönderimi (rapor PDF/CSV export) | agentclaw Ch.1 | 🟢 Orta |
| 1B.13 | Discord kanal desteği (genişletme) | agentclaw Ch.2 | 🟢 Orta |
| 1B.14 | `/report` — özel rapor (tarih aralığı, ajan filtresi) | 💡 Yeni fikir | 🟢 Orta |

---

## Faz 1C — Çoklu Model Desteği (Track C)
*Faz 0 biter bitmez başlar. 1A/1B/1D/2C ile paralel.*

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 1C.1 | Anthropic (Claude) Provider | **lobe-chat** Claude provider pattern | 🟡 Yüksek |
| 1C.2 | Google (Gemini) Provider | **lobe-chat** Gemini provider pattern | 🟡 Yüksek |
| 1C.3 | Ollama (yerel modeller) Provider + health check | **lobe-chat** Ollama entegrasyonu, appflowy LocalAI | 🟡 Yüksek |
| 1C.4 | OpenRouter Provider (tüm modeller) | **lobe-chat** provider registry | 🟢 Orta |
| 1C.5 | ProviderRegistry (dinamik kayıt sistemi) | **lobe-chat** plugin registry | 🟡 Yüksek |
| 1C.6 | Model switching API (ajanın modelini runtime değiştir) | - | 🟡 Yüksek |
| 1C.7 | Provider test/validation (anahtar doğrulama) | - | 🟢 Orta |

---

## Faz 1D — Auth + Cron + Memory (Track D)
*Faz 0 biter bitmez başlar. 1A/1B/1C/2C ile paralel. **YENİ TRACK***

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 1D.1 | Auth: API key generation + validation | - | 🔴 Kritik |
| 1D.2 | Auth: Device pairing flow | - | 🟡 Yüksek |
| 1D.3 | Auth: Agent-level data partition middleware | - | 🔴 Kritik |
| 1D.4 | Cron: Plugin-level cron registry API | agentclaw cron registry | 🟡 Yüksek |
| 1D.5 | Cron: Core heartbeat checker (missed trigger detection) | - | 🟡 Yüksek |
| 1D.6 | Memory: Kısa dönem bellek (sliding window) | **Auto-GPT** memory pattern | 🟡 Yüksek |
| 1D.7 | Memory: Summarization engine (context dolunca özetle) | **Auto-GPT** summarization | 🟡 Yüksek |

---

## Faz 2A — Task Yönetimi + Chain-of-Thought Log
*Faz 1A + 1B biter bitmez başlar. 2B ile paralel.*

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 2A.1 | Goal-based task queue (hedef → görev üret → uygula → öğren) | **AgentGPT** goal loop | 🔴 Kritik |
| 2A.2 | Chain-of-thought log sistemi (Thoughts/Reasoning/Plan/Criticism) | **Auto-GPT** COT formatı | 🔴 Kritik |
| 2A.3 | WebSocket canlı log/chain-of-thought akışı | appflowy stream prefix | 🔴 Kritik |
| 2A.4 | Agent lifecycle: pause/resume/stop (asyncio.Event) | Project_Plan.md | 🔴 Kritik |
| 2A.5 | Agent detay modalı (canlı log + zaman çizelgesi) | - | 🔴 Kritik |
| 2A.6 | Looping detection (sonsuz döngü tespiti) | **my-SuperAGI** looping detection | 🟡 Yüksek |
| 2A.7 | Feature flags sistemi (deneysel özellik aç/kapa) | appflowy FeatureFlag | 🟡 Yüksek |
| 2A.8 | Global instructions paneli (tüm ajanların ortak prompt'u) | agentclaw SOUL/USER | 🟡 Yüksek |
| 2A.9 | Backend health/status dashboard | - | 🟢 Orta |

---

## Faz 2B — Agent Yetenekleri + Tool Sistemi
*Faz 1C + 1D biter bitmez başlar. 2A ile paralel.*

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 2B.1 | Tool Registry (abstract Tool class, tool discovery) | **my-SuperAGI** tool sistemi | 🔴 Kritik |
| 2B.2 | WebSearch tool (Google search, web scraping) | **my-SuperAGI** Google Search tool | 🟡 Yüksek |
| 2B.3 | GitHub tool (repo read, issue management) | **my-SuperAGI** GitHub tool | 🟡 Yüksek |
| 2B.4 | Git tool (commit, diff, undo — aider entegrasyonu) | **aider** git integration | 🟡 Yüksek |
| 2B.5 | Looping detection per tool (tool-level) | **my-SuperAGI** | 🟡 Yüksek |
| 2B.6 | Resource manager (token/maliyet takibi) | **my-SuperAGI** resource manager | 🟡 Yüksek |
| 2B.7 | Skill sistemi (role özel prosedür şablonları) | agentclaw Ch.7 | 🟡 Yüksek |
| 2B.8 | Per-agent memory store (çalışma notları, context) | agentclaw Ch.6 | 🟡 Yüksek |
| 2B.9 | Görev zinciri (Ajan-A → Ajan-B → Ajan-C sıralı) | 💡 Yeni fikir | 🟡 Yüksek |
| 2B.10 | Görev şablonları (sık kullanılan görevleri kaydet) | 💡 Yeni fikir | 🟢 Orta |

---

## Faz 2C — MCP Client + Dış Araçlar
*Faz 0 biter bitmez başlar (bağımsız, 1A/1B/1C/1D ile paralel).*

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 2C.1 | MCP Client (harici MCP sunucularına bağlanma) | appflowy MCPClientManager | 🔴 Kritik |
| 2C.2 | Dış MCP tool'larını ajanlara yetenek olarak ekleme | appflowy | 🟡 Yüksek |
| 2C.3 | Ajanlara web scraping/file reading tool yeteneği | appflowy ai_tool | 🟡 Yüksek |
| 2C.4 | In-chain chat komutları (/add, /drop, /undo, /diff, /run) | **aider** komut sistemi | 🟡 Yüksek |
| 2C.5 | Repo haritası (ctags ile kod tabanı anlama) | **aider** repo-map | 🟢 Orta |
| 2C.6 | Continuous mode (kullanıcı onayı olmadan otonom) | **Auto-GPT** continuous mode | 🟢 Orta |

---

## Faz 3A — Production Hardening
*Faz 2A + 2B biter bitmez başlar.*

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 3A.1 | PostgreSQL desteği + Alembic migrasyonlar | - | 🔴 Kritik |
| 3A.2 | API anahtarı şifreleme (AES-256-GCM) | AGENTS.md | 🔴 Kritik |
| 3A.3 | Token kullanım takibi + kota yönetimi (resource manager) | **my-SuperAGI** resource manager | 🟡 Yüksek |
| 3A.4 | Hata kurtarma + otomatik restart (supervisor/process) | - | 🟡 Yüksek |
| 3A.5 | Performance monitoring (istek süresi, token/s) | - | 🟢 Orta |
| 3A.6 | Rate limiting ve abuse prevention | - | 🟢 Orta |

---

## Faz 3B — Ekosistem Genişletme
*Faz 1A + 2C biter bitmez başlar.*

| # | Görev | Kaynak | Öncelik |
|---|-------|--------|---------|
| 3B.1 | Antigravity plugini (MCP uyumlu) | - | 🟢 Orta |
| 3B.2 | Codex CLI entegrasyonu | - | 🟢 Orta |
| 3B.3 | Cursor plugin | - | 🟢 Orta |
| 3B.4 | Windsurf plugin | - | 🟢 Orta |
| 3B.5 | Bot komut dili (doğal dil ile ajan yönetimi) | **aider** in-chain komutlar | 🟢 Orta |
| 3B.6 | CI/CD pipeline (GitHub Actions) | - | 🟢 Orta |
| 3B.7 | Unit test + entegrasyon testleri (tüm fazlar) | - | 🔴 Kritik |
| 3B.8 | Docker Compose deployment | - | 🟢 Orta |

---

## 🏁 Özet

| Faz | Bağımlılık | Süre | Paralel mi? |
|-----|-----------|------|-------------|
| **Faz 0** Foundation | - | 2 gün | ❌ (tek) |
| **Faz 1A** MCP+Panel | Faz 0 | 3-4 gün | ✅ 1B/1C/1D/2C ile |
| **Faz 1B** Telegram Bot | Faz 0 | 2-3 gün | ✅ 1A/1C/1D/2C ile |
| **Faz 1C** Çoklu Model | Faz 0 | 2 gün | ✅ 1A/1B/1D/2C ile |
| **Faz 1D** Auth+Cron+Memory | Faz 0 | 2 gün | ✅ 1A/1B/1C/2C ile |
| **Faz 2A** Task+COT+Log | Faz 1A+1B | 3 gün | ✅ 2B ile |
| **Faz 2B** Tool+Skill+Agent | Faz 1C+1D | 3 gün | ✅ 2A ile |
| **Faz 2C** MCP Client | Faz 0 | 2 gün | ✅ 1A/1B/1C/1D ile |
| **Faz 3A** Production | Faz 2A+2B | 2-3 gün | ✅ 3B ile |
| **Faz 3B** Ekosistem | Faz 1A+2C | 2-3 gün | ✅ 3A ile |
| **Toplam** | | **~20 gün** | **5 paralel kol** |

### Paralel Yapılabilecekler
- Faz 0 (tek başına, önce yapılır)
- Sonra **1A ↔ 1B ↔ 1C ↔ 1D ↔ 2C** — 5 kol paralel
- Sonra **2A ↔ 2B** — 2 kol paralel
- Sonra **3A ↔ 3B** — 2 kol paralel

### Kaynak Referansları
- 📘 `agentclaw` → Telegram/Discord kanalları, cron registry, memory, skill, SOUL/USER
- 📗 `appflowy` → PluginSandbox, MCP Client, LocalAI, stream events, feature flags
- 📙 `lobe-chat` → Multi-provider pattern, plugin registry, Ollama integration, UI design **(YENİ)**
- 📕 `my-SuperAGI` → Tool registry, concurrent workers, resource manager, looping detection **(YENİ)**
- 📔 `Auto-GPT` → Chain-of-thought, memory backends, continuous mode, CLI flags **(YENİ)**
- 📒 `aider` → Git integration, repo-map, in-chain chat commands, VCR testing **(YENİ)**
- 📘 `AgentGPT` → Goal-based task loop, Prisma schema, UX patterns **(YENİ)**
- 📙 `Project_Plan.md` → Master-Worker modeli, 8 işçi ajan, kota izolasyonu, WebSocket izleme
- 💡 `Yeni fikir` → hiçbirinde olmayan, bu projeye özgü özellikler
