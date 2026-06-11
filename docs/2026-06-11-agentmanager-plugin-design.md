# AgentManager — Çoklu-Agent Orkestrasyon Eklentisi Tasarım Dokümanı

**Tarih:** 2026-06-11
**Durum:** Kabul Edildi

---

## 1. Hedef

AgentManager, tüm yapay zeka modelleri (Claude, Gemini, GPT, Ollama, OpenRouter vb.) ile çalışan, platform-bağımsız bir multi-agent orkestrasyon bileşenidir. VS Code, Antigravity, Codex CLI gibi platformlara eklenti/MCP server olarak kurulur ve ajanların durumlarını gösteren kalıcı bir web paneli sunar.

---

## 2. Mimari Genel Bakış

```
                    PLATFORM KATMANI
  ┌─────────────────┐ ┌──────────────┐ ┌─────────────────────┐
  │ VS Code Plugin   │ │Antigravity   │ │ Codex CLI / Diğer   │
  │ (TS, Webview)   │ │Plugin (TS)   │ │ MCP Client (her dil)│
  └────────┬────────┘ └──────┬───────┘ └──────────┬──────────┘
           │                 │                    │
           └─────────────────┼────────────────────┘
                             │ MCP Protocol / HTTP

                    SERVİS KATMANI
  ┌──────────────────────────▼──────────────────────────────┐
  │              Python Core HTTP/WS Server (FastAPI)        │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
  │  │Agent     │  │Orkestratör│  │LLM Router│  │Task    │ │
  │  │Registry  │  │(Lifecycle)│  │(Provider │  │Queue   │ │
  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
  │  ┌──────────────────────────────────────────────────┐  │
  │  │           Worker Pool (asyncio subtasks)          │  │
  │  └──────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────┐  ┌──────────────────┐
  │  MCP Server (Python MCP SDK)         │  │  State Store     │
  │  tools: list_agents, assign_task,    │  │  (SQLite/JSON)   │
  │  pause_agent, resume_agent, ...      │  │                  │
  └──────────────────────────────────────┘  └──────────────────┘

                    ARAYÜZ KATMANI
  ┌──────────────────────────────────────────────────────────┐
  │              Web Panel (React + WebSocket)                │
  │  - Ajan kartları (durum, model, görev)                    │
  │  - Canlı log/chain-of-thought akışı                       │
  │  - Pause/Resume/Stop kontrolleri                          │
  │  - Model/provider ekleme/yönetme                          │
  │  - Ajan ekleme/silme/rol değiştirme                       │
  └──────────────────────────────────────────────────────────┘
```

### Veri Akışı

1. Platform (VS Code / Antigravity) → MCP Protocol veya HTTP API ile Python Core'a istek gönderir
2. Python Core → Orkestratör emri ayrıştırır, Task Queue'ya görev ekler
3. Worker Pool → LLM Router üzerinden ilgili ajanın kendi modelini çağırır
4. Ajan → Sonucu Task Queue'ya yazarlar, WebSocket ile panele canlı akar
5. Web Panel → Tüm state değişikliklerini anlık görüntüler

---

## 3. Teknoloji Yığını

| Katman | Teknoloji | Gerekçe |
|--------|-----------|---------|
| Orkestratör, LLM Yönlendirici | Python (asyncio, FastAPI) | En geniş LLM SDK desteği, LangChain/LlamaIndex ekosistemi |
| MCP Server | Python MCP SDK | Aynı süreçte çalışır (IPC yok), doğal entegrasyon |
| Platform Eklentileri | TypeScript | VS Code, Antigravity, Codex CLI için doğal dil |
| Web Panel | React + TypeScript | VS Code Webview uyumu, standalone çalışabilir |
| State Store | SQLite (geliştirme), PostgreSQL (production) | Minimal bağımlılık, ölçeklenebilir |
| Gerçek Zamanlı | WebSocket (FastAPI + ws) | Canlı ajan takibi, düşük gecikme |
| Şifreleme | cryptography (AES-256-GCM) | API anahtarları güvenli saklama |

---

## 4. Python Core Engine (agentmanager/core)

### Dizin Yapısı

```
agentmanager/core/
├── main.py                  # FastAPI uygulaması
├── config.py                # Yapılandırma yönetimi
├── orchestrator/
│   ├── engine.py            # Ana orkestratör döngüsü (asyncio)
│   ├── lifecycle.py         # Agent yaşam döngüsü yönetimi
│   └── scheduler.py         # Görev zamanlama/kuyruk
├── agents/
│   ├── registry.py          # Agent kaydı, rol-şablon eşleme
│   ├── base.py              # BaseAgent (abstract)
│   ├── worker.py            # WorkerAgent implementasyonu
│   └── templates/           # Rol bazlı sistem talimatı şablonları
│       ├── lawyer.yaml
│       ├── developer.yaml
│       ├── frontend.yaml
│       ├── reviewer.yaml
│       └── tester.yaml
├── llm/
│   ├── router.py            # LLM sağlayıcı yönlendirici
│   ├── token_tracker.py     # Token kullanım takibi
│   └── providers/
│       ├── base.py          # BaseProvider (abstract)
│       ├── openai.py        # OpenAI / GPT
│       ├── anthropic.py     # Anthropic / Claude
│       ├── google.py        # Google / Gemini
│       ├── openrouter.py    # OpenRouter (tüm modeller)
│       └── ollama.py        # Yerel Ollama
├── state/
│   ├── store.py             # State yönetimi
│   ├── models.py            # SQLAlchemy modelleri
│   └── migrations/          # Alembic migrasyonları
├── websocket/
│   └── manager.py           # WebSocket bağlantı yönetimi
├── mcp/
│   └── server.py            # MCP Server tanımı
└── api/
    ├── routes.py            # REST API endpoint'leri
    └── schemas.py           # Pydantic şemaları
```

### Temel Soyutlamalar

```python
class BaseAgent(ABC):
    agent_id: str
    role: AgentRole
    llm_provider: BaseProvider
    system_prompt: str
    status: AgentStatus  # idle | running | paused | error
    pause_event: asyncio.Event

    @abstractmethod
    async def execute(task: Task) -> TaskResult: ...
    async def pause(): ...
    async def resume(): ...
    async def stop(): ...

class Orchestrator:
    agents: Dict[str, BaseAgent]
    task_queue: asyncio.Queue
    llm_router: LLMRouter

    async def dispatch(task: Task) -> None: ...
    async def get_agent_status() -> Dict[str, AgentStatus]: ...

class LLMRouter:
    providers: Dict[str, BaseProvider]

    def register_provider(name: str, provider: BaseProvider): ...
    async def complete(model: str, messages, **kwargs) -> Stream: ...

class BaseProvider(ABC):
    @abstractmethod
    async def complete(messages, **kwargs) -> Stream[Chunk]: ...
    @abstractmethod
    async def count_tokens(messages) -> int: ...
```

### Agent Durum Makinesi

```
IDLE → RUNNING → (PAUSED ↔ RUNNING) → IDLE
                  RUNNING → ERROR → IDLE
```

Pause/Resume: Her WorkerAgent bir `asyncio.Event` ile kontrol edilir. `pause()` → `.clear()` ile event askıya alınır, agent state'i dondurur. `resume()` → `.set()` ile kaldığı yerden devam eder.

---

## 5. MCP Server

Python MCP SDK ile aynı süreçte çalışır. Araçlar:

| Tool | Açıklama |
|------|----------|
| `list_agents` | Tüm ajanları listele + durumları |
| `get_agent_detail` | Tek ajan detayı + canlı log |
| `create_agent` | Yeni ajan oluştur (rol + model) |
| `delete_agent` | Ajan kaldır |
| `assign_task` | Ajan'a görev ata |
| `pause_agent` | Ajan'ı duraklat |
| `resume_agent` | Ajan'ı devam ettir |
| `change_agent_role` | Ajan rolünü değiştir |
| `change_agent_model` | Ajan modelini değiştir |
| `get_system_status` | Sistem genel durum |
| `list_providers` | Kayıtlı LLM sağlayıcıları |
| `register_provider` | Yeni LLM sağlayıcısı ekle |

---

## 6. Platform Eklentileri (TypeScript)

```
agentmanager-plugin/
├── packages/
│   ├── vscode/              # VS Code Extension
│   │   ├── src/
│   │   │   ├── extension.ts # Aktivasyon, komutlar
│   │   │   ├── panel.ts     # Webview panel (React)
│   │   │   └── client.ts    # Python Core HTTP istemcisi
│   │   └── package.json
│   ├── antigravity/         # Antigravity plugini
│   │   └── src/index.ts
│   ├── web-panel/           # Bağımsız web paneli (React)
│   │   └── src/
│   └── shared/              # Paylaşılan tipler
│       ├── types.ts
│       └── api-client.ts
└── package.json
```

### VS Code Extension Akışı
1. `Ctrl+Shift+P` → "AgentManager: Open Panel"
2. Extension Python Core'u arka planda başlatır (veya bağlanır)
3. React Webview paneli açar → WebSocket ile canlı güncellenir
4. Kullanıcı panelden ajanları yönetir

### Antigravity Akışı
1. Antigravity'den `manage_worker_agent` tool'u çağrılır
2. Antigravity MCP üzerinden Python Core'a iletir
3. Python Core emri işler, sonucu MCP response olarak döner

---

## 7. Web Panel (React)

Bileşenler:
- **AgentDashboard**: Tüm ajan kartları grid/liste
- **AgentCard**: Tek ajan (isim, rol, model, durum, son görev)
- **AgentDetailModal**: Detay paneli + canlı log akışı (WebSocket)
- **ProviderManager**: LLM sağlayıcı ekleme/düzenleme
- **AgentCreator**: Yeni ajan oluşturma formu
- **SystemStatusBar**: Genel sistem durumu (token kullanımı, aktif ajan)

Her ajan kartında: Pause/Resume/Stop butonları, rol değiştirme, model değiştirme.

---

## 8. Data Model

### agents
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | UUID (PK) | Benzersiz kimlik |
| name | VARCHAR | Ajan adı |
| role | ENUM | lawyer, developer, frontend, reviewer, tester |
| llm_provider_id | UUID (FK) | Kullandığı sağlayıcı |
| model_name | VARCHAR | Model adı (gpt-4, claude-3, gemini-pro) |
| system_prompt | TEXT | Rol sistem talimatı |
| status | ENUM | idle, running, paused, error |
| config | JSON | Ajan özel yapılandırması |
| created_at | TIMESTAMP | Oluşturulma zamanı |
| updated_at | TIMESTAMP | Son güncelleme |

### tasks
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | UUID (PK) | Benzersiz kimlik |
| agent_id | UUID (FK) | Hangi ajan'a ait |
| type | VARCHAR | Görev tipi |
| status | ENUM | pending, running, done, failed |
| priority | INT | Öncelik |
| input | TEXT | Görev girdisi |
| output | TEXT | Görev çıktısı |
| tokens_used | INT | Kullanılan token sayısı |
| created_at | TIMESTAMP | Oluşturulma |
| completed_at | TIMESTAMP | Tamamlanma |

### llm_providers
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | UUID (PK) | Benzersiz kimlik |
| name | VARCHAR | Sağlayıcı adı |
| provider_type | ENUM | openai, anthropic, google, ollama, openrouter |
| api_key | TEXT (encrypted) | AES-256-GCM şifreli |
| base_url | VARCHAR | Özel uç nokta |
| models | JSON | Kullanılabilir modeller listesi |
| is_active | BOOLEAN | Aktif mi |
| created_at | TIMESTAMP | |

### agent_logs
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | UUID (PK) | |
| agent_id | UUID (FK) | |
| level | ENUM | info, warn, error, debug |
| message | TEXT | Log mesajı |
| metadata | JSON | Ek bağlam |
| chain_of_thought | TEXT | Ajanın düşünce zinciri |
| token_count | INT | |
| timestamp | TIMESTAMP | |

### sessions
| Sütun | Tip | Açıklama |
|-------|-----|----------|
| id | UUID (PK) | |
| platform_type | ENUM | vscode, antigravity, codex |
| connected_at | TIMESTAMP | |
| disconnected_at | TIMESTAMP | |
| status | VARCHAR | active, closed |

---

## 9. Güvenlik

- API anahtarları `cryptography` (AES-256-GCM) ile şifrelenir, sadece runtime'da decrypt edilir
- Platform token'ları her istekte session'dan alınır, closure'a capture edilmez
- WebSocket bağlantıları JWT token ile doğrulanır
- Hassas veriler (şifre, token, kişisel bilgi) asla loglanmaz
- Production'da DEBUG log seviyesi kapalı olur

---

## 10. Loglama Standardı

| Seviye | Kullanım |
|--------|----------|
| INFO | Normal akış: ajan başlatıldı, görev tamamlandı |
| WARN | Beklenmedik ama kurtarılabilir: API timeout, rate limit |
| ERROR | Hata: sağlayıcı hatası, bağlantı kopması |
| DEBUG | Geliştirme detayı: LLM prompt/response (sadece dev) |

---

## 11. İlerleme Yolu

1. **Faz 0 — İskelet**: Python Core (FastAPI + SQLite), temel API, BaseAgent, LLMRouter (OpenAI provider)
2. **Faz 1 — MCP + Platform**: MCP Server, VS Code Extension (basit), Web Panel (React, temel)
3. **Faz 2 — Çoklu Model**: Anthropic, Google, Ollama, OpenRouter provider'ları
4. **Faz 3 — Tam Özellikler**: Tüm MCP tools, Agent lifecycle (pause/resume), WebSocket canlı akış
5. **Faz 4 — Production**: PostgreSQL, şifreleme, hata kurtarma, token takibi
6. **Faz 5 — Ekosistem**: Antigravity plugini, Codex CLI, dökümantasyon

---

## 12. Referans Alınan Projeler

- **agentclaw**: Multi-agent workspace template, kanal entegrasyonu, cron/memory/skill sistemi
- **appflowy**: Plugin mimarisi, AI entegrasyonu (MCP Client, Ollama, Cloud AI), Rust+Flutter stack
- **Project_Plan.md**: Master-Worker modeli, 8 işçi ajan, kota izolasyonu, WebSocket izleme
