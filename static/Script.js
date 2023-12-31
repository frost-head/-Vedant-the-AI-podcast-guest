const container = document.getElementById('container');
const canvas = document.getElementById('canvas1');
// const aduio = new Audio('/audio');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const ctx = canvas.getContext('2d');
//ctx.globalCompositeOperation = 'difference'
ctx.lineCap = 'round';
let audioSource;
let analyser;
const audio1 = document.getElementById('audio1');

  
// canvas.addEventListener('click', function(){

//     // fetchAudio();
//     // console.log('called');
    
//     const audio1 = document.getElementById('audio1');
    
//     const audioContext = new AudioContext();
//     // console.log(audio1)
    
//     if (audio1.paused) {
//         audio1.play();
//     } else {
//         audio1.pause();
//     }
//     audioSource = audioContext.createMediaElementSource(audio1);
//     analyser = audioContext.createAnalyser();
//     audioSource.connect(analyser);
//     analyser.connect(audioContext.destination);
//     analyser.fftSize = 512;
//     const bufferLength = analyser.frequencyBinCount;
//     const dataArray = new Uint8Array(bufferLength);

//     const barWidth = 25;
//     let barHeight;
//     let x;

//     function animate(){
//         x = 0;
//         ctx.clearRect(0, 0, canvas.width, canvas.height);
//         analyser.getByteFrequencyData(dataArray);
//         drawVisualiser(bufferLength, x, barWidth, barHeight, dataArray);
//         requestAnimationFrame(animate);
//     }
//     animate();
// });

const audioContext = new AudioContext();
startAnimation();
// Function to start the animation
function startAnimation() {
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

    function animate() {
        x = 0;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        analyser.getByteFrequencyData(dataArray);
        drawVisualiser(bufferLength, x, barWidth, barHeight, dataArray);
        requestAnimationFrame(animate);
    }
    animate();
}

// Event listener for the canvas click
canvas.addEventListener('click', function() {
    const audio1 = document.getElementById('audio1');

    // Toggle play/pause
    if (audio1.paused) {
        audio1.play();
        startAnimation(); // Call the animation when audio starts playing
    } else {
        audio1.pause();
    }
});

// Event listener for the audio play
audio1.addEventListener('play', function() {
    startAnimation(); // Call the animation when audio starts playing
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

z