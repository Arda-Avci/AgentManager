# Kurulum Kılavuzu

## Gereksinimler

- **Python 3.11+**
- **Node.js 18+** (VS Code eklentisi ve web paneli için)
- **VS Code** (isteğe bağlı, eklenti kullanımı için)
- Bir **AI API anahtarı** (OpenAI, Anthropic, Google veya OpenRouter)

## 1. Python Core Kurulumu

### pip ile

```bash
pip install agentmanager-core
```

### Kaynaktan

```bash
git clone https://github.com/your-org/agentmanager.git
cd agentmanager/core
pip install -r requirements.txt
```

## 2. VS Code Eklentisi

### VS Code Marketten

1. VS Code'u açın
2. `Ctrl+Shift+X` ile Extensions panelini açın
3. "AgentManager" yazın
4. **Install**'a tıklayın

### Kaynaktan

```bash
cd plugin/vscode
npm install
npm run package
code --install-extension agentmanager-*.vsix
```

## 3. Web Paneli

```bash
cd plugin/web-panel
npm install
npm run build
```

## 4. İlk Çalıştırma

```bash
# Core'u başlat
agentmanager start

# Web panelini aç
# http://localhost:3010

# İlk LLM sağlayıcısını ekle
agentmanager provider add
# > Sağlayıcı adı: my-openai
# > Tip: openai
# > API Anahtarı: sk-...
# > Model: gpt-4
```

## 5. Doğrulama

Terminalde şunu çalıştırın:

```bash
agentmanager status
```

Çıktı:
```
✓ AgentManager Core çalışıyor
  Web Panel: http://localhost:3010
  MCP Server: http://localhost:3010/mcp
  
  Sağlayıcılar:
  - my-openai (openai) ✅
  
  Ajanlar: (henüz ajan oluşturulmamış)
```

## 6. Platform Eklentilerini Etkinleştirme

### VS Code
1. `Ctrl+Shift+P` → "AgentManager: Open Panel"
2. Web panel VS Code içinde açılır

### Antigravity
Antigravity ayarlarından MCP sunucusu olarak ekleyin:
```
Sunucu Adresi: http://localhost:3010/mcp
```

### Codex CLI
```bash
codex --mcp-server http://localhost:3010/mcp
```

## Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| `agentmanager` komutu bulunamıyor | Python'ın Scripts klasörünün PATH'te olduğundan emin olun |
| Port 3010 kullanımda | `agentmanager start --port 3011` ile port değiştirin |
| API anahtarı hatası | `agentmanager provider list` ile sağlayıcıları kontrol edin |
