"""Animation constants for Bongo Cat.

This module contains all magic numbers and tunable parameters for animations.
Centralizing these values makes the animations easier to understand and adjust.
"""

# =============================================================================
# IDLE BREATHING ANIMATION
# =============================================================================

# Stretch animation range
IDLE_MAX_STRETCH = 1.08
"""float: Maximum stretch factor (8% taller at peak of breath)"""

IDLE_MIN_STRETCH = 0.98
"""float: Minimum stretch factor (2% shorter at bottom of breath)"""

# Timing
IDLE_TIMER_MS = 16
"""int: Idle animation timer interval in milliseconds (~60 FPS)"""

IDLE_ANIMATION_SPEED = 0.05
"""float: Speed of sine wave progression (higher = faster breathing)"""

# Image regions
FIXED_BOTTOM_PERCENT = 0.25
"""float: Percentage of image bottom that stays fixed (paws don't stretch)"""

STRETCHABLE_TOP_PERCENT = 0.75
"""float: Percentage of image top that stretches with breathing"""


# =============================================================================
# SLAP ANIMATION
# =============================================================================

SLAP_RESET_DELAY_MS = 100
"""int: Delay before returning to idle image after slap (milliseconds)"""


# =============================================================================
# COMBO COUNTER SYSTEM
# =============================================================================

# Timing
COMBO_TIMEOUT_MS = 800
"""int: Time window for chaining combos (milliseconds)"""

COMBO_TIMEOUT_TIMER_MS = 800
"""int: Timeout before combo fades out (milliseconds)"""

# Thresholds for color changes
COMBO_THRESHOLD_ORANGE = 30
"""int: Combo count where color changes from yellow to orange"""

COMBO_THRESHOLD_RED = 60
"""int: Combo count where color changes to red and overload starts"""

# Font sizing
COMBO_MIN_FONT_SIZE = 14
"""int: Minimum font size for combo counter"""

COMBO_MAX_FONT_SIZE = 20
"""int: Maximum font size for combo counter"""

COMBO_FONT_SIZE_DIVISOR = 3
"""int: Divisor for calculating font size increase (count // divisor)"""

# Colors (RGB tuples as strings for Qt stylesheets)
COMBO_COLOR_YELLOW = "255, 255, 100"
"""str: RGB color for combos 1-29 (yellow)"""

COMBO_COLOR_ORANGE = "255, 150, 50"
"""str: RGB color for combos 30-59 (orange)"""

COMBO_COLOR_RED = "255, 50, 50"
"""str: RGB color for combos 60+ (red)"""

# Positioning
COMBO_POSITION_RIGHT_MARGIN = 10
"""int: Margin from right edge for combo counter (pixels)"""

COMBO_POSITION_TOP_MARGIN = 10
"""int: Margin from top edge for combo counter (pixels)"""

COMBO_POSITION_OFFSET_BELOW_TOTAL = 5
"""int: Vertical offset below total counter when both visible (pixels)"""

# Animation
COMBO_POP_SCALE = 1.2
"""float: Scale factor for pop animation (120% of normal size)"""

COMBO_POP_DURATION_MS = 150
"""int: Duration of pop animation (milliseconds)"""

COMBO_BOUNCE_OFFSET = 5
"""int: Vertical bounce distance (pixels)"""

# Fade out animation
COMBO_FADE_DURATION_MS = 300
"""int: Duration of fade out animation (milliseconds)"""

COMBO_FADE_SCALE_FACTOR = 0.8
"""float: Scale factor during fade out (80% of original)"""

# Shadow
COMBO_SHADOW_BLUR_RADIUS = 4
"""int: Blur radius for combo counter shadow"""

COMBO_SHADOW_COLOR_ALPHA = 200
"""int: Alpha value for shadow color (0-255)"""


# =============================================================================
# OVERLOAD ANIMATION (60+ Combos)
# =============================================================================

# Timing
OVERLOAD_TIMER_MS = 33
"""int: Overload animation timer interval (~30 FPS)"""

# Scale/pulse animation
OVERLOAD_ANIMATION_SPEED = 0.08
"""float: Speed of pulse animation"""

OVERLOAD_SCALE_MIN = 0.9
"""float: Minimum scale during pulse (90%)"""

OVERLOAD_SCALE_MAX = 1.2
"""float: Maximum scale during pulse (120%)"""

# Wobble/shake
OVERLOAD_WOBBLE_X_AMPLITUDE = 8
"""int: Horizontal wobble distance (pixels)"""

OVERLOAD_WOBBLE_Y_AMPLITUDE = 5
"""int: Vertical wobble distance (pixels)"""

OVERLOAD_WOBBLE_X_FREQUENCY = 3.0
"""float: Frequency multiplier for horizontal wobble"""

OVERLOAD_WOBBLE_Y_FREQUENCY = 2.0
"""float: Frequency multiplier for vertical wobble"""

OVERLOAD_SHAKE_MAX = 2
"""int: Maximum shake offset (pixels)"""

OVERLOAD_SHAKE_THRESHOLD_HIGH = 0.8
"""float: Animation time threshold for shake (high)"""

OVERLOAD_SHAKE_THRESHOLD_LOW = 0.2
"""float: Animation time threshold for shake (low)"""

# Color intensity
OVERLOAD_INTENSITY_MIN = 0.6
"""float: Minimum color intensity (60%)"""

OVERLOAD_INTENSITY_MAX = 1.5
"""float: Maximum color intensity (150%)"""

# Shadow
OVERLOAD_SHADOW_BLUR_MIN = 4
"""int: Minimum shadow blur radius"""

OVERLOAD_SHADOW_BLUR_MAX = 7
"""int: Maximum shadow blur radius"""

OVERLOAD_SHADOW_ALPHA_MIN = 100
"""int: Minimum shadow alpha"""

OVERLOAD_SHADOW_ALPHA_MAX = 200
"""int: Maximum shadow alpha"""


# =============================================================================
# FLOATING POINTS (+1 ANIMATION)
# =============================================================================

# Timing
FLOATING_ANIMATION_DURATION_MS = 400
"""int: Duration of floating +1 animation (milliseconds)"""

# Movement
FLOATING_RISE_DISTANCE = 40
"""int: Vertical distance the +1 floats upward (pixels)"""

FLOATING_HORIZONTAL_OFFSET_MIN = -15
"""int: Minimum horizontal randomization (pixels)"""

FLOATING_HORIZONTAL_OFFSET_MAX = 15
"""int: Maximum horizontal randomization (pixels)"""

# Positioning
FLOATING_VERTICAL_CENTER_OFFSET = 10
"""int: Vertical offset from cat center (pixels)"""

FLOATING_SHADOW_OFFSET_X = 2
"""int: Shadow horizontal offset from main label (pixels)"""

FLOATING_SHADOW_OFFSET_Y = 2
"""int: Shadow vertical offset from main label (pixels)"""

# Font
FLOATING_FONT_SIZE = 14
"""int: Font size for floating +1 labels"""

# Colors
FLOATING_MAIN_COLOR = "rgba(245, 245, 245, 0.95)"
"""str: Color for main +1 label (off-white)"""

FLOATING_SHADOW_COLOR = "rgba(0, 0, 0, 0.85)"
"""str: Color for shadow +1 label (dark)"""

# Fade
FLOATING_FADE_START = 1.0
"""float: Starting opacity for fade animation"""

FLOATING_FADE_END_SINGLE = 0.8
"""float: Ending opacity for single +1 (no combo)"""

FLOATING_FADE_END_COMBO = 0.0
"""float: Ending opacity when merging into combo"""


# =============================================================================
# TOTAL SLAPS LABEL
# =============================================================================

TOTAL_SLAPS_MIN_WIDTH = 50
"""int: Minimum width for total slaps label (pixels)"""

TOTAL_SLAPS_RIGHT_MARGIN = 10
"""int: Margin from right edge (pixels)"""

TOTAL_SLAPS_TOP_MARGIN = 10
"""int: Margin from top edge (pixels)"""

TOTAL_SLAPS_FONT_SIZE = 14
"""int: Font size for total slaps counter"""

TOTAL_SLAPS_SHADOW_BLUR = 8
"""int: Shadow blur radius"""

TOTAL_SLAPS_SHADOW_ALPHA = 100
"""int: Shadow alpha value"""


# =============================================================================
# FOOTER
# =============================================================================

FOOTER_HEIGHT = 35
"""int: Height of footer widget (pixels)"""

FOOTER_VERTICAL_OFFSET = 60
"""int: Vertical offset from bottom of cat (pixels)"""

FOOTER_ANIMATION_DURATION_MS = 300
"""int: Duration of footer fade animation (milliseconds)"""

FOOTER_ALPHA_MULTIPLIER = 2.55
"""float: Multiplier to convert 0-100 alpha to 0-255"""


# =============================================================================
# WINDOW SIZING
# =============================================================================

MIN_HEIGHT_WITH_SETTINGS = 450
"""int: Minimum window height when settings panel is visible (pixels)"""


# =============================================================================
# IMAGE ROTATION
# =============================================================================

IMAGE_ROTATION_DEGREES = -13
"""int: Degrees to rotate cat images (negative = counterclockwise)"""


# =============================================================================
# CALCULATED CONSTANTS
# =============================================================================

def get_combo_font_size(combo_count: int) -> int:
    """Calculate font size based on combo count.

    Args:
        combo_count: Current combo count

    Returns:
        Font size in pixels (between COMBO_MIN_FONT_SIZE and COMBO_MAX_FONT_SIZE)

    Example:
        >>> get_combo_font_size(1)
        14
        >>> get_combo_font_size(30)
        24
    """
    size = COMBO_MIN_FONT_SIZE + (combo_count // COMBO_FONT_SIZE_DIVISOR)
    return min(size, COMBO_MAX_FONT_SIZE)


def get_combo_color(combo_count: int) -> str:
    """Get combo color based on count.

    Args:
        combo_count: Current combo count

    Returns:
        RGB color string for use in Qt stylesheets

    Example:
        >>> get_combo_color(10)
        '255, 255, 100'  # Yellow
        >>> get_combo_color(50)
        '255, 150, 50'   # Orange
        >>> get_combo_color(100)
        '255, 50, 50'    # Red
    """
    if combo_count < COMBO_THRESHOLD_ORANGE:
        return COMBO_COLOR_YELLOW
    elif combo_count < COMBO_THRESHOLD_RED:
        return COMBO_COLOR_ORANGE
    else:
        return COMBO_COLOR_RED


def is_overload(combo_count: int) -> bool:
    """Check if combo count triggers overload animation.

    Args:
        combo_count: Current combo count

    Returns:
        True if overload effects should be active

    Example:
        >>> is_overload(50)
        False
        >>> is_overload(60)
        True
    """
    return combo_count >= COMBO_THRESHOLD_RED
