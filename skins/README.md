# Bongo Cat Skins

This directory contains all available skins for Bongo Cat. Each skin is a separate folder with images and metadata.

## Available Skins

### 🐱 Default
**Location**: `skins/default/`
The classic original Bongo Cat design.

### 🕹️ Retro Cat
**Location**: `skins/retro/`
Nostalgic retro-style cat with classic vibes. Perfect for pixel art enthusiasts!

### 💫 Neon Cat
**Location**: `skins/neon/`
Vibrant cyberpunk neon-themed cat. Great for a futuristic aesthetic!

## Creating Your Own Skin

### Step 1: Create a Skin Folder

Create a new folder in `skins/` with your skin name:
```bash
mkdir skins/my-awesome-skin
```

### Step 2: Add Your Images

Add three PNG files:
- `cat-rest.png` - Idle/resting animation
- `cat-left.png` - Left paw slapping
- `cat-right.png` - Right paw slapping

**Image Tips:**
- Use PNG format with transparency
- Any size works (scaled automatically)
- Consistent style across all three images
- Higher resolution = better quality (but larger file size)

### Step 3: Create skin.json

Create a `skin.json` file with metadata:

```json
{
  "name": "My Awesome Skin",
  "author": "YourName",
  "version": "1.0.0",
  "description": "A brief description of your skin theme",
  "images": {
    "idle": "cat-rest.png",
    "left": "cat-left.png",
    "right": "cat-right.png"
  },
  "rotation_degrees": -13
}
```

**Fields Explained:**
- `name` - Display name (shown in skin selector)
- `author` - Your name or username
- `version` - Skin version (for updates)
- `description` - Brief theme description
- `images` - Image file names (relative to skin folder)
- `rotation_degrees` - Rotation angle (default: -13)

### Step 4: Test Your Skin

1. Launch Bongo Cat
2. Right-click the cat → Settings
3. Click "Skin" dropdown
4. Select your new skin
5. Enjoy!

## Skin Themes Ideas

Looking for inspiration? Try these themes:

### Aesthetic Themes
- 🌸 Pastel Cat - Soft, muted colors
- 🌈 Rainbow Cat - Colorful pride theme
- 🌙 Moonlight Cat - Dark mode friendly
- ☀️ Sunshine Cat - Bright and cheerful
- 🎃 Spooky Cat - Halloween theme
- 🎄 Holiday Cat - Festive winter theme

### Art Styles
- 🖼️ Pixel Art Cat - Retro 8-bit style
- 🎨 Watercolor Cat - Artistic brush strokes
- ✏️ Sketch Cat - Hand-drawn pencil style
- 🎭 Cartoon Cat - Animated series style
- 🤖 Robotic Cat - Sci-fi mechanical theme

### Character Themes
- 🦁 Lion Cat - Majestic mane
- 🐯 Tiger Cat - Striped pattern
- 🐼 Panda Cat - Black and white
- 🦊 Fox Cat - Fluffy tail variant
- 🐱‍👤 Ninja Cat - Stealth mode

## Sharing Your Skins

Created an awesome skin? Share it with the community!

1. **GitHub Discussions**: Post screenshots and download links
2. **GitHub Releases**: Submit as a community skin pack
3. **Social Media**: Tag #BongoCat and share your creation

### Skin Submission Checklist

Before sharing:
- [ ] All three images included (idle, left, right)
- [ ] skin.json is valid JSON
- [ ] Images are appropriate content (SFW)
- [ ] Proper attribution if using others' artwork
- [ ] Tested in Bongo Cat app

## Copyright & Attribution

**Important**: When creating skins:
- Only use images you have rights to
- Give credit if remixing others' work
- Respect original artists' licenses
- Consider using Creative Commons images
- Don't use copyrighted characters without permission

## Finding Resources

### Free Image Resources
- **Pixabay** - Free stock images (CC0)
- **Unsplash** - High-quality photos (free to use)
- **OpenGameArt** - Game sprites and art
- **Kenney.nl** - Free game assets
- **itch.io** - Indie game assets (check licenses)

### Art Tools
- **GIMP** - Free image editor (like Photoshop)
- **Krita** - Free digital painting
- **Piskel** - Browser-based pixel art tool
- **Photopea** - Browser-based Photoshop alternative
- **Aseprite** - Pixel art animation tool ($)

## Troubleshooting

**Skin doesn't appear in dropdown**
- Check skin.json is valid JSON (use JSONLint.com)
- Ensure folder name has no spaces or special characters
- Verify all three image files exist

**Images look distorted**
- Try adjusting `rotation_degrees` in skin.json
- Ensure images have similar dimensions/aspect ratios
- Check transparency layers in your PNG files

**Skin loads but looks wrong**
- Verify image file names match skin.json exactly
- Check for typos in file names
- Ensure PNG files aren't corrupted

---

**Need Help?** Open an issue on GitHub or check the main README for more info!
