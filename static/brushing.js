document.addEventListener("DOMContentLoaded", () => {
  // Brushing Time from Settings
  let countdown = parseInt(localStorage.getItem("brushingTime") || "60");

  const timerElement = document.getElementById("timer");
  const pauseButton = document.querySelector(".pause-btn");
  const shadowPokemon = document.getElementById("shadowPokemon");
  const shadowPokemonContainer = document.querySelector(".shadow-pokemon");
  const cameraPlaceholder = document.querySelector(".camera-placeholder");
  let isPaused = false;
  let mysteryPokemonName = "";
  let mysteryPokemonTypes = [];
  let mysteryPokemonGeneration = "";
  const shadowRevealTimes = [45, 30, 15, 10, 5, 2];
  const totalPokemon = 898;

  function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.error("Camera API not supported in this browser or insecure context.");
      cameraPlaceholder.textContent = "Camera not supported or insecure context.";
      return;
    }

    const video = document.createElement("video");
    video.setAttribute("autoplay", "");
    video.setAttribute("playsinline", "");
    video.style.width = "100%";
    video.style.height = "100%";
    video.style.objectFit = "cover";
    cameraPlaceholder.innerHTML = "";
    cameraPlaceholder.appendChild(video);

    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        video.srcObject = stream;
      })
      .catch((err) => {
        console.error("Camera access denied or failed:", err);
        cameraPlaceholder.textContent = "Unable to access camera";
      });
  }

  startCamera();

  function getRandomShadowPokemon(callback) {
    const randomId = Math.floor(Math.random() * totalPokemon) + 1;
    const apiUrl = `https://pokeapi.co/api/v2/pokemon/${randomId}`;

    fetch(apiUrl)
      .then(response => response.json())
      .then(data => {
        const sprite = data.sprites.front_default;
        const types = data.types.map(t => t.type.name);

        fetch(data.species.url)
          .then(resp => resp.json())
          .then(speciesData => {
            const generation = speciesData.generation.name.replace("generation-", "");
            if (sprite && callback) callback(sprite, data.name, types, generation);
          });
      })
      .catch(err => console.error("Failed to fetch shadow Pokémon:", err));
  }

  getRandomShadowPokemon((sprite, name, types, generation) => {
    shadowPokemon.src = sprite;
    shadowPokemon.alt = "Mystery Pokémon";
    mysteryPokemonName = name;
    mysteryPokemonTypes = types;
    mysteryPokemonGeneration = generation;

    const cameraBottom = cameraPlaceholder.offsetTop + cameraPlaceholder.offsetHeight;
    shadowPokemonContainer.style.top = `${cameraBottom + 10}px`;
    shadowPokemonContainer.style.bottom = "auto";
    shadowPokemon.style.filter = "brightness(0.3) sepia(1) hue-rotate(270deg) saturate(3)";
  });

  const interval = setInterval(() => {
    if (isPaused) return;
    countdown--;
    timerElement.textContent = countdown;

    if (shadowRevealTimes.includes(countdown)) {
      let opacity = (60 - countdown) / 60 + 0.2;
      shadowPokemonContainer.style.opacity = Math.min(opacity, 1);
      let brightness = 0.3 + ((60 - countdown) / 60) * 0.7;
      brightness = Math.min(brightness, 1);
      shadowPokemon.style.filter = `brightness(${brightness})`;
    }

    if (countdown <= 0) {
      clearInterval(interval);
      shadowPokemonContainer.style.opacity = 1;
      shadowPokemon.style.filter = "brightness(1)";
      timerElement.textContent = "Done!";
      setTimeout(startCaptureSequence, 1000);
    }
  }, 1000);

  pauseButton.addEventListener("click", () => {
    isPaused = !isPaused;
    pauseButton.textContent = isPaused ? "▶️" : "⏸️";
    document.querySelector(".buddy-pokemon").style.animationPlayState = isPaused ? "paused" : "running";
  });

  function startCaptureSequence() {
    const buddy = document.querySelector(".buddy-pokemon");
    if (buddy) buddy.style.display = "none";

    const pokeball = document.createElement("img");
    pokeball.src = "/static/images/pokeball.png";
    pokeball.alt = "Pokeball";
    pokeball.className = "pokeball";
    pokeball.style.position = "absolute";
    pokeball.style.bottom = "100px";
    pokeball.style.left = "50%";
    pokeball.style.transform = "translateX(-50%)";
    pokeball.style.width = "80px";
    pokeball.style.cursor = "pointer";
    pokeball.style.zIndex = "6";

    document.body.appendChild(pokeball);

    pokeball.addEventListener("click", () => {
      pokeball.style.transition = "all 0.5s ease";
      pokeball.style.top = shadowPokemonContainer.style.top;
      pokeball.style.bottom = "auto";

      setTimeout(() => {
        shadowPokemon.style.opacity = 0;
      }, 400);

      setTimeout(() => {
        pokeball.style.animation = "wiggle 0.4s ease-in-out 3 alternate";
        setTimeout(() => {
          pokeball.style.animation = "none";
          saveCaughtPokemon();
          if (!document.querySelector(".capture-popup")) showCapturePopup();
        }, 1500);
      }, 500);
    });
  }

  function saveCaughtPokemon() {
    const profile = JSON.parse(localStorage.getItem("activeProfile"));
    if (!profile?.name) {
      console.warn("No active profile found!");
      return;
    }
  
    const newPokemon = {
      name: mysteryPokemonName,
      sprite: shadowPokemon.src,
      types: mysteryPokemonTypes,
      generation: mysteryPokemonGeneration
    };
  
    // Optionally still update local cache
    const local = JSON.parse(localStorage.getItem("caught_pokemon") || "[]");
    local.push(newPokemon);
    localStorage.setItem("caught_pokemon", JSON.stringify(local));
  
    // 🔥 Send to MongoDB
    fetch(`/api/save_pokemon/${profile.name}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newPokemon)
    }).then(res => res.json())
      .then(data => console.log("Saved Pokémon to MongoDB:", data))
      .catch(err => console.error("Failed to save Pokémon to MongoDB:", err));
  }
  

  function showCapturePopup() {
    const popup = document.createElement("div");
    popup.className = "capture-popup";
    popup.style.position = "fixed";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.background = "#fff";
    popup.style.padding = "30px";
    popup.style.borderRadius = "20px";
    popup.style.boxShadow = "0 10px 20px rgba(0,0,0,0.2)";
    popup.style.zIndex = "9999";
    popup.style.textAlign = "center";

    popup.innerHTML = `
      <h2>🎉 You caught ${mysteryPokemonName}!</h2>
      <img src="${shadowPokemon.src}" alt="${mysteryPokemonName}" style="width: 100px; height: auto; image-rendering: pixelated;">
      <p>Type: ${mysteryPokemonTypes.join(", ")}</p>
      <p>Generation: ${mysteryPokemonGeneration}</p>
      <button class="ok-btn" style="margin-top: 20px; padding: 10px 20px; font-size: 16px; border: none; background: #ffcc00; border-radius: 10px; cursor: pointer;">OK</button>
    `;

    document.body.appendChild(popup);

    popup.querySelector(".ok-btn").addEventListener("click", () => {
      window.location.href = "/";
    });
  }

  const wiggleStyle = document.createElement("style");
  wiggleStyle.innerHTML = `
  @keyframes wiggle {
    0%   { transform: translateX(-50%) rotate(0deg); }
    25%  { transform: translateX(-50%) rotate(-10deg); }
    50%  { transform: translateX(-50%) rotate(10deg); }
    75%  { transform: translateX(-50%) rotate(-10deg); }
    100% { transform: translateX(-50%) rotate(0deg); }
  }`;
  document.head.appendChild(wiggleStyle);
});
