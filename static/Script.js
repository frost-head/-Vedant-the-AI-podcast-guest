const container = document.getElementById('container');
const canvas = document.getElementById('canvas1');
const file = document.getElementById('fileupload');
console.log(file)
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const ctx = canvas.getContext('2d');
//ctx.globalCompositeOperation = 'difference'
ctx.lineCap = 'round';
let audioSource;
let analyser;

async function fetchAudio() {
    try {
      const response = await fetch('/get_audio');
      const data = await response.json();
      const audioBase64 = data.audio_base64;
    
      // Use the audioBase64 string as needed, e.g., create a URL for playback
      const audioUrl = 'data:audio/wav;base64,'+ audioBase64;
      const audio = new Audio(audioUrl);
      audio.load();
      audio.play();
    } catch (error) {
      console.error('Error fetching audio:', error);
    }
  }
  
  
container.addEventListener('click', function(){

    const audio1 = document.getElementById('audio1');

    const audioContext = new AudioContext();
    fetchAudio();
    audioSource = audioContext.createMediaElementSource(audio1);
    analyser = audioContext.createAnalyser();
    audioSource.connect(analyser);
    analyser.connect(audioContext.destination);
    analyser.fftSize = 512;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const barWidth = 25;
    let barHeight;
    let x;

    function animate(){
        x = 0;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        analyser.getByteFrequencyData(dataArray);
        drawVisualiser(bufferLength, x, barWidth, barHeight, dataArray);
        requestAnimationFrame(animate);
    }
    animate();
});

file.addEventListener('change', function(){
    const files = this.files;
    const audio1 = document.getElementById('audio1');
    audio1.src = URL.createObjectURL(files[0]);
    audio1.load();
    audio1.play();

    audioSource = audioContext.createMediaElementSource(audio1);
    analyser = audioContext.createAnalyser();
    audioSource.connect(analyser);
    analyser.connect(audioContext.destination);
    analyser.fftSize = 512;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const barWidth = 25;
    let barHeight;
    let x = 0;

    function animate(){
        // x = 0;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        analyser.getByteFrequencyData(dataArray);
        drawVisualiser(bufferLength, x, barWidth, barHeight, dataArray);
        // drawVisualiser2(bufferLength, x, barWidth, barHeight, dataArray);

        requestAnimationFrame(animate);
    }
    animate();
});

function drawVisualiser(bufferLength, x, barWidth, barHeight, dataArray){
    // ctx.translate(canvas.width/2, canvas.height/2 );
    for (let i = 0; i < bufferLength; i++){
        
        barHeight = dataArray[i]+400 ;
        const hue = 200 + i;
        ctx.fillStyle = 'hsl(' + (hue-60) + ',100%, 35%)';
        ctx.fillRect(x, barHeight-540, barWidth,barHeight);
        ctx.fillStyle = 'hsl(' + (hue-40) + ',100%, 40%)';
        ctx.fillRect(x, barHeight-360, barWidth,barHeight);
        ctx.fillStyle = 'hsl(' + (hue-30) + ',100%, 40%)';
        ctx.fillRect(x, barHeight-180, barWidth,barHeight);

        ctx.fillStyle = 'hsl(' + (hue-20) + ',100%, 50%)';
        ctx.fillRect(x, canvas.height-barHeight-100, barWidth,barHeight);

        ctx.fillStyle = 'hsl(' + (hue) + ',100%, 60%)';
        ctx.fillRect(x, canvas.height-barHeight+0, barWidth,barHeight);


        ctx.fillStyle = 'hsl(' + (hue+20) + ',100%, 50%)';
        ctx.fillRect(x, canvas.height-barHeight+100, barWidth,barHeight);
        
        
        ctx.fillStyle = 'hsl(' + (hue+20) + ',100%, 40%)';
        ctx.fillRect(x, canvas.height-barHeight+180, barWidth,barHeight);

        ctx.fillStyle = 'hsl(' + (hue+40) + ',100%, 35%)';
        ctx.fillRect(x, canvas.height-barHeight+360, barWidth,barHeight);
        
        // ctx.translate(canvas.width/2, canvas.height/2);
        // ctx.rotate(i * Math.PI * 8/ bufferLength);
        
        // ctx.strokeStyle = 'hsl(' + hue + ',100%, 0%)';
        // ctx.lineWidth = barHeight*1.5;
        // ctx.fillStyle = 'hsl(' + hue + ',100%, 50%)';
        // // ctx.beginPath();
        // ctx.lineTo(x, barHeight);

        // ctx.moveTo(0,0);
      
        // ctx.stroke()
        x+=barWidth;
        // ctx.save();
        // const hue = 200 + i*2;
        // ctx.lineTo(x, barHeight);
        // ctx.stroke();
        // x += barWidth
        // ctx.lineWidth = barHeight*1.5;

        // ctx.strokeStyle = 'hsl(' + hue   + ',100%, 50%)';
        // ctx.fillStyle = 'hsl(' + hue + ',100%, 50%)';
        // ctx.beginPath();
        // // ctx.moveTo(0,0);
        // ctx.lineTo(x, barHeight);
        // ctx.stroke();


        

        // // ctx.arc(0, barHeight + barHeight/5 , barHeight/20, 0, Math.PI * 2);
        // // ctx.fill();
        // // ctx.beginPath();
        // // ctx.arc(0, barHeight + barHeight/2, barHeight/10, 0, Math.PI * 2);
        // // ctx.fill();
        // ctx.restore();
    }
    
}

// function drawVisualiser2(bufferLength, x, barWidth, barHeight, dataArray){
//     for (let i = 0; i < bufferLength; i++){
//         barHeight = dataArray[i] *5;
//         const red = i * barHeight/30;
//         const green = i/2;
//         ctx.fillStyle = 'white';
//         ctx.fillRect(x, canvas.height-barHeight - 30, barWidth,15);
//         ctx.fi
//     }}