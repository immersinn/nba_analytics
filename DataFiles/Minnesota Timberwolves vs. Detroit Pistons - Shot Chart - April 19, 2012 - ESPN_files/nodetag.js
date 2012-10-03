(function(){
var pfs={ "http://proxy.espn.go.com/chat/chatterup/chat?event_id=15261":{"nid":16567,"tr":1},
"http://games.espn.go.com/frontpage/basketball":{"nid":15892,"tr":1,"ex":"http://espn.go.com/$|http://espn.go.com/$|http://www.espn.go.com/$|http://espn.go.com/mens-college-basketball/tournament/bracket|http://espn.go.com/broadband/espn360/index|http://espn.go.com/mens-college-basketball/tournament|http://espn.go.com/broadband/espn360/index"},
"http://games.espn.go.com/frontpage/baseball":{"nid":15907,"tr":1,"ex":"http://espn.go.com/$|http://espn.go.com/$|http://www.espn.go.com/$|http://espn.go.com/mens-college-basketball/tournament/bracket|http://espn.go.com/broadband/espn360/index|http://espn.go.com/mens-college-basketball/tournament|http://espn.go.com/broadband/espn360/index"},
"http://espn.go.com/mlb/powerrankings":{"nid":26108,"tr":1,"ex":"http://espn.go.com/$|http://www.espn.go.com/$|http://espn.go.com/$|http://www.espn.go.com/$|http://espn.go.com/mens-college-basketball/tournament/bracket|http://espn.go.com/broadband/espn360/index|http://espn.go.com/mens-college-basketball/tournament|http://espn.go.com/broadband/espn360/index"},
"http://espn.go.com/nba/powerrankings":{"nid":26107,"tr":1,"ex":"http://espn.go.com/$|http://www.espn.go.com/$|http://espn.go.com/$|http://www.espn.go.com/$|http://espn.go.com/mens-college-basketball/tournament/bracket|http://espn.go.com/broadband/espn360/index|http://espn.go.com/mens-college-basketball/tournament|http://espn.go.com/broadband/espn360/index"},
"http://sports.espn.go.com/golf/":{"nid":15895,"tr":1,"ex":"http://espn.go.com/$|http://espn.go.com/$|http://www.espn.go.com/$|http://espn.go.com/mens-college-basketball/tournament/bracket|http://espn.go.com/broadband/espn360/index|http://espn.go.com/mens-college-basketball/tournament|http://espn.go.com/broadband/espn360/index"},
"http://sports.espn.go.com/nba/":{"nid":15891,"tr":1,"ex":"http://espn.go.com/$|http://espn.go.com/$|http://www.espn.go.com/$|http://espn.go.com/mens-college-basketball/tournament/bracket|http://espn.go.com/broadband/espn360/index|http://espn.go.com/mens-college-basketball/tournament|http://espn.go.com/broadband/espn360/index"},
"http://sports.espn.go.com/mlb/":{"nid":15887,"tr":1,"ex":"http://espn.go.com/$|http://espn.go.com/$|http://www.espn.go.com/$|http://espn.go.com/mens-college-basketball/tournament/bracket|http://espn.go.com/broadband/espn360/index|http://espn.go.com/mens-college-basketball/tournament|http://espn.go.com/broadband/espn360/index"} },d=document,w=window,u=(w.gm_fake_href)?w.gm_fake_href:w.location.href;

function z(n){
var s,u;

if (Math.random()>=n['tr']) {
	return;
}



s=d.createElement('SCRIPT');
u='http://content.dl-rms.com/dt/s/'+n['nid']+'/s.js';
s.src=u;
s.type='text/javascript';
d.getElementsByTagName('head')[0].appendChild(s);
}
function r() {
	var n="",p,x;
	while (1) {
		try {
			for (p in pfs) {
			  if (u.substring(0,p.length)==p && p.length > n.length) {
				if (pfs[p].ex) {
					x=new RegExp(pfs[p].ex,"i");
					if (x.test(u)) {
						continue;
					}
				}
				n=p;
			  }
			}
			if (n.length > 0) {
				z(pfs[n]);
				return;
			}
		} catch (e) {}
	
		if (w==top) {
			break;
		}
	
		if (w==window&&u!=d.referrer) {
			u=d.referrer;
		} else {
			w=w.parent;
		}
	}
}

if (d.readyState=="complete"){
	r();
} else if (w.addEventListener){ 
	w.addEventListener("load", r, false);
} else if (w.attachEvent){ 
	w.attachEvent("onload", r);
}
})();
