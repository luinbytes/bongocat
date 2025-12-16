# Phase 3: Advanced Modularization - Plan

## Objective

Extract the animation system from BongoCatWindow into a dedicated AnimationManager to further improve code organization and testability.

---

## Current State Analysis

### Animation Code in BongoCatWindow

The main window contains **~700 lines** of animation-related code:

#### 1. **Idle Animation System** (~120 lines)
- `update_idle_stretch()` - Sine wave breathing animation
- `update_stretched_image()` - Apply stretch factor to images
- Uses QTimer at 60 FPS

#### 2. **Combo Counter System** (~400 lines)
- `setup_combo_counter()` - Initialize combo tracking
- `show_combo_pop()` - Display/update combo counter
- `update_combo_style()` - Color/size based on count
- `setup_combo_animations()` - Pop and bounce effects
- `setup_overload_animation()` - Special 60+ combo effects
- `update_overload_animation()` - Wobble, pulse, shake
- `update_overload_effects()` - Visual intensity changes
- `fade_out_combo()` - Timeout fade animation
- `cleanup_combo()` - Resource cleanup

#### 3. **Floating Points System** (~180 lines)
- `show_bouncing_slaps()` - Animated +1 labels
- `cleanup_slap_label()` - Label cleanup
- `cleanup_multiple_labels()` - Batch cleanup
- Shadow effects and positioning

#### 4. **Animation Constants**
Currently hardcoded throughout:
```python
self.max_stretch = 1.08
self.min_stretch = 0.98
self.combo_timeout = 800
self.footer_height = 35
# ... many more
```

---

## Phase 3 Goals

### ✅ Primary Objectives

1. **Extract AnimationManager Class**
   - Centralize all animation logic
   - Decouple from UI implementation
   - Make animations independently testable

2. **Create Animation Constants Module**
   - Define all magic numbers
   - Document their purposes
   - Make values easily tunable

3. **Simplify BongoCatWindow**
   - Reduce to UI event handling only
   - Delegate animation work to manager
   - Cleaner, more maintainable code

4. **Add Animation Tests**
   - Test easing functions
   - Test timer coordination
   - Test resource cleanup

5. **Performance Optimization**
   - Profile animation rendering
   - Optimize hot paths
   - Reduce unnecessary redraws

---

## Proposed Architecture

### New Files to Create

```
bongo_cat/
├── animations/
│   ├── __init__.py
│   ├── manager.py              # AnimationManager class
│   ├── constants.py            # Animation constants
│   ├── idle_animation.py       # IdleAnimator
│   ├── combo_animation.py      # ComboAnimator
│   └── floating_animation.py   # FloatingPointAnimator
```

### AnimationManager API

```python
class AnimationManager:
    """Manages all animations for Bongo Cat.

    Coordinates idle breathing, combo counters, and floating points.
    Handles timers, easing functions, and resource cleanup.
    """

    def __init__(self, parent_widget, cat_label, container):
        self.parent = parent_widget
        self.cat_label = cat_label
        self.container = container

        self.idle_animator = IdleAnimator(cat_label)
        self.combo_animator = ComboAnimator(container)
        self.floating_animator = FloatingPointAnimator(container)

    def start_idle_animation(self):
        """Start the breathing animation."""

    def stop_idle_animation(self):
        """Stop the breathing animation."""

    def show_slap(self, side: str):
        """Display slap animation."""

    def show_combo(self, count: int):
        """Show/update combo counter."""

    def show_floating_point(self, count: int = 1):
        """Show floating +1 animation."""

    def pause(self):
        """Pause all animations."""

    def resume(self):
        """Resume all animations."""

    def cleanup(self):
        """Clean up all animation resources."""
```

### Constants Module

```python
# bongo_cat/animations/constants.py

# Idle Animation
IDLE_MAX_STRETCH = 1.08      # 8% taller at maximum
IDLE_MIN_STRETCH = 0.98      # 2% shorter at minimum
IDLE_FPS = 60                # Animation frame rate
IDLE_TIMER_MS = 16           # ~60 FPS (1000/60)

# Image Stretching
FIXED_BOTTOM_PERCENT = 0.25  # Bottom 25% stays fixed
STRETCHABLE_TOP_PERCENT = 0.75  # Top 75% stretches

# Slap Animation
SLAP_RESET_DELAY_MS = 100    # Return to idle after 100ms

# Combo System
COMBO_TIMEOUT_MS = 800       # Combo window
COMBO_THRESHOLD_ORANGE = 30  # Yellow → Orange
COMBO_THRESHOLD_RED = 60     # Orange → Red
COMBO_MIN_FONT_SIZE = 14
COMBO_MAX_FONT_SIZE = 20

# Combo Colors
COMBO_COLOR_YELLOW = (255, 255, 100)
COMBO_COLOR_ORANGE = (255, 150, 50)
COMBO_COLOR_RED = (255, 50, 50)

# Overload Animation (60+ combos)
OVERLOAD_TIMER_MS = 33       # ~30 FPS
OVERLOAD_SCALE_MIN = 0.9
OVERLOAD_SCALE_MAX = 1.2
OVERLOAD_WOBBLE_X = 8
OVERLOAD_WOBBLE_Y = 5

# Floating Points
FLOATING_ANIMATION_MS = 400
FLOATING_RISE_DISTANCE = 40
FLOATING_OFFSET_RANGE = (-15, 15)

# Footer
FOOTER_HEIGHT = 35
FOOTER_ANIMATION_MS = 300
```

---

## Implementation Phases

### Phase 3.1: Extract Constants (30 mins)
- Create `animations/constants.py`
- Move all magic numbers
- Add documentation
- Update main_window.py to use constants

### Phase 3.2: Create AnimationManager (2 hours)
- Create base AnimationManager class
- Extract idle animation logic
- Extract combo counter logic
- Extract floating points logic
- Add proper lifecycle management

### Phase 3.3: Update BongoCatWindow (1 hour)
- Replace inline animation code with manager calls
- Simplify event handlers
- Clean up timer management
- Test integration

### Phase 3.4: Add Tests (1 hour)
- Test animation constants
- Test easing functions
- Test timer coordination
- Test resource cleanup

### Phase 3.5: Optimize & Document (30 mins)
- Profile performance
- Optimize hot paths
- Update documentation
- Create usage examples

**Total Estimated Time**: 5 hours

---

## Benefits

### Code Organization
- **700 lines** moved from window to dedicated manager
- Clear separation: UI events → Animation logic
- Each animation type in its own module

### Testability
- Animations testable without GUI
- Mock timers for deterministic tests
- Test each animator independently

### Maintainability
- Constants in one place - easy to tune
- Animation logic centralized
- Easier to add new animation types

### Performance
- Opportunity to optimize rendering
- Better frame time consistency
- Reduced unnecessary updates

### Reusability
- AnimationManager could work with other widgets
- Easing functions can be reused
- Clean API for other projects

---

## Complexity Assessment

### Challenges

1. **Qt Timer Integration** 🟡 MEDIUM
   - Timers are tightly coupled with QWidget
   - Need proper parent widget references
   - Careful lifecycle management required

2. **Label/Widget References** 🟡 MEDIUM
   - Animations create/destroy QLabels dynamically
   - Need proper widget hierarchy
   - Memory management critical

3. **State Management** 🟡 MEDIUM
   - Animation state (paused, running, etc.)
   - Current stretch factor
   - Active combo count
   - Requires careful coordination

4. **Backward Compatibility** 🟢 EASY
   - Internal refactoring only
   - No API changes needed
   - Tests ensure nothing breaks

### Risks

- **Breaking animations** - Comprehensive testing needed
- **Performance regression** - Profile before/after
- **Memory leaks** - Careful widget cleanup
- **Timer conflicts** - Proper synchronization

### Mitigation

- ✅ Keep comprehensive tests running
- ✅ Profile performance continuously
- ✅ Manual testing of all animations
- ✅ Gradual refactoring with validation

---

## Success Criteria

Phase 3 complete when:

- [ ] All animation code extracted from main_window.py
- [ ] AnimationManager fully functional
- [ ] All constants in constants.py
- [ ] All tests passing
- [ ] No performance regression
- [ ] Comprehensive documentation
- [ ] Manual testing confirms all animations work

---

## Alternative: Minimal Phase 3

If full extraction is too complex, a **minimal approach**:

### Just Extract Constants (1 hour)
- Create constants.py only
- Document all magic numbers
- Update main_window.py
- **Benefit**: 80% of the value, 20% of the work

This would:
- Make animations easily tunable
- Improve code readability
- Document animation parameters
- Low risk, high value

---

## Recommendation

Given the complexity and time investment, I recommend:

### Option A: **Full Phase 3** (5 hours)
- Complete extraction
- Maximum modularity
- Best long-term maintainability
- **Choose if**: You want maximum code quality and plan active development

### Option B: **Minimal Phase 3** (1 hour)
- Extract constants only
- Keep animations in window
- Good enough for most cases
- **Choose if**: Current structure is working well and time is limited

### Option C: **Skip Phase 3**
- Phase 2 is already excellent
- Animations work fine in window
- Focus on new features instead
- **Choose if**: You want to add features rather than refactor

---

## My Vote: **Option B - Minimal Phase 3**

**Why**:
1. **80/20 rule** - Constants extraction gives most of the benefit
2. **Low risk** - Simple refactoring, hard to break
3. **High value** - Makes animations tunable and documented
4. **Quick wins** - 1 hour vs 5 hours
5. **Good enough** - Animations don't need to be tested in isolation

**What we'd do**:
1. Create `animations/constants.py` with all magic numbers
2. Document what each constant does
3. Update main_window.py to use constants
4. Add a few basic tests
5. Done in 1 hour!

---

## Decision Point

**What would you like to do?**

A) **Full Phase 3** - Complete AnimationManager extraction (5 hours)
B) **Minimal Phase 3** - Just extract constants (1 hour) ⭐ **Recommended**
C) **Skip Phase 3** - Phase 2 is complete, move to features
D) **Something else** - Your custom approach

Let me know and I'll proceed accordingly!
