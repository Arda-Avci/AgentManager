import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

interface SimStep {
  type: "THOUGHT" | "PLAN" | "ACTION" | "CRITICISM" | "SUCCESS";
  title: string;
  message: string;
}

const SIMULATION_STEPS: SimStep[] = [
  {
    type: "THOUGHT",
    title: "DÜŞÜNCE (Thought)",
    message: "Hedef: 'panel/src/components/Header.tsx' dosyasındaki eksik TypeScript tip tanımlarını analiz et ve düzelt."
  },
  {
    type: "PLAN",
    title: "PLAN (Plan)",
    message: "1. Dosyayı oku ve derleyici hatalarını belirle.\n2. Interface tanımlarını kontrol et.\n3. Gerekli generic veya opsiyonel tipleri ekle.\n4. Değişiklikleri doğrulamak için tsc çalıştır."
  },
  {
    type: "ACTION",
    title: "EYLEM (Action)",
    message: "HeaderProps interface'i güncelleniyor. 'user' objesine 'avatarUrl?: string' alanı ekleniyor..."
  },
  {
    type: "CRITICISM",
    title: "KRİTİK (Criticism)",
    message: "Düzeltme yapıldı ancak 'avatarUrl' null gelirse fallback görsel kontrolü yapılmalı. Tekrar döngüsüne girmemek için component kodunu incele."
  },
  {
    type: "ACTION",
    title: "EYLEM (Action)",
    message: "Header.tsx bileşeni güncellendi. Arayüze avatarUrl fallback kontrolü eklendi."
  },
  {
    type: "SUCCESS",
    title: "BAŞARI (Success)",
    message: "Tip tanımları başarıyla düzeltildi. ESLint ve TSC kontrolleri hatasız geçti. Görev tamamlandı!"
  }
];

export default function Landing() {
  const [simIndex, setSimIndex] = useState<number>(-1);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    if (isRunning && simIndex < SIMULATION_STEPS.length - 1) {
      timer = setTimeout(() => {
        setSimIndex((prev) => prev + 1);
      }, 2000);
    } else if (simIndex === SIMULATION_STEPS.length - 1) {
      setIsRunning(false);
    }
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [isRunning, simIndex]);

  const startSimulation = () => {
    setSimIndex(0);
    setIsRunning(true);
  };

  const resetSimulation = () => {
    setSimIndex(-1);
    setIsRunning(false);
  };

  return (
    <div className="landing-page">
      {/* Top Gradient Spot */}
      <div className="glowing-spot red-glow"></div>
      <div className="glowing-spot blue-glow"></div>

      {/* Navigation Header */}
      <header className="landing-header">
        <div className="nav-container">
          <div className="landing-logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#logo-grad-1)" />
              <path d="M2 17L12 22L22 17" stroke="url(#logo-grad-2)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M2 12L12 17L22 12" stroke="url(#logo-grad-3)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <defs>
                <linearGradient id="logo-grad-1" x1="2" y1="2" x2="22" y2="12" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#6366f1" />
                  <stop offset="1" stopColor="#a855f7" />
                </linearGradient>
                <linearGradient id="logo-grad-2" x1="2" y1="12" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#6366f1" />
                  <stop offset="1" stopColor="#ec4899" />
                </linearGradient>
                <linearGradient id="logo-grad-3" x1="2" y1="7" x2="22" y2="17" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#4f46e5" />
                  <stop offset="1" stopColor="#a855f7" />
                </linearGradient>
              </defs>
            </svg>
            <span className="logo-text">AgentManager</span>
          </div>

          <nav className="landing-nav">
            <a href="#features">Özellikler</a>
            <a href="#simulator">Simülatör</a>
            <a href="#agents">Hazır Ajanlar</a>
            <a href="#architecture">Mimari</a>
          </nav>

          <div className="landing-nav-actions">
            <Link to="/dashboard" className="btn-nav-primary">
              Paneli Başlat
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="landing-hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="badge-wrapper">
              <span className="hero-badge">Faz 2B: Skill & Delegation Aktif</span>
            </div>
            <h1>
              Yapay Zeka Ajanlarınızı <br />
              <span className="text-gradient">Tek Bir Noktadan</span> Yönetin
            </h1>
            <p>
              FastAPI altyapısı, Model Context Protocol (MCP) desteği ve Chain-of-Thought (CoT) akış motoruyla, 
              otonom yazılım ajanlarınızı koordine edin. Kod yazın, araştırma yapın ve testleri otomatize edin.
            </p>
            <div className="hero-actions">
              <Link to="/dashboard" className="btn-hero-primary">
                Kontrol Panelini Aç
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
              </Link>
              <a href="https://github.com/Arda-Avci/AgentManager" target="_blank" rel="noreferrer" className="btn-hero-secondary">
                GitHub Repository
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                </svg>
              </a>
            </div>
          </div>
          <div className="hero-visual">
            <div className="glass-card visual-card">
              <img src="/assets/hero_bg.png" alt="AgentManager Platform Background" className="visual-image" />
              <div className="visual-overlay"></div>
              <div className="pulse-point p1"></div>
              <div className="pulse-point p2"></div>
              <div className="pulse-point p3"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="landing-features">
        <div className="section-header">
          <h2>Platform Özellikleri</h2>
          <p>Yapay zeka ekosistemindeki en güçlü kalıpları tek bir çatı altında birleştirdik.</p>
        </div>
        <div className="features-grid">
          <div className="glass-card feature-card">
            <div className="feature-icon mcp">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
                <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
                <line x1="6" y1="6" x2="6.01" y2="6"></line>
                <line x1="6" y1="18" x2="6.01" y2="18"></line>
              </svg>
            </div>
            <h3>MCP Server & Client</h3>
            <p>
              Model Context Protocol entegrasyonu sayesinde harici araçlara ve API'lere kolayca bağlanın. Ajanlarınızı dış dünyaya tool olarak sunun.
            </p>
          </div>

          <div className="glass-card feature-card">
            <div className="feature-icon cot">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
            </div>
            <h3>Chain-of-Thought İzleme</h3>
            <p>
              Ajanların problem çözerken yürüttüğü akıl yürütme (Reasoning), planlama ve eleştiri (Criticism) süreçlerini canlı WebSocket akışıyla takip edin.
            </p>
          </div>

          <div className="glass-card feature-card">
            <div className="feature-icon queue">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
              </svg>
            </div>
            <h3>Hedef Tabanlı Task Queue</h3>
            <p>
              Büyük hedefleri otonom olarak parçalayan alt görev yapısı. Sonsuz döngüleri anında fark eden akıllı Loop Detection motoru.
            </p>
          </div>

          <div className="glass-card feature-card">
            <div className="feature-icon llm">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
              </svg>
            </div>
            <h3>Çoklu LLM & Fallback</h3>
            <p>
              Claude, GPT, Gemini ve yerel Ollama modelleri arasında dinamik geçiş. Hata durumlarında otomatik devreye giren yedek sağlayıcılar.
            </p>
          </div>

          <div className="glass-card feature-card">
            <div className="feature-icon telegram">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </div>
            <h3>Telegram Bot Kontrolü</h3>
            <p>
              Ajanlarınızı `/status`, `/pause` veya `/resume` komutlarıyla Telegram'dan yönetin. Düzenli sabah ve akşam raporlarıyla iş gelişimini izleyin.
            </p>
          </div>

          <div className="glass-card feature-card">
            <div className="feature-icon ide">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="16 18 22 12 16 6"></polyline>
                <polyline points="8 6 2 12 8 18"></polyline>
              </svg>
            </div>
            <h3>VS Code & IDE Entegrasyonu</h3>
            <p>
              Geliştirme sürecinizi aksatmadan, ajan yeteneklerini doğrudan VS Code eklentisi ve Webview paneliyle projenize dahil edin.
            </p>
          </div>
        </div>
      </section>

      {/* Simulator Section */}
      <section id="simulator" className="landing-simulator">
        <div className="section-header">
          <h2>Canlı Ajan Simülatörü</h2>
          <p>Bir ajanın arka planda nasıl düşündüğünü ve kararlar aldığını adım adım gözlemleyin.</p>
        </div>

        <div className="simulator-container">
          <div className="simulator-sidebar">
            <div className="sim-controls">
              <button onClick={startSimulation} disabled={isRunning} className="btn-sim-primary">
                {simIndex === -1 ? "Simülasyonu Başlat" : isRunning ? "Çalışıyor..." : "Simülasyon Bitti"}
              </button>
              <button onClick={resetSimulation} className="btn-sim-secondary">
                Sıfırla
              </button>
            </div>
            <div className="sim-status-list">
              {SIMULATION_STEPS.map((step, idx) => (
                <div key={idx} className={`sim-status-item ${simIndex >= idx ? "active" : ""} ${simIndex === idx ? "current" : ""}`}>
                  <span className={`sim-dot ${step.type.toLowerCase()}`}></span>
                  <span className="sim-item-title">{step.title}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="simulator-terminal">
            <div className="terminal-header">
              <div className="terminal-buttons">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div className="terminal-title">agentmanager-executor.sh</div>
            </div>
            <div className="terminal-body">
              {simIndex === -1 ? (
                <div className="terminal-placeholder">
                  <p>$ agentmanager --run-simulation</p>
                  <p className="blink-text">Simülasyonu başlatmak için butona tıklayın...</p>
                </div>
              ) : (
                <div className="terminal-logs">
                  {SIMULATION_STEPS.slice(0, simIndex + 1).map((step, idx) => (
                    <div key={idx} className={`terminal-line fade-in ${step.type.toLowerCase()}`}>
                      <div className="line-header">
                        <span className="line-symbol">▶</span>
                        <span className="line-type">{step.title}</span>
                      </div>
                      <pre className="line-content">{step.message}</pre>
                    </div>
                  ))}
                  {isRunning && (
                    <div className="terminal-line active-line">
                      <span className="blink-text">Ajan analiz ediyor...</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Predefined Agents Showcase */}
      <section id="agents" className="landing-agents">
        <div className="section-header">
          <h2>Hazır Ajan Şablonları</h2>
          <p>Belirli roller için optimize edilmiş şablonları anında devreye alın.</p>
        </div>

        <div className="agents-grid">
          <div className="glass-card agent-showcase-card">
            <div className="agent-showcase-header">
              <span className="agent-badge code">Yazılım</span>
              <h3>Code-Reviewer</h3>
            </div>
            <p>Kod tabanınızı analiz eder, PR'lardaki kritik mantıksal hataları bulur ve iyileştirme önerilerinde bulunur.</p>
            <div className="agent-skills">
              <span>Git Integration</span>
              <span>Aider Pattern</span>
              <span>ESLint Check</span>
            </div>
          </div>

          <div className="glass-card agent-showcase-card">
            <div className="agent-showcase-header">
              <span className="agent-badge research">Araştırma</span>
              <h3>Researcher</h3>
            </div>
            <p>Google Search ve Web Scraping entegrasyonuyla interneti tarar, verileri filtreler ve raporlar hazırlar.</p>
            <div className="agent-skills">
              <span>Web Search</span>
              <span>Content Scraping</span>
              <span>Markdown Export</span>
            </div>
          </div>

          <div className="glass-card agent-showcase-card">
            <div className="agent-showcase-header">
              <span className="agent-badge qa">Test</span>
              <h3>QA-Tester</h3>
            </div>
            <p>Geliştirdiğiniz kodlar için otomatik testler yazar, uç durumları (edge cases) araştırır ve rapor sunar.</p>
            <div className="agent-skills">
              <span>Vitest / Jest</span>
              <span>PyTest</span>
              <span>VCR Recorder</span>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="landing-architecture">
        <div className="section-header">
          <h2>Sistem Mimarisi</h2>
          <p>Python Core ile harici arayüzlerin ve ajanların eşsiz uyumu.</p>
        </div>

        <div className="architecture-container">
          <div className="architecture-text">
            <div className="arch-step">
              <div className="arch-num">1</div>
              <div>
                <h4>Platform & IDE</h4>
                <p>Kullanıcılar React Web Panel veya VS Code eklentisi üzerinden ajanları yönetir ve görevleri tanımlar.</p>
              </div>
            </div>

            <div className="arch-step">
              <div className="arch-num">2</div>
              <div>
                <h4>Python Orkestratör</h4>
                <p>FastAPI tabanlı çekirdek, görevleri yönetir, WebSocket üzerinden canlı durumları ve COT loglarını yayınlar.</p>
              </div>
            </div>

            <div className="arch-step">
              <div className="arch-num">3</div>
              <div>
                <h4>Ajan ve Tool Havuzu</h4>
                <p>Ajanlar master-worker hiyerarşisinde çalışır. MCP Client ile veritabanı, arama motorları ve Git gibi harici araçları (tools) kullanır.</p>
              </div>
            </div>
          </div>

          <div className="architecture-visual">
            <div className="glass-card visual-card">
              <img src="/assets/agent_collab.png" alt="AgentManager Architecture Illustration" className="visual-image" />
              <div className="visual-overlay"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action (CTA) */}
      <section className="landing-cta">
        <div className="cta-content">
          <h2>Ajan Gücünüzü Serbest Bırakın</h2>
          <p>Daha verimli ve otonom bir yazılım geliştirme ekosistemine şimdi geçiş yapın.</p>
          <Link to="/dashboard" className="btn-cta">
            Kontrol Panelini Başlat
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-container">
          <p>&copy; 2026 AgentManager. Tüm Hakları Saklıdır.</p>
          <div className="footer-links">
            <a href="https://github.com/Arda-Avci/AgentManager" target="_blank" rel="noreferrer">GitHub</a>
            <a href="#features">Özellikler</a>
            <a href="/dashboard">Dashboard</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
