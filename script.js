import * as THREE from 'https://cdn.skypack.dev/three@0.136.0';

// Initialize 3D Background smoothly
function init3D() {
    const container = document.getElementById('canvas-container');
    if (!container) return;

    // Scene setup
    const scene = new THREE.Scene();

    // Camera setup
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 25;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Create a 3D Robotic Core / Mesh
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 1500;

    const posArray = new Float32Array(particlesCount * 3);
    for (let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 60;
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

    const material = new THREE.PointsMaterial({
        size: 0.1,
        color: 0x0066FF,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });

    const particlesMesh = new THREE.Points(particlesGeometry, material);
    scene.add(particlesMesh);

    // Add a structural geometric shape for the "Robotics" vibe
    const geoGeometry = new THREE.IcosahedronGeometry(7, 1);
    const geoMaterial = new THREE.MeshBasicMaterial({
        color: 0x0066FF,
        wireframe: true,
        transparent: true,
        opacity: 0.15
    });
    const geoMesh = new THREE.Mesh(geoGeometry, geoMaterial);
    scene.add(geoMesh);

    // Mouse Interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX - windowHalfX);
        mouseY = (event.clientY - windowHalfY);
    });

    // Animation Loop
    const clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        // Rotate particles slowly
        particlesMesh.rotation.y = elapsedTime * 0.05;
        particlesMesh.rotation.x = elapsedTime * 0.02;

        // Rotate center geometry
        geoMesh.rotation.x += 0.002;
        geoMesh.rotation.y += 0.003;

        // Smooth mouse follow
        targetX = mouseX * 0.001;
        targetY = mouseY * 0.001;

        particlesMesh.rotation.y += 0.05 * (targetX - particlesMesh.rotation.y);
        particlesMesh.rotation.x += 0.05 * (targetY - particlesMesh.rotation.x);

        renderer.render(scene, camera);
    }

    animate();

    // Handle Resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
    init3D();

    // AI Chat Enter Key support (Mock)
    const chatInput = document.querySelector('.chat-input-area input');
    const chatBtn = document.querySelector('.chat-input-area button');
    const chatWindow = document.querySelector('.chat-window');

    const handleChat = () => {
        const text = chatInput.value.trim();
        if (text) {
            // Append user msg
            const userMsg = document.createElement('div');
            userMsg.className = 'chat-msg user';
            userMsg.textContent = text;
            chatWindow.appendChild(userMsg);
            chatInput.value = '';

            chatWindow.scrollTop = chatWindow.scrollHeight;

            // Fake bot reply
            setTimeout(() => {
                const botMsg = document.createElement('div');
                botMsg.className = 'chat-msg bot';
                botMsg.textContent = "That's a great question! I'm currently a demo UI, but I would normally fetch the latest robotics events or help debug your setup.";
                chatWindow.appendChild(botMsg);
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }, 1000);
        }
    };

    chatBtn.addEventListener('click', handleChat);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleChat();
    });
});
