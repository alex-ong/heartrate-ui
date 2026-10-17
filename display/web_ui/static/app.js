const rateLabel = document.querySelector("#rate");
const heartCanvas = document.querySelector("#heart");
const heartContext = heartCanvas.getContext("2d");
const graphCanvas = document.querySelector("#graph");
const graphContext = graphCanvas.getContext("2d");
const heartFrames = Array.from({ length: 5 }, (_, index) => {
  const image = new Image();
  image.src = `/assets/hearts/${index + 1}.png`;
  return image;
});
const history = Array(240).fill(60);
let currentRate = 60;

function drawHeart(frame) {
  heartContext.clearRect(0, 0, heartCanvas.width, heartCanvas.height);
  if (heartFrames[frame].complete) {
    heartContext.drawImage(heartFrames[frame], 0, 0, 60, 52);
  }
}

function animationIntensity(rate) {
  if (rate < 70) return 2;
  if (rate < 100) return 3;
  if (rate < 130) return 4;
  if (rate < 160) return 5;
  return 6;
}

function animationOrder(maxFrames) {
  const end = Math.min(maxFrames, heartFrames.length);
  return [
    ...Array.from({ length: end }, (_, index) => index),
    ...Array.from(
      { length: Math.max(0, end - 2) },
      (_, index) => end - 2 - index,
    ),
  ];
}

const delay = (milliseconds) =>
  new Promise((resolve) => window.setTimeout(resolve, milliseconds));

async function animateHeart() {
  while (true) {
    const rate = currentRate;
    if (rate <= 0) {
      heartContext.clearRect(0, 0, heartCanvas.width, heartCanvas.height);
      await delay(500);
      continue;
    }

    const order = animationOrder(animationIntensity(rate));
    const stepTime = 60000 / rate / order.length;
    for (const frame of order) {
      drawHeart(frame);
      await delay(stepTime);
    }
  }
}

function drawGraph() {
  const bounds = graphCanvas.getBoundingClientRect();
  if (!bounds.width) return;

  const ratio = window.devicePixelRatio || 1;
  const width = bounds.width;
  const height = width / 2;
  graphCanvas.width = Math.round(width * ratio);
  graphCanvas.height = Math.round(height * ratio);
  graphContext.setTransform(ratio, 0, 0, ratio, 0, 0);
  graphContext.clearRect(0, 0, width, height);

  const ticks = Array.from({ length: 9 }, (_, index) => 40 + index * 20);
  graphContext.font = '16px "Press Start 2P", monospace';
  const labelWidth = Math.max(
    ...ticks.map((tick) => graphContext.measureText(String(tick)).width),
  );
  const left = 4;
  const right = width - labelWidth - 12;
  const top = 8;
  const bottom = height - 8;
  graphContext.textBaseline = "middle";
  ticks.forEach((tick, index) => {
    const y = bottom - ((tick - 40) / 160) * (bottom - top);
    const green = Math.round(15 + (200 / (ticks.length - 1)) * index);
    graphContext.fillStyle = `rgb(255, ${green}, 0)`;
    graphContext.fillText(String(tick), right + 6, y);
  });

  graphContext.strokeStyle = "red";
  graphContext.lineWidth = 1;
  graphContext.beginPath();
  graphContext.moveTo(right, top);
  graphContext.lineTo(right, bottom);
  graphContext.lineTo(left, bottom);
  graphContext.stroke();

  graphContext.strokeStyle = "#f00";
  graphContext.lineWidth = 3;
  graphContext.beginPath();
  history.forEach((value, index) => {
    const x = left + (index / (history.length - 1)) * (right - left);
    const y = bottom - ((value - 40) / 160) * (bottom - top);
    if (index === 0) graphContext.moveTo(x, y);
    else graphContext.lineTo(x, y);
  });
  graphContext.stroke();
}

function connect() {
  const socket = new WebSocket(`ws://${window.location.host}/ws`);
  socket.addEventListener("message", (event) => {
    const sample = JSON.parse(event.data);
    currentRate = sample.rate;
    rateLabel.textContent = String(currentRate).padStart(3, " ");
    history.push(currentRate);
    history.shift();
    drawGraph();
  });
  socket.addEventListener("close", (event) => {
    if (event.code === 1000 || event.code === 1001) return;
    window.setTimeout(connect, 1000);
  });
}

new ResizeObserver(drawGraph).observe(graphCanvas);
document.fonts.ready.then(drawGraph);
drawGraph();
animateHeart();
connect();