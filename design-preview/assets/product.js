/* Shared navigation only. Evaluation dispatch belongs to the existing start.js. */
(()=>{'use strict';
const sidebar=document.querySelector('#sidebar'),toggle=document.querySelector('.mobile-menu');
function close(){const wasOpen=sidebar.classList.contains('open');sidebar.classList.remove('open');toggle.setAttribute('aria-expanded','false');if(wasOpen)toggle.focus()}
toggle.addEventListener('click',()=>{if(sidebar.classList.contains('open'))close();else{sidebar.classList.add('open');toggle.setAttribute('aria-expanded','true')}});
document.addEventListener('keydown',event=>{if(event.key==='Escape')close()});
document.addEventListener('click',event=>{if(sidebar.classList.contains('open')&&!sidebar.contains(event.target)&&!toggle.contains(event.target))close()});
})();
