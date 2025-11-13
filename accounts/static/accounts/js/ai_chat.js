(function(){
  // Simple floating chat widget
  function $(sel){return document.querySelector(sel)}

  function createWidget(){
    const wrapper = document.createElement('div');
    wrapper.id = 'ai-chat-wrapper';
    wrapper.innerHTML = `
      <button id="ai-chat-toggle" aria-label="Open chat">💬</button>
      <div id="ai-chat-box" class="closed" role="dialog" aria-hidden="true">
        <div id="ai-chat-header">AI Tutor <span class="status" id="ai-status">ready</span></div>
        <div id="ai-chat-messages" aria-live="polite"></div>
        <form id="ai-chat-form">
          <input id="ai-chat-input" placeholder="Hỏi tôi về ngữ pháp, từ vựng, bài tập..." autocomplete="off" />
          <button type="submit">Gửi</button>
        </form>
      </div>
    `;
    document.body.appendChild(wrapper);

    const toggle = document.getElementById('ai-chat-toggle');
    const box = document.getElementById('ai-chat-box');
    toggle.addEventListener('click', ()=>{
      if(box.classList.contains('closed')){
        box.classList.remove('closed');
        box.setAttribute('aria-hidden','false');
      } else {
        box.classList.add('closed');
        box.setAttribute('aria-hidden','true');
      }
    });

    const form = document.getElementById('ai-chat-form');
    const messages = document.getElementById('ai-chat-messages');
    const input = document.getElementById('ai-chat-input');

    function appendMessage(who, text){
      const el = document.createElement('div');
      el.className = 'ai-msg ' + (who==='user'?'user':'bot');
      el.textContent = text;
      messages.appendChild(el);
      messages.scrollTop = messages.scrollHeight;
    }

    function getCSRF(){
      const name = 'csrftoken';
      const cookies = document.cookie.split(';').map(c=>c.trim());
      for(const c of cookies){
        if(c.startsWith(name+'=')) return decodeURIComponent(c.split('=')[1]);
      }
      return '';
    }

    form.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const text = input.value.trim();
      if(!text) return;
      appendMessage('user', text);
      input.value = '';
      const status = document.getElementById('ai-status');
      status.textContent = 'thinking...';

      try{
        const resp = await fetch('/accounts/api/ai_chat/', {
          method: 'POST',
          headers: {'Content-Type':'application/json','X-CSRFToken': getCSRF()},
          body: JSON.stringify({message: text})
        });
        if(resp.status === 401){
          appendMessage('bot', 'Bạn cần đăng nhập để sử dụng chat.');
          status.textContent = 'error';
          return;
        }
        if(!resp.ok){
          // Try to parse JSON error body for more details
          let err = null;
          try{ err = await resp.json(); }catch(e){ err = {error: 'http_' + resp.status, body: await resp.text().catch(()=>'')} }
          const msg = err && (err.error || err.message || JSON.stringify(err));
          appendMessage('bot', 'Lỗi từ server: ' + msg);
          status.textContent = 'error';
          return;
        }
        const j = await resp.json();
        const botText = j.response || (j.response_raw? JSON.stringify(j.response_raw): 'Không có phản hồi');
        // If upstream error present, show clearer message
        if(j.error){
          appendMessage('bot', 'Lỗi từ server: ' + (j.message || j.error || JSON.stringify(j)));
          status.textContent = 'error';
          return;
        }
        appendMessage('bot', botText);
        status.textContent = 'ready';
      }catch(err){
        // Network level error (CORS, network down, server unreachable)
        appendMessage('bot', 'Yêu cầu thất bại: '+ (err.message || String(err)));
        status.textContent = 'error';
        console.error('AI chat fetch failed:', err);
      }
    });
  }

  // Initialize once DOM loaded
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', createWidget);
  else createWidget();
})();
