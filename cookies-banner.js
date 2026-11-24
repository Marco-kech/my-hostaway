/* DPM Conciergerie — Bannière de cookies RGPD/CNDP */
(function(){
  if(localStorage.getItem('dpm_cookies_accepted'))return;
  var b=document.createElement('div');
  b.id='cookieBanner';
  b.style.cssText='position:fixed;bottom:0;left:0;right:0;background:#14352A;color:#fff;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;z-index:9999;font-family:Inter,Arial,sans-serif;font-size:13px;box-shadow:0 -2px 12px rgba(0,0,0,.2)';
  b.innerHTML='<span>Ce site utilise des cookies pour améliorer votre expérience. <a href="livre-or.html" style="color:#C9A227;text-decoration:underline">En savoir plus</a></span><div style="display:flex;gap:8px"><button id="ckRefuse" style="background:transparent;border:1px solid #fff;color:#fff;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:12px">Refuser</button><button id="ckAccept" style="background:#C9A227;border:none;color:#fff;padding:8px 16px;border-radius:6px;cursor:pointer;font-weight:700;font-size:12px">Accepter</button></div>';
  document.body.appendChild(b);
  document.getElementById('ckAccept').onclick=function(){localStorage.setItem('dpm_cookies_accepted','1');b.remove();};
  document.getElementById('ckRefuse').onclick=function(){localStorage.setItem('dpm_cookies_accepted','0');b.remove();};
})();
