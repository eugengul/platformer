import pygame
from level_objects import Block, Fire, BlueFire, LevelExit, Player


class Level:
    """Load level map and store information about level objects.

    Attributes:
        _sprite_size: Sprite size

        all_objects: A group of all level objects.
        safe_objects: A group of objects except traps and exits.
        traps: A group of objects that can kill the player.
        exits: A group of objects that allow to successfully complete a level.

        player: Store information about player. Initialized when the level is loaded.
    """

    def __init__(self, name: str, map_filename: str, sprite_size) -> None:
        """
        Args:
            name: level name
            map_filename: text file with level map
            sprite_size: sprite size
        """
        super().__init__()
        self.name = name
        self._sprite_size = sprite_size

        self.player: Player | None = None
        self.all_objects: pygame.sprite.Group = pygame.sprite.Group()
        self.safe_objects: pygame.sprite.Group = pygame.sprite.Group()
        self.traps: pygame.sprite.Group = pygame.sprite.Group()
        self.exits: pygame.sprite.Group = pygame.sprite.Group()

        self.load_map(map_filename)

    def load_map(self, filename: str) -> None:
        """Load the level map from the file

        Args:
            filename: Name of the text file with a map
        """
        level_map = self._read_from_file(filename)
        # Loop through level map and create objects
        for row_num, row in enumerate(level_map):
            for column_num, cell in enumerate(row):
                # Calculate screen coordinates
                x = column_num * self._sprite_size
                y = row_num * self._sprite_size

                # Safe blocks that won't kill you
                if cell == "B":
                    block = Block(x, y, self._sprite_size)
                    self.safe_objects.add(block)
                # Trap that can kill you
                if cell == "T":
                    trap = Fire(x, y, self._sprite_size)
                    self.traps.add(trap)
                if cell == "t":
                    trap = BlueFire(x, y, self._sprite_size)
                    self.traps.add(trap)
                # Exit from the level
                if cell == "E":
                    level_exit = LevelExit(x, y, self._sprite_size)
                    self.exits.add(level_exit)
                # Player
                if cell == "P":
                    if self.player is not None:
                        raise ValueError("You can have only one player on the level. Please check your map.")
                    self.player: Player = Player(x, y, self._sprite_size)

        self.all_objects.add(self.player)
        self.all_objects.add(self.safe_objects)
        self.all_objects.add(self.traps)
        self.all_objects.add(self.exits)

    def update(self, pressed_keys: pygame.key.ScancodeWrapper) -> None:
        """Move player and show animations

        Args:
            pressed_keys: Keys that have been pressed by the user
        """
        self.player.update(pressed_keys, self.safe_objects)

        # Animate objects
        for obj in self.all_objects:
            obj.animate()

    @staticmethod
    def _read_from_file(filename: str) -> list[list[str]]:
        """Read map from text file and convert it to the nested list

        Args:
            filename: Name of the text file with a map
        """
        with open(filename, "r") as f:
            text_map = f.readlines()
        return [list(row.strip()) for row in text_map]

