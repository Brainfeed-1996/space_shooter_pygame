import pygame
import random
import math
from pygame import mixer
import os

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()

# Configuration de l'écran
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Space Shooter")

# Couleurs
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)

# Sons
shoot_sound = mixer.Sound(os.path.join("sounds", "laser.wav"))
shoot_sound.set_volume(0.3)
explosion_sound = mixer.Sound(os.path.join("sounds", "explosion.wav"))
explosion_sound.set_volume(0.4)
powerup_sound = mixer.Sound(os.path.join("sounds", "powerup.wav"))
powerup_sound.set_volume(0.3)
background_music = mixer.Sound(os.path.join("sounds", "background.wav"))
background_music.set_volume(0.2)
background_music.play(-1)  # -1 pour jouer en boucle

# Classe du joueur
class Player:
    def __init__(self):
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, NEON_BLUE, [(25, 0), (0, 50), (50, 50)])
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5
        self.health = 100
        self.level = 1
        self.score = 0
        self.shield_active = False
        self.weapon_level = 1

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)
        if self.shield_active:
            pygame.draw.circle(screen, NEON_GREEN, self.rect.center, 30, 2)

# Classe des projectiles
class Bullet:
    def __init__(self, x, y, weapon_level):
        self.speed = 7
        self.weapon_level = weapon_level
        if weapon_level == 1:
            self.image = pygame.Surface((4, 15), pygame.SRCALPHA)
            pygame.draw.rect(self.image, NEON_BLUE, (0, 0, 4, 15))
        elif weapon_level == 2:
            self.image = pygame.Surface((6, 20), pygame.SRCALPHA)
            pygame.draw.rect(self.image, NEON_PINK, (0, 0, 6, 20))
        else:
            self.image = pygame.Surface((8, 25), pygame.SRCALPHA)
            pygame.draw.rect(self.image, NEON_GREEN, (0, 0, 8, 25))
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.y -= self.speed
        return self.rect.bottom < 0

    def draw(self):
        screen.blit(self.image, self.rect)

# Classe des ennemis
class Enemy:
    def __init__(self, level):
        self.level = level
        size = 30 + (level * 5)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        pygame.draw.rect(self.image, color, (0, 0, size, size))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - size)
        self.rect.y = random.randint(-100, -50)
        self.speed = 2 + (level * 0.5)
        self.health = level * 10

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > HEIGHT

    def draw(self):
        screen.blit(self.image, self.rect)

# Classe des bonus
class PowerUp:
    def __init__(self):
        self.types = ['health', 'speed', 'weapon', 'shield']
        self.type = random.choice(self.types)
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        
        if self.type == 'health':
            color = (255, 0, 0)
        elif self.type == 'speed':
            color = NEON_BLUE
        elif self.type == 'weapon':
            color = NEON_PINK
        else:  # shield
            color = NEON_GREEN
            
        pygame.draw.circle(self.image, color, (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - 20)
        self.rect.y = -20
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > HEIGHT

    def draw(self):
        screen.blit(self.image, self.rect)

# Classe du jeu
class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.powerups = []
        self.game_over = False
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

    def spawn_enemy(self):
        if len(self.enemies) < 5 + self.player.level:
            self.enemies.append(Enemy(self.player.level))

    def spawn_powerup(self):
        if random.random() < 0.01:
            self.powerups.append(PowerUp())

    def handle_collisions(self):
        # Collisions bullets-enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= (10 * bullet.weapon_level)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        explosion_sound.play()
                        self.player.score += 10 * self.player.level
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

        # Collisions player-enemies
        for enemy in self.enemies[:]:
            if self.player.rect.colliderect(enemy.rect):
                if not self.player.shield_active:
                    self.player.health -= 20
                self.enemies.remove(enemy)
                if self.player.health <= 0:
                    self.game_over = True

        # Collisions player-powerups
        for powerup in self.powerups[:]:
            if self.player.rect.colliderect(powerup.rect):
                if powerup.type == 'health':
                    self.player.health = min(100, self.player.health + 20)
                    powerup_sound.play()
                elif powerup.type == 'speed':
                    self.player.speed = min(10, self.player.speed + 1)
                    powerup_sound.play()
                elif powerup.type == 'weapon':
                    self.player.weapon_level = min(3, self.player.weapon_level + 1)
                    powerup_sound.play()
                else:  # shield
                    self.player.shield_active = True
                    powerup_sound.play()
                self.powerups.remove(powerup)

    def draw_hud(self):
        health_text = self.font.render(f"Health: {self.player.health}", True, NEON_BLUE)
        score_text = self.font.render(f"Score: {self.player.score}", True, NEON_PINK)
        level_text = self.font.render(f"Level: {self.player.level}", True, NEON_GREEN)
        
        screen.blit(health_text, (10, 10))
        screen.blit(score_text, (10, 40))
        screen.blit(level_text, (10, 70))

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.bullets.append(Bullet(self.player.rect.centerx, self.player.rect.top, self.player.weapon_level))
                        shoot_sound.play()

            if not self.game_over:
                # Update
                self.player.move()
                
                # Update bullets
                for bullet in self.bullets[:]:
                    if bullet.update():
                        self.bullets.remove(bullet)

                # Update enemies
                for enemy in self.enemies[:]:
                    if enemy.update():
                        self.enemies.remove(enemy)

                # Update powerups
                for powerup in self.powerups[:]:
                    if powerup.update():
                        self.powerups.remove(powerup)

                # Spawn enemies and powerups
                self.spawn_enemy()
                self.spawn_powerup()

                # Handle collisions
                self.handle_collisions()

                # Level up system
                if self.player.score >= self.player.level * 100:
                    self.player.level += 1

                # Draw
                screen.fill((0, 0, 20))  # Dark blue background
                
                for bullet in self.bullets:
                    bullet.draw()
                for enemy in self.enemies:
                    enemy.draw()
                for powerup in self.powerups:
                    powerup.draw()
                    
                self.player.draw()
                self.draw_hud()

            else:
                game_over_text = self.font.render("GAME OVER", True, NEON_PINK)
                screen.blit(game_over_text, (WIDTH//2 - 100, HEIGHT//2))
                final_score_text = self.font.render(f"Final Score: {self.player.score}", True, NEON_BLUE)
                screen.blit(final_score_text, (WIDTH//2 - 100, HEIGHT//2 + 50))

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
