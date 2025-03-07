import pygame
import sys
import math
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAP_WIDTH = 3200
MAP_HEIGHT = 2400
FPS = 60

PLAYER_SPEED = 5
ENEMY_SPEED = 3
PROJECTILE_SPEED = 5
SHIELD_DURATION = 5 * FPS  # 5 seconds in frames
BOOST_PROJECTILE_SPEED = ENEMY_SPEED * 2  # Twice enemy speed

def get_camera_offset(player):
    offset_x = player.rect.centerx - SCREEN_WIDTH // 2
    offset_y = player.rect.centery - SCREEN_HEIGHT // 2
    offset_x = max(0, min(offset_x, MAP_WIDTH - SCREEN_WIDTH))
    offset_y = max(0, min(offset_y, MAP_HEIGHT - SCREEN_HEIGHT))
    return (offset_x, offset_y)

# Player class with shield and boost functionality
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.health = 300
        self.shield_timer = 0
        self.is_shielded = False
        self.color = (255, 255, 255)  # Default white
        self.has_boost = False  # Tracks if boost is available
        self.dx = 0  # Last movement direction x
        self.dy = 0  # Last movement direction y

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        if dx != 0 or dy != 0:  # Update direction only if moving
            self.dx = dx
            self.dy = dy
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.x > MAP_WIDTH - self.rect.width:
            self.rect.x = MAP_WIDTH - self.rect.width
        if self.rect.y > MAP_HEIGHT - self.rect.height:
            self.rect.y = MAP_HEIGHT - self.rect.height

    def update(self):
        if self.shield_timer > 0:
            self.shield_timer -= 1
            self.is_shielded = True
            self.color = (0, 0, 255)  # Blue when shielded
        else:
            self.is_shielded = False
            self.color = (255, 255, 255)  # Back to white

    def draw(self, screen, camera_offset):
        offset_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        pygame.draw.rect(screen, self.color, offset_rect)

# GreenEnemy class (unchanged)
class GreenEnemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.shoot_delay = random.randint(30, 60)
        self.shoot_timer = self.shoot_delay

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx = (dx / dist) * ENEMY_SPEED
            dy = (dy / dist) * ENEMY_SPEED
            self.rect.x += dx
            self.rect.y += dy
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.x > MAP_WIDTH - self.rect.width:
            self.rect.x = MAP_WIDTH - self.rect.width
        if self.rect.y > MAP_HEIGHT - self.rect.height:
            self.rect.y = MAP_HEIGHT - self.rect.height
        self.shoot_timer -= 1

    def can_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_delay
            return True
        return False

    def draw(self, screen, camera_offset):
        offset_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        pygame.draw.rect(screen, (0, 255, 0), offset_rect)

# RedEnemy class (unchanged)
class RedEnemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.shoot_delay = random.randint(90, 150)
        self.shoot_timer = self.shoot_delay

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx = (dx / dist) * ENEMY_SPEED
            dy = (dy / dist) * ENEMY_SPEED
            self.rect.x += dx
            self.rect.y += dy
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.x > MAP_WIDTH - self.rect.width:
            self.rect.x = MAP_WIDTH - self.rect.width
        if self.rect.y > MAP_HEIGHT - self.rect.height:
            self.rect.y = MAP_HEIGHT - self.rect.height
        self.shoot_timer -= 1

    def can_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_delay
            return True
        return False

    def draw(self, screen, camera_offset):
        offset_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        pygame.draw.rect(screen, (255, 0, 0), offset_rect)

# Projectile class (enemy projectiles, unchanged)
class Projectile:
    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y, 10, 10)
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        self.dx = (dx / dist) * PROJECTILE_SPEED
        self.dy = (dy / dist) * PROJECTILE_SPEED

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen, camera_offset):
        offset_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        pygame.draw.rect(screen, (0, 0, 0), offset_rect)

# BoostProjectile class (player's yellow rectangle)
class BoostProjectile:
    def __init__(self, x, y, dx, dy):
        self.rect = pygame.Rect(x, y, 300, 600)  # Keeping the size from the last update
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.dx = (dx / dist) * BOOST_PROJECTILE_SPEED
            self.dy = (dy / dist) * BOOST_PROJECTILE_SPEED
        else:
            self.dx = BOOST_PROJECTILE_SPEED
            self.dy = 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen, camera_offset):
        offset_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        pygame.draw.rect(screen, (255, 255, 0), offset_rect)

# Building class (unchanged)
class Building:
    def __init__(self, x, y, width, height, health=500):
        self.rect = pygame.Rect(x, y, width, height)
        self.health = health
        self.max_health = health
        self.damage_timer = 0

    def update(self):
        if self.damage_timer > 0:
            self.damage_timer -= 1

    def take_damage(self, amount):
        if self.damage_timer <= 0:
            self.health -= amount
            self.damage_timer = 10
            if self.health < 0:
                self.health = 0

    def draw(self, screen, camera_offset):
        offset_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        health_ratio = self.health / self.max_health
        color_value = int(100 + 155 * health_ratio)
        pygame.draw.rect(screen, (color_value, color_value, color_value), offset_rect)

# Shield class (now blue)
class Shield:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)

    def draw(self, screen, camera_offset, font):
        offset_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        pygame.draw.rect(screen, (0, 0, 255), offset_rect)  # Blue shield
        s_text = font.render("S", True, (255, 255, 255))
        text_rect = s_text.get_rect(center=offset_rect.center)
        screen.blit(s_text, text_rect)

# Boost class (yellow boost)
class Boost:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)

    def draw(self, screen, camera_offset, font):
        offset_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        pygame.draw.rect(screen, (255, 255, 0), offset_rect)  # Yellow boost
        b_text = font.render("B", True, (0, 0, 0))
        text_rect = b_text.get_rect(center=offset_rect.center)
        screen.blit(b_text, text_rect)

# UI functions (unchanged)
def draw_hp_bar(screen, x, y, width, height, current_health, max_health):
    ratio = current_health / max_health
    pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, width * ratio, height))

def draw_enemy_count(screen, enemy_count):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Enemies: {enemy_count}", True, (0, 0, 0))
    screen.blit(text, (SCREEN_WIDTH - 150, 10))

def generate_buildings(num_buildings):
    buildings = []
    attempts = 0
    while len(buildings) < num_buildings and attempts < num_buildings * 10:
        width = random.randint(80, 150)
        height = random.randint(80, 150)
        x = random.randint(0, MAP_WIDTH - width)
        y = random.randint(0, MAP_HEIGHT - height)
        new_rect = pygame.Rect(x, y, width, height)
        overlap = False
        for b in buildings:
            if new_rect.colliderect(b.rect.inflate(20, 20)):
                overlap = True
                break
        if not overlap:
            health = random.choice([100, 150])
            buildings.append(Building(x, y, width, height, health))
        attempts += 1
    return buildings

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Top-Down Rampage - Street Map Style")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    running = True

    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    red_enemies = []
    green_enemies = []
    projectiles = []
    boost_projectiles = []  # Player's yellow projectiles
    shields = []
    boosts = []  # Yellow boost power-ups
    buildings = generate_buildings(20)

    # Initial spawn: 3 red + 2 green
    for i in range(3):
        enemy_x = random.randint(0, MAP_WIDTH - 40)
        enemy_y = random.randint(0, MAP_HEIGHT - 40)
        red_enemies.append(RedEnemy(enemy_x, enemy_y))
    for i in range(2):
        enemy_x = random.randint(0, MAP_WIDTH - 40)
        enemy_y = random.randint(0, MAP_HEIGHT - 40)
        green_enemies.append(GreenEnemy(enemy_x, enemy_y))

    last_spawn_time = pygame.time.get_ticks()
    last_shield_spawn = pygame.time.get_ticks()
    last_boost_spawn = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if player.has_boost:
                    proj = BoostProjectile(player.rect.centerx, player.rect.centery,
                                         player.dx, player.dy)
                    boost_projectiles.append(proj)
                    player.has_boost = False  # Use up the boost

        # Player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += PLAYER_SPEED
        player.move(dx, dy)
        player.update()

        # Update buildings
        for building in buildings:
            building.update()
            if player.rect.colliderect(building.rect):
                building.take_damage(1)
        buildings = [b for b in buildings if b.health > 0]

        # Spawn enemies every 5 seconds
        current_time = pygame.time.get_ticks()
        if current_time - last_spawn_time >= 5000:
            for i in range(3):
                enemy_x = random.randint(0, MAP_WIDTH - 40)
                enemy_y = random.randint(0, MAP_HEIGHT - 40)
                red_enemies.append(RedEnemy(enemy_x, enemy_y))
            for i in range(2):
                enemy_x = random.randint(0, MAP_WIDTH - 40)
                enemy_y = random.randint(0, MAP_HEIGHT - 40)
                green_enemies.append(GreenEnemy(enemy_x, enemy_y))
            last_spawn_time = current_time

        # Spawn shield every 15 seconds
        if current_time - last_shield_spawn >= 15000:
            shield_x = random.randint(0, MAP_WIDTH - 30)
            shield_y = random.randint(0, MAP_HEIGHT - 30)
            shields.append(Shield(shield_x, shield_y))
            last_shield_spawn = current_time

        # Spawn boost every 15 seconds
        if current_time - last_boost_spawn >= 15000:
            boost_x = random.randint(0, MAP_WIDTH - 30)
            boost_y = random.randint(0, MAP_HEIGHT - 30)
            boosts.append(Boost(boost_x, boost_y))
            last_boost_spawn = current_time

        # Update red enemies
        for enemy in red_enemies[:]:
            enemy.update(player)
            if enemy.can_shoot():
                proj = Projectile(enemy.rect.centerx, enemy.rect.centery,
                                player.rect.centerx, player.rect.centery)
                projectiles.append(proj)
            if player.rect.colliderect(enemy.rect):
                red_enemies.remove(enemy)

        # Update green enemies
        for green_enemy in green_enemies[:]:
            green_enemy.update(player)
            if green_enemy.can_shoot():
                proj = Projectile(green_enemy.rect.centerx, green_enemy.rect.centery,
                                player.rect.centerx, player.rect.centery)
                projectiles.append(proj)
            if player.rect.colliderect(green_enemy.rect):
                green_enemies.remove(green_enemy)

        # Update shields
        for shield in shields[:]:
            if player.rect.colliderect(shield.rect):
                shields.remove(shield)
                player.shield_timer = SHIELD_DURATION
                break

        # Update boosts
        for boost in boosts[:]:
            if player.rect.colliderect(boost.rect):
                boosts.remove(boost)
                player.has_boost = True
                break

        # Update enemy projectiles
        for proj in projectiles[:]:
            proj.update()
            if (proj.rect.x < 0 or proj.rect.x > MAP_WIDTH or
                proj.rect.y < 0 or proj.rect.y > MAP_HEIGHT):
                projectiles.remove(proj)
                continue
            if proj.rect.colliderect(player.rect) and not player.is_shielded:
                player.health -= 10
                projectiles.remove(proj)
                if player.health < 0:
                    player.health = 0
                continue
            elif proj.rect.colliderect(player.rect) and player.is_shielded:
                projectiles.remove(proj)
            for building in buildings:
                if proj.rect.colliderect(building.rect):
                    building.take_damage(10)
                    if proj in projectiles:
                        projectiles.remove(proj)
                    break

        # Update boost projectiles
                # Update boost projectiles
               # Update boost projectiles
        for b_proj in boost_projectiles[:]:
            b_proj.update()
            if (b_proj.rect.x < 0 or b_proj.rect.x > MAP_WIDTH or
                b_proj.rect.y < 0 or b_proj.rect.y > MAP_HEIGHT):
                boost_projectiles.remove(b_proj)
                continue
            for building in buildings:
                if b_proj.rect.colliderect(building.rect):
                    building.take_damage(20)  # Damages building
            for enemy in red_enemies[:]:  # Check red enemies
                if b_proj.rect.colliderect(enemy.rect):
                    red_enemies.remove(enemy)  # Kills red enemy
            for green_enemy in green_enemies[:]:  # Check green enemies
                if b_proj.rect.colliderect(green_enemy.rect):
                    green_enemies.remove(green_enemy)  # Kills green enemy

        camera_offset = get_camera_offset(player)

        # Draw everything
        screen.fill((120, 120, 120))
        draw_hp_bar(screen, 10, 10, 200, 20, player.health, 300)
        draw_enemy_count(screen, len(red_enemies) + len(green_enemies))

        for building in buildings:
            building.draw(screen, camera_offset)
        player.draw(screen, camera_offset)
        for enemy in red_enemies:
            enemy.draw(screen, camera_offset)
        for green_enemy in green_enemies:
            green_enemy.draw(screen, camera_offset)
        for shield in shields:
            shield.draw(screen, camera_offset, font)
        for boost in boosts:
            boost.draw(screen, camera_offset, font)
        for proj in projectiles:
            proj.draw(screen, camera_offset)
        for b_proj in boost_projectiles:
            b_proj.draw(screen, camera_offset)

        pygame.display.flip()
        clock.tick(FPS)

        if player.health <= 0:
            running = False

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()