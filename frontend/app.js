/* ==========================================================================
   DEUTSCHE TELEKOM TELEAGENT AI — CORPORATE TECH PRODUCT WEBSITE
   Interactive Frontend Engine & Stateful Agent Synchronizer v5.0
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const API_URL = '/api/chat';

  // Mobile Hamburger Menu Toggle
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
  
  function toggleMobileMenu() {
    const isExpanded = document.body.classList.toggle('mobile-menu-open');
    if (mobileMenuBtn) {
      mobileMenuBtn.setAttribute('aria-expanded', isExpanded);
    }
  }
  
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', toggleMobileMenu);
  }
  if (mobileMenuOverlay) {
    mobileMenuOverlay.addEventListener('click', () => {
      if (document.body.classList.contains('mobile-menu-open')) {
        toggleMobileMenu();
      }
    });
  }

  // Close mobile menu on link click
  document.querySelectorAll('.nav-link, .btn-primary-nav').forEach(link => {
    link.addEventListener('click', () => {
      if (document.body.classList.contains('mobile-menu-open')) toggleMobileMenu();
    });
  });

  // Smooth Scroll Active Nav Link Highlight
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('section');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      if (pageYOffset >= sectionTop - 150) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });

  // Global Helper to trigger Ask AI & scroll smoothly to live playground
  window.triggerAskAI = function(promptText) {
    const playgroundEl = document.getElementById('playground');
    if (playgroundEl) {
      playgroundEl.scrollIntoView({ behavior: 'smooth' });
    }

    const userInput = document.getElementById('userInput');
    const chatForm = document.getElementById('chatForm');
    if (userInput && chatForm) {
      userInput.value = promptText;
      setTimeout(() => {
        chatForm.dispatchEvent(new Event('submit'));
      }, 400);
    }
  };

  // State Variables
  let currentChannel = 'OneShop Web';
  let currentAbVariant = 'Variant A (Discount Focus)';

  // Core UI Elements
  const customerSelect = document.getElementById('customerSelect');
  const btnOneShop = document.getElementById('btnOneShop');
  const btnOneApp = document.getElementById('btnOneApp');
  const btnVariantA = document.getElementById('btnVariantA');
  const btnVariantB = document.getElementById('btnVariantB');
  const channelIndicator = document.getElementById('channelIndicator');
  const clearChatBtn = document.getElementById('clearChatBtn');

  const messagesContainer = document.getElementById('messagesContainer');
  const chatForm = document.getElementById('chatForm');
  const userInput = document.getElementById('userInput');

  const cartDrawer = document.getElementById('cartDrawer');
  const openCartBtn = document.getElementById('openCartBtn');
  const closeCartBtn = document.getElementById('closeCartBtn');

  const xaiModal = document.getElementById('xaiModal');
  const closeXaiBtn = document.getElementById('closeXaiBtn');

  const nbaActionBtn = document.getElementById('nbaActionBtn');

  // Customer Selector Handler
  if (customerSelect) {
    customerSelect.addEventListener('change', () => {
      const selectedId = customerSelect.value;
      appendLog('Subscriber Engine', `Switched active subscriber context to [${selectedId}]`, 'system');
      fetchCart();
    });
  }

  // 1. Omnichannel Viewport Switcher Handlers
  if (btnOneShop && btnOneApp) {
    btnOneShop.addEventListener('click', () => {
      btnOneShop.classList.add('active');
      btnOneApp.classList.remove('active');
      document.body.className = 'mode-oneshop';
      currentChannel = 'OneShop Web';
      if (channelIndicator) {
        channelIndicator.innerHTML = `
          <span class="channel-icon">💻</span>
          <span class="channel-title">Connected via <strong>OneShop Web Storefront</strong></span>
          <span class="sync-tag">⚡ State Synced (Session: session_default)</span>
        `;
      }
      appendLog('Omnichannel Sync', 'Switched viewport context to OneShop Web Storefront', 'system');
    });

    btnOneApp.addEventListener('click', () => {
      btnOneApp.classList.add('active');
      btnOneShop.classList.remove('active');
      document.body.className = 'mode-oneapp';
      currentChannel = 'OneApp Mobile';
      if (channelIndicator) {
        channelIndicator.innerHTML = `
          <span class="channel-icon">📱</span>
          <span class="channel-title">Connected via <strong>OneApp Mobile Client</strong></span>
          <span class="sync-tag">⚡ State Synced (Session: session_default)</span>
        `;
      }
      appendLog('Omnichannel Sync', 'Switched viewport context to OneApp Mobile Client', 'system');
    });
  }

  // 2. A/B Strategy Switcher Handlers
  if (btnVariantA && btnVariantB) {
    btnVariantA.addEventListener('click', () => {
      btnVariantA.classList.add('active');
      btnVariantB.classList.remove('active');
      currentAbVariant = 'Variant A (Discount Focus)';
      appendLog('A/B Testing Engine', 'Switched AI strategy to Variant A (Discount Focus)', 'system');
    });

    btnVariantB.addEventListener('click', () => {
      btnVariantB.classList.add('active');
      btnVariantA.classList.remove('active');
      currentAbVariant = 'Variant B (Speed Focus)';
      appendLog('A/B Testing Engine', 'Switched AI strategy to Variant B (Speed & Latency Focus)', 'system');
    });
  }

  // 3. Quick Action Chips & NBA Buttons
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const promptText = chip.getAttribute('data-prompt');
      window.triggerAskAI(promptText);
    });
  });

  if (nbaActionBtn) {
    nbaActionBtn.addEventListener('click', () => {
      window.triggerAskAI('Check my Speedport WiFi speed and router diagnostics in Bonn right now.');
    });
  }

  // Clear Session History
  if (clearChatBtn) {
    clearChatBtn.addEventListener('click', () => {
      messagesContainer.innerHTML = `
        <div class="message assistant-message">
          <div class="avatar"><img src="public/logo.png" alt="Logo" style="max-width: 100%; max-height: 100%;"></div>
          <div class="message-content">
            <div class="assistant-welcome-header">
              <span class="welcome-badge">DEUTSCHE TELEKOM DIGITAL LABS</span>
              <h4>Session History Reset</h4>
            </div>
            <p>Omnichannel Multi-Agent graph reset. BNetzA & GDPR compliance active.</p>
          </div>
        </div>
      `;
      appendLog('Session Engine', 'Cleared active chat history and graph state', 'system');
    });
  }

  // 4. Voice Assistant Handler (Web Speech API + Fallback)
  const micBtn = document.getElementById('micBtn');
  if (micBtn) {
    micBtn.addEventListener('click', () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
          micBtn.classList.add('listening');
          userInput.placeholder = "Listening to your voice... Speak now!";
          appendLog('Voice Assistant', '🎙️ Listening to microphone stream...', 'system');
        };

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          userInput.value = transcript;
          appendLog('Voice Assistant', `Transcribed Voice Input: "${transcript}"`, 'system');
          chatForm.dispatchEvent(new Event('submit'));
        };

        recognition.onerror = (event) => {
          micBtn.classList.remove('listening');
          userInput.placeholder = "Ask about billing, WiFi speed, router reboot, 5G plans, or speak...";
          appendLog('Voice Assistant', `⚠️ Speech Recognition error: ${event.error}`, 'system');
        };

        recognition.onend = () => {
          micBtn.classList.remove('listening');
          userInput.placeholder = "Ask about billing, WiFi speed, router reboot, 5G plans, or speak...";
        };

        try { recognition.start(); } catch (e) { console.error(e); }
      } else {
        const sampleVoicePrompts = [
          "Check my Speedport WiFi speed and router diagnostics in Bonn right now.",
          "Please apply a bill credit refund of €29.75 for the unrecognized FIFA pass charge.",
          "Recommend a Magenta 5G Unlimited package and Speedport WiFi 6 Mesh Extender."
        ];
        const chosenVoice = sampleVoicePrompts[Math.floor(Math.random() * sampleVoicePrompts.length)];

        micBtn.classList.add('listening');
        userInput.placeholder = "Listening to voice input...";
        appendLog('Voice Assistant', '🎙️ Voice Assistant Active (Demo Simulation Mode)...', 'system');

        setTimeout(() => {
          micBtn.classList.remove('listening');
          userInput.value = chosenVoice;
          userInput.placeholder = "Ask about billing, WiFi speed, router reboot, 5G plans, or speak...";
          appendLog('Voice Assistant', `Transcribed Voice Input: "${chosenVoice}"`, 'system');
          chatForm.dispatchEvent(new Event('submit'));
        }, 500);
      }
    });
  }

  // 5. HITL Approval Handlers
  const hitlBanner = document.getElementById('hitlBanner');
  const approveBtn = document.getElementById('approveBtn');
  const rejectBtn = document.getElementById('rejectBtn');

  if (approveBtn) {
    approveBtn.addEventListener('click', async () => {
      if (hitlBanner) hitlBanner.style.display = 'none';
      const customerId = customerSelect ? customerSelect.value : 'CUST-101';
      appendLog('Human Supervisor', 'Approved €29.75 refund credit action (BNetzA SLA)', 'system');
      
      try {
        const res = await fetch('/api/approve-action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ approved: true, customer_id: customerId })
        });
        const data = await res.json();
        appendMessage(`✅ **Action Executed**: ${data.message}`, 'assistant');
        appendLog('Billing Agent', 'Transaction TXN-SEPA-DE-9982341 applied successfully', 'tool');
        fetchCart();
      } catch (err) {
        appendMessage(`⚠️ Error approving action: ${err.message}`, 'assistant');
      }
    });
  }

  if (rejectBtn) {
    rejectBtn.addEventListener('click', () => {
      if (hitlBanner) hitlBanner.style.display = 'none';
      appendLog('Human Supervisor', 'Cancelled financial credit action', 'system');
      appendMessage('❌ **Action Cancelled**: Bill refund credit was declined by Human Supervisor.', 'assistant');
    });
  }

  // 6. Form Submit Handler for Chat
  if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const promptText = userInput.value.trim();
      if (!promptText) return;

      appendMessage(promptText, 'user');
      userInput.value = '';
      if (hitlBanner) hitlBanner.style.display = 'none';

      const loadingMessageId = appendLoadingMessage();
      const customerId = customerSelect ? customerSelect.value : 'CUST-101';

      resetAgentNodes();
      setAgentNodeActive('supervisor');

      appendLog('Supervisor', `[${currentChannel}] Processing intent: "${promptText.substring(0, 30)}..."`, 'system');

      try {
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: promptText, customer_id: customerId, ab_variant: currentAbVariant })
        });

        const data = await response.json();
        removeMessage(loadingMessageId);

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to communicate with AI server');
        }

        if (data.active_agent) {
          setAgentNodeActive(data.active_agent);
        }

        if (data.execution_logs && data.execution_logs.length > 0) {
          data.execution_logs.forEach(log => {
            appendLog(log.node || 'Agent', log.action || log.reasoning, 'tool');
          });
        }

        appendMessage(data.response, 'assistant', data.tool_outputs);

        if (data.requires_human_approval && hitlBanner) {
          hitlBanner.style.display = 'flex';
          appendLog('HITL Checkpoint', 'Sensitive financial tool execution paused. Awaiting human confirmation...', 'system');
        }

      } catch (err) {
        removeMessage(loadingMessageId);
        appendMessage(`⚠️ Error: ${err.message}`, 'assistant');
        appendLog('Error', err.message, 'system');
      }
    });
  }

  // 7. Cart Drawer Controls
  if (openCartBtn && closeCartBtn && cartDrawer) {
    openCartBtn.addEventListener('click', () => {
      fetchCart();
      cartDrawer.classList.add('open');
    });

    closeCartBtn.addEventListener('click', () => {
      cartDrawer.classList.remove('open');
    });
  }

  async function fetchCart() {
    const customerId = customerSelect ? customerSelect.value : 'CUST-101';
    try {
      const res = await fetch(`/api/cart/${customerId}`);
      const data = await res.json();

      const customerNameEl = document.getElementById('cartCustomerName');
      const cartItemsList = document.getElementById('cartItemsList');
      const cartSubtotal = document.getElementById('cartSubtotal');
      const cartDiscount = document.getElementById('cartDiscount');
      const cartTotal = document.getElementById('cartTotal');
      const cartCount = document.getElementById('cartCount');
      const cartNudgeBox = document.getElementById('cartNudgeBox');

      if (customerNameEl) {
        if (customerId === 'CUST-101') customerNameEl.textContent = 'Alex Mercer (Bonn, Germany)';
        else if (customerId === 'CUST-102') customerNameEl.textContent = 'Sarah Connor (Berlin, Germany)';
        else customerNameEl.textContent = 'Lukas Weber (Frankfurt, Germany)';
      }

      let itemsHTML = '';
      if (data.cart_items && data.cart_items.length > 0) {
        data.cart_items.forEach(item => {
          itemsHTML += `
            <div class="cart-item-row">
              <div class="cart-item-info">
                <strong>${item.name}</strong>
                <span>${item.type}</span>
              </div>
              <div class="cart-item-price">€${item.price.toFixed(2)}</div>
            </div>
          `;
        });
        if (cartCount) cartCount.textContent = data.cart_items.length;
      } else {
        itemsHTML = '<p style="font-size:0.8rem; color:var(--text-muted);">Cart is empty.</p>';
        if (cartCount) cartCount.textContent = '0';
      }

      if (cartItemsList) cartItemsList.innerHTML = itemsHTML;
      if (cartSubtotal) cartSubtotal.textContent = data.subtotal_base || data.subtotal;
      if (cartDiscount) cartDiscount.textContent = `-${data.bundle_discount}`;
      if (cartTotal) cartTotal.textContent = data.total;

      if (cartNudgeBox) {
        if (data.applied_nudge) {
          cartNudgeBox.innerHTML = `<div class="nudge-icon">🎉</div> <div class="nudge-text">${data.applied_nudge}</div>`;
        } else {
          cartNudgeBox.innerHTML = `<div class="nudge-icon">🎁</div> <div class="nudge-text">Add <strong>Speedport WiFi 6 Mesh Disc (€4.95/mo)</strong> to unlock MagentaEins discount!</div>`;
        }
      }

    } catch (err) {
      console.error('Failed to fetch cart:', err);
    }
  }

  window.addToCart = function(name, price, type) {
    fetchCart();
    if (cartDrawer) cartDrawer.classList.add('open');
    appendLog('Smart Cart', `Added [${name}] (€${price.toFixed(2)}) to active cart`, 'system');
  };

  // 8. Explainable AI Modal Controls
  if (closeXaiBtn && xaiModal) {
    closeXaiBtn.addEventListener('click', () => {
      xaiModal.style.display = 'none';
    });
  }

  window.openXaiModal = async function(productId = 'PROD-FIBER-1000') {
    const customerId = customerSelect ? customerSelect.value : 'CUST-101';
    try {
      const res = await fetch(`/api/explainable-ai/${productId}?customer_id=${customerId}`);
      const data = await res.json();

      const matchedRulesEl = document.getElementById('xaiMatchedRules');
      const channelStatusEl = document.getElementById('xaiChannelStatus');

      if (matchedRulesEl && data.matched_rules) {
        matchedRulesEl.innerHTML = data.matched_rules.map(r => `<li><span class="check-icon">✓</span> ${r}</li>`).join('');
      }

      if (channelStatusEl && data.omnichannel_status) {
        channelStatusEl.textContent = `⚡ ${data.omnichannel_status}`;
      }

      if (xaiModal) xaiModal.style.display = 'flex';
      appendLog('Explainable AI', `Loaded vector justification for ${data.product || productId}`, 'system');
    } catch (err) {
      console.error('XAI error:', err);
    }
  };

  // UI Message & Log Helpers
  function renderToolOutputHTML(tool) {
    let parsed = null;
    try {
      parsed = JSON.parse(tool.output);
    } catch (e) {
      parsed = null;
    }

    if (parsed && typeof parsed === 'object') {
      if (tool.tool === 'check_router_diagnostics') {
        const healthColor = parsed.wifi_health === 'Optimal' ? 'var(--dt-green)' : 'var(--dt-amber)';
        return `
          <div class="tool-output-card formatted-card">
            <div class="t-card-header">
              <span class="t-card-title">📡 SPEEDPORT ROUTER DIAGNOSTICS</span>
              <span class="t-card-status" style="color:${healthColor}; font-weight:700;">${parsed.wifi_health || 'Online'}</span>
            </div>
            <div class="t-card-grid">
              <div><span>Subscriber:</span> <strong>${parsed.customer_name || 'Alex Mercer'}</strong></div>
              <div><span>Location:</span> <strong>${parsed.location || 'Bonn, Germany'}</strong></div>
              <div><span>Router:</span> <strong>${parsed.router_model || 'Speedport Smart 4'}</strong></div>
              <div><span>Signal:</span> <strong style="color:var(--dt-amber);">${parsed.signal_strength || '-74 dBm'}</strong></div>
              <div><span>Channel:</span> <strong>${parsed.channel_congestion || 'Channel 6'}</strong></div>
              <div><span>Devices:</span> <strong>${parsed.connected_devices || 14} Connected</strong></div>
            </div>
            ${parsed.next_best_action ? `
              <div class="t-card-nba">
                <strong>💡 Next Best Action:</strong> ${parsed.next_best_action.description}
              </div>
            ` : ''}
            <details style="margin-top:0.4rem; font-size:0.68rem; color:var(--text-muted);">
              <summary style="cursor:pointer; font-weight:600;">Inspect Raw JSON Telemetry</summary>
              <pre style="white-space:pre-wrap; margin-top:0.3rem; font-family:var(--font-mono); font-size:0.68rem;">${escapeHtml(JSON.stringify(parsed, null, 2))}</pre>
            </details>
          </div>
        `;
      }

      if (tool.tool === 'fetch_billing_statement') {
        return `
          <div class="tool-output-card formatted-card">
            <div class="t-card-header">
              <span class="t-card-title">💳 MONTHLY INVOICE STATEMENT</span>
              <span class="t-card-status" style="color:var(--dt-red); font-weight:700;">DISCREPANCY</span>
            </div>
            <div class="t-card-grid">
              <div><span>Subscriber:</span> <strong>${parsed.customer_name || 'Alex Mercer'}</strong></div>
              <div><span>Current Plan:</span> <strong>${parsed.current_plan || 'MagentaZuhause Fiber'}</strong></div>
              <div><span>Standard Bill:</span> <strong>${parsed.base_plan_cost || '€59.45'}</strong></div>
              <div><span>Total Billed:</span> <strong style="color:var(--dt-magenta-light);">${parsed.total_billed_with_vat || '€89.20'}</strong></div>
              <div style="grid-column: span 2;"><span>Extra Charge:</span> <strong style="color:var(--dt-red);">${parsed.unexpected_extra_charges || '€29.75'} (${parsed.dispute_reason})</strong></div>
            </div>
            <details style="margin-top:0.4rem; font-size:0.68rem; color:var(--text-muted);">
              <summary style="cursor:pointer; font-weight:600;">Inspect Raw JSON Statement</summary>
              <pre style="white-space:pre-wrap; margin-top:0.3rem; font-family:var(--font-mono); font-size:0.68rem;">${escapeHtml(JSON.stringify(parsed, null, 2))}</pre>
            </details>
          </div>
        `;
      }

      if (tool.tool === 'reboot_router') {
        return `
          <div class="tool-output-card formatted-card">
            <div class="t-card-header">
              <span class="t-card-title">⚡ SPEEDPORT REBOOT & CHANNEL OPTIMIZATION</span>
              <span class="t-card-status" style="color:var(--dt-green); font-weight:700;">SUCCESS</span>
            </div>
            <div style="font-size:0.8rem; color:var(--text-primary); margin-top:0.3rem;">
              ✓ ${parsed.message || 'Router rebooted and channel optimized.'}
            </div>
            <div class="t-card-grid" style="margin-top:0.4rem;">
              <div><span>New Channel:</span> <strong style="color:var(--dt-green);">${parsed.new_channel || 'Channel 11'}</strong></div>
              <div><span>Latency:</span> <strong>${parsed.latency_ms || 6} ms</strong></div>
            </div>
            <details style="margin-top:0.4rem; font-size:0.68rem; color:var(--text-muted);">
              <summary style="cursor:pointer; font-weight:600;">Inspect Raw JSON Response</summary>
              <pre style="white-space:pre-wrap; margin-top:0.3rem; font-family:var(--font-mono); font-size:0.68rem;">${escapeHtml(JSON.stringify(parsed, null, 2))}</pre>
            </details>
          </div>
        `;
      }

      if (tool.tool === 'apply_bill_credit') {
        return `
          <div class="tool-output-card formatted-card">
            <div class="t-card-header">
              <span class="t-card-title">✅ SEPA DIRECT DEBIT CREDIT RECEIPT</span>
              <span class="t-card-status" style="color:var(--dt-green); font-weight:700;">APPROVED</span>
            </div>
            <div class="t-card-grid">
              <div><span>Transaction ID:</span> <strong>${parsed.transaction_id || 'TXN-SEPA-DE-9982341'}</strong></div>
              <div><span>Credited Amount:</span> <strong style="color:var(--dt-green);">${parsed.credited_amount || '€29.75'}</strong></div>
              <div style="grid-column: span 2;"><span>Target IBAN:</span> <strong>${parsed.credited_to_iban || 'SEPA Account'}</strong></div>
            </div>
            <details style="margin-top:0.4rem; font-size:0.68rem; color:var(--text-muted);">
              <summary style="cursor:pointer; font-weight:600;">Inspect Raw SEPA JSON</summary>
              <pre style="white-space:pre-wrap; margin-top:0.3rem; font-family:var(--font-mono); font-size:0.68rem;">${escapeHtml(JSON.stringify(parsed, null, 2))}</pre>
            </details>
          </div>
        `;
      }

      // Generic JSON fallback formatting
      return `
        <div class="tool-output-card formatted-card">
          <div class="t-card-header">
            <span class="t-card-title">⚙️ EXECUTED TOOL: ${tool.tool}</span>
          </div>
          <details open style="margin-top:0.4rem; font-size:0.7rem;">
            <summary style="cursor:pointer; font-weight:600; color:var(--dt-cyan);">Structured Output</summary>
            <pre style="white-space:pre-wrap; margin-top:0.3rem; font-family:var(--font-mono); font-size:0.72rem; color:var(--text-secondary);">${escapeHtml(JSON.stringify(parsed, null, 2))}</pre>
          </details>
        </div>
      `;
    }

    // String fallback
    return `
      <div class="tool-output-card" style="margin-top:0.4rem; padding:0.4rem 0.6rem; background:rgba(10,14,23,0.8); border:1px solid rgba(255,255,255,0.08); border-radius:6px;">
        <span style="font-size:0.65rem; font-weight:700; color:var(--dt-cyan); display:block;">⚙️ EXECUTED TOOL: ${tool.tool}</span>
        <pre style="white-space:pre-wrap; font-size:0.72rem; color:var(--text-secondary); margin-top:0.2rem; font-family:var(--font-mono);">${escapeHtml(tool.output)}</pre>
      </div>
    `;
  }

  function appendMessage(text, sender, toolOutputs = []) {
    if (!messagesContainer) return;

    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', `${sender}-message`);
    const avatarContent = sender === 'user' ? 'YOU' : '<img src="public/logo.png" alt="Logo" style="max-width: 100%; max-height: 100%;">';
    
    let toolCardsHTML = '';
    if (toolOutputs && toolOutputs.length > 0) {
      toolOutputs.forEach(tool => {
        toolCardsHTML += renderToolOutputHTML(tool);
      });
    }

    let feedbackHTML = '';
    if (sender === 'assistant') {
      feedbackHTML = `
        <div class="feedback-actions" style="margin-top:0.6rem; padding-top:0.4rem; border-top:1px solid rgba(255,255,255,0.06); display:flex; align-items:center; gap:0.5rem; font-size:0.75rem; color:var(--text-muted);">
          <span>Rate Answer:</span>
          <button class="feedback-btn" onclick="handleFeedback(this, 'like')" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08); color:#fff; border-radius:4px; padding:0.15rem 0.45rem; cursor:pointer; font-size:0.75rem;">👍 Helpful</button>
          <button class="feedback-btn" onclick="handleFeedback(this, 'dislike')" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08); color:#fff; border-radius:4px; padding:0.15rem 0.45rem; cursor:pointer; font-size:0.75rem;">👎 Needs Work</button>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      <div class="avatar">${avatarContent}</div>
      <div class="message-content">
        <p>${formatMarkdown(text)}</p>
        ${toolCardsHTML}
        ${feedbackHTML}
      </div>
    `;

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendLoadingMessage() {
    const id = 'loading-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'assistant-message');
    msgDiv.id = id;

    msgDiv.innerHTML = `
      <div class="avatar"><img src="public/logo.png" alt="Logo" style="max-width: 100%; max-height: 100%;"></div>
      <div class="message-content">
        <p><em>Thinking & running LangGraph state workflow...</em></p>
      </div>
    `;

    if (messagesContainer) {
      messagesContainer.appendChild(msgDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    return id;
  }

  function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function appendLog(source, text, type = 'system') {
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

    const createEntry = () => {
      const entry = document.createElement('div');
      entry.classList.add('log-entry', `${type}-log`);
      entry.innerHTML = `
        <span class="log-badge ${type === 'tool' ? 'badge-tool' : 'badge-sys'}">${source.toUpperCase()}</span>
        <span class="log-text">[${time}] ${escapeHtml(text)}</span>
      `;
      return entry;
    };

    const logContainer = document.getElementById('logContainer');
    if (logContainer) {
      logContainer.appendChild(createEntry());
      logContainer.scrollTop = logContainer.scrollHeight;
    }
  }

  function resetAgentNodes() {
    document.querySelectorAll('.agent-node').forEach(node => {
      node.classList.remove('active');
      const statusEl = node.querySelector('.node-badge');
      if (statusEl) statusEl.textContent = 'READY';
    });
  }

  function setAgentNodeActive(agentName) {
    resetAgentNodes();
    document.querySelectorAll(`[id*="node-${agentName}"]`).forEach(targetNode => {
      targetNode.classList.add('active');
      const statusEl = targetNode.querySelector('.node-badge');
      if (statusEl) statusEl.textContent = 'ACTIVE';
    });
  }

  function formatMarkdown(str) {
    if (!str) return '';
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  fetchCart();
});

// Global RLHF Feedback Handler
window.handleFeedback = async function(btn, type) {
  const container = btn.parentElement;
  const customerId = document.getElementById('customerSelect') ? document.getElementById('customerSelect').value : 'CUST-101';
  container.innerHTML = `<span style="color:var(--dt-cyan); font-weight:600;">✓ Recorded ${type === 'like' ? '+1.0' : '-1.0'} reward signal via RLHF API</span>`;
  try {
    await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id: customerId, rating: type })
    });
  } catch (e) {
    console.error('Feedback error:', e);
  }
};
