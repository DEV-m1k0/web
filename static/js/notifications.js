// static/js/notifications.js
(function(){
  // key for localStorage history
  const STORAGE_KEY = 'notif_history_v1';

  function nowISO(){ return new Date().toISOString(); }
  function saveHistory(history){
    try{ localStorage.setItem(STORAGE_KEY, JSON.stringify(history)); }catch(e){}
  }
  function loadHistory(){
    try{ const v = localStorage.getItem(STORAGE_KEY); return v ? JSON.parse(v) : []; } catch(e){ return []; }
  }

  // add item to history and update badge + center
  function addToHistory(obj){
    const history = loadHistory();
    history.unshift(obj); // newest first
    // cap history to 200 items
    if(history.length > 200) history.length = 200;
    saveHistory(history);
    renderCenterList();
    updateBadge();
  }

  // toast creation
  function showToast({type='info', title='', text='', timeout=6000}={}){
    const root = document.getElementById('toast-root');
    if(!root) return;
    const div = document.createElement('div');
    div.className = 'toast ' + type;
    div.setAttribute('role','status');
    div.innerHTML = '<div class="t-body"><div class="t-title">'+(title||capitalize(type))+'</div><div class="t-text">'+escapeHtml(text)+'</div></div>';
    const close = document.createElement('button');
    close.className = 't-close';
    close.innerHTML = '✕';
    close.addEventListener('click', ()=>{ hideToast(div); });
    div.appendChild(close);
    root.prepend(div);
    // show animation
    requestAnimationFrame(()=>div.classList.add('show'));
    if(timeout>0){
      setTimeout(()=>{ hideToast(div); }, timeout);
    }
    // save to history
    addToHistory({type, title, text, ts: nowISO()});
    return div;
  }

  function hideToast(el){
    if(!el) return;
    el.classList.remove('show');
    setTimeout(()=>{ try{ el.remove(); }catch(e){} }, 220);
  }

  function capitalize(s){ return s && s.charAt(0).toUpperCase()+s.slice(1) || ''; }
  function escapeHtml(s){ return (s+'').replace(/[&<>"']/g, function(m){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]; }); }

  // render notification center list
  function renderCenterList(){
    const listEl = document.getElementById('nc-list');
    const emptyEl = document.getElementById('nc-empty');
    if(!listEl) return;
    const history = loadHistory();
    listEl.innerHTML = '';
    if(history.length === 0){
      if(emptyEl) emptyEl.style.display='block';
      return;
    } else { if(emptyEl) emptyEl.style.display='none'; }

    history.forEach(item => {
      const it = document.createElement('div');
      it.className = 'nc-item ' + (item.type || '');
      const txt = item.text || item.message || '';
      const title = item.title || capitalize(item.type || 'info');
      const date = new Date(item.ts || nowISO());
      const meta = date.toLocaleString();

      it.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:flex-start"><strong>'+escapeHtml(title)+'</strong><div class="meta">'+escapeHtml(meta)+'</div></div>'
                    + '<div class="nc-text" style="margin-top:6px">'+escapeHtml(txt)+'</div>';
      listEl.appendChild(it);
    });
  }

  function clearHistory(){
    try{ localStorage.removeItem(STORAGE_KEY); }catch(e){}
    renderCenterList();
    updateBadge();
  }

  function markAllRead(){
    // we'll just update a "read" flag by moving items and mark badge 0
    // for simplicity we keep history but set a readAt timestamp in storage meta
    // For now: just update badge: store lastReadAt
    try{ localStorage.setItem(STORAGE_KEY + '_lastRead', new Date().toISOString()); }catch(e){}
    updateBadge();
  }

  function updateBadge(){
    const badge = document.getElementById('notif-badge');
    if(!badge) return;
    const history = loadHistory();
    // compute unread = items newer than lastRead
    const lastRead = (function(){ try { return localStorage.getItem(STORAGE_KEY + '_lastRead'); } catch(e){return null;} })();
    let unread = 0;
    if(!lastRead) unread = history.length;
    else {
      const lr = new Date(lastRead);
      unread = history.filter(h=> new Date(h.ts) > lr ).length;
    }
    badge.textContent = unread>99 ? '99+' : String(unread);
    badge.style.display = unread>0 ? 'inline-block' : 'none';
  }

  // toggle center open/close
  function toggleCenter(open){
    const panel = document.getElementById('notification-center');
    const toggle = document.getElementById('notif-toggle');
    if(!panel || !toggle) return;
    const isOpen = panel.classList.contains('open');
    if(typeof open === 'boolean') {
      if(open && !isOpen) panel.classList.add('open');
      if(!open && isOpen) panel.classList.remove('open');
    } else {
      panel.classList.toggle('open');
    }
    panel.setAttribute('aria-hidden', panel.classList.contains('open') ? 'false' : 'true');
    toggle.setAttribute('aria-expanded', panel.classList.contains('open') ? 'true' : 'false');
  }

  // init on DOM ready
  document.addEventListener('DOMContentLoaded', function(){
    renderCenterList();
    updateBadge();

    const toggle = document.getElementById('notif-toggle');
    if(toggle) toggle.addEventListener('click', function(e){ toggleCenter(); });

    const clearBtn = document.getElementById('nc-clear');
    if(clearBtn) clearBtn.addEventListener('click', function(){ if(confirm('Очистить историю уведомлений?')) clearHistory(); });

    const markBtn = document.getElementById('nc-mark-read');
    if(markBtn) markBtn.addEventListener('click', function(){ markAllRead(); });

    // handle DJ_MESSAGES from Django
    try {
      if(window.DJ_MESSAGES && Array.isArray(window.DJ_MESSAGES)){
        window.DJ_MESSAGES.forEach(m=>{
          // m.tags may contain space-separated tags e.g. 'error' or 'success'
          const t = (m.tags||'').split(' ')[0] || 'info';
          showToast({type: mapLevelToType(t), text: m.message || ''});
        });
      }
    } catch(e){ console.error(e); }

    // expose API
    window.appNotify = { showToast, addToHistory, clearHistory };
  });

  function mapLevelToType(tag){
    tag = (tag||'').toLowerCase();
    if(tag.indexOf('error')!==-1 || tag.indexOf('danger')!==-1) return 'error';
    if(tag.indexOf('success')!==-1) return 'success';
    if(tag.indexOf('warning')!==-1) return 'error';
    return 'info';
  }

})();
