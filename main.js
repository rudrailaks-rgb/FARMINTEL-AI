// ==========================================================================
// ILAKS Laptop Remote - Core Logic & Interactive Controller
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  // --- Audio Haptic Synthesizer using Web Audio API ---
  let audioCtx = null;
  let audioFeedbackEnabled = true;

  function initAudio() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        audioCtx = new AudioContext();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  function playHapticBeep(frequency = 800, duration = 0.04, type = 'sine') {
    if (!audioFeedbackEnabled) return;
    try {
      initAudio();
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      
      osc.type = type;
      osc.frequency.setValueAtTime(frequency, audioCtx.currentTime);
      
      gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
      
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch {
      // Audio context might be restricted before first interaction
    }
  }

  // --- Toast Notification Manager ---
  const toastContainer = document.getElementById('toastContainer');
  function showToast(message, icon = '⚡') {
    if (!toastContainer) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 250);
    }, 2200);
  }

  // --- Status Bar Clock ---
  const statusClock = document.getElementById('statusClock');
  function updateClock() {
    if (!statusClock) return;
    const now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    const formattedMinutes = minutes < 10 ? '0' + minutes : minutes;
    statusClock.textContent = `${hours}:${formattedMinutes}`;
  }
  updateClock();
  setInterval(updateClock, 30000);

  // --- View Mode Switcher (Desktop Phone Frame vs Expanded) ---
  const btnPhoneView = document.getElementById('btnPhoneView');
  const btnFullView = document.getElementById('btnFullView');
  const phoneFrame = document.getElementById('phoneFrame');

  if (btnPhoneView && btnFullView && phoneFrame) {
    btnPhoneView.addEventListener('click', () => {
      btnPhoneView.classList.add('active');
      btnFullView.classList.remove('active');
      phoneFrame.classList.remove('expanded');
      showToast('Switched to Mobile Frame Mode', '📱');
    });

    btnFullView.addEventListener('click', () => {
      btnFullView.classList.add('active');
      btnPhoneView.classList.remove('active');
      phoneFrame.classList.add('expanded');
      showToast('Switched to Expanded View', '💻');
    });
  }

  // --- Interactive Modals & Slide-up Sheets ---
  const connectionModal = document.getElementById('connectionModal');
  const keyboardModal = document.getElementById('keyboardModal');
  const appsModal = document.getElementById('appsModal');
  const presentationModal = document.getElementById('presentationModal');
  const settingsModal = document.getElementById('settingsModal');

  function openModal(modal) {
    if (!modal) return;
    modal.classList.add('open');
    playHapticBeep(900, 0.05);
  }

  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove('open');
    playHapticBeep(500, 0.04);
  }

  // Close modals on clicking backdrop or close buttons
  document.querySelectorAll('.modal-backdrop').forEach((backdrop) => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        closeModal(backdrop);
      }
    });
  });

  document.querySelectorAll('[data-close-modal]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const parentModal = btn.closest('.modal-backdrop');
      if (parentModal) closeModal(parentModal);
    });
  });

  // Top header button triggers
  const openSettingsBtn = document.getElementById('openSettingsBtn');
  if (openSettingsBtn) {
    openSettingsBtn.addEventListener('click', () => openModal(settingsModal));
  }

  const manageConnectionBtn = document.getElementById('manageConnectionBtn');
  const deviceDetailsTrigger = document.getElementById('deviceDetailsTrigger');
  if (manageConnectionBtn) {
    manageConnectionBtn.addEventListener('click', () => openModal(connectionModal));
  }
  if (deviceDetailsTrigger) {
    deviceDetailsTrigger.addEventListener('click', () => openModal(connectionModal));
  }

  // Control Center 6 Cards Triggers
  const cardTouchpad = document.getElementById('cardTouchpad');
  const cardKeyboard = document.getElementById('cardKeyboard');
  const cardMedia = document.getElementById('cardMedia');
  const cardApps = document.getElementById('cardApps');
  const cardFiles = document.getElementById('cardFiles');
  const cardPresentation = document.getElementById('cardPresentation');

  if (cardTouchpad) {
    cardTouchpad.addEventListener('click', () => {
      playHapticBeep(700, 0.04);
      const quickTouchpad = document.getElementById('quickTouchpadSection');
      if (quickTouchpad) {
        quickTouchpad.scrollIntoView({ behavior: 'smooth', block: 'center' });
        quickTouchpad.style.transition = 'box-shadow 0.3s ease';
        quickTouchpad.style.boxShadow = '0 0 25px rgba(124, 58, 237, 0.6)';
        setTimeout(() => {
          quickTouchpad.style.boxShadow = '';
        }, 800);
      }
    });
  }

  if (cardKeyboard) {
    cardKeyboard.addEventListener('click', () => openModal(keyboardModal));
  }

  if (cardMedia) {
    cardMedia.addEventListener('click', () => {
      playHapticBeep(700, 0.04);
      const mediaBanner = document.getElementById('mediaBannerCard');
      if (mediaBanner) {
        mediaBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
        toggleMediaPlayState();
      }
    });
  }

  if (cardApps) {
    cardApps.addEventListener('click', () => openModal(appsModal));
  }

  if (cardFiles) {
    cardFiles.addEventListener('click', () => {
      playHapticBeep(650, 0.04);
      showToast('Files Clipboard Sync Active with PC', '📁');
    });
  }

  if (cardPresentation) {
    cardPresentation.addEventListener('click', () => openModal(presentationModal));
  }

  // --- Quick Touchpad Interactive Surface Logic ---
  const touchpadSurface = document.getElementById('touchpadSurface');
  const pointerMarker = document.getElementById('pointerMarker');
  const rippleContainer = document.getElementById('rippleContainer');
  const touchpadCoords = document.getElementById('touchpadCoords');
  const btnLeftClick = document.getElementById('btnLeftClick');
  const btnRightClick = document.getElementById('btnRightClick');
  const expandTouchpadBtn = document.getElementById('expandTouchpadBtn');

  let isTouching = false;
  let lastX = 0;
  let lastY = 0;
  let sensitivity = 1.4;

  if (touchpadSurface) {
    function startTouch(clientX, clientY) {
      isTouching = true;
      const rect = touchpadSurface.getBoundingClientRect();
      const x = clientX - rect.left;
      const y = clientY - rect.top;
      lastX = x;
      lastY = y;
      touchpadSurface.classList.add('interacting');
      updatePointerPos(x, y);
      createRipple(x, y);
      playHapticBeep(1200, 0.02, 'triangle');
    }

    function moveTouch(clientX, clientY) {
      if (!isTouching) return;
      const rect = touchpadSurface.getBoundingClientRect();
      const x = Math.max(0, Math.min(rect.width, clientX - rect.left));
      const y = Math.max(0, Math.min(rect.height, clientY - rect.top));

      const dx = Math.round((x - lastX) * sensitivity);
      const dy = Math.round((y - lastY) * sensitivity);

      lastX = x;
      lastY = y;

      updatePointerPos(x, y);
      if (touchpadCoords) {
        touchpadCoords.textContent = `dx: ${dx > 0 ? '+' + dx : dx}, dy: ${dy > 0 ? '+' + dy : dy}`;
      }
    }

    function endTouch() {
      isTouching = false;
      touchpadSurface.classList.remove('interacting');
      if (touchpadCoords) {
        touchpadCoords.textContent = 'dx: 0, dy: 0';
      }
    }

    function updatePointerPos(x, y) {
      if (pointerMarker) {
        pointerMarker.style.left = `${x}px`;
        pointerMarker.style.top = `${y}px`;
      }
    }

    function createRipple(x, y) {
      if (!rippleContainer) return;
      const ripple = document.createElement('div');
      ripple.className = 'touch-ripple';
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      rippleContainer.appendChild(ripple);
      setTimeout(() => ripple.remove(), 550);
    }

    // Mouse Listeners
    touchpadSurface.addEventListener('mousedown', (e) => startTouch(e.clientX, e.clientY));
    window.addEventListener('mousemove', (e) => {
      if (isTouching) moveTouch(e.clientX, e.clientY);
    });
    window.addEventListener('mouseup', () => {
      if (isTouching) endTouch();
    });

    // Touch Listeners
    touchpadSurface.addEventListener('touchstart', (e) => {
      if (e.touches.length > 0) {
        const touch = e.touches[0];
        startTouch(touch.clientX, touch.clientY);
      }
    }, { passive: true });

    touchpadSurface.addEventListener('touchmove', (e) => {
      if (e.touches.length > 0) {
        const touch = e.touches[0];
        moveTouch(touch.clientX, touch.clientY);
      }
    }, { passive: true });

    touchpadSurface.addEventListener('touchend', endTouch);
    touchpadSurface.addEventListener('touchcancel', endTouch);

    // Prevent default context menu on touch pad
    touchpadSurface.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      triggerRightClick();
    });
  }

  // Click Buttons Handlers
  function triggerLeftClick() {
    playHapticBeep(1100, 0.05, 'square');
    btnLeftClick?.classList.add('pressed');
    setTimeout(() => btnLeftClick?.classList.remove('pressed'), 120);
    showToast('Left Click sent', '🖱️');
  }

  function triggerRightClick() {
    playHapticBeep(850, 0.06, 'triangle');
    btnRightClick?.classList.add('pressed');
    setTimeout(() => btnRightClick?.classList.remove('pressed'), 120);
    showToast('Right Click sent', '🖱️');
  }

  if (btnLeftClick) btnLeftClick.addEventListener('click', triggerLeftClick);
  if (btnRightClick) btnRightClick.addEventListener('click', triggerRightClick);

  if (expandTouchpadBtn) {
    expandTouchpadBtn.addEventListener('click', () => {
      playHapticBeep(750, 0.05);
      showToast('Fullscreen Touchpad gesture mode active', '↗');
    });
  }

  // --- Media Controller Logic ---
  const playlist = [
    { title: 'The Weeknd • Blinding Lights', status: 'Spotify' },
    { title: 'Daft Punk • Starboy', status: 'Spotify' },
    { title: 'Dua Lipa • Levitating', status: 'Apple Music' },
    { title: 'Post Malone • Circles', status: 'YouTube' }
  ];
  let currentTrackIndex = 0;
  let isMediaPlaying = false;

  const btnPlayPause = document.getElementById('btnPlayPause');
  const iconPlay = document.getElementById('iconPlay');
  const iconPause = document.getElementById('iconPause');
  const mediaStatusSubtitle = document.getElementById('mediaStatusSubtitle');
  const equalizerVisualizer = document.getElementById('equalizerVisualizer');
  const btnPrevTrack = document.getElementById('btnPrevTrack');
  const btnNextTrack = document.getElementById('btnNextTrack');

  function updateMediaUI() {
    if (isMediaPlaying) {
      iconPlay?.classList.add('hide');
      iconPause?.classList.remove('hide');
      equalizerVisualizer?.classList.add('active');
      if (mediaStatusSubtitle) {
        mediaStatusSubtitle.textContent = playlist[currentTrackIndex].title;
        mediaStatusSubtitle.style.color = '#F1F5F9';
      }
    } else {
      iconPlay?.classList.remove('hide');
      iconPause?.classList.add('hide');
      equalizerVisualizer?.classList.remove('active');
      if (mediaStatusSubtitle) {
        mediaStatusSubtitle.textContent = 'No media playing';
        mediaStatusSubtitle.style.color = 'var(--text-muted)';
      }
    }
  }

  function toggleMediaPlayState() {
    isMediaPlaying = !isMediaPlaying;
    playHapticBeep(isMediaPlaying ? 950 : 600, 0.05);
    updateMediaUI();
    showToast(isMediaPlaying ? `Playing: ${playlist[currentTrackIndex].title}` : 'Media Paused', isMediaPlaying ? '▶' : '⏸');
  }

  if (btnPlayPause) {
    btnPlayPause.addEventListener('click', toggleMediaPlayState);
  }

  if (btnPrevTrack) {
    btnPrevTrack.addEventListener('click', () => {
      playHapticBeep(700, 0.04);
      currentTrackIndex = (currentTrackIndex - 1 + playlist.length) % playlist.length;
      isMediaPlaying = true;
      updateMediaUI();
      showToast(`Previous Track: ${playlist[currentTrackIndex].title}`, '⏮');
    });
  }

  if (btnNextTrack) {
    btnNextTrack.addEventListener('click', () => {
      playHapticBeep(700, 0.04);
      currentTrackIndex = (currentTrackIndex + 1) % playlist.length;
      isMediaPlaying = true;
      updateMediaUI();
      showToast(`Next Track: ${playlist[currentTrackIndex].title}`, '⏭');
    });
  }

  // --- Bottom Navigation Tab Switching ---
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach((item) => {
    item.addEventListener('click', () => {
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');
      playHapticBeep(800, 0.03);

      const tab = item.getAttribute('data-tab');
      if (tab === 'home') {
        document.getElementById('appScrollContainer')?.scrollTo({ top: 0, behavior: 'smooth' });
      } else if (tab === 'touchpad') {
        document.getElementById('quickTouchpadSection')?.scrollIntoView({ behavior: 'smooth' });
      } else if (tab === 'keyboard') {
        openModal(keyboardModal);
      } else if (tab === 'media') {
        document.getElementById('mediaBannerCard')?.scrollIntoView({ behavior: 'smooth' });
      } else if (tab === 'more') {
        openModal(settingsModal);
      }
    });
  });

  // --- Keyboard Modal Keystrokes & Live Typing ---
  const remoteTextInput = document.getElementById('remoteTextInput');
  const btnSendText = document.getElementById('btnSendText');

  function sendTextToPC(text) {
    if (!text.trim()) return;
    playHapticBeep(1000, 0.04);
    showToast(`Typed to laptop: "${text}"`, '⌨️');
    if (remoteTextInput) remoteTextInput.value = '';
  }

  if (btnSendText && remoteTextInput) {
    btnSendText.addEventListener('click', () => sendTextToPC(remoteTextInput.value));
    remoteTextInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        sendTextToPC(remoteTextInput.value);
      }
    });
  }

  document.querySelectorAll('.key-shortcut').forEach((btn) => {
    btn.addEventListener('click', () => {
      const key = btn.getAttribute('data-key');
      playHapticBeep(850, 0.04);
      showToast(`Sent Shortcut: [${key}]`, '⚡');
    });
  });

  document.querySelectorAll('.vk-key').forEach((keyElem) => {
    keyElem.addEventListener('click', () => {
      const char = keyElem.getAttribute('data-char');
      const action = keyElem.getAttribute('data-action');
      playHapticBeep(1100, 0.02, 'triangle');

      if (char && remoteTextInput) {
        remoteTextInput.value += char;
      } else if (action === 'backspace' && remoteTextInput) {
        remoteTextInput.value = remoteTextInput.value.slice(0, -1);
      } else if (action === 'enter' && remoteTextInput) {
        sendTextToPC(remoteTextInput.value);
      }
    });
  });

  // --- Apps Launcher Items ---
  document.querySelectorAll('.app-item-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const appName = btn.getAttribute('data-app');
      playHapticBeep(900, 0.05);
      showToast(`Launching ${appName} on Windows PC...`, '🚀');
      setTimeout(() => closeModal(appsModal), 500);
    });
  });

  // --- Presentation Controls ---
  let slideNum = 12;
  const maxSlides = 45;
  const slideCounterDisplay = document.getElementById('slideCounterDisplay');
  const btnSlidePrev = document.getElementById('btnSlidePrev');
  const btnSlideNext = document.getElementById('btnSlideNext');
  const btnLaserPointer = document.getElementById('btnLaserPointer');
  const btnBlackoutScreen = document.getElementById('btnBlackoutScreen');

  function updateSlideDisplay() {
    if (slideCounterDisplay) {
      slideCounterDisplay.textContent = `Slide ${slideNum} / ${maxSlides}`;
    }
  }

  if (btnSlidePrev) {
    btnSlidePrev.addEventListener('click', () => {
      if (slideNum > 1) slideNum--;
      playHapticBeep(700, 0.04);
      updateSlideDisplay();
      showToast(`Navigated to Slide ${slideNum}`, '◀');
    });
  }

  if (btnSlideNext) {
    btnSlideNext.addEventListener('click', () => {
      if (slideNum < maxSlides) slideNum++;
      playHapticBeep(900, 0.04);
      updateSlideDisplay();
      showToast(`Navigated to Slide ${slideNum}`, '▶');
    });
  }

  if (btnLaserPointer) {
    btnLaserPointer.addEventListener('click', () => {
      playHapticBeep(1300, 0.04);
      showToast('Virtual Laser Pointer Active on Screen', '🔴');
    });
  }

  if (btnBlackoutScreen) {
    btnBlackoutScreen.addEventListener('click', () => {
      playHapticBeep(600, 0.04);
      showToast('Screen Blackout toggled (B)', '⬛');
    });
  }

  // --- Connection Settings: Ping & Disconnect Toggle ---
  const btnTestPing = document.getElementById('btnTestPing');
  const btnDisconnectToggle = document.getElementById('btnDisconnectToggle');
  const connectionStatusText = document.getElementById('connectionStatusText');
  let isConnected = true;

  if (btnTestPing) {
    btnTestPing.addEventListener('click', () => {
      playHapticBeep(1200, 0.04);
      showToast('Ping: 3.1 ms (Low latency, 0 packet loss)', '📶');
    });
  }

  if (btnDisconnectToggle && connectionStatusText) {
    btnDisconnectToggle.addEventListener('click', () => {
      isConnected = !isConnected;
      playHapticBeep(500, 0.08);
      if (isConnected) {
        connectionStatusText.textContent = 'Connected via Bluetooth';
        connectionStatusText.style.color = 'var(--status-connected)';
        btnDisconnectToggle.textContent = 'Disconnect from Laptop';
        showToast('Connected to My Windows Laptop', '✅');
      } else {
        connectionStatusText.textContent = 'Disconnected - Tap to connect';
        connectionStatusText.style.color = 'var(--status-danger)';
        btnDisconnectToggle.textContent = 'Reconnect to Laptop';
        showToast('Disconnected from Laptop', '❌');
      }
    });
  }

  // --- Settings Slider Updates ---
  const sensSlider = document.getElementById('sensSlider');
  const sensValue = document.getElementById('sensValue');
  if (sensSlider && sensValue) {
    sensSlider.addEventListener('input', (e) => {
      sensitivity = parseFloat(e.target.value);
      sensValue.textContent = `${sensitivity.toFixed(1)}x`;
    });
  }

  const scrollSlider = document.getElementById('scrollSlider');
  const scrollValue = document.getElementById('scrollValue');
  if (scrollSlider && scrollValue) {
    scrollSlider.addEventListener('input', (e) => {
      scrollValue.textContent = `${parseFloat(e.target.value).toFixed(1)}x`;
    });
  }

  const hapticAudioToggle = document.getElementById('hapticAudioToggle');
  if (hapticAudioToggle) {
    hapticAudioToggle.addEventListener('change', (e) => {
      audioFeedbackEnabled = e.target.checked;
      showToast(audioFeedbackEnabled ? 'Audio feedback enabled' : 'Audio feedback muted', '🔊');
    });
  }

  // Accent Theme Color Picker
  document.querySelectorAll('.accent-dot').forEach((dot) => {
    dot.addEventListener('click', () => {
      document.querySelectorAll('.accent-dot').forEach(d => d.classList.remove('active'));
      dot.classList.add('active');
      const color = dot.getAttribute('data-color');
      document.documentElement.style.setProperty('--primary', color);
      document.documentElement.style.setProperty('--accent-active', color);
      document.documentElement.style.setProperty('--primary-glow', `${color}77`);
      playHapticBeep(850, 0.04);
      showToast('Accent Theme Updated', '🎨');
    });
  });
});
