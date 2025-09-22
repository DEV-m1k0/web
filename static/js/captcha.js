(function(window){
  function rnd(a,b){return Math.floor(Math.random()*(b-a+1))+a}
  function pick(arr){return arr[Math.floor(Math.random()*arr.length)]}
  function generateExpression(){
    const ops = ['+','-','*','/']
    const nOps = Math.max(3, rnd(3,4)) // min 3 operations
    const nums = []
    for(let i=0;i<nOps+1;i++) nums.push(rnd(1,20))
    const opsList = []
    for(let i=0;i<nOps;i++) opsList.push(pick(ops))
    let expr = ''
    if (Math.random() < 0.6){
      const start = Math.floor(Math.random()*(opsList.length))
      const end = Math.min(opsList.length, start + Math.floor(Math.random()*2)+1)
      for(let i=0;i<nums.length;i++){
        if(i===start) expr += '('
        expr += nums[i]
        if(i<=opsList.length-1) expr += ' ' + opsList[i] + ' '
        if(i===end) expr += ')'
      }
    } else {
      expr = nums[0].toString()
      for(let i=0;i<opsList.length;i++) expr += ' ' + opsList[i] + ' ' + nums[i+1]
    }
    return expr
  }

  function pretty(expr){
    return expr.replace(/\*/g,'×').replace(/\//g,'÷')
  }

  function compute(expr){
    try{
      const v = Function('"use strict";return ('+expr+')')()
      return Math.round(v * 1000000)/1000000
    } catch(e){
      return null
    }
  }

  function render(){
    const q = generateExpression()
    const el = document.getElementById('captcha-question')
    if(!el) return
    el.textContent = pretty(q) + ' = ?'
    el.style.fontSize = '20px'
    window._captcha_value = compute(q)
    window.captchaVerified = false
    const input = document.getElementById('captcha-answer')
    if(input){ input.value=''; input.classList.remove('valid','invalid') }
  }

  document.addEventListener('DOMContentLoaded', function(){
    render()
    const btnCheck = document.getElementById('captcha-check')
    if(btnCheck) btnCheck.addEventListener('click', function(){
      const ansEl = document.getElementById('captcha-answer')
      const val = (ansEl && ansEl.value || '').trim()
      if(val === ''){ alert('Введите ответ'); return }
      const expected = window._captcha_value
      if(expected === null){ alert('Ошибка генерации. Попробуйте обновить.'); render(); return; }
      const userVal = Number(val)
      if(Number.isNaN(userVal)){ ansEl.classList.add('invalid'); ansEl.classList.remove('valid'); alert('Введите корректное числовое значение.'); return; }
      if(Math.abs(userVal - expected) <= 0.001){
        window.captchaVerified = true
        ansEl.classList.remove('invalid'); ansEl.classList.add('valid')
        alert('CAPTCHA пройдена.')
        const sendBtn = document.getElementById('send-email-code')
        if(sendBtn) sendBtn.disabled = false
      } else {
        window.captchaVerified = false
        ansEl.classList.remove('valid'); ansEl.classList.add('invalid')
        alert('Неверный ответ. Попробуйте еще раз.')
        render()
      }
    })
    const refresh = document.getElementById('captcha-refresh')
    if(refresh) refresh.addEventListener('click', render)
  })

  window.captchaRender = render
})(window);
