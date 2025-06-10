import asyncio
import random
import platform

# Player class to track conquests and abilities
class Player:
    def __init__(self, name):
        self.name = name
        self.conquered = 0
        self.war_cry_cooldown = -1  # -1 means not unlocked, 0 means available

# Territory class with unit types
class Territory:
    def __init__(self, name, is_neutral=False):
        self.name = name
        self.units = {"swordsman": 0, "spearman": 0, "archer": 0}
        self.owner = None
        self.adjacent = []
        self.is_neutral = is_neutral

# Helper function to format units for display
def format_units(units):
    return ", ".join([f"{count} {unit}{'s' if count > 1 else ''}" for unit, count in units.items() if count > 0]) or "0 units"

# Helper function to remove random units
def remove_random_units(units, excess):
    while excess > 0:
        available = [unit for unit in units if units[unit] > 0]
        if not available:
            break
        unit_to_remove = random.choice(available)
        units[unit_to_remove] -= 1
        excess -= 1

# Helper function to clear all units
def clear_units(units_dict):
    for key in units_dict:
        units_dict[key] = 0

# Helper function to distribute units proportionally
def distribute_units(original_units, total):
    if total <= 0:
        return {"swordsman": 0, "spearman": 0, "archer": 0}
    original_total = sum(original_units.values())
    if original_total == 0:
        return {"swordsman": total, "spearman": 0, "archer": 0}
    new_units = {"swordsman": 0, "spearman": 0, "archer": 0}
    for unit, count in original_units.items():
        new_units[unit] = round(count * total / original_total)
    # Adjust for rounding errors
    current_total = sum(new_units.values())
    if current_total > total:
        remove_random_units(new_units, current_total - total)
    elif current_total < total:
        available = [unit for unit in new_units if original_units[unit] > 0]
        if available:
            new_units[random.choice(available)] += total - current_total
    return new_units

# Battle resolution function
def battle(attacker_territory, defender_territory, k, use_war_cry=False, territories=None, ai=None):
    beats = {"swordsman": "spearman", "spearman": "archer", "archer": "swordsman"}
    
    # Sample k units from attacker_territory
    all_units = [unit for unit, count in attacker_territory.units.items() for _ in range(count)]
    if k > len(all_units) - 1:
        return False
    committed = random.sample(all_units, k)
    committed_units = {"swordsman": 0, "spearman": 0, "archer": 0}
    for unit in committed:
        committed_units[unit] += 1
    # Remove from attacker_territory
    for unit, count in committed_units.items():
        attacker_territory.units[unit] -= count
    
    # Store defender's original units for proportional distribution
    defender_original_units = defender_territory.units.copy()
    
    # Calculate base strengths
    attack_base = k
    defense_base = sum(defender_territory.units.values())
    
    # Determine advantages
    committed_types = [unit for unit in committed_units if committed_units[unit] > 0]
    defender_types = [unit for unit in defender_territory.units if defender_territory.units[unit] > 0]
    attacker_advantage = sum(1 for attacker_type in committed_types if beats[attacker_type] in defender_types)
    defender_advantage = sum(1 for defender_type in defender_types if beats[defender_type] in committed_types)
    
    # Calculate total strengths
    A = attack_base + attacker_advantage + (1 if use_war_cry else 0)
    D = defense_base + defender_advantage
    
    # Resolve battle
    if A > D:
        clear_units(defender_territory.units)
        remaining = max(1, A - D)
        if sum(committed_units.values()) > 0:
            for unit in committed_units:
                defender_territory.units[unit] = committed_units[unit]
            total_remaining = sum(defender_territory.units.values())
            if total_remaining > remaining:
                excess = total_remaining - remaining
                remove_random_units(defender_territory.units, excess)
        else:
            defender_territory.units["swordsman"] = 1
        defender_territory.owner = attacker_territory.owner
        defender_territory.is_neutral = False
        attacker_territory.owner.conquered += 1
        if attacker_territory.owner.conquered >= 3 and attacker_territory.owner.war_cry_cooldown == -1:
            attacker_territory.owner.war_cry_cooldown = 0
        # If attacking a neutral territory, AI gains a random neutral territory
        if defender_territory.is_neutral and territories and ai:
            neutral_territories = [t for t in territories.values() if t.is_neutral]
            if neutral_territories:
                neutral_to_ai = random.choice(neutral_territories)
                neutral_to_ai.owner = ai
                neutral_to_ai.is_neutral = False
                ai.conquered += 1
                print(f"AI gains {neutral_to_ai.name} due to neutral territory attack.")
    elif A < D:
        clear_units(attacker_territory.units)
        for unit, count in committed_units.items():
            attacker_territory.units[unit] += count  # Return unused units
        clear_units(defender_territory.units)
        remaining_defense = max(1, D - A)
        defender_territory.units = distribute_units(defender_original_units, remaining_defense)
    else:  # Draw
        clear_units(attacker_territory.units)
        for unit, count in committed_units.items():
            attacker_territory.units[unit] += count  # Return unused units
        clear_units(defender_territory.units)
        if use_war_cry:
            defender_territory.units["swordsman"] = 1
            defender_territory.owner = attacker_territory.owner
            defender_territory.is_neutral = False
            attacker_territory.owner.conquered += 1
            if attacker_territory.owner.conquered >= 3 and attacker_territory.owner.war_cry_cooldown == -1:
                attacker_territory.owner.war_cry_cooldown = 0
            # If attacking a neutral territory, AI gains a random neutral territory
            if defender_territory.is_neutral and territories and ai:
                neutral_territories = [t for t in territories.values() if t.is_neutral]
                if neutral_territories:
                    neutral_to_ai = random.choice(neutral_territories)
                    neutral_to_ai.owner = ai
                    neutral_to_ai.is_neutral = False
                    ai.conquered += 1
                    print(f"AI gains {neutral_to_ai.name} due to neutral territory attack.")
        else:
            defender_territory.units = distribute_units(defender_original_units, 1)
    
    return True

# Diplomacy questions
questions = [
    {"question": "Which god is the patron of this city?", "answers": ["Athena", "Apollo"], "correct": random.choice([0, 1])},
    {"question": "What is the main export of this region?", "answers": ["Olives", "Pottery"], "correct": random.choice([0, 1])},
    {"question": "Who founded this city according to legend?", "answers": ["Cadmus", "Theseus"], "correct": random.choice([0, 1])},
    {"question": "Which festival is most celebrated here?", "answers": ["Panathenaea", "Dionysia"], "correct": random.choice([0, 1])},
    {"question": "What is the city's famous landmark?", "answers": ["Temple", "Theater"], "correct": random.choice([0, 1])}
]

# Diplomacy meeting function
def diplomacy_meeting(player, ai, territories):
    if random.random() < 1/3:  # 1/3 chance of a meeting
        neutral_territories = [t for t in territories.values() if t.is_neutral]
        if not neutral_territories:
            return
        target_territory = random.choice(neutral_territories)
        is_player_meeting = random.random() < 0.5
        recipient = player if is_player_meeting else ai
        print(f"Diplomacy Meeting with {target_territory.name} for {recipient.name}!")
        question_data = random.choice(questions)
        print(f"Question: {question_data['question']}")
        print(f"Options: 1) {question_data['answers'][0]}, 2) {question_data['answers'][1]}")
        if is_player_meeting:
            try:
                answer = int(input("Choose answer (1 or 2): ").strip()) - 1
                if answer not in [0, 1]:
                    print("Invalid choice, treated as incorrect.")
                    answer = 1 - question_data['correct']  # Force incorrect
            except ValueError:
                print("Invalid input, treated as incorrect.")
                answer = 1 - question_data['correct']
        else:
            answer = random.choice([0, 1])  # AI picks randomly
        if answer == question_data['correct']:
            print(f"Correct! {target_territory.name} joins {recipient.name}.")
            target_territory.owner = recipient
            target_territory.is_neutral = False
            recipient.conquered += 1
            if recipient.conquered >= 3 and recipient.war_cry_cooldown == -1:
                recipient.war_cry_cooldown = 0
        else:
            print(f"Incorrect! {target_territory.name} joins {ai.name if is_player_meeting else player.name}.")
            target_territory.owner = ai if is_player_meeting else player
            target_territory.is_neutral = False
            (ai if is_player_meeting else player).conquered += 1
            if (ai if is_player_meeting else player).conquered >= 3 and (ai if is_player_meeting else player).war_cry_cooldown == -1:
                (ai if is_player_meeting else player).war_cry_cooldown = 0

# Game setup
player = Player("player")
ai = Player("AI")
neutral = Player("neutral")
territories = {name: Territory(name, is_neutral=(name in ["Pylos", "Larissa"])) 
               for name in ["Sparta", "Athens", "Thebes", "Corinth", "Olympia", "Delphi", "Pylos", "Larissa"]}
adjacencies = {
    "Sparta": ["Corinth", "Olympia"],
    "Athens": ["Thebes", "Corinth"],
    "Thebes": ["Athens", "Delphi", "Larissa"],
    "Corinth": ["Sparta", "Athens", "Olympia"],
    "Olympia": ["Sparta", "Corinth", "Delphi", "Pylos"],
    "Delphi": ["Thebes", "Olympia", "Larissa"],
    "Pylos": ["Olympia"],
    "Larissa": ["Thebes", "Delphi"]
}
for name, adj_names in adjacencies.items():
    territories[name].adjacent = [territories[adj_name] for adj_name in adj_names]

# Initial territory assignment and units
territories["Sparta"].owner = player
territories["Sparta"].units = {"swordsman": 5, "spearman": 5, "archer": 0}
territories["Corinth"].owner = player
territories["Corinth"].units = {"swordsman": 3, "spearman": 3, "archer": 3}
territories["Olympia"].owner = player
territories["Olympia"].units = {"swordsman": 4, "spearman": 2, "archer": 1}
territories["Athens"].owner = ai
territories["Athens"].units = {"swordsman": 0, "spearman": 5, "archer": 5}
territories["Thebes"].owner = ai
territories["Thebes"].units = {"swordsman": 2, "spearman": 4, "archer": 3}
territories["Delphi"].owner = ai
territories["Delphi"].units = {"swordsman": 1, "spearman": 3, "archer": 4}
for name in ["Pylos", "Larissa"]:
    territories[name].owner = neutral
    territories[name].units = {
        "swordsman": random.randint(1, 5),
        "spearman": random.randint(1, 5),
        "archer": random.randint(1, 5)
    }

# Game state
game_running = True
FPS = 60

def display_state():
    state = "\n".join([f"{t.name}: {format_units(t.units)}, owned by {t.owner.name}" for t in territories.values()])
    print(state)
    return state

async def player_turn():
    global game_running
    print("Player's turn")
    display_state()
    while True:
        attack_from = input("Select territory to attack from (or 'done'): ").strip()
        if attack_from.lower() == "done":
            break
        if attack_from not in territories or territories[attack_from].owner != player:
            print("Invalid selection")
            continue
        total_units = sum(territories[attack_from].units.values())
        if total_units < 2:
            print("Not enough units to attack")
            continue
        adjacent_targets = [t for t in territories[attack_from].adjacent if t.owner != player]
        if not adjacent_targets:
            print("No enemy or neutral territories adjacent")
            continue
        print(f"Adjacent targets: {[t.name for t in adjacent_targets]}")
        target = input("Select target territory: ").strip()
        if target not in territories or territories[target] not in adjacent_targets:
            print("Invalid target")
            continue
        max_k = total_units - 1
        try:
            k = int(input(f"Choose number of units to commit (1 to {max_k}): ").strip())
            if k < 1 or k > max_k:
                print("Invalid number")
                continue
        except ValueError:
            print("Please enter a number")
            continue
        use_war_cry = False
        if player.war_cry_cooldown == 0:
            choice = input("Use War Cry? (y/n): ").strip().lower()
            if choice == "y":
                use_war_cry = True
        if battle(territories[attack_from], territories[target], k, use_war_cry, territories, ai):
            if territories[target].owner == player:
                print(f"{attack_from} (Player) Wins! {format_units(territories[target].units)} remaining on {target}.")
            else:
                print(f"Attack from {attack_from} failed. {format_units(territories[target].units)} on {target}.")
            display_state()
        if use_war_cry:
            player.war_cry_cooldown = 2
        if player.war_cry_cooldown > 0:
            player.war_cry_cooldown -= 1
        if all(territory.owner in [player, neutral] for territory in territories.values()):
            print("Player wins!")
            game_running = False
            break

async def ai_turn():
    global game_running
    print("AI's turn")
    possible_attacks = [(t, adj) for t in territories.values() if t.owner == ai and sum(t.units.values()) > 1 for adj in t.adjacent if adj.owner == player]
    if possible_attacks:
        attack_from, target = random.choice(possible_attacks)
        k = random.randint(1, min(3, sum(attack_from.units.values()) - 1))  # Limit to 3 units for balance
        print(f"AI attacks from {attack_from.name} to {target.name} with {k} units")
        if battle(attack_from, target, k, False, territories, ai):
            if target.owner == ai:
                print(f"{attack_from.name} (AI) Wins! {format_units(target.units)} remaining on {target.name}.")
            else:
                print(f"Attack from {attack_from.name} failed. {format_units(target.units)} on {target.name}.")
            display_state()
    else:
        print("AI has no valid attacks this turn.")
    if all(territory.owner in [ai, neutral] for territory in territories.values()):
        print("AI wins!")
        game_running = False

async def main():
    global game_running
    while game_running:
        await player_turn()
        if not game_running:
            break
        await ai_turn()
        if not game_running:
            break
        diplomacy_meeting(player, ai, territories)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())