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
  let chatThreadId = `session_${Date.now()}`;

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
      startAbandonmentTimer();
    });

    closeCartBtn.addEventListener('click', () => {
      cartDrawer.classList.remove('open');
      clearAbandonmentTimer();
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
      if (cartSubtotal) cartSubtotal.textContent = data.subtotal_base || data.subtotal || '₹0.00';
      if (cartDiscount) cartDiscount.textContent = `-${(data.bundle_discount || '₹0.00').replace('₹', '')}`;
      if (cartTotal) cartTotal.textContent = data.total || '₹0.00';

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

  // ========== CHECKOUT FUNNEL ==========
  const checkoutModal = document.getElementById('checkoutModal');
  const checkoutBtn = document.getElementById('checkoutBtn');
  const closeCheckoutBtn = document.getElementById('closeCheckoutBtn');
  const checkoutNextBtn = document.getElementById('checkoutNextBtn');
  const checkoutBackBtn = document.getElementById('checkoutBackBtn');
  const checkoutStepContent = document.getElementById('checkoutStepContent');

  let checkoutStep = 1;
  let checkoutPreview = null;
  let selectedPayment = 'upi';
  let abandonmentTimer = null;
  let checkoutStarted = false;

  function clearAbandonmentTimer() {
    if (abandonmentTimer) {
      clearTimeout(abandonmentTimer);
      abandonmentTimer = null;
    }
  }

  function startAbandonmentTimer() {
    clearAbandonmentTimer();
    checkoutStarted = false;

    abandonmentTimer = setTimeout(async () => {
      if (checkoutStarted) return;

      const customerId = customerSelect.value;
      try {
        const res = await fetch('/api/checkout/abandonment-nudge', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            customer_id: customerId,
            channel: currentChannel,
            seconds_open: 30
          })
        });
        const data = await res.json();

        if (nbaBanner && data.nudge) {
          nbaBanner.classList.add('abandonment-nudge');
          document.getElementById('nbaMessage').textContent =
            `${data.nudge.message} ${data.nudge.discount_hint || ''}`;
          nbaBanner.style.display = 'flex';
        }
        appendLog('Cart Abandonment NBA', data.nudge?.message || 'Nudge triggered', 'system');
      } catch (err) {
        console.error('Abandonment nudge failed:', err);
      }
    }, 30000);
  }

  function updateCheckoutStepUI() {
    document.querySelectorAll('.checkout-step').forEach(el => {
      const step = parseInt(el.dataset.step, 10);
      el.classList.remove('active', 'done');
      if (step < checkoutStep) el.classList.add('done');
      if (step === checkoutStep) el.classList.add('active');
    });
    checkoutBackBtn.style.display = checkoutStep > 1 && checkoutStep < 4 ? 'inline-block' : 'none';
    checkoutNextBtn.textContent =
      checkoutStep === 3 ? 'Pay Now' :
      checkoutStep === 4 ? 'Done' : 'Continue';
  }

  async function loadCheckoutPreview() {
    const customerId = customerSelect.value;
    const res = await fetch(`/api/checkout/preview/${customerId}`);
    checkoutPreview = await res.json();
    if (!res.ok) throw new Error(checkoutPreview.detail || 'Preview failed');
    return checkoutPreview;
  }

  function renderCheckoutStep() {
    updateCheckoutStepUI();
    const s = checkoutPreview?.cart_summary || {};

    if (checkoutStep === 1) {
      checkoutStepContent.innerHTML = `
        <h4>Cart Review</h4>
        <p style="font-size:0.85rem;color:var(--text-muted);">Review items before checkout.</p>
        <div class="cart-items-list" style="margin-top:0.75rem;">
          ${(s.cart_items || []).map(i => `
            <div class="cart-item">
              <div><div class="cart-item-name">${i.name}</div><div style="font-size:0.7rem;color:var(--text-muted);">${i.type}</div></div>
              <div class="cart-item-price">₹${i.price.toFixed(2)}</div>
            </div>`).join('') || '<p>Cart is empty.</p>'}
        </div>
        <div class="cart-summary" style="margin-top:1rem;">
          <div class="summary-row"><span>Subtotal</span><span>${s.subtotal_base || '-'}</span></div>
          <div class="summary-row discount"><span>Discount</span><span>-${(s.bundle_discount || '₹0.00').replace('₹','')}</span></div>
          <div class="summary-row total"><span>Total</span><span>${s.total || '-'}</span></div>
        </div>`;
    }

    if (checkoutStep === 2) {
      const suggestions = checkoutPreview?.bundle_suggestions || [];
      checkoutStepContent.innerHTML = `
        <h4>Bundle Optimization</h4>
        <p style="font-size:0.85rem;color:var(--text-muted);">AI-optimized pricing for your cart.</p>
        ${s.applied_nudge ? `<div class="nudge-box"><span class="nudge-icon">🎉</span><span>${s.applied_nudge}</span></div>` : ''}
        <ul style="margin-top:0.75rem;font-size:0.85rem;padding-left:1.2rem;">
          ${suggestions.map(x => `<li>${x.message}</li>`).join('') || '<li>No extra optimizations needed.</li>'}
        </ul>`;
    }

    if (checkoutStep === 3) {
      const upi = checkoutPreview?.subscriber?.upi_id || 'rahul.sharma@okicici';
      checkoutStepContent.innerHTML = `
        <h4>Payment Method</h4>
        <div class="checkout-payment-options">
          <label class="payment-option selected" data-method="upi">
            <input type="radio" name="pay" value="upi" checked> 📱 UPI (${upi})
          </label>
          <label class="payment-option" data-method="card">
            <input type="radio" name="pay" value="card"> 💳 Credit / Debit Card
          </label>
          <label class="payment-option" data-method="netbanking">
            <input type="radio" name="pay" value="netbanking"> 🏦 Net Banking
          </label>
        </div>`;

      checkoutStepContent.querySelectorAll('.payment-option').forEach(opt => {
        opt.addEventListener('click', () => {
          checkoutStepContent.querySelectorAll('.payment-option').forEach(o => o.classList.remove('selected'));
          opt.classList.add('selected');
          selectedPayment = opt.dataset.method;
        });
      });
    }

    if (checkoutStep === 4 && checkoutPreview?.confirmation) {
      const c = checkoutPreview.confirmation;
      checkoutStepContent.innerHTML = `
        <div class="checkout-success">
          <div style="font-size:2.5rem;">✅</div>
          <h4>Order Confirmed!</h4>
          <div class="order-id">${c.order_id}</div>
          <p style="font-size:0.85rem;color:var(--text-muted);">${c.message}</p>
          <p style="font-size:0.8rem;margin-top:0.5rem;">Txn: ${c.payment?.transaction_id}</p>
        </div>`;
    }
  }

  async function openCheckoutWizard() {
    checkoutStarted = true;
    clearAbandonmentTimer();
    checkoutStep = 1;
    selectedPayment = 'upi';

    try {
      await loadCheckoutPreview();
      if (checkoutPreview.status === 'empty_cart') {
        appendMessage('⚠️ Your cart is empty. Add items before checkout.', 'assistant');
        return;
      }
      checkoutModal.style.display = 'flex';
      renderCheckoutStep();
      appendLog('Checkout Funnel', 'Step 1: Cart review started', 'system');
    } catch (err) {
      appendMessage(`⚠️ Checkout error: ${err.message}`, 'assistant');
    }
  }

  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', openCheckoutWizard);
  }

  if (closeCheckoutBtn) {
    closeCheckoutBtn.addEventListener('click', () => {
      checkoutModal.style.display = 'none';
    });
  }

  if (checkoutBackBtn) {
    checkoutBackBtn.addEventListener('click', () => {
      if (checkoutStep > 1) {
        checkoutStep--;
        renderCheckoutStep();
      }
    });
  }

  if (checkoutNextBtn) {
    checkoutNextBtn.addEventListener('click', async () => {
      if (checkoutStep === 3) {
        checkoutNextBtn.disabled = true;
        try {
          const res = await fetch('/api/checkout/complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              customer_id: customerSelect.value,
              payment_method: selectedPayment,
              channel: currentChannel
            })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || 'Payment failed');

          checkoutPreview.confirmation = data;
          checkoutStep = 4;
          renderCheckoutStep();

          appendLog('Conversion Event', `Order ${data.order_id} — ${data.payment?.amount_paid}`, 'system');
          fetchCart();
        } catch (err) {
          appendMessage(`⚠️ Payment failed: ${err.message}`, 'assistant');
        } finally {
          checkoutNextBtn.disabled = false;
        }
        return;
      }

      if (checkoutStep === 4) {
        checkoutModal.style.display = 'none';
        cartDrawer.classList.remove('open');
        appendMessage(`🎉 **Checkout complete!** Your order is synced across ${currentChannel}.`, 'assistant');
        return;
      }

      checkoutStep++;
      renderCheckoutStep();
      appendLog('Checkout Funnel', `Advanced to step ${checkoutStep}`, 'system');
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
    chatThreadId = `session_${Date.now()}`;
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
        body: JSON.stringify({
          message: promptText,
          customer_id: customerId,
          thread_id: chatThreadId,
        })
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
      appendMessage(data.response, 'assistant');

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
  function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', `${sender}-message`);

    const avatarText = sender === 'user' ? 'YOU' : 'DT';

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

