
// ── Reveal-on-scroll observer ──
const io=new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting)x.target.classList.add('v')})},{threshold:.1,rootMargin:'0px 0px -40px 0px'});
document.querySelectorAll('.r').forEach(el=>io.observe(el));
document.querySelectorAll('.nl a').forEach(a=>a.addEventListener('click',()=>document.querySelector('.nl').classList.remove('open')));
const nav=document.querySelector('.nav');window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>60)},{passive:true});

// ── Scroll-spy sidebar + nav active link ──
(function(){
  const spy=document.getElementById('spy');
  const spyDots=spy?spy.querySelectorAll('.spy-dot'):[];
  const navLinks=document.querySelectorAll('.nl a[href*="#"]');
  const sections=['hero-top','features','how','numbers','cta-section'];
  const sectionEls=sections.map(id=>document.getElementById(id)).filter(Boolean);

  function updateActive(){
    const scrollY=window.scrollY;
    const heroH=document.getElementById('hero-top');
    let currentIdx=0;
    sectionEls.forEach((sec,i)=>{
      if(sec.offsetTop - 200 <= scrollY) currentIdx=i;
    });
    const currentId=sections[currentIdx];
    if(spy){
      const showSpy=!!(heroH && scrollY > heroH.offsetHeight * 0.5);
      spy.classList.toggle('visible',showSpy);
    }
    spyDots.forEach((dot,i)=>{
      dot.classList.toggle('active',i===currentIdx);
    });
    navLinks.forEach(a=>{
      const href=a.getAttribute('href');
      if(href && href.includes('#')){
        const hash=href.split('#')[1];
        a.classList.toggle('on',hash===currentId);
      }
    });
  }
  window.addEventListener('scroll',updateActive,{passive:true});
  updateActive();
})();

// ── Layer stack: wheel-controlled + hover-gated ──
(function(){
  const featSection=document.getElementById('features');
  const stage=document.getElementById('layers-stage');
  const stack=document.getElementById('layers-stack');
  const cards=document.querySelectorAll('.layer-card');
  const layers=stack?stack.querySelectorAll('.map-layer'):[];
  const LAYER_COUNT=5;
  const desktopMq=window.matchMedia('(min-width: 769px)');
  const glowColors=[
    'rgba(250,204,21,',
    'rgba(251,146,60,',
    'rgba(134,239,172,',
    'rgba(232,121,249,',
    'rgba(192,132,252,'
  ];

  let currentLayer=0;
  let autoTimer=null;
  let autoIdx=0;
  let stageHovered=false;
  let wheelLocked=false;

  const stepper=document.getElementById('layer-stepper');
  const stepperLabel=document.getElementById('layer-stepper-label');
  const stepperDots=stepper?stepper.querySelectorAll('.layer-stepper-dot'):[];
  const stepperLineFills=stepper?stepper.querySelectorAll('.layer-stepper-line-fill'):[];
  const cardsWrap=document.querySelector('.layer-cards');
  const panelTitle=document.getElementById('layer-panel-title');
  const panelCopy=document.getElementById('layer-panel-copy');
  const legendSwatches=[
    document.getElementById('legend-swatch-1'),
    document.getElementById('legend-swatch-2'),
    document.getElementById('legend-swatch-3')
  ];
  const legendLabels=[
    document.getElementById('legend-label-1'),
    document.getElementById('legend-label-2'),
    document.getElementById('legend-label-3')
  ];
  const legendValues=[
    document.getElementById('legend-value-1'),
    document.getElementById('legend-value-2'),
    document.getElementById('legend-value-3')
  ];
  const metricSignal=document.getElementById('metric-signal');
  const metricUpdate=document.getElementById('metric-update');
  const metricWeight=document.getElementById('metric-weight');
  const layerDatasets=[
    {
      title:'Speed Model',
      copy:'Road-class based free-flow speed. Motorways at 120 km/h, residential at 30.',
      legend:[
        {label:'Primary',value:'120 km/h',color:'#FACC15'},
        {label:'Secondary',value:'90 km/h',color:'#FCD34D'},
        {label:'Residential',value:'30 km/h',color:'#FEF08A'}
      ],
      metrics:{signal:'Free Flow',update:'Static',weight:'0.35'}
    },
    {
      title:'Traffic Congestion',
      copy:'BPR volume-delay model with 15% lane-filtering advantage for motorcycles.',
      legend:[
        {label:'Moderate',value:'V/C 0.75',color:'#FB923C'},
        {label:'Heavy',value:'V/C 0.91',color:'#F97316'},
        {label:'Severe',value:'Delay +42%',color:'#EA580C'}
      ],
      metrics:{signal:'Realtime',update:'15 min',weight:'0.22'}
    },
    {
      title:'Surface Detection',
      copy:'20 classified surface types from asphalt (1.0) to mud (0.35).',
      legend:[
        {label:'Asphalt',value:'Factor 1.00',color:'#86EFAC'},
        {label:'Gravel',value:'Factor 0.78',color:'#FB923C'},
        {label:'Cobble',value:'Factor 0.61',color:'#CBD5E1'}
      ],
      metrics:{signal:'Material',update:'Tile',weight:'0.18'}
    },
    {
      title:'Curvature Analysis',
      copy:'Bearing-change classification: hairpin, sharp, fun, and mild turns.',
      legend:[
        {label:'Mild',value:'40-90°',color:'#F0ABFC'},
        {label:'Sharp',value:'90-140°',color:'#E879F9'},
        {label:'Hairpin',value:'140°+',color:'#C026D3'}
      ],
      metrics:{signal:'Geometry',update:'Static',weight:'0.14'}
    },
    {
      title:'Elevation Grade',
      copy:'Kinematic speed adjustment for slopes. 8% grade = 0.68 factor.',
      legend:[
        {label:'Grade',value:'+8%',color:'#C084FC'},
        {label:'Summit',value:'1120 m',color:'#A78BFA'},
        {label:'Penalty',value:'0.68x',color:'#DDD6FE'}
      ],
      metrics:{signal:'Terrain',update:'DEM',weight:'0.11'}
    }
  ];

  function updateStepper(idx){
    if(!stepper) return;
    const progress=idx/(LAYER_COUNT - 1);
    const continuousStep=progress*(LAYER_COUNT - 1);
    stepperDots.forEach((d,i)=>{
      d.classList.remove('done','current');
      if(i<idx) d.classList.add('done');
      if(i===idx) d.classList.add('current');
    });
    stepperLineFills.forEach((fill,i)=>{
      const lineProgress=Math.max(0,Math.min(1,continuousStep - i));
      fill.style.height=(lineProgress * 100)+'%';
    });
    if(stepperLabel){
      stepperLabel.textContent=String(idx + 1).padStart(2,'0')+' / '+String(LAYER_COUNT).padStart(2,'0');
      stepperLabel.classList.add('active');
    }
  }

  function activate(idx){
    if(idx<0) idx=0;
    if(idx>=LAYER_COUNT) idx=LAYER_COUNT-1;
    currentLayer=idx;

    cards.forEach((c,i)=>{c.classList.toggle('active',i===idx)});
    layers.forEach((l,i)=>{
      const offset=i-idx;
      const isActive=i===idx;
      const base=52;
      const z=offset*-18;
      const s=1-Math.abs(offset)*0.03;
      const o=isActive?1:Math.max(.35,1-Math.abs(offset)*.25);
      l.style.transform='rotateX('+base+'deg) translateZ('+z+'px) scale('+s+')';
      l.style.opacity=o;
      l.style.zIndex=isActive?10:5-Math.abs(offset);
      if(isActive){
        const gc=glowColors[i]||glowColors[0];
        l.style.filter='brightness(1.4) saturate(1.2)';
        l.style.boxShadow='0 30px 60px -15px '+gc+'.3), 0 0 50px -8px '+gc+'.15), inset 0 1px 0 '+gc+'.15)';
        l.style.borderColor=gc+'.4)';
      } else {
        l.style.filter='brightness(1)';
        l.style.boxShadow='';
        l.style.borderColor='';
      }
    });

    const meta=layerDatasets[idx];
    if(meta){
      if(panelTitle) panelTitle.textContent=meta.title;
      if(panelCopy) panelCopy.textContent=meta.copy;
      meta.legend.forEach((item,i)=>{
        if(legendSwatches[i]) legendSwatches[i].style.background=item.color;
        if(legendSwatches[i]) legendSwatches[i].style.boxShadow='0 0 10px '+item.color+'55';
        if(legendLabels[i]) legendLabels[i].textContent=item.label;
        if(legendValues[i]) legendValues[i].textContent=item.value;
      });
      if(metricSignal) metricSignal.textContent=meta.metrics.signal;
      if(metricUpdate) metricUpdate.textContent=meta.metrics.update;
      if(metricWeight) metricWeight.textContent=meta.metrics.weight;
    }
    updateStepper(idx);
    autoIdx=idx;
  }

  function stopAuto(){
    if(autoTimer){
      clearInterval(autoTimer);
      autoTimer=null;
    }
  }

  function startAuto(){
    stopAuto();
    if(stageHovered) return;
    autoTimer=setInterval(()=>{
      autoIdx=(autoIdx+1)%LAYER_COUNT;
      activate(autoIdx);
    },3200);
  }

  cards.forEach((c,i)=>{
    c.addEventListener('mouseenter',()=>{
      stopAuto();
      activate(i);
    });
    c.addEventListener('click',()=>{
      stopAuto();
      activate(i);
    });
  });

  layers.forEach((l,i)=>{
    l.addEventListener('mouseenter',()=>{
      stopAuto();
      activate(i);
    });
    l.addEventListener('click',()=>{
      stopAuto();
      activate(i);
    });
  });

  if(stage){
    stage.addEventListener('mouseenter',()=>{
      stageHovered=true;
      stopAuto();
    });
    stage.addEventListener('mouseleave',()=>{
      stageHovered=false;
      startAuto();
    });
    stage.addEventListener('wheel',(event)=>{
      if(!desktopMq.matches) return;
      const direction=Math.sign(event.deltaY);
      if(!direction) return;
      const next=currentLayer + direction;
      if(next<0 || next>=LAYER_COUNT || wheelLocked) return;
      event.preventDefault();
      stopAuto();
      wheelLocked=true;
      activate(next);
      window.scrollBy({top:direction*56,left:0,behavior:'auto'});
      window.setTimeout(()=>{wheelLocked=false;},320);
    },{passive:false});
  }

  if(cardsWrap){
    cardsWrap.addEventListener('mouseenter',stopAuto);
    cardsWrap.addEventListener('mouseleave',()=>{if(!stageHovered)startAuto()});
  }

  function updateVisibility(){
    if(!featSection || !stepper) return;
    const rect=featSection.getBoundingClientRect();
    const visible=desktopMq.matches && rect.top < window.innerHeight*0.78 && rect.bottom > window.innerHeight*0.22;
    stepper.classList.toggle('visible',visible);
  }

  window.addEventListener('scroll',updateVisibility,{passive:true});
  window.addEventListener('resize',updateVisibility,{passive:true});
  if(desktopMq.addEventListener){
    desktopMq.addEventListener('change',updateVisibility);
  }else if(desktopMq.addListener){
    desktopMq.addListener(updateVisibility);
  }

  activate(0);
  startAuto();
  updateVisibility();
})();

// ── Logo hover: tilt on mouse move ──
(function(){
  const brand=document.querySelector('.nav-b');
  const logo=brand?brand.querySelector('img'):null;
  if(!brand||!logo)return;
  brand.addEventListener('mousemove',function(e){
    const r=brand.getBoundingClientRect();
    const cx=(e.clientX-r.left)/r.width-0.5;
    const cy=(e.clientY-r.top)/r.height-0.5;
    logo.style.transform='scale(1.15) rotate('+(-5+cx*10)+'deg) translateY('+(cy*-4)+'px)';
  });
  brand.addEventListener('mouseleave',function(){
    logo.style.transform='';
  });
})();

// ── Rider card mouse-follow glow ──
document.querySelectorAll('.rider-card').forEach(card=>{
  card.addEventListener('mousemove',e=>{
    const r=card.getBoundingClientRect();
    card.style.setProperty('--mx',e.clientX-r.left+'px');
    card.style.setProperty('--my',e.clientY-r.top+'px');
  });
});

// ── Animated count-up ──
const countObserver=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(!entry.isIntersecting)return;const el=entry.target;const target=parseFloat(el.dataset.to);const decimals=el.dataset.decimals!=null?parseInt(el.dataset.decimals,10):(el.dataset.to.includes('.')?1:0);const duration=1800;const start=performance.now();function tick(now){const p=Math.min((now-start)/duration,1);const eased=1-Math.pow(1-p,4);const val=eased*target;el.textContent=decimals>0?val.toFixed(decimals):Math.round(val).toLocaleString();if(p<1)requestAnimationFrame(tick)}requestAnimationFrame(tick);countObserver.unobserve(el)})},{threshold:.3});
document.querySelectorAll('[data-to]').forEach(el=>countObserver.observe(el));

// ── Vanta.js HALO (richer config) ──
window.addEventListener("DOMContentLoaded",function(){
  if(window.VANTA&&window.VANTA.HALO){
    VANTA.HALO({
      el:".hero",
      mouseControls:true,
      touchControls:true,
      minHeight:400,
      minWidth:400,
      baseColor:0x6B1D5E,
      backgroundColor:0x130B1A,
      amplitudeFactor:2.2,
      size:2.4,
      xOffset:0.18,
      yOffset:0.1,
      speed:1.2
    });
  }
});

