# ILAKS - Laptop Remote Control Center

A modern, high-fidelity web replication of the **ILAKS Laptop Remote** interface for Windows PC.

![ILAKS Laptop Remote Preview](./screenshot-preview.png)

## ✨ Features

- **Pixel-Perfect Aesthetic**: Matching the dark midnight blue/indigo palette (`#0B0E19`, `#131728`), vivid purple accents (`#7C3AED`), emerald status indicators (`#10B981`), and modern typography (Google Fonts: *Plus Jakarta Sans*).
- **Interactive Quick Touchpad**:
  - Drag cursor/finger across the touch surface with real-time particle ripple effects and pointer marker tracking.
  - Live coordinate tracking (`dx`, `dy`).
  - Tactile **Left Click** and **Right Click** buttons with visual active states, synthesized audio feedback (Web Audio API), and toast confirmations.
- **Media Controller**:
  - Functional Play / Pause toggle.
  - Animated soundwave equalizer visualizer.
  - Previous and Next track controls cycling through media streams.
- **Control Center Suite (6 Interactive Modules)**:
  - **Touchpad**: Quick jump to touchpad with highlight animation.
  - **Keyboard**: Slide-up virtual keyboard sheet with text sender and Windows shortcuts (`Ctrl+C`, `Ctrl+V`, `Win`, `Alt+Tab`, `Esc`).
  - **Media**: Instant media player trigger.
  - **Apps**: Windows App Launcher (`Chrome`, `VS Code`, `Spotify`, `File Explorer`, `Terminal`, `Task Manager`, `Lock PC`).
  - **Files**: Instant file clipboard sync trigger.
  - **Presentation**: PowerPoint / Slides remote with Next/Prev slide navigation, slide counter, virtual laser pointer, and blackout mode.
- **Connection Manager**:
  - Live Bluetooth 5.3 telemetry (`-44 dBm` RSSI, `3.2 ms` latency, laptop battery status).
  - Ping test for latency verification.
  - Connect/Disconnect toggle with dynamic status dot.
- **Preferences & Themes**:
  - Mouse sensitivity slider (`0.5x` - `3.0x`).
  - Scroll speed slider (`0.5x` - `2.5x`).
  - Synthesized haptic audio toggle.
  - Real-time accent theme picker (Violet, Blue, Emerald, Fuchsia, Amber).
- **Responsive Modes**:
  - **Mobile Frame**: Renders the interface in a sleek smartphone shell with dynamic status bar and notch.
  - **Expanded View**: Responsive layout adaptable for larger tablet and desktop screens.

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)

### Installation & Run

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open your browser at:
`http://localhost:5173/`
