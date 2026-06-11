<p align="center">
  <img src="https://placehold.co/120x120/1a1a2e/eee?text=AM" alt="AgentManager Logo" width="120" height="120"/>
</p>

<h1 align="center">AgentManager</h1>

<p align="center">
  <b>Çoklu-Ajan Orkestrasyon Platformu</b><br>
  <b>Multi-Agent Orchestration Platform</b>
</p>

<p align="center">
  <i>Tüm yapay zeka modelleri için evrensel ajan yönetimi, otonom planlama ve zengin ekosistem</i><br>
  <i>Universal agent management, autonomous planning, and rich ecosystem for all AI models</i>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-purple">
</p>

---

## 🇹🇷 Türkçe

### AgentManager Nedir?

**AgentManager**, birden çok yapay zeka sağlayıcısını (Claude, Gemini, GPT, Ollama, OpenRouter...) tek bir çatı altında yönetmenizi, otonom görev zincirleri kurmanızı ve bunları popüler IDE/CLI platformlarıyla entegre etmenizi sağlayan, **platform-bağımsız** ve production-ready bir multi-agent orkestrasyon sistemidir.

Ajanlarınızın durumunu, düşünen akışlarını (Chain-of-Thought) ve araç kullanımlarını gerçek zamanlı izleyebileceğiniz modern bir web panelinin yanı sıra; VS Code, Windsurf, Cursor gibi popüler IDE'ler için eklentiler ve komut satırı araçları (Codex CLI) sunar.

### Temel Özellikler

*   🤖 **Gelişmiş Çoklu Sağlayıcı (Multi-Provider)**: Her ajan için bağımsız model (OpenAI, Anthropic, Google, OpenRouter, Ollama) seçimi ve hata durumunda otomatik model değiştirme (fallback).
*   🎯 **Hedef Odaklı Görev Yönetimi (Goal-Based Task Queue)**: Verilen ana hedefleri alt görevlere bölen, önceliklendiren ve sırayla otonom olarak işleten akıllı kuyruk sistemi.
*   💭 **Chain-of-Thought (CoT) & WebSocket Canlı Log**: Ajanların düşüncelerini, planlarını, eleştirilerini ve aksiyonlarını gerçek zamanlı takip etme.
*   🔄 **Continuous Mode (Otonom Çalışma)**: Kullanıcı onayı gerekmeden ajanların hedefe ulaşana kadar otonom döngüde çalışabilmesi.
*   🗺️ **Repo Map (Kod Haritası)**: Ajanların kod tabanını daha iyi anlaması için AST ve ctags tabanlı kaynak kod haritalandırma motoru.
*   🛡️ **Kurumsal Güvenlik & Dayanıklılık (Production Hardening)**:
    *   **PostgreSQL & SQLite**: Geliştirme için hafif, canlı ortam için gelişmiş DB entegrasyonu.
    *   **AES-256 API Key Şifreleme**: Hassas API anahtarlarının şifreli saklanması.
    *   **Token & Kota Takibi**: Ajan başına token limitleri, maliyet analizi ve bütçelendirme.
    *   **Supervisor Hata Kurtarma**: Çöken ajanların durumunu saklayıp otomatik yeniden başlatma.
    *   **Rate Limiting**: API koruması ve istek limitleme.

### Desteklenen Platformlar

| Platform | Tip | Durum |
|----------|-----|-------|
| **VS Code** | Extension (TS + Webview) | ✅ Tamamlandı |
| **Windsurf** | Extension (TS + Status bar) | ✅ Tamamlandı |
| **Cursor** | Extension (Webview + Chat) | ✅ Tamamlandı |
| **Antigravity** | MCP Plugin (FastAPI mount) | ✅ Tamamlandı |
| **Codex CLI** | MCP over stdio CLI | ✅ Tamamlandı |
| **Diğer MCP istemcileri** | Standard MCP SDK | ✅ Uyumlu |

### Hızlı Kurulum

```bash
# Core (FastAPI) bağımlılıklarını kurun
cd agentmanager-core
pip install -r requirements.txt

# Panel (React) bağımlılıklarını kurun
cd ../panel
npm install

# Eklenti ve platform araçlarını kurun
cd ../agentmanager-plugins
npm install
```

### Çalıştırma

```bash
# Core backend'i başlatın (Port: 3010)
npm run dev # veya doğrudan python core başlatıcı

# Web panel arayüzünü açın
# http://localhost:3010
```

---

## 🇬🇧 English

### What is AgentManager?

**AgentManager** is a **platform-independent**, production-ready multi-agent orchestration system that allows you to manage multiple AI providers (Claude, Gemini, GPT, Ollama, OpenRouter...) under a single interface, construct autonomous task pipelines, and integrate them with popular IDEs and CLI tools.

It comes with a modern React web panel to monitor agent status, Chain-of-Thought (CoT) reasoning, and tool executions in real-time, accompanied by plugins for VS Code, Windsurf, Cursor, and a command-line interface (Codex CLI).

### Core Features

*   🤖 **Advanced Multi-Provider Routing**: Independent model assignment per agent (OpenAI, Anthropic, Google, OpenRouter, Ollama) with automated fallback management.
*   🎯 **Goal-Based Task Queue & Executor**: Smart queue engine that decomposes high-level goals into subtasks, prioritizing and executing them autonomously.
*   💭 **Chain-of-Thought (CoT) & WebSocket Streaming**: Real-time visualization of agent reasoning steps (Thought -> Reasoning -> Plan -> Criticism -> Action).
*   🔄 **Continuous Mode**: Autonomous mode allowing agents to loop and accomplish goals without requiring constant user approval.
*   🗺️ **Repo Map**: AST and ctags-based codebase mapper for agents to better navigate and understand project structures.
*   🛡️ **Production Hardening & Enterprise Resilience**:
    *   **PostgreSQL & SQLite**: Toggle between local development SQLite and production PostgreSQL.
    *   **AES-256 API Key Encryption**: Fernet-based cryptographic storage of external API keys.
    *   **Token & Quota Tracker**: Token consumption limits, cost estimations, and resource management.
    *   **Supervisor Crash Recovery**: Session state checkpointing and automatic agent restart (up to 3 retries).
    *   **Rate Limiting**: Global Token Bucket middleware protecting the API.

### Supported Platforms

| Platform | Type | Status |
|----------|------|--------|
| **VS Code** | Extension (TS + Webview) | ✅ Completed |
| **Windsurf** | Extension (TS + Status bar) | ✅ Completed |
| **Cursor** | Extension (Webview + Chat) | ✅ Completed |
| **Antigravity** | MCP Plugin (FastAPI SSE) | ✅ Completed |
| **Codex CLI** | MCP over stdio CLI | ✅ Completed |
| **Other MCP Clients** | Standard MCP SDK | ✅ Compatible |

### Quick Start

```bash
# Install Core (FastAPI) dependencies
cd agentmanager-core
pip install -r requirements.txt

# Install Panel (React) dependencies
cd ../panel
npm install

# Install plugin/extension dependencies
cd ../agentmanager-plugins
npm install
```

### Running

```bash
# Start core backend (Port: 3010)
npm run dev

# Open the web panel
# http://localhost:3010
```

---

## Proje Yapısı / Project Structure

```
AgentManager/
├── agentmanager-core/      # Python FastAPI Çekirdek / Python FastAPI Core
│   ├── src/                # İş mantığı, Ajanlar, Loglama, Kota, Hata Kurtarma
│   └── tests/              # Test suite (244+ test)
├── agentmanager-plugins/   # IDE Eklentileri / IDE Plugins (VS Code, Windsurf, Cursor, Codex CLI)
│   └── src/
├── panel/                  # React Web Panel Arayüzü / React Web Panel
│   ├── src/
│   └── public/
└── docs/                   # Dokümantasyon / Documentation
    └── help/               # Yardım dökümanları / User Guides (Kurulum, Ajan Yönetimi, SSS)
```

---

## Dokümantasyon / Documentation

| 🇹🇷 Türkçe | 🇬🇧 English |
|------------|-------------|
| [Kurulum Kılavuzu](docs/help/kurulum.md) | [Setup Guide](docs/help/setup.md) |
| [Kullanım Kılavuzu](docs/help/kullanim.md) | [Usage Guide](docs/help/usage.md) |
| [Ajan Yönetimi](docs/help/ajan-yonetimi.md) | [Agent Management](docs/help/agent-management.md) |
| [SSS](docs/help/sss.md) | [FAQ](docs/help/faq.md) |
| [Tasarım Dokümanı](docs/2026-06-11-agentmanager-plugin-design.md) | [Design Document](docs/2026-06-11-agentmanager-plugin-design.md) |

---

<p align="center">
  <sub>
    AgentManager — Tüm yapay zeka modelleri için multi-agent orkestrasyon<br>
    Multi-agent orchestration for all AI models
  </sub>
</p>
