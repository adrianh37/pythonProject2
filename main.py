import copy
import random
import pygame

pygame.init()
# game variables
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
one_deck = 4 * cards
decks = 4
WIDTH = 600
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Pygame Blackjack!')
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 20)
smaller_font = pygame.font.Font('freesansbold.ttf', 36)
active = False
# win, loss, draw/push
records = [0, 0, 0]
player_score = 0
dealer_score = 0
initial_deal = False
my_hand = []
dealer_hand = []
outcome = 0
reveal_dealer = False
hand_active = False
outcome = 0
add_score = False
results = ['', 'PLAYER BUSTED o_O', 'Player WINS! :)', 'DEALER WINS :(', 'TIE GAME...']
balance = 1000  # Player's starting balance
bet = 0  # Current bet amount

background_image = pygame.image.load('assets/photo2pixel_download.png')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))


# deal cards by selecting randomly from deck, and make function for one card at a time
def deal_cards(current_hand, current_deck):
    card = random.randint(0, len(current_deck) - 1)
    current_hand.append(current_deck[card])
    current_deck.pop(card)
    return current_hand, current_deck


# draw scores for player and dealer on screen
def draw_scores(player, dealer):
    screen.blit(font.render(f'Score[{player}]', True, 'white'), (350, 400))
    if reveal_dealer:
        screen.blit(font.render(f'Score[{dealer}]', True, 'white'), (350, 100))


def draw_cards(player, dealer, reveal):
    card_width = 60
    card_height = 110
    for i in range(len(player)):
        pygame.draw.rect(screen, 'white', [50 + (card_width + 10) * i, 460 + (5 * i), card_width, card_height], 0, 5)
        screen.blit(font.render(player[i], True, 'black'), (55 + (card_width + 10) * i, 465 + (5 * i)))
        screen.blit(font.render(player[i], True, 'black'), (55 + (card_width + 10) * i, 545 + (5 * i)))
        pygame.draw.rect(screen, 'red', [50 + (card_width + 10) * i, 460 + (5 * i), card_width, card_height], 5, 5)

    # if player hasn't finished turn, dealer will hide one card
    for i in range(len(dealer)):
        pygame.draw.rect(screen, 'white', [50 + (card_width + 10) * i, 160 + (5 * i), card_width, card_height], 0, 5)
        if i != 0 or reveal:
            screen.blit(font.render(dealer[i], True, 'black'), (55 + (card_width + 10) * i, 165 + (5 * i)))
            screen.blit(font.render(dealer[i], True, 'black'), (55 + (card_width + 10) * i, 245 + (5 * i)))
        else:
            screen.blit(font.render('???', True, 'black'), (55 + (card_width + 10) * i, 165 + (5 * i)))
            screen.blit(font.render('???', True, 'black'), (55 + (card_width + 10) * i, 245 + (5 * i)))
        pygame.draw.rect(screen, 'blue', [50 + (card_width + 10) * i, 160 + (5 * i), card_width, card_height], 5, 5)


# pass in player or dealer hand and get best score possible
def calculate_score(hand):
    # calculate hand score fresh every time, check how many aces we have
    hand_score = 0
    aces_count = hand.count('A')
    for i in range(len(hand)):
        # for 2,3,4,5,6,7,8,9 - just add the number to total
        for j in range(8):
            if hand[i] == cards[j]:
                hand_score += int(hand[i])
        # for 10 and face cards, add 10
        if hand[i] in ['10', 'J', 'Q', 'K']:
            hand_score += 10
        # for aces start by adding 11, we'll check if we need to reduce afterwards
        elif hand[i] == 'A':
            hand_score += 11
    # determine how many aces need to be 1 instead of 11 to get under 21 if possible
    if hand_score > 21 and aces_count > 0:
        for i in range(aces_count):
            if hand_score > 21:
                hand_score -= 10
    return hand_score


# draw game conditions and buttons
def draw_game(act, record, result, bal, current_bet):
    button_list = []
    # initially on startup (not active) only option is to deal new hand
    if not act:
        deal = pygame.draw.rect(screen, 'white', [150, 20, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 20, 300, 100], 3, 5)
        deal_text = font.render('DEAL HAND', True, 'black')
        screen.blit(deal_text, (165, 50))
        button_list.append(deal)

        # Bet buttons
        bet_10 = pygame.draw.rect(screen, 'white', [150, 140, 80, 50], 0, 5)
        screen.blit(font.render('Bet 10', True, 'black'), (160, 155))
        button_list.append(bet_10)

        bet_50 = pygame.draw.rect(screen, 'white', [240, 140, 80, 50], 0, 5)
        screen.blit(font.render('Bet 50', True, 'black'), (250, 155))
        button_list.append(bet_50)

        bet_100 = pygame.draw.rect(screen, 'white', [330, 140, 80, 50], 0, 5)
        screen.blit(font.render('Bet 100', True, 'black'), (340, 155))
        button_list.append(bet_100)
    # once game started, show hit and stand buttons and win/loss records
    else:
        hit = pygame.draw.rect(screen, 'white', [0, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [0, 700, 300, 100], 3, 5)
        hit_text = font.render('HIT ME', True, 'black')
        screen.blit(hit_text, (55, 735))
        button_list.append(hit)

        stand = pygame.draw.rect(screen, 'white', [300, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [300, 700, 300, 100], 3, 5)
        stand_text = font.render('STAND', True, 'black')
        screen.blit(stand_text, (200, 500))
        button_list.append(stand)

        score_text = smaller_font.render(f'Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white')
        screen.blit(score_text, (15, 840))

    if result != 0:
        screen.blit(font.render(results[result], True, 'white'), (15, 25))
        deal = pygame.draw.rect(screen, 'white', [150, 220, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 220, 300, 100], 3, 5)
        pygame.draw.rect(screen, 'black', [153, 223, 294, 94], 3, 5)
        deal_text = font.render('NEW HAND', True, 'black')
        screen.blit(deal_text, (165, 250))
        button_list.append(deal)

    # Display balance and current bet
    screen.blit(font.render(f'Balance: ${bal}', True, 'white'), (15, 25))
    screen.blit(font.render(f'Current Bet: ${current_bet}', True, 'white'), (15, 60))

    return button_list


# check endgame conditions function
def check_endgame(hand_act, deal_score, play_score, result, totals, add, bal, current_bet):
    # check end game scenarios if player has stood, busted or blackjacked
    # result 1- player bust, 2-win, 3-loss, 4-push
    if not hand_act and deal_score >= 17:
        if play_score > 21:
            result = 1
        elif deal_score < play_score <= 21 or deal_score > 21:
            result = 2
        elif play_score < deal_score <= 21:
            result = 3
        else:
            result = 4
        if add:
            if result == 1 or result == 3:
                totals[1] += 1
                bal -= current_bet
            elif result == 2:
                totals[0] += 1
                bal += current_bet
            else:
                totals[2] += 1
            add = False
    return result, totals, add, bal


# main game loop
run = True
while run:
    # run game at our framerate and fill screen with bg color
    timer.tick(fps)
    screen.blit(background_image, (0, 0))

    # initial deal to player and dealer
    if initial_deal:
        for i in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        initial_deal = False

    # once game is activated and dealt, calculate scores and display cards
    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, reveal_dealer)
        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)
            if dealer_score < 17:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        draw_scores(player_score, dealer_score)

    buttons = draw_game(active, records, outcome, balance, bet)

    # event handling, if quit pressed, then exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            if not active:
                if buttons[0].collidepoint(event.pos):
                    if bet > 0:  # Ensure a bet has been placed before starting
                        active = True
                        initial_deal = True
                        game_deck = copy.deepcopy(decks * one_deck)
                        my_hand = []
                        dealer_hand = []
                        outcome = 0
                        hand_active = True
                        reveal_dealer = False
                        outcome = 0
                        add_score = True
                # Handle bet buttons
                elif buttons[1].collidepoint(event.pos):
                    if balance >= 10:
                        bet += 10
                        balance -= 10
                elif buttons[2].collidepoint(event.pos):
                    if balance >= 50:
                        bet += 50
                        balance -= 50
                elif buttons[3].collidepoint(event.pos):
                    if balance >= 100:
                        bet += 100
                        balance -= 100
            else:
                # if player can hit, allow them to draw a card
                if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                # allow player to end turn (stand)
                elif buttons[1].collidepoint(event.pos) and not reveal_dealer:
                    reveal_dealer = True
                    hand_active = False
                elif len(buttons) == 3:
                    if buttons[2].collidepoint(event.pos):
                        active = True
                        initial_deal = True
                        game_deck = copy.deepcopy(decks * one_deck)
                        my_hand = []
                        dealer_hand = []
                        outcome = 0
                        hand_active = True
                        reveal_dealer = False
                        outcome = 0
                        add_score = True
                        dealer_score = 0
                        player_score = 0

    if hand_active and player_score >= 21:
        hand_active = False
        reveal_dealer = True

    outcome, records, add_score, balance = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_score, balance, bet)

    pygame.display.flip()
pygame.quit()
