// https://observablehq.com/@mbostock/fourier-series-progressive@978
function _1(md,m){return(
md`# Fourier Series - Progressive

Currently showing a Fourier series with ${m} terms. Inspired by [3Blue1Brown](https://www.youtube.com/watch?v=r6sGWTCMz2k). Portrait of Fourier by [Stuart Jantzen](https://twitter.com/Biocinematics/status/1143334994175283201).`
)}

function* _m(DOM,width,height,viewbox,M,q,add,mul,DFT,expim,K)
{
  const context = DOM.context2d(width, height);
  const scale = width / viewbox.width * 1.8;
  context.lineCap = "round";
  context.lineJoin = "round";
  for (let m = 0; true; m = (m + 1) % M) {
    context.save();
    context.fillStyle = "rgba(255, 255, 255, 0.04)";
    context.fillRect(0, 0, width, height);
    context.translate(width / 2, height / 2);
    context.scale(scale, scale);
    context.translate(-viewbox.width / 2, -viewbox.height / 2);
    context.beginPath();
    for (let t = 0; t < q; ++t) {
      const a = t * 2 / q * Math.PI;
      let p = [0, 0];
      for (let i = 0; i < m; ++i) {
        p = add(p, mul(DFT[i], expim(a * K[i])));
      }
      if (t === 0) context.moveTo(...p);
      else context.lineTo(...p);
    }
    context.closePath();
    context.lineWidth = 1.5 / scale;
    context.stroke();
    context.restore();
    context.canvas.value = m;
    yield context.canvas;
  }
}


function _3(md){return(
md`---

## Appendix`
)}

function _svg(DOMParser){return(
fetch("https://gist.githubusercontent.com/mbostock/a4fd7a68925d4039c22996cc1d4862ce/raw/d813a42956d311d73fee336e1b5aac899c835883/fourier.svg")
  .then(response => response.text())
  .then(text => (new DOMParser).parseFromString(text, "image/svg+xml"))
  .then(svg => svg.documentElement)
)}

function _P(svg,PathSampler,N)
{
  const path = svg.querySelector("path");
  const pathSampler = new PathSampler(path.getAttribute("d"));
  return Array.from({length: N}, (_, i) => pathSampler.pointAt(i / N));
}


function _K(M){return(
Int16Array.from({length: M}, (_, i) => (1 + i >> 1) * (i & 1 ? -1 : 1))
)}

function _DFT(K,N,add,mul,P,expim){return(
Array.from(K, k => {
  let x = [0, 0];
  for (let i = 0; i < N; ++i) {
    x = add(x, mul(P[i], expim(k * i * 2 / N * -Math.PI)));
  }
  return [x[0] / N, x[1] / N];
})
)}

function _N(){return(
2000
)}

function _M(){return(
350
)}

function _q(){return(
2000
)}

function _abs(){return(
function abs([re, im]) {
  return Math.hypot(re, im);
}
)}

function _expim(){return(
function expim(im) {
  return [Math.cos(im), Math.sin(im)];
}
)}

function _add(){return(
function add([rea, ima], [reb, imb]) {
  return [rea + reb, ima + imb];
}
)}

function _mul(){return(
function mul([rea, ima], [reb, imb]) {
  return [rea * reb - ima * imb, rea * imb + ima * reb];
}
)}

function _viewbox(svg){return(
svg.viewBox.baseVal
)}

function _height(width){return(
width
)}

function _PathSampler(PathData,C,L){return(
class PathSampler {
  constructor(source) {
    const data = PathData.parse(source, {normalize: true});
    const d0 = data[0];
    const d1 = data[data.length - 1];
    if (d0.type !== "M") throw new Error("expected M");
    if (d1.type !== "Z") throw new Error("expected Z");
    const segments = Array.from({length: data.length - 2}, (_, i) => {
      const {type, values} = data[i + 1];
      switch (type) {
        case "C": return new C(data[i].values.slice(-2).concat(values));
        case "L": return new L(data[i].values.slice(-2).concat(values));
      }
    });
    const start = d0.values.slice(0, 2);
    const end = data[data.length - 2].values.slice(-2);
    if (start[0] !== end[0] || start[1] !== end[1]) {
      segments.push(new L(end.concat(start)));
    }
    this.segments = segments;
  }
  pointAt(t) {
    const n = this.segments.length;
    if (!((t *= n) >= t)) return;
    const i = Math.max(0, Math.min(n - 1, Math.floor(t)));
    return this.segments[i].pointAt(t % 1);
  }
}
)}

function _L(){return(
class L {
  constructor(values) {
    this.values = values;
  }
  pointAt(t) {
    const [x0, y0, x1, y1] = this.values;
    const a = t;
    const b = 1 - t;
    return [
      a * x0 + b * x1,
      a * y0 + b * y1
    ];
  }
}
)}

function _C(){return(
class C {
  constructor(values) {
    this.values = values;
  }
  pointAt(t) {
    const [x0, y0, x1, y1, x2, y2, x3, y3] = this.values;
    const a = (1 - t) ** 3;
    const b = 3 * (1 - t) ** 2 * t;
    const c = 3 * (1 - t) * t ** 2;
    const d = t ** 3;
    return [
      a * x0 + b * x1 + c * x2 + d * x3,
      a * y0 + b * y1 + c * y2 + d * y3
    ];
  }
}
)}

function _PathData(require){return(
require("path-data@0.0.2")
)}

export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer()).define(["md","m"], _1);
  main.variable(observer("viewof m")).define("viewof m", ["DOM","width","height","viewbox","M","q","add","mul","DFT","expim","K"], _m);
  main.variable(observer("m")).define("m", ["Generators", "viewof m"], (G, _) => G.input(_));
  main.variable(observer()).define(["md"], _3);
  main.variable(observer("svg")).define("svg", ["DOMParser"], _svg);
  main.variable(observer("P")).define("P", ["svg","PathSampler","N"], _P);
  main.variable(observer("K")).define("K", ["M"], _K);
  main.variable(observer("DFT")).define("DFT", ["K","N","add","mul","P","expim"], _DFT);
  main.variable(observer("N")).define("N", _N);
  main.variable(observer("M")).define("M", _M);
  main.variable(observer("q")).define("q", _q);
  main.variable(observer("abs")).define("abs", _abs);
  main.variable(observer("expim")).define("expim", _expim);
  main.variable(observer("add")).define("add", _add);
  main.variable(observer("mul")).define("mul", _mul);
  main.variable(observer("viewbox")).define("viewbox", ["svg"], _viewbox);
  main.variable(observer("height")).define("height", ["width"], _height);
  main.variable(observer("PathSampler")).define("PathSampler", ["PathData","C","L"], _PathSampler);
  main.variable(observer("L")).define("L", _L);
  main.variable(observer("C")).define("C", _C);
  main.variable(observer("PathData")).define("PathData", ["require"], _PathData);
  return main;
}
