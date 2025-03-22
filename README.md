# 🐱 BONGO CAT DESKTOP BUDDY 🐱

![Bongo Cat](img/cat-rest.png)

**Bongo Cat Desktop Buddy** is an interactive pet that lives on your desktop and responds to *every* keystroke, mouse click, and controller button press by slapping its little paws! Watch as your furry desktop companion reacts to your inputs in real-time.

## ✨ Features

- **Input Responsive**: Slaps its paws when you press keys, click mouse buttons, or use a controller
- **Combo System**: Chain slaps together to build combos with escalating visual effects
- **Animations**: Subtle breathing animation when idle, dynamic slapping actions
- **Counters**: Track your total slaps with floating animations and combo counters
- **Customizable**: Extensive settings to personalize your experience
- **Always-on-Top**: Stays visible while you work or play
- **System Tray**: Minimizes to system tray for easy access

## 🚀 Usage

Just launch the application and Bongo Cat will appear on your screen, ready to react to your inputs:

- **Keyboard presses**: Cat slaps its paws
- **Mouse clicks**: More paw slapping
- **Controller buttons**: Even more slapping!

Right-click the cat for quick menu options or access the settings panel through the footer.

## ⚙️ Configuration

Access settings by:
1. Hovering over the cat to reveal the footer
2. Clicking the ⚙ Settings button

### Available Settings:

| Setting | Description |
|---------|-------------|
| Auto-hide footer | Toggle footer visibility when not hovering |
| Footer opacity | Adjust the transparency of the footer |
| Always show total | Display permanent counter of total slaps |
| Floating +1 animations | Show animated "+1" popups for each slap |
| Invert cat | Mirror the cat horizontally |
| Start with Windows | Launch automatically at system startup |
| Max slap count | Set a maximum slap count (or unlimited) |

## 🎮 Input Detection

Bongo Cat responds to:
- Any keyboard key press
- Any mouse button click
- Controller buttons, triggers, joysticks, and d-pad inputs

All inputs are detected globally, so Bongo Cat works even when using other applications!

## 🌈 Special Effects

- **Combo System**: Chain inputs within 800ms to build combos
- **Visual Feedback**: Increasing excitement in the combo counter as chain grows
- **Level-based Effects**: 
  - 1-30 combos: Yellow counter
  - 30-60 combos: Orange counter
  - 60+ combos: Red counter with pulsing effects and shake

## 💼 Other Features

- **Slap Counter**: Keep track of total slaps
- **Draggable Window**: Position the cat anywhere on your screen
- **Pause Mode**: Temporarily disable animations and input detection
- **System Tray Icon**: Quick access even when minimized
- **Config File**: Advanced configuration through bongo.ini file

## 🔧 Technical Details

Built using:
- PyQt5 for the user interface
- pynput for global keyboard and mouse hooks
- pygame for controller input detection
- Custom animation system for smooth transitions
- Transparent, frameless window that stays on top

## 🤔 Why Bongo Cat?

Why not? Everyone needs a desktop companion to keep them company during long coding sessions or gaming marathons. Plus, watching the slap counter reach astronomical numbers is oddly satisfying!

---

*Bongo Cat is not affiliated with the original Bongo Cat meme. This is a fan-made desktop application inspired by the internet phenomenon.*