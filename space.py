import pygame, sys, time
from pygame.locals import *
from pygame.sprite import Sprite
import random

colorPals = {"yellows": [(225,220,13), (240,235,0), (255,249,0), (242,238,85), (249,246,92)],
             "greens": [(8,108,2), (71,106,55), (23,179,38), (68,132,90), (16,168,46)],
             "reds": [(255, 160, 122), (255, 99, 71), (205, 92, 92), (139, 0, 0), (255, 0, 0)],
             "blues":[(1,31,75), (3,57,108), (0,91,150), (100,151,177), (179,205,224)],
             "violets":[(148, 0, 211), (238, 130, 238), (255, 0, 255), (255, 20, 147), (220, 20, 60)],
             "white": [(0, 0, 0)]}

WINDOWWIDTH = 1000
WINDOWHEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255,255,255)
RED = (255,0,0)
YELLOW = (200,200,10)

FIRE0 = pygame.image.load('images/fire-xs-0.png')
ALIEN0 = pygame.image.load('images/spaceship0.png')
ALIEN1 = pygame.image.load('images/spaceship1.png')

SPLASH = pygame.image.load('images/blood-xs.png')
SPLASH0 = pygame.transform.scale(SPLASH, (100, 100))
CRACK = pygame.image.load('images/crack.png')
CRACK0 = pygame.transform.scale(CRACK, (100, 100))


class SpaceWars:

    def __init__ (self, window_title="SpaceWars", fps=60, init_lifes=3, enemies=3):
        super().__init__()

        self.score = 0
        self.init_lifes = init_lifes
        self.lifes = init_lifes

        self.start_time = time.time ()
        self.anim_run = True
        self.game_over = False
        self.fps = fps # default animation speed

        self.num_bg_stars = 100
        self.num_flystars = 10

        self.num_enemies = enemies

        self.has_been_hit = False
        self.hit_time = 0
        self.screen_shake = False

        # Set up pygame.
        self.input_mode = 'joy'
        pygame.init ()
        pygame.joystick.init()
        try:
            self.joystick = pygame.joystick.Joystick(0)
        except pygame.error:
            print("No gamepad present, please use keyboard!")
            self.input_mode = 'key'

        # Set up the window.
        self.window = pygame.display.set_mode ((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
        pygame.display.set_caption (window_title)

        self.clock = pygame.time.Clock ()

        # change mouse pointer
        #pygame.mouse.set_cursor (*pygame.cursors.diamond)
        pygame.mouse.set_visible(False)

        self.init_time = time.time()

        self.init_objects()
        self.runLoop()

    def init_objects(self):
        self.enemy_counter = 0
        self.init_time = time.time()
        self.anim_run = True
        self.game_over = False
        self.lifes = self.init_lifes
        self.score = 0

        # Init Objects

        self.ship = pygame.sprite.Group()
        self.myship = Ship()
        self.ship.add(self.myship)

        self.rockets = pygame.sprite.Group()
        
        self.background_stars = pygame.sprite.Group()
        for i in range(self.num_bg_stars):
            self.background_stars.add(BackgroundStar(random.randint(0, WINDOWWIDTH), random.randint(0, WINDOWHEIGHT)))

        self.flying_bg_stars = pygame.sprite.Group()
        for i in range(self.num_flystars):
            self.flying_bg_stars.add(FlyingBackgroundStar())
            
        self.enemy_objects = pygame.sprite.Group()
        for i in range(self.num_enemies):
            self.enemy_objects.add(EnemyObject())

        self.explosions = pygame.sprite.Group()

        self.overlays = pygame.sprite.Group()


    def runLoop(self):

        # Run the game/animation loop.
        while True:

            # Game Over screen and event handling
            if self.game_over:
                time.sleep(2)
                self.game_over_screen()
                while self.game_over:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()
                            if event.key == pygame.K_y:
                                self.init_objects()
                                break
                            if event.key == pygame.K_n:
                                pygame.quit()
                                sys.exit()

            # HANDLE GAMEPLAY EVENTS
            for event in pygame.event.get ():
                #print(event)
                if event.type == QUIT:
                    pygame.quit ()
                    sys.exit ()

                # KEYBOARD CONTROL
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit ()
                        sys.exit ()
                    if event.key == pygame.K_p: # pause animation
                        if self.anim_run == False:
                            self.anim_run = True
                        else:
                            self.anim_run = False
                    if event.key == pygame.K_r:  # reload animation
                        self.init_objects()

                    if event.key == pygame.K_KP_PLUS: # increase anim speed
                        if self.fps < 60:
                            self.fps += 1
                    if event.key == pygame.K_KP_MINUS: # decrease anim speed
                        self.fps -= 1

                # JOYPAD CONTROL
                if self.input_mode == 'joy':
                    if event.type == pygame.JOYAXISMOTION:
                        #print(event)
                        x_val = int(self.joystick.get_axis(0)*10)/10
                        y_val = int(self.joystick.get_axis(1)*10)/10

                        if abs(x_val) > 0:
                            self.myship.x_speed = x_val * 5
                            self.myship.is_horizontal_breaking = False
                            for star in self.background_stars:
                                star.x_speed = x_val * 3
                        else:
                            self.myship.is_horizontal_breaking = True
                            for star in self.background_stars:
                                star.x_speed = 0

                        if abs(y_val) > 0:
                            self.myship.y_speed = y_val * 5
                            self.myship.is_vertical_breaking = False
                            # modify background stars speed
                            for star in self.background_stars:
                                star.y_speed = y_val * 3
                        else:
                            self.myship.is_vertical_breaking = True
                            for star in self.background_stars:
                                star.y_speed = 0

                    # fire button
                    if event.type == pygame.JOYBUTTONDOWN:
                        self.mouse_down = True
                    if self.mouse_down:
                        if event.type == pygame.JOYBUTTONUP:
                            self.rockets.add(
                                Rocket(self.myship.rect.x, self.myship.rect.y + 75,
                                       self.rocket_size))
                            self.rockets.add(
                                Rocket(self.myship.rect.x + WINDOWWIDTH/2, self.myship.rect.y + 75,
                                       self.rocket_size))
                            self.rocket_size = 1
                            self.mouse_down = False

                # KEYBOARD INPUT
                elif self.input_mode == 'key':

                    if event.type == pygame.KEYDOWN:
                        # fire button
                        if event.key == pygame.K_SPACE:
                            self.rockets.add(
                                Rocket(self.myship.rect.x,
                                       self.myship.rect.y + WINDOWHEIGHT/2
                                       ))
                            self.rockets.add(
                                Rocket(self.myship.rect.x + WINDOWWIDTH / 2, self.myship.rect.y + WINDOWHEIGHT/2
                                       ))
                            self.mouse_down = True

                        # fly control
                        if event.key == pygame.K_RIGHT:
                            x_val = -1
                            for star in self.background_stars:
                                star.x_speed = x_val * 3

                            for star in self.enemy_objects:
                                star.x_speed = x_val * 3

                            self.myship.is_horizontal_breaking = False
                        elif event.key == pygame.K_LEFT:
                            x_val = 1
                            for star in self.background_stars:
                                star.x_speed = x_val * 3
                            for star in self.enemy_objects:
                                star.x_speed = x_val * 3

                            self.myship.is_horizontal_breaking = False

                        if event.key == pygame.K_UP:
                            y_val = -1
                            for star in self.background_stars:
                                star.y_speed = y_val * 3
                            for star in self.enemy_objects:
                                star.y_speed = y_val * 3
                            self.myship.is_vertical_breaking = False
                        elif event.key == pygame.K_DOWN:
                            y_val = 1
                            for star in self.background_stars:
                                star.y_speed = y_val * 3
                            for star in self.enemy_objects:
                                star.y_speed = y_val * 3
                            self.myship.is_vertical_breaking = False


                    if event.type == pygame.KEYUP:

                        # fire button
                        if event.key == pygame.K_SPACE and self.mouse_down:
                            pass
                        # fly control
                        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                            self.myship.is_horizontal_breaking = True
                        if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            self.myship.is_vertical_breaking = True

            # run / pause animation
            if self.anim_run:

                if self.lifes <= 0:
                    self.game_over = True
                    self.anim_run = False
                    print("Game Over!")

                # UPDATE objects
                self.background_stars.update(self.myship.is_vertical_breaking, self.myship.is_horizontal_breaking)
                self.flying_bg_stars.update()
                self.enemy_objects.update(self.myship.rect, self.window)
                self.rockets.update()
                self.explosions.update()
                self.overlays.update()

                # COLLISION DETECTION
                for enemy in self.enemy_objects:
                    for rocket in self.rockets:
                        if enemy.rect.colliderect(rocket.rect):
                            for i in range(int(enemy.size/4)):
                                explosion = Explosion(enemy.rect.x, enemy.rect.y, enemy.color)
                                self.explosions.add(explosion)
                            if enemy.distance <= 100:
                                splash = Splash(enemy.rect.x, enemy.rect.y, enemy.size)
                                self.overlays.add(splash)
                            self.enemy_objects.remove(enemy)
                            self.enemy_objects.add(EnemyObject())
                            self.score += 100
                            rocket.remove(self.rockets)

                for rocket in self.rockets:
                    if rocket.life < 1 or rocket.rect.y < WINDOWHEIGHT/2:
                        self.rockets.remove(rocket)

                for enemy in self.enemy_objects:
                    if enemy.distance <= 0:
                        if enemy.rect.colliderect(self.myship.rect) and not self.has_been_hit:
                            self.has_been_hit = True
                            self.hit_time = time.time()
                            self.lifes -= 1
                            self.enemy_objects.remove(enemy)
                            self.enemy_objects.add(EnemyObject())
                            crack = Crack(enemy.rect.x, enemy.rect.y)
                            self.overlays.add(crack)
                        else:
                            enemy.set_fly_by_mode()
                    if enemy.distance < 100:
                        if enemy.rect.colliderect(self.myship.rect):
                            enemy.image = pygame.transform.scale(ALIEN1, (enemy.rect.w, enemy.rect.h))
                    if enemy.distance < -50:
                        self.enemy_objects.remove(enemy)
                        self.enemy_objects.add(EnemyObject())

                for star in self.flying_bg_stars:
                    if star.distance <= 0:
                        self.flying_bg_stars.remove(star)
                        self.flying_bg_stars.add(FlyingBackgroundStar())

                for explosion in self.explosions:
                    if explosion.life < 1:
                        self.explosions.remove(explosion)

                for item in self.overlays:
                    if item.life <= 0:
                        self.overlays.remove(item)

                # DRAW OBJECTS
                self.window.fill (BLACK)
                # Draw objects
                self.background_stars.draw(self.window)
                self.flying_bg_stars.draw(self.window)
                self.enemy_objects.draw(self.window)
                self.explosions.draw(self.window)
                self.rockets.draw(self.window)
                self.myship.draw(self.window)
                self.overlays.draw(self.window)

                self.draw_infos()

                # draw red frame and shake screen when ship has been hit
                if time.time() > self.hit_time + 1:
                    self.has_been_hit = False
                if self.has_been_hit:
                    self.draw_has_been_hit_screen ()

                # Draw the window onto the screen.
                pygame.display.update ()

                self.clock.tick (self.fps)

        self.game_over_screen()
        time.sleep(3)


    def draw_has_been_hit_screen(self):
        # draw red frame
        pygame.draw.lines(self.window, RED, True,
                          [(0, 0), (WINDOWWIDTH, 0), (WINDOWWIDTH, WINDOWHEIGHT), (0, WINDOWHEIGHT)], 5)
        # shake screen when hit by an asteroid

        if self.screen_shake:
            delta = 10
            self.screen_shake = False
        else:
            delta = -10
            self.screen_shake = True

        for star in self.background_stars:
            star.rect.x += delta
        for star in self.flying_bg_stars:
            star.rect.x += delta
        for star in self.enemy_objects:
            star.rect.x += delta
        for star in self.explosions:
            star.rect.x += delta
        #self.myship.rect.x += delta

        pygame.display.update()

    def draw_infos(self):
        font = pygame.font.SysFont("Arial", 18)

        text = "Score: " + str(self.score)
        renderText = font.render(text, True, WHITE)
        self.window.blit(renderText, (30, WINDOWHEIGHT - 60))

        text = "Lifes: " + str(self.lifes)
        renderText = font.render(text, True, WHITE)
        self.window.blit(renderText, (30, WINDOWHEIGHT - 30))

        text = "fps: " + str(int(self.clock.get_fps())) + " (" + str(self.fps) + ")"
        renderText = font.render(text, True, WHITE)
        self.window.blit(renderText, (WINDOWWIDTH - 100, WINDOWHEIGHT - 30))

    def game_over_screen (self):
        # show high score
        try:
            with open("highscore.txt", "r") as hs_file:
                hs = int(hs_file.read())
        except Exception as e:
            hs = 0

        with open("highscore.txt", "w") as hs_file:
            if self.score > hs:
                new_hs = self.score
                print("New High Score!")
            else:
                new_hs = hs
            hs_file.write(str(new_hs))

        self.window.fill (BLACK)

        font = pygame.font.SysFont ("Arial", 36)
        text = "GAME OVER"
        renderText = font.render (text, True, WHITE)
        self.window.blit (renderText, (WINDOWWIDTH / 3, WINDOWHEIGHT / 2 - 100))

        if self.score > hs:
            text = "NEW HIGH SCORE!!!"
            renderText = font.render(text, True, WHITE)
            self.window.blit(renderText, (WINDOWWIDTH / 3, WINDOWHEIGHT / 2 - 50))

        font = pygame.font.SysFont ("Arial", 18)
        text = "Your score: " + str (self.score)
        renderText = font.render (text, True, WHITE)
        self.window.blit (renderText, (WINDOWWIDTH / 3, WINDOWHEIGHT / 2 + 50))

        font = pygame.font.SysFont ("Arial", 18)
        text = "Play again? Yes (Y) / No (N)"
        renderText = font.render (text, True, WHITE)
        self.window.blit (renderText, (WINDOWWIDTH / 3, WINDOWHEIGHT / 2 + 100))

        pygame.draw.lines (self.window, RED, True,
                           [(0, 0), (WINDOWWIDTH, 0), (WINDOWWIDTH, WINDOWHEIGHT), (0, WINDOWHEIGHT)], 5)

        pygame.display.update ()


class BackgroundStar(Sprite):
    def __init__ (self, x_pos, y_pos):
        super(BackgroundStar, self).__init__()
        self.base_speed = 0
        self.x_speed = self.base_speed
        self.y_speed = self.base_speed
        self.size = random.randint(1,2)
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(WHITE)
        self.rect = pygame.Rect(x_pos, y_pos, self.size, self.size)

    def update(self, is_vertical_breaking, is_horizontal_breaking):
        if is_vertical_breaking:
            if self.y_speed < 0:
                self.y_speed += 0.1
            elif self.y_speed > 0:
                self.y_speed -= 0.1
        if is_horizontal_breaking:
            if self.x_speed < 0:
                self.x_speed += 0.1
            elif self.x_speed > 0:
                self.x_speed -= 0.1

        self.rect.y += self.y_speed
        self.rect.x += self.x_speed

        # screen overflow
        if self.rect.y > WINDOWHEIGHT-1 or self.rect.y <= 0 or self.rect.x > WINDOWWIDTH-1 or self.rect.x < 0:
            self.rect.y = random.randint(0, WINDOWHEIGHT)
            self.rect.x = random.randint(0, WINDOWWIDTH)


class FlyingBackgroundStar(Sprite):
    def __init__ (self):
        super(FlyingBackgroundStar, self).__init__()

        self.size = random.randint(1,5)
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(WHITE)
        self.rect = pygame.Rect(int(random.randint(int(WINDOWWIDTH/3), int(WINDOWWIDTH/3*2))), int(random.randint(int(WINDOWHEIGHT/3), int(WINDOWHEIGHT/3*2))), self.size, self.size)
        self.distance = random.randint(50,100)

        if self.rect.x > WINDOWWIDTH / 2:
            self.x_speed = random.randint(2,10)
        else:
            self.x_speed = -random.randint(2,10)
        if self.rect.y > WINDOWHEIGHT / 2:
            self.y_speed = random.randint(2,10)
        else:
            self.y_speed = -random.randint(2,10)

    def update(self):
        self.distance -= 1
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed


class Ship(Sprite):
    def __init__ (self):
        super(Ship, self).__init__()
        self.rect = pygame.Rect(int(WINDOWWIDTH / 4), int(WINDOWHEIGHT/4), WINDOWWIDTH/2, WINDOWHEIGHT/2)
        self.outer_rect = pygame.Rect(0, 0, WINDOWWIDTH, WINDOWHEIGHT)
        self.is_vertical_breaking = True
        self.is_horizontal_breaking = True


    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.outer_rect, width=2)

        # INNER
        pygame.draw.rect(screen, WHITE, self.rect, width=2)

        # FRAME
        pygame.draw.line(screen, WHITE, (0, 0),
                         (int(WINDOWWIDTH / 4), int(WINDOWHEIGHT / 4)), width=2)
        pygame.draw.line(screen, WHITE, (0, WINDOWHEIGHT - 1),
                         (int(WINDOWWIDTH / 4), int(WINDOWHEIGHT / 4 * 3)), width=2)
        pygame.draw.line(screen, WHITE, (WINDOWWIDTH, 0),
                         (int(WINDOWWIDTH / 4 * 3), int(WINDOWHEIGHT / 4)), width=2)
        pygame.draw.line(screen, WHITE, (WINDOWWIDTH, WINDOWHEIGHT - 1),
                         (int(WINDOWWIDTH / 4 * 3), int(WINDOWHEIGHT / 4 * 3)), width=2)


class Rocket(Sprite):
    def __init__ (self, x_pos, y_pos):
        super(Rocket, self).__init__()
        self.colors = colorPals["blues"]
        self.y_speed = 10
        if x_pos > WINDOWHEIGHT / 2:
            self.x_speed = 5
        else:
            self.x_speed = -5
        self.life = 40
        self.rect = pygame.Rect(x_pos, y_pos+200, self.life, self.life)
        self.image = pygame.Surface([self.life, self.life])
        self.image.fill(self.colors[int(self.life/10)])

    def update(self):
        self.rect.y -= self.y_speed
        self.rect.x -= self.x_speed

        # scale rockets as they fly away
        if self.life > 2:
            self.life -= 1
        self.image = pygame.transform.scale(self.image, (self.life, self.life))
        self.rect.w, self.rect.h = self.life, self.life

        self.image.fill(self.colors[4-int(self.life/10)])


class EnemyObject(Sprite):
    def __init__ (self):
        super(EnemyObject, self).__init__()
        self.color = (0,0,0)

        self.size = random.randint(10,30)

        self.alien_img_0 = pygame.transform.scale(ALIEN0, (self.size, self.size))
        self.alien_img_1 = pygame.transform.scale(ALIEN1, (self.size, self.size))

        self.image = self.alien_img_0

        #self.image = pygame.Surface([self.size, self.size])
        self.rect = pygame.Rect(random.randint(0, WINDOWWIDTH), random.randint(0, WINDOWHEIGHT), self.size, self.size)

        self.distance = 250 #random.randint(200, 400)
        self.max_size = 150
        self.step = 1

        #self.explosion_count = 100

        # set initial speeds
        if self.rect.x > WINDOWWIDTH / 2:
            self.x_speed = -1
        else:
            self.x_speed = 1
        if self.rect.y > WINDOWHEIGHT / 2:
            self.y_speed = -1
        else:
            self.y_speed = 1

    def update(self, ship_rect, screen):
        self.distance -= 1

        # update position according to x- and y-speed
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

        # increase object size amid distance reduction
        if self.rect.w < self.max_size:
            self.rect.w += self.step
            self.rect.h += self.step
            self.size += self.step

            self.image = pygame.transform.scale(ALIEN0, (self.rect.w, self.rect.h))

        # resize rect as object nears
        #self.image = pygame.Surface([self.rect.w, self.rect.h])

        # set color according to distance
        #self.color = (255-abs(self.distance),10,10)
        #self.image.fill(self.color)


    def set_fly_by_mode(self):
        if self.rect.x > WINDOWWIDTH / 2:
            self.x_speed = 10
        else:
            self.x_speed = -10
        if self.rect.y > WINDOWHEIGHT / 2:
            self.y_speed = 10
        else:
            self.y_speed = -10


class Explosion(Sprite):
    def __init__ (self, init_x_pos, init_y_pos, color):
        super(Explosion, self).__init__()
        self.color = color
        self.size = random.randint(10, 20)
        self.y_speed = random.randint(-20, 20)
        self.x_speed = random.randint(-20, 20)
        self.x_pos = init_x_pos
        self.y_pos = init_y_pos
        self.life = random.randint(10,30) #determines when a explosion is gonna fade out

        self.image = FIRE0
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

        #self.image = pygame.Surface([self.size, self.size])
        self.rect = pygame.Rect(init_x_pos, init_y_pos, self.size, self.size)

        #self.image.fill(self.color)

    def update(self):
        self.rect.x += self.y_speed
        self.rect.y += self.x_speed
        self.life -= 1

        # decelerate speeds

        self.x_speed *= 0.95
        self.y_speed *= 0.95


class Splash(Sprite):
    def __init__ (self, x_pos, y_pos, size):
        super(Splash, self).__init__()
        self.life = random.randint(30, 60)  # determines when blood
        self.image = pygame.transform.rotate(SPLASH0, random.randint(0,360))
        self.size = size
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.rect = pygame.Rect(x_pos, y_pos, self.size, self.size)

    def update(self):
        self.life -= 1


class Crack(Sprite):
    def __init__(self, x_pos, y_pos):
        super(Crack, self).__init__()
        self.image = pygame.transform.rotate(CRACK0, random.randint(0, 360))
        self.size = 100
        self.rect = pygame.Rect(x_pos, y_pos, self.size, self.size)
        self.life = 100


if __name__ == "__main__":
    # init fireworks class
    space = SpaceWars(fps=60, init_lifes=5, enemies=0)

