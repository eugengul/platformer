import pygame
import random


class BaseObject(pygame.sprite.Sprite):
    """
    Load level map and store information about level objects.

    Attributes:
        ANIMATION_SPEED: (class attribute) Time between sprite changes.
        sprite_filenames: (class attribute)List of filenames with sprites.

        sprite_size: Sprite size.
        self.sprites: Sprites loaded from files.
        self.sprite_animation_index: Current sprite index(animation)
        self.next_animation_time: At this time we can change sprite(animation)

        self.surf: The current sprite that is being displayed.
    """
    ANIMATION_SPEED = 150
    sprite_filenames = ["sprites/block.png"]

    def __init__(self, x: float, y: float, sprite_size: int):
        """
        Args:
            x: Horizontal position on the screen.
            y: Vertical position on the screen.
            sprite_size: Sprite size.
        """
        super().__init__()
        self.sprite_size = sprite_size

        # Load sprites and set initial values for animation
        self.sprites = []
        self.sprite_animation_index: int = 0
        self.next_animation_time: int = pygame.time.get_ticks() + random.randint(0, 500)
        self._load_sprites()

        # Set current sprite
        self.surf: pygame.Surface = self.sprites[0]
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        self.rect: pygame.Rect = self.surf.get_rect(left=x, top=y)

    def _load_sprites(self) -> None:
        """Load sprites from files"""
        for filename in self.sprite_filenames:
            self.sprites.append(pygame.image.load(filename).convert_alpha())

    def animate(self):
        """Change current sprite to the next in animation"""
        # Check that object has several sprites and it's time to change sprite
        if len(self.sprites) > 1 and pygame.time.get_ticks() - self.next_animation_time > 0:
            # Take next sprite
            self.sprite_animation_index += 1
            # Index should not be greater than the length
            self.sprite_animation_index %= len(self.sprites)
            self.surf = self.sprites[self.sprite_animation_index]
            # Set time for the next animation
            self.next_animation_time = self.next_animation_time + self.ANIMATION_SPEED


class Block(BaseObject):
    """Safe object"""
    sprite_filenames = ["sprites/block.png",]


class LevelExit(BaseObject):
    """Level exit. The level should finish if player hits this object."""
    sprite_filenames = ["sprites/door.png",]


class Fire(BaseObject):
    """Dangerous object. The player should die if hits this object"""
    sprite_filenames = ["sprites/fire.png", "sprites/fire1.png",
                        "sprites/fire2.png", "sprites/fire3.png",
                        "sprites/fire4.png", "sprites/fire5.png",
                        "sprites/fire6.png"]


class BlueFire(BaseObject):
    """Dangerous object. The player should die if hits this object"""
    sprite_filenames = ["sprites/bluefire.png", "sprites/bluefire1.png",
                        "sprites/bluefire2.png", "sprites/bluefire3.png",
                        "sprites/bluefire4.png", "sprites/bluefire5.png",
                        "sprites/bluefire6.png"]


class Player(BaseObject):
    """The player himself.

    Attributes:
        FALL_ACCELERATION: (class attribute) The acceleration of a player's fall.
        MOVE_SPEED: (class attribute) The speed of the player when moving left and right.
        JUMP_SPEED: (class attribute) Initial speed when jumping.
    """
    sprite_filenames = ["sprites/player.png", "sprites/player1.png",
                        "sprites/player2.png", "sprites/player3.png",]
    FALL_ACCELERATION: float = 0.3
    MOVE_SPEED: int = 2
    JUMP_SPEED: int = 10

    def __init__(self, x: float, y: float, sprite_size: int):
        """

        Args:
            x: Horizontal position on the screen.
            y: Vertical position on the screen.
            sprite_size: Sprite size.
        """
        super().__init__(x, y, sprite_size)
        self.bottom_collision: bool = False

        self.horizontal_speed: int = 0
        self.vertical_speed: int = 0

    def _load_sprites(self):
        """Load sprites from files. For player we should have different sprites for left and right movement."""
        super()._load_sprites()
        self.sprites_right = self.sprites
        # Mirror sprites for left movement.
        self.sprites_left = [pygame.transform.flip(sprite, True, False) for sprite in self.sprites]

    def update(self, pressed_keys: pygame.key.ScancodeWrapper, level_objects: pygame.sprite.Group) -> None:
        """Change the player's position in response to keypresses.

        Args:
            pressed_keys: Keys pressed by the user.
            level_objects: Level objects
        """
        # Player can't jump in the air
        self.horizontal_speed = 0
        # Jump
        if pressed_keys[pygame.K_UP] and self.bottom_collision:
            self.vertical_speed = -self.JUMP_SPEED
        # Move left
        if pressed_keys[pygame.K_LEFT]:
            # Change sprites(player should look to the left)
            self.sprites = self.sprites_left
            self.horizontal_speed = -self.MOVE_SPEED
        # Move right
        if pressed_keys[pygame.K_RIGHT]:
            # Change sprites(player should look to the left)
            self.sprites = self.sprites_right
            self.horizontal_speed = self.MOVE_SPEED

        # Check collisions with other objects
        self._movement_with_collision(level_objects)

        # If the player is not standing on the surface, increase the fall speed.
        if not self.bottom_collision:
            self.vertical_speed += self.FALL_ACCELERATION

    def _movement_with_collision(self, level_objects: pygame.sprite.Group) -> None:
        """Check collisions. Stop player if necessary and fix objects overlapping

        Args:
            level_objects: level objects
        """
        self.bottom_collision: bool = False

        # First check horizontal collisions(don't move sprite vertically)
        self.rect.move_ip(self.horizontal_speed, 0)
        for level_object in level_objects:
            if level_object.rect.colliderect(self.rect):
                # Player moves right
                if self.horizontal_speed > 0 and self.rect.right >= level_object.rect.left:
                    self.horizontal_speed = 0
                    # Fix overlap
                    self.rect.move_ip(level_object.rect.left - self.rect.right, 0)
                # Sprite moves left
                elif self.horizontal_speed < 0 and self.rect.left <= level_object.rect.right:
                    # Stop
                    self.horizontal_speed = 0
                    # Player shouldn't overlap the object
                    self.rect.move_ip(level_object.rect.right - self.rect.left, 0)

        # Check vertical collisions
        self.rect.move_ip(0, self.vertical_speed)
        for level_object in level_objects:
            if level_object.rect.colliderect(self.rect):
                # Player moves down and collides with an object
                if self.vertical_speed > 0 and self.rect.bottom > level_object.rect.top:
                    # Stop
                    self.vertical_speed = 0
                    # Mark that player is standing on something
                    self.bottom_collision = True
                    # Player shouldn't overlap the object
                    self.rect.move_ip(0, level_object.rect.top - self.rect.bottom)
                # Player moves up
                elif self.vertical_speed < 0 and self.rect.top <= level_object.rect.bottom:
                    # Stop
                    self.vertical_speed = 0
                    # Player shouldn't overlap the object
                    self.rect.move_ip(0, level_object.rect.bottom - self.rect.top)