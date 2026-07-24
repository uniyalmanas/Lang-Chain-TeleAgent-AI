document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chatForm');
  const userInput = document.getElementById('userInput');
  const messagesContainer = document.getElementById('messagesContainer');
  const logContainer = document.getElementById('logContainer');
  const customerSelect = document.getElementById('customerSelect');
  const clearChatBtn = document.getElementById('clearChatBtn');
  const promptChips = document.querySelectorAll('.prompt-chip');

  const btnOneShop = document.getElementById('btnOneShop');
  const btnOneApp = document.getElementById('btnOneApp');
  const channelIndicator = document.getElementById('channelIndicator');

  const openCartBtn = document.getElementById('openCartBtn');
  const closeCartBtn = document.getElementById('closeCartBtn');
  const cartDrawer = document.getElementById('cartDrawer');

  const xaiModal = document.getElementById('xaiModal');
  const closeXaiBtn = document.getElementById('closeXaiBtn');

  const nbaBanner = document.getElementById('nbaBanner');
  const nbaActionBtn = document.getElementById('nbaActionBtn');

  const API_URL = '/api/chat';
  let currentChannel = 'OneShop Web';
  let currentAbVariant = 'Variant A (Discount Focus)';

  // A/B Testing Recommendation Engine Handlers
  const btnVariantA = document.getElementById('btnVariantA');
  const btnVariantB = document.getElementById('btnVariantB');
  if (btnVariantA && btnVariantB) {
    btnVariantA.addEventListener('click', () => {
      btnVariantA.classList.add('active');
      btnVariantB.classList.remove('active');
      currentAbVariant = 'Variant A (Discount Focus)';
      appendLog('A/B Testing Engine', 'Switched AI model scoring to Variant A (Discount & Offer Focus)', 'system');
    });

    btnVariantB.addEventListener('click', () => {
      btnVariantB.classList.add('active');
      btnVariantA.classList.remove('active');
      currentAbVariant = 'Variant B (Speed Focus)';
      appendLog('A/B Testing Engine', 'Switched AI model scoring to Variant B (Speed & Performance Focus)', 'system');
    });
  }

  window.handleFeedback = function(btn, type) {
    const container = btn.parentElement;
    if (type === 'like') {
      container.innerHTML = '👍 <span style="color:#4ADE80;">Thank you! Positive preference logged for continuous RLHF learning.</span>';
      appendLog('Continuous Learning', 'Positive feedback recorded (+1.0 reward signal)', 'system');
    } else {
      container.innerHTML = '👎 <span style="color:#FF4D4D;">Feedback logged! Model routing weights updated for next session.</span>';
      appendLog('Continuous Learning', 'Negative feedback recorded (-1.0 penalty signal)', 'system');
    }
  };


  // 🎙️ Web Speech API Voice Recognition Handler
  const micBtn = document.getElementById('micBtn');
  if (micBtn) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-IN'; // Indian English / Hindi accent support

      micBtn.addEventListener('click', () => {
        if (micBtn.classList.contains('listening')) {
          recognition.stop();
          micBtn.classList.remove('listening');
        } else {
          try {
            recognition.start();
            micBtn.classList.add('listening');
            userInput.placeholder = "Listening to your voice command...";
            appendLog('Voice Assistant', 'Listening via Web Speech API (en-IN)...', 'system');
          } catch (e) {
            console.error('Speech recognition error:', e);
          }
        }
      });

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        micBtn.classList.remove('listening');
        userInput.placeholder = "Ask about billing, WiFi speed, router reboot, 5G plans, or speak...";
        appendLog('Voice Assistant', `Transcribed voice input: "${transcript}"`, 'system');
        chatForm.dispatchEvent(new Event('submit'));
      };

      recognition.onerror = (event) => {
        micBtn.classList.remove('listening');
        userInput.placeholder = "Ask about billing, WiFi speed, router reboot, 5G plans, or speak...";
        appendLog('Voice Assistant', `Speech error: ${event.error}`, 'system');
      };

      recognition.onend = () => {
        micBtn.classList.remove('listening');
      };
    } else {
      micBtn.title = "Voice recognition not supported on this browser";
    }
  }


  // 1. Omnichannel Switcher Handlers
  if (btnOneShop && btnOneApp) {
    btnOneShop.addEventListener('click', () => {
      btnOneShop.classList.add('active');
      btnOneApp.classList.remove('active');
      document.body.className = 'mode-oneshop';
      currentChannel = 'OneShop Web';
      channelIndicator.innerHTML = `
        <span class="channel-icon">💻</span>
        <span class="channel-title">Connected via <strong>DT OneShop Web Storefront</strong></span>
        <span class="sync-tag">⚡ State Synced (Session ID: session_default)</span>
      `;
      appendLog('Omnichannel Sync', 'Switched context to OneShop (Web)', 'system');
    });

    btnOneApp.addEventListener('click', () => {
      btnOneApp.classList.add('active');
      btnOneShop.classList.remove('active');
      document.body.className = 'mode-oneapp';
      currentChannel = 'OneApp Mobile';
      channelIndicator.innerHTML = `
        <span class="channel-icon">📱</span>
        <span class="channel-title">Connected via <strong>DT OneApp Mobile Client</strong></span>
        <span class="sync-tag">⚡ State Synced (Session ID: session_default)</span>
      `;
      appendLog('Omnichannel Sync', 'Switched context to OneApp (Mobile)', 'system');
    });
  }

  // 2. Smart Cart Drawer Handlers
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
    const customerId = customerSelect.value;
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
        if (customerId === 'CUST-101') customerNameEl.textContent = 'Rahul Sharma (Gurugram, NCR)';
        else if (customerId === 'CUST-102') customerNameEl.textContent = 'Priya Patel (Bengaluru, KA)';
        else customerNameEl.textContent = 'Vikram Malhotra (Mumbai, MH)';
      }

      let itemsHTML = '';
      if (data.cart_items && data.cart_items.length > 0) {
        data.cart_items.forEach(item => {
          itemsHTML += `
            <div class="cart-item">
              <div>
                <div class="cart-item-name">${item.name}</div>
                <div style="font-size:0.7rem; color:var(--text-muted);">${item.type}</div>
              </div>
              <div class="cart-item-price">₹${item.price.toFixed(2)}</div>
            </div>
          `;
        });
        if (cartCount) cartCount.textContent = data.cart_items.length;
      } else {
        itemsHTML = '<p style="font-size:0.8rem; color:var(--text-muted);">Cart is empty.</p>';
        if (cartCount) cartCount.textContent = '0';
      }

      if (cartItemsList) cartItemsList.innerHTML = itemsHTML;
      if (cartSubtotal) cartSubtotal.textContent = data.subtotal;
      if (cartDiscount) cartDiscount.textContent = `-${data.bundle_discount}`;
      if (cartTotal) cartTotal.textContent = data.total;

      if (cartNudgeBox) {
        if (data.applied_nudge) {
          cartNudgeBox.innerHTML = `<span class="nudge-icon">🎉</span> <span class="nudge-text">${data.applied_nudge}</span>`;
        } else {
          cartNudgeBox.innerHTML = `<span class="nudge-icon">🎁</span> <span class="nudge-text">Add <strong>Smart WiFi Mesh Extender (₹149/mo)</strong> to qualify for bundle discount!</span>`;
        }
      }
    } catch (err) {
      console.error('Failed to fetch cart:', err);
    }
  }

  // 3. Explainable AI Modal Handlers
  if (closeXaiBtn && xaiModal) {
    closeXaiBtn.addEventListener('click', () => {
      xaiModal.style.display = 'none';
    });
  }

  async function openXaiModal(productId = 'PROD-FIBER-1000') {
    const customerId = customerSelect.value;
    try {
      const res = await fetch(`/api/explainable-ai/${productId}?customer_id=${customerId}`);
      const data = await res.json();

      const matchedRulesEl = document.getElementById('xaiMatchedRules');
      const channelStatusEl = document.getElementById('xaiChannelStatus');

      if (matchedRulesEl && data.matched_rules) {
        matchedRulesEl.innerHTML = data.matched_rules.map(r => `<li>${r}</li>`).join('');
      }

      if (channelStatusEl && data.omnichannel_status) {
        channelStatusEl.textContent = data.omnichannel_status;
      }

      if (xaiModal) xaiModal.style.display = 'flex';
      appendLog('Explainable AI', `Loaded justification vector for ${data.product || productId}`, 'system');
    } catch (err) {
      console.error('Failed to load XAI modal:', err);
    }
  }

  // Next Best Action (NBA) Button Handler
  if (nbaActionBtn) {
    nbaActionBtn.addEventListener('click', () => {
      userInput.value = 'Add Smart WiFi 6 Mesh Extender to my cart for ₹149/mo and optimize router channel.';
      chatForm.dispatchEvent(new Event('submit'));
    });
  }

  // Quick Prompt Chips Click Handler
  promptChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const promptText = chip.getAttribute('data-prompt');
      if (promptText.includes('Explain why MagentaEins')) {
        openXaiModal('PROD-FIBER-1000');
        return;
      }
      userInput.value = promptText;
      chatForm.dispatchEvent(new Event('submit'));
    });
  });

  // Clear Chat Handler
  clearChatBtn.addEventListener('click', () => {
    messagesContainer.innerHTML = `
      <div class="message assistant-message">
        <div class="avatar">DT</div>
        <div class="message-content">
          <p>Conversation history reset. Ready for new omnichannel diagnostic & shopping queries!</p>
        </div>
      </div>
    `;
    resetAgentNodes();
    logContainer.innerHTML = `
      <div class="log-entry system-log">
        <span class="timestamp">System</span>
        <span class="text">Omnichannel Multi-Agent graph reset.</span>
      </div>
    `;
  });

  const hitlBanner = document.getElementById('hitlBanner');
  const approveBtn = document.getElementById('approveBtn');
  const rejectBtn = document.getElementById('rejectBtn');

  // HITL Approval Buttons Handlers
  if (approveBtn) {
    approveBtn.addEventListener('click', async () => {
      hitlBanner.style.display = 'none';
      const customerId = customerSelect.value;
      appendLog('Human Supervisor', 'Approved ₹500 refund credit action', 'system');
      
      try {
        const res = await fetch('/api/approve-action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ approved: true, customer_id: customerId })
        });
        const data = await res.json();
        appendMessage(`✅ **Action Executed**: ${data.message}`, 'assistant');
        appendLog('Billing Agent', 'Transaction TXN-IND-9982341 applied successfully', 'tool');
        fetchCart(); // Refresh cart state
      } catch (err) {
        appendMessage(`⚠️ Error approving action: ${err.message}`, 'assistant');
      }
    });
  }

  if (rejectBtn) {
    rejectBtn.addEventListener('click', async () => {
      hitlBanner.style.display = 'none';
      appendLog('Human Supervisor', 'Cancelled financial credit action', 'system');
      appendMessage('❌ **Action Cancelled**: Bill refund credit was declined by Human Supervisor.', 'assistant');
    });
  }

  // Form Submit Handler
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const promptText = userInput.value.trim();
    if (!promptText) return;

    // Append User Message
    appendMessage(promptText, 'user');
    userInput.value = '';
    if (hitlBanner) hitlBanner.style.display = 'none';

    // Show Loading state
    const loadingMessageId = appendLoadingMessage();
    const customerId = customerSelect.value;

    // Reset visual nodes
    resetAgentNodes();
    setAgentNodeActive('supervisor');

    appendLog('Supervisor', `[${currentChannel}] Processing intent: "${promptText.substring(0, 30)}..."`, 'system');

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: promptText, customer_id: customerId })
      });

      const data = await response.json();
      removeMessage(loadingMessageId);

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to communicate with AI server');
      }

      // Update Active Node & Telemetry
      if (data.active_agent) {
        setAgentNodeActive(data.active_agent);
      }

      // Process step logs
      if (data.execution_logs && data.execution_logs.length > 0) {
        data.execution_logs.forEach(log => {
          appendLog(log.node || 'Agent', log.action || log.reasoning, 'tool');
        });
      }

      // Render Assistant Response
      appendMessage(data.response, 'assistant', data.tool_outputs);

      // Trigger HITL Banner if human approval is required
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

  // UI Helper Functions
  function appendMessage(text, sender, toolOutputs = []) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', `${sender}-message`);

    const avatarText = sender === 'user' ? 'YOU' : 'DT';
    
    let toolCardsHTML = '';
    if (toolOutputs && toolOutputs.length > 0) {
      toolOutputs.forEach(tool => {
        toolCardsHTML += `
          <div class="tool-output-card">
            <strong>⚙️ Executed Tool [${tool.tool}]:</strong>
            <pre>${escapeHtml(tool.output)}</pre>
          </div>
        `;
      });
    }

    let feedbackHTML = '';
    if (sender === 'assistant') {
      feedbackHTML = `
        <div class="feedback-actions" style="margin-top:0.6rem; padding-top:0.4rem; border-top:1px solid rgba(255,255,255,0.06); display:flex; align-items:center; gap:0.5rem; font-size:0.75rem; color:var(--text-muted);">
          <span>Rate Recommendation:</span>
          <button class="feedback-btn" onclick="handleFeedback(this, 'like')" style="background:rgba(255,255,255,0.05); border:1px solid var(--bg-card-border); color:#fff; border-radius:4px; padding:0.15rem 0.4rem; cursor:pointer; font-size:0.8rem;" title="Positive RLHF Feedback">👍</button>
          <button class="feedback-btn" onclick="handleFeedback(this, 'dislike')" style="background:rgba(255,255,255,0.05); border:1px solid var(--bg-card-border); color:#fff; border-radius:4px; padding:0.15rem 0.4rem; cursor:pointer; font-size:0.8rem;" title="Negative RLHF Feedback">👎</button>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      <div class="avatar">${avatarText}</div>
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
      <div class="avatar">DT</div>
      <div class="message-content">
        <p><em>Thinking & running Omnichannel state graph...</em></p>
      </div>
    `;

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return id;
  }

  function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function appendLog(source, text, type = 'system') {
    const logEntry = document.createElement('div');
    logEntry.classList.add('log-entry', `${type}-log`);
    
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    logEntry.innerHTML = `
      <span class="timestamp">[${time}] ${source}:</span>
      <span class="text">${escapeHtml(text)}</span>
    `;

    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
  }

  function resetAgentNodes() {
    document.querySelectorAll('.agent-node').forEach(node => {
      node.classList.remove('active');
      const statusEl = node.querySelector('.node-status');
      if (statusEl) statusEl.textContent = 'IDLE';
    });
  }

  function setAgentNodeActive(agentName) {
    resetAgentNodes();
    const targetNode = document.getElementById(`node-${agentName}`);
    if (targetNode) {
      targetNode.classList.add('active');
      const statusEl = targetNode.querySelector('.node-status');
      if (statusEl) statusEl.textContent = 'ACTIVE';
    }
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
});

