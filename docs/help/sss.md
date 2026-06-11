# Sıkça Sorulan Sorular (SSS)

## Genel

### AgentManager nedir?
AgentManager, birden çok yapay zeka modelini tek bir çatı altında yönetmenizi sağlayan, platform-bağımsız bir multi-agent orkestrasyon bileşenidir. VS Code, Antigravity, Codex CLI gibi platformlara eklenti veya MCP sunucusu olarak kurulur.

### Hangi AI modellerini destekliyor?
OpenAI (GPT-4, GPT-4o, o1), Anthropic (Claude 3.5, 4), Google (Gemini Pro, Ultra), OpenRouter (tüm modeller) ve Ollama (yerel modeller: Llama 3, Mistral, vb.). OpenAI-uyumlu API sunan herhangi bir özel uç nokta da desteklenir.

### Bir ajanın modelini sonradan değiştirebilir miyim?
Evet. Runtime'da herhangi bir ajanın modelini ve sağlayıcısını değiştirebilirsiniz. Devam eden görev varsa mevcut modelleriyle tamamlanır.

### Kaç tane ajan oluşturabilirim?
Sınırsız. Tek sınır sağlayıcılarınızın API kotaları ve rate limitleridir.

## Kurulum

### Python 3.11'im yok, 3.10 ile çalışır mı?
Python 3.10+ ile çalışır ancak 3.11 önerilir (asyncio iyileştirmeleri, ExceptionGroups).

### VS Code eklentisi hangi VS Code sürümlerini destekliyor?
VS Code 1.85+ (2024). Webview panel için modern HTML/CSS desteği gerekir.

### Windows'da çalışıyor mu?
Evet. Python Core Windows'da tam desteklidir. VS Code eklentisi de Windows'da test edilmiştir.

## Kullanım

### Ajan neden yanıt vermiyor?
1. `agentmanager status` ile core'un çalıştığını kontrol edin
2. Sağlayıcı API anahtarının doğru olduğundan emin olun: `agentmanager provider list`
3. Web panelinde ajanın durumunu kontrol edin
4. Logları inceleyin: Web paneli > Ajan detayı > Loglar

### Token limitine takıldım, ne yapmalıyım?
1. Daha küçük görevler verin
2. Farklı bir model deneyin (gpt-4 yerine gpt-4o-mini)
3. Token takibi için paneldeki "Token Kullanımı" bölümünü izleyin
4. Gerekirse sağlayıcıdan daha yüksek limit talep edin

### Ajanı yanlışlıkla sildim, geri getirebilir miyim?
Ajan silindiğinde görev geçmişi arşivlenir ancak ajanın kendisi kalıcı olarak silinir. Aynı ayarlarla yeni bir ajan oluşturabilirsiniz.

## Performans

### Çok sayıda ajan çalıştırmak bilgisayarı yavaşlatır mı?
AgentManager'ın kendisi hafiftir (FastAPI + asyncio). Asıl yük LLM API çağrılarındadır — ve bunlar sizin bilgisayarınızda değil, sağlayıcının sunucularında çalışır. Ollama gibi yerel modeller kullanıyorsanız GPU/CPU kullanımı artar.

### Ajanlar paralel çalışabilir mi?
Evet. Tüm ajanlar asenkron olarak paralel çalışır. Her ajan kendi `asyncio.Task`'inde bağımsız olarak yürütülür.

## Güvenlik

### API anahtarlarım güvende mi?
API anahtarlarınız AES-256-GCM ile şifrelenerek veritabanında saklanır. Sadece runtime'da çözülür ve asla loglanmaz.

### AgentManager internet bağlantısı gerektiriyor mu?
LLM API'leri için evet (Ollama hariç). Ancak core'un kendisi local'de çalışır. Web paneli ve VS Code eklentisi localhost üzerinden bağlanır.

### Ajanlar birbirinin verisini görebilir mi?
Hayır. Her ajan izole çalışır. Bir ajanın çıktısını diğerine iletmek için sizin manuel olarak atamanız gerekir.

## Sorun Giderme

### Core başlamıyor
```
Log: Address already in use
```
→ Port 3010 kullanımda olabilir: `agentmanager start --port 3011`

### WebSocket bağlantısı sürekli kopuyor
→ Güvenlik duvarı/firewall ayarlarını kontrol edin
→ Web proxy kullanıyorsanız WebSocket'leri engellemediğından emin olun

### "Provider not found" hatası
→ Sağlayıcı eklediğinizden emin olun: `agentmanager provider list`
→ Ajan oluştururken doğru sağlayıcı adını kullandığınızı kontrol edin

### API rate limit hatası
→ Aynı sağlayıcıyı kullanan ajan sayısını azaltın
→ Daha düşük öncelikli görevler için farklı bir sağlayıcı ekleyin
