"""Achievement system for Bongo Cat."""

import json
import os
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger("BongoCat")


@dataclass
class Achievement:
    """An achievement definition.

    Attributes:
        id: Unique identifier for the achievement
        name: Display name of the achievement
        description: Description of how to unlock
        icon: Icon emoji or character
        category: Category (slaps, combos, time, special)
        hidden: Whether the achievement is hidden until unlocked
        requirement: Requirement value (e.g., slap count)
        unlocked: Whether the achievement is unlocked
        unlock_time: When the achievement was unlocked (ISO format)
    """
    id: str
    name: str
    description: str
    icon: str
    category: str
    hidden: bool = False
    requirement: int = 0
    unlocked: bool = False
    unlock_time: Optional[str] = None


class AchievementManager:
    """Manages achievement tracking and unlocking.

    Achievements are saved to achievements.json in the user's config directory.

    Attributes:
        achievements: Dictionary of all achievements
        unlocked_count: Number of unlocked achievements
        save_path: Path to save file
        on_unlock_callback: Callback function when achievement unlocks
    """

    def __init__(self, save_path: str = "achievements.json"):
        """Initialize the achievement manager.

        Args:
            save_path: Path to save unlocked achievements
        """
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked_count = 0
        self.save_path = save_path
        self.on_unlock_callback: Optional[Callable[[Achievement], None]] = None

        self._define_achievements()
        self._load_progress()

    def _define_achievements(self) -> None:
        """Define all available achievements."""
        achievement_defs = [
            # Slap Count Achievements
            Achievement(
                id="first_slap",
                name="First Slap!",
                description="Perform your first slap",
                icon="👋",
                category="slaps",
                requirement=1
            ),
            Achievement(
                id="slaps_100",
                name="Century Club",
                description="Reach 100 slaps",
                icon="💯",
                category="slaps",
                requirement=100
            ),
            Achievement(
                id="slaps_500",
                name="Dedicated Drummer",
                description="Reach 500 slaps",
                icon="🥁",
                category="slaps",
                requirement=500
            ),
            Achievement(
                id="slaps_1000",
                name="Thousand Taps",
                description="Reach 1,000 slaps",
                icon="🎯",
                category="slaps",
                requirement=1000
            ),
            Achievement(
                id="slaps_5000",
                name="Rhythm Master",
                description="Reach 5,000 slaps",
                icon="🎵",
                category="slaps",
                requirement=5000
            ),
            Achievement(
                id="slaps_10000",
                name="Ten Thousand Touches",
                description="Reach 10,000 slaps",
                icon="⭐",
                category="slaps",
                requirement=10000
            ),
            Achievement(
                id="slaps_25000",
                name="Quarter Century",
                description="Reach 25,000 slaps",
                icon="🎖️",
                category="slaps",
                requirement=25000
            ),
            Achievement(
                id="slaps_50000",
                name="Fifty Thousand Fury",
                description="Reach 50,000 slaps",
                icon="👑",
                category="slaps",
                requirement=50000
            ),
            Achievement(
                id="slaps_100000",
                name="One Hundred Thousand Legend",
                description="Reach 100,000 slaps",
                icon="🏆",
                category="slaps",
                requirement=100000
            ),

            # Combo Achievements
            Achievement(
                id="combo_10",
                name="Getting Started",
                description="Achieve a 10x combo",
                icon="🔟",
                category="combos",
                requirement=10
            ),
            Achievement(
                id="combo_25",
                name="Combo Novice",
                description="Achieve a 25x combo",
                icon="🔥",
                category="combos",
                requirement=25
            ),
            Achievement(
                id="combo_50",
                name="Combo Expert",
                description="Achieve a 50x combo",
                icon="⚡",
                category="combos",
                requirement=50
            ),
            Achievement(
                id="combo_100",
                name="Combo Master",
                description="Achieve a 100x combo",
                icon="💥",
                category="combos",
                requirement=100
            ),
            Achievement(
                id="combo_200",
                name="Unstoppable",
                description="Achieve a 200x combo",
                icon="🌟",
                category="combos",
                requirement=200
            ),
            Achievement(
                id="combo_300",
                name="Triple Century",
                description="Achieve a 300x combo",
                icon="🚀",
                category="combos",
                requirement=300
            ),
            Achievement(
                id="combo_500",
                name="Five Hundred Frenzy",
                description="Achieve a 500x combo",
                icon="🔮",
                category="combos",
                requirement=500
            ),
            Achievement(
                id="combo_1000",
                name="Legendary Combo",
                description="Achieve a 1000x combo",
                icon="💎",
                category="combos",
                requirement=1000
            ),

            # Special Achievements
            Achievement(
                id="night_owl",
                name="Night Owl",
                description="Slap between midnight and 3 AM",
                icon="🦉",
                category="special",
                hidden=True
            ),
            Achievement(
                id="early_bird",
                name="Early Bird",
                description="Slap between 5 AM and 7 AM",
                icon="🐦",
                category="special",
                hidden=True
            ),
            Achievement(
                id="overload_survivor",
                name="Overload Survivor",
                description="Achieve the overload effect (60+ combo)",
                icon="💫",
                category="special",
                requirement=60
            ),
            Achievement(
                id="weekend_warrior",
                name="Weekend Warrior",
                description="Slap on Saturday or Sunday",
                icon="🎮",
                category="special",
                hidden=True
            ),
            Achievement(
                id="dedication",
                name="Dedicated",
                description="Open Bongo Cat 10 times",
                icon="📅",
                category="special",
                requirement=10
            ),
            Achievement(
                id="persistence",
                name="Persistence",
                description="Open Bongo Cat 50 times",
                icon="🎯",
                category="special",
                requirement=50
            ),
            Achievement(
                id="devotion",
                name="True Devotion",
                description="Open Bongo Cat 100 times",
                icon="💖",
                category="special",
                requirement=100
            ),
            Achievement(
                id="speed_demon",
                name="Speed Demon",
                description="Reach 10 combo in under 2 seconds",
                icon="⚡",
                category="special",
                hidden=True
            ),
            Achievement(
                id="marathon_session",
                name="Marathon Session",
                description="Keep a 100+ combo for over 30 seconds",
                icon="🏃",
                category="special",
                hidden=True
            ),
        ]

        for achievement in achievement_defs:
            self.achievements[achievement.id] = achievement

    def _load_progress(self) -> None:
        """Load achievement progress from save file."""
        if not os.path.exists(self.save_path):
            return

        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for achievement_id, achievement_data in data.items():
                if achievement_id in self.achievements:
                    self.achievements[achievement_id].unlocked = achievement_data.get('unlocked', False)
                    self.achievements[achievement_id].unlock_time = achievement_data.get('unlock_time')

                    if self.achievements[achievement_id].unlocked:
                        self.unlocked_count += 1

            logger.info(f"Loaded {self.unlocked_count} unlocked achievements")

        except (json.JSONDecodeError, IOError, Exception) as e:
            logger.error(f"Error loading achievements: {e}")

    def _save_progress(self) -> None:
        """Save achievement progress to file."""
        try:
            data = {}
            for achievement_id, achievement in self.achievements.items():
                if achievement.unlocked:
                    data[achievement_id] = {
                        'unlocked': True,
                        'unlock_time': achievement.unlock_time
                    }

            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except (IOError, Exception) as e:
            logger.error(f"Error saving achievements: {e}")

    def unlock(self, achievement_id: str) -> bool:
        """Unlock an achievement.

        Args:
            achievement_id: ID of the achievement to unlock

        Returns:
            True if newly unlocked, False if already unlocked or not found
        """
        if achievement_id not in self.achievements:
            return False

        achievement = self.achievements[achievement_id]

        if achievement.unlocked:
            return False

        achievement.unlocked = True
        achievement.unlock_time = datetime.now().isoformat()
        self.unlocked_count += 1

        logger.info(f"🏆 Achievement Unlocked: {achievement.name}")

        self._save_progress()

        if self.on_unlock_callback:
            self.on_unlock_callback(achievement)

        return True

    def check_slap_count(self, slap_count: int) -> List[Achievement]:
        """Check and unlock slap count achievements.

        Args:
            slap_count: Current total slap count

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []

        for achievement in self.achievements.values():
            if achievement.category == "slaps" and not achievement.unlocked:
                if slap_count >= achievement.requirement:
                    if self.unlock(achievement.id):
                        newly_unlocked.append(achievement)

        return newly_unlocked

    def check_combo(self, combo_count: int) -> List[Achievement]:
        """Check and unlock combo achievements.

        Args:
            combo_count: Current combo count

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []

        for achievement in self.achievements.values():
            if achievement.category == "combos" and not achievement.unlocked:
                if combo_count >= achievement.requirement:
                    if self.unlock(achievement.id):
                        newly_unlocked.append(achievement)

        # Check overload achievement
        if combo_count >= 60 and not self.achievements["overload_survivor"].unlocked:
            if self.unlock("overload_survivor"):
                newly_unlocked.append(self.achievements["overload_survivor"])

        return newly_unlocked

    def check_time_based(self) -> List[Achievement]:
        """Check and unlock time-based achievements.

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        now = datetime.now()
        current_hour = now.hour
        current_weekday = now.weekday()  # 0 = Monday, 6 = Sunday

        # Night Owl: midnight to 3 AM
        if 0 <= current_hour < 3 and not self.achievements["night_owl"].unlocked:
            if self.unlock("night_owl"):
                newly_unlocked.append(self.achievements["night_owl"])

        # Early Bird: 5 AM to 7 AM
        if 5 <= current_hour < 7 and not self.achievements["early_bird"].unlocked:
            if self.unlock("early_bird"):
                newly_unlocked.append(self.achievements["early_bird"])

        # Weekend Warrior: Saturday (5) or Sunday (6)
        if current_weekday >= 5 and not self.achievements["weekend_warrior"].unlocked:
            if self.unlock("weekend_warrior"):
                newly_unlocked.append(self.achievements["weekend_warrior"])

        return newly_unlocked

    def check_launch_count(self, launch_count: int) -> List[Achievement]:
        """Check and unlock launch count achievements.

        Args:
            launch_count: Total number of times app has been launched

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []

        if launch_count >= 10 and not self.achievements["dedication"].unlocked:
            if self.unlock("dedication"):
                newly_unlocked.append(self.achievements["dedication"])

        if launch_count >= 50 and not self.achievements["persistence"].unlocked:
            if self.unlock("persistence"):
                newly_unlocked.append(self.achievements["persistence"])

        if launch_count >= 100 and not self.achievements["devotion"].unlocked:
            if self.unlock("devotion"):
                newly_unlocked.append(self.achievements["devotion"])

        return newly_unlocked

    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements.

        Returns:
            List of all achievements
        """
        return list(self.achievements.values())

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get only unlocked achievements.

        Returns:
            List of unlocked achievements
        """
        return [a for a in self.achievements.values() if a.unlocked]

    def get_progress_percent(self) -> float:
        """Get achievement completion percentage.

        Returns:
            Percentage of achievements unlocked (0-100)
        """
        if not self.achievements:
            return 0.0

        return (self.unlocked_count / len(self.achievements)) * 100

    def set_unlock_callback(self, callback: Callable[[Achievement], None]) -> None:
        """Set a callback function to be called when an achievement is unlocked.

        Args:
            callback: Function to call with the unlocked achievement
        """
        self.on_unlock_callback = callback
