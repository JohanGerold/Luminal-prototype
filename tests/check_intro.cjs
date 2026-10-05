// Browser-independent interaction guards; no network or model calls.
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('design-preview/assets/intro.js', 'utf8');
function scene(reduced = false) {
  const handlers = {}, classes = new Set(), elements = {};
  const windowHandlers = {};
  const el = () => ({style:{}, addEventListener:(n,f)=>handlers[n]=f});
  ['.intro-copy','.intro-caption','.intro-robot','.intro-human'].forEach(k=>elements[k]=el());
  const link = el(), page = {...el(), inert:false, removeAttribute(){this.style={};}};
  const main = {setAttribute(){}, focus(){this.focused=true;}};
  const intro = {style:{}, querySelector:k=>elements[k], querySelectorAll:()=>[link], contains:()=>false};
  const body = {style:{removeProperty(k){delete this[k];}},classList:{add:(...keys)=>keys.forEach(k=>classes.add(k)),remove:(...keys)=>keys.forEach(k=>classes.delete(k))}};
  const doc = {body,
    getElementById:k=>({'liminal-intro':intro,'workspace-page':page,main}[k]),
    querySelector:k=>k==='.intro-distance'?{offsetHeight:2400}:null};
  const context = {document:doc,URLSearchParams,matchMedia:()=>({matches:reduced,addEventListener(){},removeEventListener(){}}),
    requestAnimationFrame:f=>{context.frame=f;},innerHeight:1000,scrollY:0,location:{search:''},
    cancelAnimationFrame(){},
    history:{replaceState(a,b,url){context.url=url;}},window:{addEventListener:(n,f)=>{windowHandlers[n]=f;},removeEventListener(){},scrollTo(){},setTimeout:f=>{context.timeout=f;return 1;},clearTimeout(){}}};
  vm.runInNewContext(source,context);
  return {context,handlers,windowHandlers,classes,intro,page,main,elements};
}
const reduced=scene(true);
assert.equal(reduced.page.inert,false);
assert.equal(reduced.classes.size,0);
assert.equal(reduced.context.frame,undefined);
const skip=scene();
assert.equal(skip.page.inert,true);
skip.handlers.click({button:0,preventDefault(){}});
skip.context.frame(); skip.context.timeout();
assert.equal(skip.page.inert,false);
assert.equal(skip.main.focused,true);
assert.equal(skip.context.url,'/workspace');
const scroll=scene();
scroll.context.scrollY=1400*.76; scroll.context.frame();
assert.equal(scroll.elements['.intro-copy'].style.opacity,0);
assert.ok(scroll.elements['.intro-robot'].style.transform.startsWith('translateX(2.15'));
assert.equal(scroll.page.inert,true);
scroll.context.scrollY=1400; scroll.context.frame();
scroll.context.frame(); scroll.context.timeout();
assert.equal(scroll.intro.hidden,true);
assert.equal(scroll.page.inert,false);
assert.equal(scroll.classes.has('intro-awaiting-scroll'),true);
scroll.windowHandlers.wheel({preventDefault(){}});
assert.equal(scroll.classes.size,0);
console.log('Intro: reduced motion, keyboard skip, contact-before-reveal and scroll completion passed.');
