document.addEventListener('DOMContentLoaded', function(){
  console.log('DOM loaded');
  console.log('Send code button:', document.getElementById('send-email-code'));
  console.log('Modal:', document.getElementById('email-modal'));
});

document.addEventListener('DOMContentLoaded', function(){
  const passwordInput = document.getElementById('id_password1');
  const passwordToggle = document.getElementById('password-toggle');
  const sendCodeBtn = document.getElementById('send-email-code');
  const verifyEmailBtn = document.getElementById('verify-email-code');
  const emailInput = document.getElementById('id_email');
  const emailCodeInput = document.getElementById('email-code');
  const franchiseInput = document.getElementById('id_franchise_code');
  const submitBtn = document.getElementById('submit-btn');

  if(sendCodeBtn) sendCodeBtn.disabled = true;
  if(submitBtn) submitBtn.disabled = true;
  if(franchiseInput) franchiseInput.disabled = true;

  if(passwordToggle && passwordInput){
    passwordToggle.addEventListener('click', function(e){
      e.preventDefault();
      if(passwordInput.type === 'password'){ passwordInput.type = 'text'; passwordToggle.textContent='Скрыть'; }
      else { passwordInput.type = 'password'; passwordToggle.textContent='Показать'; }
    });
  }

  const pwdMsg = document.getElementById('password-msg');
  if(passwordInput){
    passwordInput.addEventListener('input', function(){
      const v = passwordInput.value;
      let ok = true; let msgs = [];
      if(v.length < 8){ ok=false; msgs.push('мин 8 символов'); }
      if(!/\d/.test(v)){ ok=false; msgs.push('мин 1 цифра'); }
      if(!/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\/;\'`~]/.test(v)){ ok=false; msgs.push('мин 1 спец. символ'); }
      if(ok){ passwordInput.classList.add('valid'); passwordInput.classList.remove('invalid'); pwdMsg.textContent='Пароль подходит'; pwdMsg.style.color='green'; }
      else { passwordInput.classList.add('invalid'); passwordInput.classList.remove('valid'); pwdMsg.textContent='Требования: '+msgs.join(', '); pwdMsg.style.color='crimson'; }
    });
  }

  // enable send-email-button when captcha verified (polling small interval)
  const interv = setInterval(function(){
    if(window.captchaVerified){
      if(sendCodeBtn) sendCodeBtn.disabled = false;
      clearInterval(interv);
    }
  }, 300);

  // email code emulation
  let currentEmailCode = null;
  function openModalWithCode(code){
    const modal = document.getElementById('email-modal');
    const codeEl = document.getElementById('modal-code');
    if(codeEl) codeEl.textContent = code;
    modal.classList.add('open');
    modal.style.display = 'flex';
  }
  function closeModal(){
    const modal = document.getElementById('email-modal');
    modal.classList.remove('open');
    modal.style.display = 'none';
  }
  document.querySelectorAll('.modal-close').forEach(b => b.addEventListener('click', closeModal));

  if(sendCodeBtn){
    sendCodeBtn.addEventListener('click', function(e){
      try {
          e.preventDefault();
          if(!window.captchaVerified){ alert('Сначала решите CAPTCHA'); return; }
          const email = emailInput && emailInput.value.trim();
          if(!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)){ alert('Введите корректный email'); return; }
          currentEmailCode = String(Math.floor(100000 + Math.random()*900000));
          openModalWithCode(currentEmailCode);
          if(emailCodeInput){ emailCodeInput.disabled = false; emailCodeInput.value=''; emailCodeInput.classList.remove('valid','invalid'); }
        } catch (error) {
          console.error(error);
        }
    });
  }

  if(verifyEmailBtn){
    verifyEmailBtn.addEventListener('click', function(e){
      try {
        e.preventDefault();
        const v = emailCodeInput && emailCodeInput.value.trim();
        if(!v){ alert('Введите код подтверждения'); return; }
        if(v === currentEmailCode){
          alert('Email подтверждён');
          emailCodeInput.classList.remove('invalid'); emailCodeInput.classList.add('valid');
          if(franchiseInput) franchiseInput.disabled = false;
          if(submitBtn) submitBtn.disabled = false;
        } else {
          alert('Неверный код. Генерируем новый.');
          emailCodeInput.classList.remove('valid'); emailCodeInput.classList.add('invalid');
          currentEmailCode = String(Math.floor(100000 + Math.random()*900000));
          openModalWithCode(currentEmailCode);
        } 
      } catch (error) {
          console.error(error);
      }
    });
  }

  // modal click outside to close
  const modalRoot = document.getElementById('email-modal');
  if(modalRoot){
    modalRoot.addEventListener('click', function(e){
      if(e.target === modalRoot) closeModal();
    });
  }

  // final form submit guard (redundant checks)
  const form = document.getElementById('register-form');
  if(form){
    form.addEventListener('submit', function(e){
      if(!window.captchaVerified){ e.preventDefault(); alert('Решите CAPTCHA'); return; }
      if(!currentEmailCode){ e.preventDefault(); alert('Подтвердите email (нажмите "Отправить код")'); return; }
      if(!(emailCodeInput && emailCodeInput.classList.contains('valid'))){ e.preventDefault(); alert('Введите корректный код подтверждения email'); return; }
      if(!(franchiseInput && franchiseInput.value.trim())){ e.preventDefault(); alert('Введите код франчайзи'); return; }
      const pwd = passwordInput && passwordInput.value || '';
      if(pwd.length<8 || !/\d/.test(pwd) || !/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\/;\'`~]/.test(pwd)){
        e.preventDefault(); alert('Пароль не соответствует требованиям'); return;
      }
      // форма отправляется на сервер — сервер проверит franchise_code.
    });
  }
});
