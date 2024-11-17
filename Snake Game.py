import pygame, sys, time, random
import os

# Kich co cua cua so
frame_size_x = 1280
frame_size_y = 720

# Size cua cac bo phan ran va do an
sprite_size = 50

# Khoi tao pygame
pygame.init()
pygame.mixer.init()
# Khoi tao cua so game
pygame.display.set_caption('Sizzle Sizzle')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
pygame.display.set_mode((frame_size_x, frame_size_y), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)

# Tao mau
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

#Tai am thanh
eating_sound = pygame.mixer.Sound('eat.wav')
death_sound = pygame.mixer.Sound('die.wav')
pygame.mixer.music.load('background.mp3')
pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

# Tai anh
def load_image(name, size):
    image = pygame.image.load(name)
    return pygame.transform.scale(image, (size, size))

# Tai cac anh can dung len
snake_head = load_image('snake-head.png', sprite_size)
snake_body = load_image('snake-body.png', sprite_size)
snake_tail = load_image('snake-tail.png', sprite_size)
food_img = load_image('food.png', sprite_size)
background_img = pygame.transform.scale(pygame.image.load('grass-background.png'), (frame_size_x, frame_size_y))
# FPS controller
fps_controller = pygame.time.Clock()

# Difficulty settings
DIFFICULTIES = {
    "Easy": 5,
    "Medium": 7,
    "Hard": 10,
    "Harder": 15,
    "Impossible": 20
}


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont('arial', 32)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, white)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def generate_food_position(snake_segments):
    while True:
        x = random.randrange(0, (frame_size_x - sprite_size), sprite_size)
        y = random.randrange(0, (frame_size_y - sprite_size), sprite_size)
        food_pos = [x, y]

        if food_pos not in snake_segments:
            return food_pos


def init_game():
    initial_snake_segments = [[100, 50], [100 - sprite_size, 50], [100 - (2 * sprite_size), 50]]
    return {
        'snake_pos': [100, 50],
        'snake_segments': initial_snake_segments.copy(),
        'segment_directions': ['RIGHT', 'RIGHT', 'RIGHT'],
        'food_pos': generate_food_position(initial_snake_segments),
        'direction': 'RIGHT',
        'change_to': 'RIGHT',
        'score': 0
    }


def show_menu(text, buttons):
    while True:
        game_window.fill(black)
        game_window.blit(background_img, (0, 0))
        font = pygame.font.SysFont('times new roman', 64)
        text_surface = font.render(text, True, white)
        text_rect = text_surface.get_rect(center=(frame_size_x / 2, frame_size_y / 4))
        game_window.blit(text_surface, text_rect)

        for button in buttons:
            button.draw(game_window)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.is_clicked(event.pos):
                        return button.text
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit()


def difficulty_menu():
    button_width = 200
    button_height = 50
    button_spacing = 20
    total_height = (button_height + button_spacing) * len(DIFFICULTIES)
    start_y = (frame_size_y - total_height) // 1.5

    buttons = []
    for i, difficulty in enumerate(DIFFICULTIES.keys()):
        y = start_y + i * (button_height + button_spacing)
        color = blue if difficulty == "Medium" else green  # Highlight default difficulty
        buttons.append(Button(frame_size_x / 2 - button_width / 2, y, button_width, button_height, difficulty, color))

    return show_menu("SELECT DIFFICULTY", buttons)


def main_menu():
    buttons = [
        Button(frame_size_x / 2 - 100, frame_size_y / 2, 200, 50, "Start Game", green),
        Button(frame_size_x / 2 - 100, frame_size_y / 2 + 70, 200, 50, "Quit", red)
    ]
    return show_menu("SIZZLE SIZZLE", buttons)


def death_menu(score, difficulty):
    death_sound.play()
    pygame.mixer.music.stop()
    buttons = [
        Button(frame_size_x / 2 - 100, frame_size_y / 2, 200, 50, "Play Again", green),
        Button(frame_size_x / 2 - 100, frame_size_y / 2 + 70, 200, 50, "Difficulty", blue),
        Button(frame_size_x / 2 - 100, frame_size_y / 2 + 140, 200, 50, "Quit", red)
    ]
    return show_menu(f"GAME OVER\nScore: {score}\nDifficulty: {difficulty}", buttons)


def show_score(score, difficulty, choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render(f'Score: {score} | Difficulty: {difficulty}', True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x / 2, 15)
    else:
        score_rect.midtop = (frame_size_x / 2, frame_size_y / 1.25)
    game_window.blit(score_surface, score_rect)


def get_rotation_angle(direction):
    angles = {'RIGHT': 0, 'DOWN': 90, 'LEFT': 180, 'UP': -90}
    return angles.get(direction, 0)


def get_segment_direction(prev_pos, curr_pos, next_pos):
    if prev_pos and next_pos:
        dx1 = next_pos[0] - curr_pos[0]
        dy1 = next_pos[1] - curr_pos[1]
        if dx1 > 0: return 'RIGHT'
        if dx1 < 0: return 'LEFT'
        if dy1 > 0: return 'DOWN'
        if dy1 < 0: return 'UP'
    return 'RIGHT'


def game_loop(difficulty_name):
    difficulty = DIFFICULTIES[difficulty_name]
    game_state = init_game()
    pygame.mixer.music.play(-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    game_state['change_to'] = 'UP'
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    game_state['change_to'] = 'DOWN'
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    game_state['change_to'] = 'LEFT'
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    game_state['change_to'] = 'RIGHT'
                if event.key == pygame.K_ESCAPE:
                    return "Quit"

        # Direction logic
        if game_state['change_to'] == 'UP' and game_state['direction'] != 'DOWN':
            game_state['direction'] = 'UP'
        if game_state['change_to'] == 'DOWN' and game_state['direction'] != 'UP':
            game_state['direction'] = 'DOWN'
        if game_state['change_to'] == 'LEFT' and game_state['direction'] != 'RIGHT':
            game_state['direction'] = 'LEFT'
        if game_state['change_to'] == 'RIGHT' and game_state['direction'] != 'LEFT':
            game_state['direction'] = 'RIGHT'

        # Moving the snake
        new_head_pos = list(game_state['snake_pos'])
        if game_state['direction'] == 'UP':
            new_head_pos[1] -= sprite_size
        if game_state['direction'] == 'DOWN':
            new_head_pos[1] += sprite_size
        if game_state['direction'] == 'LEFT':
            new_head_pos[0] -= sprite_size
        if game_state['direction'] == 'RIGHT':
            new_head_pos[0] += sprite_size

        game_state['snake_pos'] = new_head_pos
        game_state['snake_segments'].insert(0, list(new_head_pos))
        game_state['segment_directions'].insert(0, game_state['direction'])

        # Check if snake ate food
        head_rect = pygame.Rect(game_state['snake_pos'][0], game_state['snake_pos'][1], sprite_size, sprite_size)
        food_rect = pygame.Rect(game_state['food_pos'][0], game_state['food_pos'][1], sprite_size, sprite_size)

        if head_rect.colliderect(food_rect):
            eating_sound.play()
            game_state['score'] += 1
            game_state['food_pos'] = generate_food_position(game_state['snake_segments'])
        else:
            game_state['snake_segments'].pop()
            game_state['segment_directions'].pop()

        # Draw everything
        game_window.fill(black)
        # Draw background image
        game_window.blit(background_img, (0, 0))
        # Draw snake
        for i, pos in enumerate(game_state['snake_segments']):
            if i == 0:  # Head
                if snake_head:
                    rotated_head = pygame.transform.rotate(snake_head,
                                                           get_rotation_angle(game_state['segment_directions'][i]))
                    game_window.blit(rotated_head, tuple(pos))
                else:
                    pygame.draw.rect(game_window, white, pygame.Rect(pos[0], pos[1], sprite_size, sprite_size))
            elif i == len(game_state['snake_segments']) - 1:  # Tail
                if snake_tail:
                    rotated_tail = pygame.transform.rotate(snake_tail,
                                                           get_rotation_angle(game_state['segment_directions'][i]))
                    game_window.blit(rotated_tail, tuple(pos))
                else:
                    pygame.draw.rect(game_window, white, pygame.Rect(pos[0], pos[1], sprite_size, sprite_size))
            else:  # Body
                if snake_body:
                    rotated_body = pygame.transform.rotate(snake_body,
                                                           get_rotation_angle(game_state['segment_directions'][i]))
                    game_window.blit(rotated_body, tuple(pos))
                else:
                    pygame.draw.rect(game_window, white, pygame.Rect(pos[0], pos[1], sprite_size, sprite_size))

        # Draw food
        if food_img:
            game_window.blit(food_img, tuple(game_state['food_pos']))
        else:
            pygame.draw.rect(game_window, red,
                             pygame.Rect(game_state['food_pos'][0], game_state['food_pos'][1], sprite_size,
                                         sprite_size))

        # Game Over conditions
        if (game_state['snake_pos'][0] < 0 or game_state['snake_pos'][0] > frame_size_x - sprite_size or
                game_state['snake_pos'][1] < 0 or game_state['snake_pos'][1] > frame_size_y - sprite_size):
            return death_menu(game_state['score'], difficulty_name)

        # Snake collision with itself
        for block in game_state['snake_segments'][1:]:
            if block[0] == game_state['snake_pos'][0] and block[1] == game_state['snake_pos'][1]:
                return death_menu(game_state['score'], difficulty_name)

        show_score(game_state['score'], difficulty_name, 1, white, 'consolas', 20)
        pygame.display.update()
        fps_controller.tick(difficulty)


def main():
    difficulty = "Medium"  # Default difficulty

    while True:
        choice = main_menu()
        if choice == "Quit":
            break

        while choice == "Start Game" or choice == "Play Again" or choice == "Change Difficulty":
            if choice == "Start Game" or choice == "Change Difficulty":
                difficulty = difficulty_menu()

            choice = game_loop(difficulty)
            if choice == "Quit":
                pygame.quit()
                sys.exit()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()