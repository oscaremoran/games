import time

def display_welcome():
    print("Welcome to CYOA! Please pick your adventure: The Dragon's Cave (type 1).")
    choice = input().strip()
    if choice == '1':
        print("Welcome to the Dragon's Cave! You are in the entrance. There is a bush on the left and a rustling bush on the right. There are also two chests behind the rustling bush. You can interact with BUSH, RUSTLINGBUSH, CHEST1, CHEST2.")
    else:
        print("Invalid choice. Exiting.")
        exit()

def save_game(player, rooms):
    chest1_opened = int(rooms[1]['CHEST1']['opened'])
    chest2_opened = int(rooms[1]['CHEST2']['opened'])
    save_code = f"{player['room']}-{player['hp']}-{player['gold']}-{player['gems']}-{chest1_opened}-{chest2_opened}"
    print(f"Save code: {save_code}")

def load_game():
    save_code = input("Enter save code: ").strip()
    try:
        parts = save_code.split('-')
        if len(parts) != 6:
            raise ValueError
        room, hp, gold, gems, chest1_opened, chest2_opened = map(int, parts)
        return room, hp, gold, gems, bool(chest1_opened), bool(chest2_opened)
    except ValueError:
        print("Invalid save code.")
        return None

def combat_with_goblin(player):
    goblin_hp = 7
    player_damage = 5
    goblin_damage = 3
    print("Combat starts! Choose (A)ttack or (F)lee.")
    while True:
        choice = input("Enter A or F: ").strip().upper()
        if choice == 'A':
            goblin_hp -= player_damage
            print(f"You attack the Goblin for {player_damage} damage. Goblin HP: {goblin_hp}")
            if goblin_hp <= 0:
                print("You defeated the Goblin!")
                return True
            player['hp'] -= goblin_damage
            print(f"The Goblin attacks you for {goblin_damage} damage. Your HP: {player['hp']}")
            if player['hp'] <= 0:
                print("You have been defeated.")
                return False
        elif choice == 'F':
            print("You fled.")
            return False
        else:
            print("Invalid choice. Please enter A or F.")

def game_over():
    print("GAME OVER.")
    time.sleep(5)
    exit()

def attack_object(object_name, player, rooms):
    room = rooms[player['room']]
    if object_name not in room:
        print("No such object.")
        return
    obj = room[object_name]
    if object_name == 'BUSH':
        if not obj['attacked']:
            print("You chopped the bush. There's nothing inside.")
            obj['attacked'] = True
        else:
            print("The bush is already chopped.")
    elif object_name == 'RUSTLINGBUSH':
        if not obj['attacked']:
            print("A Goblin jumps out!")
            if combat_with_goblin(player):
                print("You defeated the Goblin and found 1 Gold.")
                player['gold'] += 1
                obj['attacked'] = True
            else:
                print("Welcome to the Dragon's Cave! You are in the entrance. There is a bush on the left and a rustling bush on the right. There are also two chests behind the rustling bush. You can interact with BUSH, RUSTLINGBUSH, CHEST1, CHEST2.")
        else:
            print("The bush is already chopped.")
    elif object_name in ['CHEST1', 'CHEST2']:
        print("You dented the chest!")

def interact_with_object(object_name, player, rooms):
    room = rooms[player['room']]
    if object_name not in room:
        print("No such object.")
        return
    obj = room[object_name]
    if object_name in ['BUSH', 'RUSTLINGBUSH']:
        print("You walk into the bush. There's nothing here.")
    elif object_name in ['CHEST1', 'CHEST2']:
        if not obj['opened']:
            content = obj['content']
            if content == 'Gold':
                player['gold'] += 1
                print("You found 1 Gold in the chest.")
            elif content == 'Gem':
                player['gems'] += 1
                print("You found a Gem in the chest.")
            obj['opened'] = True
        else:
            print("The chest is already empty.")

def main():
    display_welcome()
    player = {'room': 1, 'hp': 20, 'gold': 0, 'gems': 0}
    rooms = {
        1: {
            'BUSH': {'attacked': False, 'content': None},
            'RUSTLINGBUSH': {'attacked': False, 'content': 'Goblin'},
            'CHEST1': {'opened': False, 'content': 'Gold'},
            'CHEST2': {'opened': False, 'content': 'Gem'}
        }
    }
    print(f"HP: {player['hp']}, Gold: {player['gold']}, Gems: {player['gems']}")
    while True:
        command_input = input("Enter command: ").strip().upper()
        parts = command_input.split()
        if len(parts) == 0:
            continue
        command = parts[0]
        object_name = parts[1] if len(parts) > 1 else None
        if command == 'Q':
            print("Quitting the game.")
            break
        elif command == 'A':
            if object_name:
                attack_object(object_name, player, rooms)
            else:
                print("Attack what?")
        elif command == 'G':
            if object_name:
                interact_with_object(object_name, player, rooms)
            else:
                print("Interact with what?")
        elif command == 'S':
            save_game(player, rooms)
        elif command == 'L':
            loaded_data = load_game()
            if loaded_data:
                room, hp, gold, gems, chest1_opened, chest2_opened = loaded_data
                player['room'] = room
                player['hp'] = hp
                player['gold'] = gold
                player['gems'] = gems
                rooms[1]['CHEST1']['opened'] = chest1_opened
                rooms[1]['CHEST2']['opened'] = chest2_opened
                print("Game loaded successfully.")
        else:
            print("Invalid command.")
        print(f"HP: {player['hp']}, Gold: {player['gold']}, Gems: {player['gems']}")

if __name__ == "__main__":
    main()