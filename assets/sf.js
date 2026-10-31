/* ListingSteward free-sample-fix request form. Posts to our own beacon (VPS, logs to hits.jsonl as p=sample-request); falls back to email if the post fails. */
(function(){
  var EP="https://srv1514683.hstgr.cloud/ls/hit?p=sample-request&form=free_sample";
  function mailto(d){
    var b="Hi Lorenzo,\n\nPlease send my free sample fix.\n\nBusiness name: "+d.business+"\nTown: "+d.town+"\nMy email: "+d.email+(d.score?"\nGrader score: "+d.score:"")+"\n";
    return "mailto:lorenzo@listingsteward.com?subject="+encodeURIComponent("Free sample fix: "+d.business)+"&body="+encodeURIComponent(b);
  }
  document.querySelectorAll("form.sf").forEach(function(f){
    f.addEventListener("submit",function(e){
      e.preventDefault();
      if(f.website&&f.website.value)return; /* honeypot */
      var d={business:f.business.value.trim(),town:f.town.value.trim(),email:f.email.value.trim(),page:location.pathname,score:(f.dataset.score||"")};
      var q=new URLSearchParams(location.search),tq=q.has("test")?"&test=1":"";q.forEach(function(v,k){if(/^utm_/.test(k))d[k]=v});
      var btn=f.querySelector("button"),msg=f.querySelector(".sf-msg");btn.disabled=true;btn.textContent="Sending…";
      var body=new URLSearchParams(d);
      fetch(EP+tq+"&src="+encodeURIComponent(location.pathname),{method:"POST",body:body,mode:"cors"}).then(function(r){
        if(!r.ok)throw 0;
        f.classList.add("done");msg.hidden=false;
        msg.innerHTML="<strong>Got it.</strong> I'll email your free sample fix for "+d.business.replace(/[<>&"]/g,"")+" to "+d.email.replace(/[<>&"]/g,"")+" within 1 business day. Nothing to pay.";
        btn.textContent="Request sent";
      }).catch(function(){
        btn.disabled=false;btn.textContent="Get my free sample fix";msg.hidden=false;
        msg.innerHTML="That didn't go through. <a href=\""+mailto(d)+"\">Email the request instead</a> (it's pre-filled).";
      });
    });
  });
})();
