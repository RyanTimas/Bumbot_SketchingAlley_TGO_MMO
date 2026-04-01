from src.database.queries.tgommo_avatar_quest_db_queries import *
from src.database.queries.tgommo_db_queries import *
from src.resources.constants.TGO_MMO_constants import *


def define_avatar_records(queryHandler):
    # Collect all avatars into a single list
    all_avatars = []

    # Append all avatar types to the central list
    all_avatars.extend(get_default_avatar_records())
    all_avatars.extend(get_secret_avatar_records())
    all_avatars.extend(get_event_avatar_records())
    all_avatars.extend(get_quest_avatar_records())
    all_avatars.extend(get_shop_avatar_records())
    all_avatars.extend(get_transcendant_avatar_records())

    # Call insert once with all avatars
    insert_user_avatar_records(all_avatars, queryHandler)


def get_default_avatar_records():
    default_avatars = [
        ('D1', 'Red', AVATAR_TYPE_DEFAULT, 'Red', 'Pokemon',),
        ('D2', 'Leaf', AVATAR_TYPE_DEFAULT, 'Leaf', 'Pokemon',),
        ('D3', 'Ethan', AVATAR_TYPE_DEFAULT, 'Ethan', 'Pokemon',),
        ('D4', 'Lyra', AVATAR_TYPE_DEFAULT, 'Lyra', 'Pokemon',),
        ('D5', 'Brendan', AVATAR_TYPE_DEFAULT, 'Brendan', 'Pokemon',),
        ('D6', 'May', AVATAR_TYPE_DEFAULT, 'May', 'Pokemon',),
        ('D7', 'Lucas', AVATAR_TYPE_DEFAULT, 'Lucas', 'Pokemon',),
        ('D8', 'Dawn', AVATAR_TYPE_DEFAULT, 'Dawn', 'Pokemon',),
        ('D9', 'Hilbert', AVATAR_TYPE_DEFAULT, 'Hilbert', 'Pokemon',),
        ('D10', 'Hilda', AVATAR_TYPE_DEFAULT, 'Hilda', 'Pokemon',),
        ('D11', 'Callum', AVATAR_TYPE_DEFAULT, 'Callum', 'Pokemon',),
        ('D12', 'Serena', AVATAR_TYPE_DEFAULT, 'Serena', 'Pokemon',),
        ('D13', 'Elio', AVATAR_TYPE_DEFAULT, 'Elio', 'Pokemon',),
        ('D14', 'Selene', AVATAR_TYPE_DEFAULT, 'Selene', 'Pokemon',),
        ('D15', 'Victor', AVATAR_TYPE_DEFAULT, 'Victor', 'Pokemon',),
        ('D16', 'Gloria', AVATAR_TYPE_DEFAULT, 'Gloria', 'Pokemon'),
        ('D17','Florian',AVATAR_TYPE_DEFAULT,'Florian','Pokemon'),
        ('D18','Juliana',AVATAR_TYPE_DEFAULT,'Juliana','Pokemon'),
        ('D19','Paxton',AVATAR_TYPE_DEFAULT,'Paxton','Pokemon'),
        ('D20','Harmony',AVATAR_TYPE_DEFAULT,'Harmony','Pokemon'),
    ]
    return default_avatars

def get_secret_avatar_records():
    secret_avatars = [
        # WAVE 1
        ('S1', 'Jordo', AVATAR_TYPE_SECRET, 'Jordo', 'Sketching Alley',),
        ('S2', 'Miku', AVATAR_TYPE_SECRET, 'Miku', 'Vocaloid',),
        ('S3', 'Garfield', AVATAR_TYPE_SECRET, 'Garfield', 'Garfield',),
        ('S4', 'Samus', AVATAR_TYPE_SECRET, 'Samus', 'Metroid',),
        ('S5', 'Boss Baby', AVATAR_TYPE_SECRET, 'BossBaby', 'Boss Baby',),
        ('S6', 'Walter White', AVATAR_TYPE_SECRET, 'WalterWhite', 'Breaking Bad',),
        # WAVE 2
        ('S7', 'Jesse Pinkman', AVATAR_TYPE_SECRET, 'JessePinkman', 'Breaking Bad',),
        ('S8', 'Mike Ehrmantraut', AVATAR_TYPE_SECRET, 'MikeEhrmantraut', 'Breaking Bad',),
        ('S9', 'Porky Pig', AVATAR_TYPE_SECRET, 'Porky', 'Looney Tunes',),
        ('S10', 'Jason Vorhees', AVATAR_TYPE_SECRET, 'JasonVorhees', 'Friday the 13th',),
        # WAVE 3
        ('S11', 'Wildmutt', AVATAR_TYPE_SECRET, 'Wildmutt', 'Ben 10', ),
        ('S12', 'Ripjaws', AVATAR_TYPE_SECRET, 'Ripjaws', 'Ben 10', ),
        ('S13', 'Upgrade', AVATAR_TYPE_SECRET, 'Upgrade', 'Ben 10', ),
        ('S14', 'Jake the Dog', AVATAR_TYPE_SECRET, 'JakeTheDog', 'Adventure Time',),
        ('S15', 'Patrick Star', AVATAR_TYPE_SECRET, 'PatrickStar', 'Spongebob Squarepants',),
        ('S16', 'Plankton', AVATAR_TYPE_SECRET, 'Plankton', 'Spongebob Squarepants',),
        ('S17', 'Tony the Tiger', AVATAR_TYPE_SECRET, 'TonyTheTiger', 'Kelloggs', ),
        ('S18', 'Hulk', AVATAR_TYPE_SECRET, 'Hulk', 'Marvel', ),
        ('S19', 'Woodstock', AVATAR_TYPE_SECRET, 'Woodstock', 'Peanuts',),
    ]
    return secret_avatars

def get_event_avatar_records():
    event_avatars = [
        # WAVE 1
        ('E1', 'Pim', AVATAR_TYPE_EVENT, 'Pim', 'Smiling Friends',),
        ('E2', 'Charlie', AVATAR_TYPE_EVENT, 'Charlie', 'Smiling Friends',),
        ('E3', 'Freddy Fazbear', AVATAR_TYPE_EVENT, 'FreddyFazbear', 'Five Nights at Freddy\'s',),
        ('E4', 'Allan', AVATAR_TYPE_EVENT, 'Allan', 'Smiling Friends',),
        ('E5', 'Glep', AVATAR_TYPE_EVENT, 'Glep', 'Smiling Friends',),
        ('E6', 'The Boss', AVATAR_TYPE_EVENT, 'TheBoss', 'Smiling Friends',),
        ('E7', 'Mr. Frog', AVATAR_TYPE_EVENT, 'MrFrog', 'Smiling Friends',),
        ('E8', 'Tyler', AVATAR_TYPE_EVENT, 'Tyler', 'Smiling Friends',),
        ('E9', 'Smormu', AVATAR_TYPE_EVENT, 'Smormu', 'Smiling Friends',),
        ('E10', 'Blue Janitor Dude', AVATAR_TYPE_EVENT, 'BlueJanitorDude', 'Smiling Friends',),
        ('E11', 'Dolly Dimpley', AVATAR_TYPE_EVENT, 'DollyDimpley', 'Smiling Friends',),
        ('E12', 'Cool Autistic Gamer 774', AVATAR_TYPE_EVENT, 'CoolAutisticGamer774', 'Smiling Friends',),
        # WAVE 2
        ('E13', 'Yuji Itadori', AVATAR_TYPE_EVENT, 'YujiItadori', 'Jujutsu Kaisen',),
        ('E14', 'Megumi Fushiguro', AVATAR_TYPE_EVENT, 'MegumiFushiguro', 'Jujutsu Kaisen',),
        ('E15', 'Nobara Kugisaki', AVATAR_TYPE_EVENT, 'NobaraKugisaki', 'Jujutsu Kaisen',),
        ('E16', 'Satoru Gojo', AVATAR_TYPE_EVENT, 'SatoruGojo', 'Jujutsu Kaisen',),
        ('E17', 'Kento Nanami', AVATAR_TYPE_EVENT, 'KentoNanami', 'Jujutsu Kaisen',),
        ('E18', 'Maki Zen\'in', AVATAR_TYPE_EVENT, 'MakiZenin', 'Jujutsu Kaisen',),
        ('E19', 'Suguru Geto', AVATAR_TYPE_EVENT, 'SuguruGeto', 'Jujutsu Kaisen',),
        ('E20', 'Toji Fushiguro', AVATAR_TYPE_EVENT, 'TojiFushiguro', 'Jujutsu Kaisen',),
        ('E21', 'Mahito', AVATAR_TYPE_EVENT, 'Mahito', 'Jujutsu Kaisen',),
        ('E22', 'Panda', AVATAR_TYPE_EVENT, 'Panda', 'Jujutsu Kaisen',),
        ('E23', 'Jogo', AVATAR_TYPE_EVENT, 'Jogo', 'Jujutsu Kaisen',),
        ('E24', 'Ryomen Sukuna', AVATAR_TYPE_EVENT, 'RyomenSukuna', 'Jujutsu Kaisen',),
        # WAVE 3
        ('E25', 'Invincible (Blue Suit)', AVATAR_TYPE_EVENT, 'InvincibleBlueSuit', 'Invincible',),
        ('E26', 'Mark Grayson', AVATAR_TYPE_EVENT, 'MarkGrayson', 'Invincible',),
        ('E27', 'Nolan Grayson', AVATAR_TYPE_EVENT, 'NolanGrayson', 'Invincible',),
        ('E28', 'Monster Girl', AVATAR_TYPE_EVENT, 'MonsterGirl', 'Invincible',),
        ('E29', 'Robot', AVATAR_TYPE_EVENT, 'Robot', 'Invincible',),
        ('E30', 'Dinosaurus', AVATAR_TYPE_EVENT, 'Dinosaurus', 'Invincible',),
        # WAVE 4
        ('E31', 'Crewmate (Blue)', AVATAR_TYPE_EVENT, 'CrewmateBlue', 'Among Us',),
        ('E32', 'Crewmate (Yellow)', AVATAR_TYPE_EVENT, 'CrewmateYellow', 'Among Us',),
        ('E33', 'Crewmate (Green)', AVATAR_TYPE_EVENT, 'CrewmateGreen', 'Among Us',),
        ('E34', 'Crewmate (Geoff Keighley)', AVATAR_TYPE_EVENT, 'CrewmateGreen', 'Among Us',),
    ]
    return event_avatars

def get_quest_avatar_records():
    quest_avatars = [
        #  COLLECTIONS
        ('Q1', 'Donkey Kong', AVATAR_TYPE_QUEST, 'DonkeyKong', 'Donkey Kong Country', 50),
        ('Q2', 'Big Bird', AVATAR_TYPE_QUEST, 'BigBird', 'Sesame Street',),
        ('Q3', 'Gex', AVATAR_TYPE_QUEST, 'Gex', 'Gex',),
        ('Q4', 'Kermit', AVATAR_TYPE_QUEST, 'Kermit', 'Muppets',),
        ('Q5', 'Hornet', AVATAR_TYPE_QUEST, 'Hornet', 'Hollow Knight',),
        ('Q6', 'TMNT', AVATAR_TYPE_QUEST, 'TMNT', 'Teenage Mutant Ninja Turtles', 0, True,),
        ('Q6a', 'Leonardo', AVATAR_TYPE_QUEST, 'Leonardo', 'Teenage Mutant Ninja Turtles',),
        ('Q6b', 'Raphael', AVATAR_TYPE_QUEST, 'Raphael', 'Teenage Mutant Ninja Turtles',),
        ('Q6c', 'Michelangelo', AVATAR_TYPE_QUEST, 'Michelangelo', 'Teenage Mutant Ninja Turtles',),
        ('Q6d', 'Donatello', AVATAR_TYPE_QUEST, 'Donatello', 'Teenage Mutant Ninja Turtles',),
        # WAVE 1
        ('Q7', 'Gold/Silver & Crystal Protagonists', AVATAR_TYPE_QUEST, 'GSC', 'Pokemon', 0, True,),
        ('Q7a', 'Gold', AVATAR_TYPE_QUEST, 'Gold', 'Pokemon',),
        ('Q7b', 'Kris', AVATAR_TYPE_QUEST, 'Kris', 'Pokemon',),
        ('Q8', 'Homer', AVATAR_TYPE_QUEST, 'Homer', 'The Simpsons',),
        # WAVE 2
        ('Q9', 'Turbo Granny', AVATAR_TYPE_QUEST, 'TurboGranny', 'DanDaDan',),
        ('Q10', 'Mordecai', AVATAR_TYPE_QUEST, 'Mordecai', 'Regular Show',),
        ('Q11', 'Rigby', AVATAR_TYPE_QUEST, 'Rigby', 'Regular Show',),
        ('Q12', 'Squirrel Girl', AVATAR_TYPE_QUEST, 'SquirrelGirl', 'Marvel',),
        ('Q13', 'Noko Shikanoko', AVATAR_TYPE_QUEST, 'NokoShikanoko', 'Anime',),
        ('Q14', 'Huntrix', AVATAR_TYPE_QUEST, 'Huntrix', 'K-Pop Demon Hunters', 100, True,),
        ('Q14a', 'Rumi', AVATAR_TYPE_QUEST, 'Rumi', 'K-Pop Demon Hunters',),
        ('Q14b', 'Mira', AVATAR_TYPE_QUEST, 'Mira', 'K-Pop Demon Hunters',),
        ('Q14c', 'Zoey', AVATAR_TYPE_QUEST, 'Zoey', 'K-Pop Demon Hunters',),
        ('Q15', 'Shuma Gorath', AVATAR_TYPE_QUEST, 'ShumaGorath', 'Marvel',),
        ('Q16', 'Gary', AVATAR_TYPE_QUEST, 'Gary', 'Pokemon',),
        # WAVE 3
        ('Q17', 'Bugs Bunny', AVATAR_TYPE_QUEST, 'Bugs', 'Looney Tunes',),
        ('Q18', 'Daffy Duck', AVATAR_TYPE_QUEST, 'Daffy', 'Looney Tunes',),
        ('Q19', 'Puss In Boots', AVATAR_TYPE_QUEST, 'PussInBoots', 'Shrek',),
        ('Q20', 'Bubsy', AVATAR_TYPE_QUEST, 'Bubsy', 'Bubsy',),
        ('Q21', 'Spider-Man', AVATAR_TYPE_QUEST, 'SpiderMan', 'Marvel',),
        ('Q22', 'Cynthia', AVATAR_TYPE_QUEST, 'Cynthia', 'Pokemon',),
        ('Q23', 'Marceline', AVATAR_TYPE_QUEST, 'Marceline', 'Adventure Time',),
        # WAVE 4
        ('Q24', 'Mickey Mouse', AVATAR_TYPE_QUEST, 'MickeyMouse', 'Mickey Mouse',),
        ('Q25', 'Betel Geuse', AVATAR_TYPE_QUEST, 'Beetlejuice', 'Beetlejuice',),
        ('Q26', 'XLR8', AVATAR_TYPE_QUEST, 'XLR8', 'Ben 10',),
        ('Q27', 'Stinkfly', AVATAR_TYPE_QUEST, 'Stinkfly', 'Ben 10',),
        ('Q28', 'Gray Matter', AVATAR_TYPE_QUEST, 'GrayMatter', 'Ben 10',),
        ('Q29', 'King K Rool', AVATAR_TYPE_QUEST, 'KingKRool', 'Donkey Kong',),
        ('Q30', 'Funky Kong', AVATAR_TYPE_QUEST, 'FunkyKong', 'Donkey Kong',),
        ('Q31', 'Edelgard', AVATAR_TYPE_QUEST, 'Edelgard', 'Fire Emblem',),
        ('Q32', 'Dimitri', AVATAR_TYPE_QUEST, 'Dimitri', 'Fire Emblem',),
        ('Q33', 'Claude', AVATAR_TYPE_QUEST, 'Claude', 'Fire Emblem',),
        ('Q34', 'Fox McCloud', AVATAR_TYPE_QUEST, 'Fox', 'Star Fox',),
        ('Q35', 'Falco Lombardi', AVATAR_TYPE_QUEST, 'Falco', 'Star Fox',),
        ('Q36', 'Big Boss', AVATAR_TYPE_QUEST, 'BigBoss', 'MetalGear',),
        ('Q37', 'Solid Snake', AVATAR_TYPE_QUEST, 'SolidSnake', 'MetalGear',),
        ('Q38', 'Buck Bumble', AVATAR_TYPE_QUEST, 'BuckBumble', 'Buck Bumble',),
        ('Q39', 'Miss Piggy', AVATAR_TYPE_QUEST, 'MissPiggy', 'Muppets',),
        ('Q40', 'Mr. Krabs', AVATAR_TYPE_QUEST, 'MrKrabs', 'Spongebob Squarepants',),
        ('Q41', 'Sandy Cheeks', AVATAR_TYPE_QUEST, 'SandyCheeks', 'Spongebob Squarepants',),
        ('Q42', 'Felix the Cat', AVATAR_TYPE_QUEST, 'FelixTheCat', 'Felix the Cat',),
        ('Q43', 'Snoopy', AVATAR_TYPE_QUEST, 'Snoopy', 'Peanuts',),
        ('Q44', 'Marmaduke', AVATAR_TYPE_QUEST, 'Marmaduke', 'Marmaduke',),
        ('Q45', 'Dwayne LaFontant', AVATAR_TYPE_QUEST, 'DwayneLaFontant', 'Over the Hedge',),
        ('Q46', 'Marcus', AVATAR_TYPE_QUEST, 'Marcus', 'Roblox',),
    ]
    return quest_avatars

def get_shop_avatar_records():
    shop_avatars = [
        # WAVE 4
        ('P1', 'Kasane Teto', AVATAR_TYPE_SHOP, 'KasaneTeto', 'Vocaloid', AVATAR_SHOP_PRICE_COMMON),
        ('P2', 'Charlie (Brazil)', AVATAR_TYPE_SHOP, 'CharlieBrazil', 'Smiling Friends', AVATAR_SHOP_PRICE_UNCOMMON),
        ('P3', 'Pim (Depressed)', AVATAR_TYPE_SHOP, 'PimDepressed', 'Smiling Friends', AVATAR_SHOP_PRICE_UNCOMMON),
        ('P4', 'DJ Spit', AVATAR_TYPE_SHOP, 'DJSpitSmilingFriends', 'Smiling Friends', AVATAR_SHOP_PRICE_COMMON),
        ('P5', 'James', AVATAR_TYPE_SHOP, 'JamesSmilingFriends', 'Smiling Friends', AVATAR_SHOP_PRICE_COMMON),
        ('P6', 'Dave', AVATAR_TYPE_SHOP, 'DaveSmilingFriends', 'Smiling Friends', AVATAR_SHOP_PRICE_EPIC),
        ('P7', 'Gojo (Hidden Inventory)', AVATAR_TYPE_SHOP, 'GojoHiddenInventory', 'Jujutsu Kaisen', AVATAR_SHOP_PRICE_RARE),
        ('P8', 'Todo', AVATAR_TYPE_SHOP, 'TodoJJK', 'Jujutsu Kaisen', AVATAR_SHOP_PRICE_COMMON),
        ('P9', 'Hanami', AVATAR_TYPE_SHOP, 'HanamiJJK', 'Jujutsu Kaisen', AVATAR_SHOP_PRICE_COMMON),
        ('P10', 'Mahoraga', AVATAR_TYPE_SHOP, 'MahoragaJJK', 'Jujutsu Kaisen', AVATAR_SHOP_PRICE_LEGENDARY),
        ('P11', 'Invincible', AVATAR_TYPE_SHOP, 'InvincibleYellowSuit', 'Invincible', AVATAR_SHOP_PRICE_COMMON),
        ('P12', 'Omni-Man', AVATAR_TYPE_SHOP, 'OmniMan', 'Invincible', AVATAR_SHOP_PRICE_UNCOMMON),
        ('P13', 'Atom Eve', AVATAR_TYPE_SHOP, 'AtomEve', 'Invincible', AVATAR_SHOP_PRICE_COMMON),
        ('P14', 'Allen the Alien', AVATAR_TYPE_SHOP, 'AllenTheAlien', 'Invincible', AVATAR_SHOP_PRICE_UNCOMMON),
        ('P15', 'Crew Mate (Red)', AVATAR_TYPE_SHOP, 'CrewMateRed', 'Among Us', AVATAR_SHOP_PRICE_COMMON),
        ('P16', 'Iron Man', AVATAR_TYPE_SHOP, 'IronMan', 'Marvel', AVATAR_SHOP_PRICE_RARE),
        ('P17', 'Captain America', AVATAR_TYPE_SHOP, 'CaptainAmerica', 'Marvel', AVATAR_SHOP_PRICE_RARE),
        ('P18', 'Thor', AVATAR_TYPE_SHOP, 'Thor', 'Marvel', AVATAR_SHOP_PRICE_RARE),
        ('P19', 'Storm', AVATAR_TYPE_SHOP, 'Storm', 'Marvel', AVATAR_SHOP_PRICE_UNCOMMON),
        ('P20', 'Magik', AVATAR_TYPE_SHOP, 'Magik', 'Marvel', AVATAR_SHOP_PRICE_UNCOMMON),
        ('P21', 'Spongebob', AVATAR_TYPE_SHOP, 'SpongebobSquarepants', 'Spongebob Squarepants', AVATAR_SHOP_PRICE_RARE),
        ('P22', 'Squidward', AVATAR_TYPE_SHOP, 'Squidward', 'Spongebob Squarepants', AVATAR_SHOP_PRICE_UNCOMMON),
        ('P23', 'Finn The Human', AVATAR_TYPE_SHOP, 'FinnTheHuman', 'Adventure Time', AVATAR_SHOP_PRICE_COMMON),
        ('P24', 'Princess Bubblegum', AVATAR_TYPE_SHOP, 'PrincessBubblegum', 'Adventure Time', AVATAR_SHOP_PRICE_COMMON),
        ('P25', 'Benson', AVATAR_TYPE_SHOP, 'Benson', 'Regular Show', AVATAR_SHOP_PRICE_UNCOMMON),
        ('P26', 'Ben 10', AVATAR_TYPE_SHOP, 'Ben10', 'Ben 10', AVATAR_SHOP_PRICE_COMMON),
        ('P27', 'Heatblast', AVATAR_TYPE_SHOP, 'Heatblast', 'Ben 10', AVATAR_SHOP_PRICE_RARE),
        ('P28', 'Diamondhead', AVATAR_TYPE_SHOP, 'Diamondhead', 'Ben 10', AVATAR_SHOP_PRICE_RARE),
        ('P29', 'Four Arms', AVATAR_TYPE_SHOP, 'FourArms', 'Ben 10', AVATAR_SHOP_PRICE_RARE),
        ('P30', 'Ghost Freak', AVATAR_TYPE_SHOP, 'GhostFreak', 'Ben 10', AVATAR_SHOP_PRICE_RARE),
        ('P31', 'SamuraiJack', AVATAR_TYPE_SHOP, 'SamuraiJack', 'Samurai Jack', AVATAR_SHOP_PRICE_UNCOMMON),
        ('P32', 'Elmo', AVATAR_TYPE_SHOP, 'Elmo', 'Sesame Street', AVATAR_SHOP_PRICE_COMMON),
        ('P33', 'The Knight', AVATAR_TYPE_SHOP, 'TheKnight', 'Hollow Knight', AVATAR_SHOP_PRICE_COMMON),
        ('P34', 'Diddy Kong', AVATAR_TYPE_SHOP, 'DiddyKong', 'Donkey Kong', AVATAR_SHOP_PRICE_COMMON),
        ('P35', 'April O\'Neil', AVATAR_TYPE_SHOP, 'AprilONeil', 'Teenage Mutant Ninja Turtles', AVATAR_SHOP_PRICE_RARE),
        ('P36', 'Shredder', AVATAR_TYPE_SHOP, 'Shredder', 'Teenage Mutant Ninja Turtles', AVATAR_SHOP_PRICE_RARE),
        ('P37', 'Underdog', AVATAR_TYPE_SHOP, 'Underdog', 'Underdog', AVATAR_SHOP_PRICE_COMMON),
        ('P38', 'Linus', AVATAR_TYPE_SHOP, 'LinusVanPelt', 'Peanuts', AVATAR_SHOP_PRICE_COMMON),
        ('P39', 'Lucy', AVATAR_TYPE_SHOP, 'LinusVanPelt', 'Peanuts', AVATAR_SHOP_PRICE_COMMON),
        ('P40', 'Charlie Brown', AVATAR_TYPE_SHOP, 'CharlieBrown', 'Peanuts', AVATAR_SHOP_PRICE_COMMON),
        ('P41', 'Big the Cat', AVATAR_TYPE_SHOP, 'BigTheCat', 'Sonic the Hedgehog', AVATAR_SHOP_PRICE_LEGENDARY),
        ('P42', 'Wolf', AVATAR_TYPE_SHOP, 'Wolf', 'Star Fox', AVATAR_SHOP_PRICE_RARE),
        ('P43', 'Senator Armstrong', AVATAR_TYPE_SHOP, 'SenatorArmstrong', 'Metal Gear', AVATAR_SHOP_PRICE_EPIC),
        ('P44', 'Raiden', AVATAR_TYPE_SHOP, 'Raiden', 'Metal Gear', AVATAR_SHOP_PRICE_RARE),
        ('P45', 'Sora', AVATAR_TYPE_SHOP, 'Sora', 'Kingdom Hearts', AVATAR_SHOP_PRICE_RARE),
        ('P46', 'Mickey Mouse (Kingdom Hearts)', AVATAR_TYPE_SHOP, 'MickeyMouseKH', 'Kingdom Hearts', AVATAR_SHOP_PRICE_COMMON),
        ('P47', 'Sonny', AVATAR_TYPE_SHOP, 'Sonny', 'Kelloggs', AVATAR_SHOP_PRICE_COMMON),
        ('P48', 'Toucan Sam', AVATAR_TYPE_SHOP, 'ToucanSam', 'Kelloggs', AVATAR_SHOP_PRICE_COMMON),
        ('P49', 'Moon', AVATAR_TYPE_SHOP, 'Moon', 'Soul Eater', AVATAR_SHOP_PRICE_LEGENDARY),
    ]
    return shop_avatars

def get_transcendant_avatar_records():
    transcendant_avatars = [
        ('T1', 'Bigfoot', AVATAR_TYPE_TRANSCENDANT, 'Bigfoot', 'Cryptid',),
        ('T2', 'Mothman', AVATAR_TYPE_TRANSCENDANT, 'Mothman', 'Cryptid',),
        ('T3', 'Frogman', AVATAR_TYPE_TRANSCENDANT, 'Frogman', 'Cryptid',),
        ('T4', 'SkunkApe', AVATAR_TYPE_TRANSCENDANT, 'SkunkApe', 'Cryptid',),

        # Fallback Avatars
        ('F1', 'Fallback-1', AVATAR_TYPE_FALLBACK, 'DefaultM', '',),
        ('F2', 'Fallback-2', AVATAR_TYPE_FALLBACK, 'DefaultF', '',),
    ]
    return transcendant_avatars

def insert_user_avatar_records(avatar_data, queryHandler):
    # avatar_data = [
    #     # ----DEFAULT AVATARS----
    #     ('D1', 'Red', AVATAR_TYPE_DEFAULT, 'Red', 'Pokemon',),
    #     ('D2', 'Leaf', AVATAR_TYPE_DEFAULT, 'Leaf', 'Pokemon',),
    #     ('D3', 'Ethan', AVATAR_TYPE_DEFAULT, 'Ethan', 'Pokemon',),
    #     ('D4', 'Lyra', AVATAR_TYPE_DEFAULT, 'Lyra', 'Pokemon',),
    #     ('D5', 'Brendan', AVATAR_TYPE_DEFAULT, 'Brendan', 'Pokemon',),
    #     ('D6', 'May', AVATAR_TYPE_DEFAULT, 'May', 'Pokemon',),
    #     ('D7', 'Lucas', AVATAR_TYPE_DEFAULT, 'Lucas', 'Pokemon',),
    #     ('D8', 'Dawn', AVATAR_TYPE_DEFAULT, 'Dawn', 'Pokemon',),
    #     ('D9', 'Hilbert', AVATAR_TYPE_DEFAULT, 'Hilbert', 'Pokemon',),
    #     ('D10', 'Hilda', AVATAR_TYPE_DEFAULT, 'Hilda', 'Pokemon',),
    #     ('D11', 'Callum', AVATAR_TYPE_DEFAULT, 'Callum', 'Pokemon',),
    #     ('D12', 'Serena', AVATAR_TYPE_DEFAULT, 'Serena', 'Pokemon',),
    #     ('D13', 'Elio', AVATAR_TYPE_DEFAULT, 'Elio', 'Pokemon',),
    #     ('D14', 'Selene', AVATAR_TYPE_DEFAULT, 'Selene', 'Pokemon',),
    #     ('D15', 'Victor', AVATAR_TYPE_DEFAULT, 'Victor', 'Pokemon',),
    #     ('D16', 'Gloria', AVATAR_TYPE_DEFAULT, 'Gloria', 'Pokemon',),
    #     ('D17', 'Florian', AVATAR_TYPE_DEFAULT, 'Florian', 'Pokemon',),
    #     ('D18', 'Juliana', AVATAR_TYPE_DEFAULT, 'Juliana', 'Pokemon',),
    #     ('D19', 'Paxton', AVATAR_TYPE_DEFAULT, 'Paxton', 'Pokemon',),
    #     ('D20', 'Harmony', AVATAR_TYPE_DEFAULT, 'Harmony', 'Pokemon',),
    #
    #     # ----SECRET AVATARS----
    #     # WAVE 1
    #     ('S1', 'Jordo', AVATAR_TYPE_SECRET, 'Jordo', 'Sketching Alley',),
    #     ('S2', 'Miku', AVATAR_TYPE_SECRET, 'Miku', 'Vocaloid',),
    #     ('S3', 'Garfield', AVATAR_TYPE_SECRET, 'Garfield', 'Garfield',),
    #     ('S4', 'Samus', AVATAR_TYPE_SECRET, 'Samus', 'Metroid',),
    #     ('S5', 'Boss Baby', AVATAR_TYPE_SECRET, 'BossBaby', 'Boss Baby',),
    #     ('S6', 'Walter White', AVATAR_TYPE_SECRET, 'WalterWhite', 'Breaking Bad',),
    #     # WAVE 2
    #     ('S7', 'Jesse Pinkman', AVATAR_TYPE_SECRET, 'JessePinkman', 'Breaking Bad',),
    #     ('S8', 'Mike Ehrmantraut', AVATAR_TYPE_SECRET, 'MikeEhrmantraut', 'Breaking Bad',),
    #     ('S9', 'Porky Pig', AVATAR_TYPE_SECRET, 'Porky', 'Looney Tunes',),
    #     ('S10', 'Jason Vorhees', AVATAR_TYPE_SECRET, 'JasonVorhees', 'Friday the 13th',),
    #
    #     # Event Avatars
    #     ('E1', 'Pim', AVATAR_TYPE_EVENT, 'Pim', 'Smiling Friends',),
    #     ('E2', 'Charlie', AVATAR_TYPE_EVENT, 'Charlie', 'Smiling Friends',),
    #     ('E3', 'Freddy Fazbear', AVATAR_TYPE_EVENT, 'FreddyFazbear', 'Five Nights at Freddy\'s',),
    #     ('E4', 'Allan', AVATAR_TYPE_EVENT, 'Allan', 'Smiling Friends',),
    #     ('E5', 'Glep', AVATAR_TYPE_EVENT, 'Glep', 'Smiling Friends',),
    #     ('E6', 'The Boss', AVATAR_TYPE_EVENT, 'TheBoss', 'Smiling Friends',),
    #     ('E7', 'Mr. Frog', AVATAR_TYPE_EVENT, 'MrFrog', 'Smiling Friends',),
    #     ('E8', 'Tyler', AVATAR_TYPE_EVENT, 'Tyler', 'Smiling Friends',),
    #     ('E9', 'Smormu', AVATAR_TYPE_EVENT, 'Smormu', 'Smiling Friends',),
    #     ('E10', 'Blue Janitor Dude', AVATAR_TYPE_EVENT, 'BlueJanitorDude', 'Smiling Friends',),
    #     ('E11', 'Dolly Dimpley', AVATAR_TYPE_EVENT, 'DollyDimpley', 'Smiling Friends',),
    #     ('E12', 'Cool Autistic Gamer 774', AVATAR_TYPE_EVENT, 'CoolAutisticGamer774', 'Smiling Friends',),
    #     # WAVE 2
    #     ('E13', 'Yuji Itadori', AVATAR_TYPE_EVENT, 'YujiItadori', 'Jujutsu Kaisen',),
    #     ('E14', 'Megumi Fushiguro', AVATAR_TYPE_EVENT, 'MegumiFushiguro', 'Jujutsu Kaisen',),
    #     ('E15', 'Nobara Kugisaki', AVATAR_TYPE_EVENT, 'NobaraKugisaki', 'Jujutsu Kaisen',),
    #     ('E16', 'Satoru Gojo', AVATAR_TYPE_EVENT, 'SatoruGojo', 'Jujutsu Kaisen',),
    #     ('E17', 'Kento Nanami', AVATAR_TYPE_EVENT, 'KentoNanami', 'Jujutsu Kaisen',),
    #     ('E18', 'Maki Zen\'in', AVATAR_TYPE_EVENT, 'MakiZenin', 'Jujutsu Kaisen',),
    #     ('E19', 'Suguru Geto', AVATAR_TYPE_EVENT, 'SuguruGeto', 'Jujutsu Kaisen',),
    #     ('E20', 'Toji Fushiguro', AVATAR_TYPE_EVENT, 'TojiFushiguro', 'Jujutsu Kaisen',),
    #     ('E21', 'Mahito', AVATAR_TYPE_EVENT, 'Mahito', 'Jujutsu Kaisen',),
    #     ('E22', 'Panda', AVATAR_TYPE_EVENT, 'Panda', 'Jujutsu Kaisen',),
    #     ('E23', 'Jogo', AVATAR_TYPE_EVENT, 'Jogo', 'Jujutsu Kaisen',),
    #     ('E24', 'Ryomen Sukuna', AVATAR_TYPE_EVENT, 'RyomenSukuna', 'Jujutsu Kaisen',),
    #
    #     # ----QUEST AVATARS----
    #     #  COLLECTIONS
    #     ('Q1', 'Donkey Kong', AVATAR_TYPE_QUEST, 'DonkeyKong', 'Donkey Kong Country', 50),
    #     ('Q2', 'Big Bird', AVATAR_TYPE_QUEST, 'BigBird', 'Sesame Street',),
    #     ('Q3', 'Gex', AVATAR_TYPE_QUEST, 'Gex', 'Gex',),
    #     ('Q4', 'Kermit', AVATAR_TYPE_QUEST, 'Kermit', 'Muppets',),
    #     ('Q5', 'Hornet', AVATAR_TYPE_QUEST, 'Hornet', 'Hollow Knight',),
    #     ('Q6', 'TMNT', AVATAR_TYPE_QUEST, 'TMNT', 'Teenage Mutant Ninja Turtles', 0, True,),
    #     ('Q6a', 'Leonardo', AVATAR_TYPE_QUEST, 'Leonardo', 'Teenage Mutant Ninja Turtles',),
    #     ('Q6b', 'Raphael', AVATAR_TYPE_QUEST, 'Raphael', 'Teenage Mutant Ninja Turtles',),
    #     ('Q6c', 'Michelangelo', AVATAR_TYPE_QUEST, 'Michelangelo', 'Teenage Mutant Ninja Turtles',),
    #     ('Q6d', 'Donatello', AVATAR_TYPE_QUEST, 'Donatello', 'Teenage Mutant Ninja Turtles',),
    #     # WAVE 1
    #     ('Q7', 'Gold/ Silver Protagonists', AVATAR_TYPE_QUEST, 'HGSS', 'Pokemon', 0, True,),
    #     ('Q7a', 'Gold', AVATAR_TYPE_QUEST, 'Gold', 'Pokemon',),
    #     ('Q7b', 'Kris', AVATAR_TYPE_QUEST, 'Kris', 'Pokemon',),
    #     ('Q8', 'Homer', AVATAR_TYPE_QUEST, 'Homer', 'The Simpsons',),
    #     # WAVE 2
    #     ('Q9', 'Turbo Granny', AVATAR_TYPE_QUEST, 'TurboGranny', 'DanDaDan',),
    #     ('Q10', 'Mordecai', AVATAR_TYPE_QUEST, 'Mordecai', 'Regular Show',),
    #     ('Q11', 'Rigby', AVATAR_TYPE_QUEST, 'Rigby', 'Regular Show',),
    #     ('Q12', 'Squirrel Girl', AVATAR_TYPE_QUEST, 'SquirrelGirl', 'Marvel',),
    #     ('Q13', 'Noko Shikanoko', AVATAR_TYPE_QUEST, 'NokoShikanoko', 'Anime',),
    #     ('Q14', 'Huntrix', AVATAR_TYPE_QUEST, 'Huntrix', 'K-Pop Demon Hunters', 100, True,),
    #     ('Q14a', 'Rumi', AVATAR_TYPE_QUEST, 'Rumi', 'K-Pop Demon Hunters',),
    #     ('Q14b', 'Mira', AVATAR_TYPE_QUEST, 'Mira', 'K-Pop Demon Hunters',),
    #     ('Q14c', 'Zoey', AVATAR_TYPE_QUEST, 'Zoey', 'K-Pop Demon Hunters',),
    #     ('Q15', 'Shuma Gorath', AVATAR_TYPE_QUEST, 'ShumaGorath', 'Marvel',),
    #     ('Q16', 'Gary', AVATAR_TYPE_QUEST, 'Gary', 'Pokemon',),
    #     # WAVE 3
    #     ('Q17', 'Bugs Bunny', AVATAR_TYPE_QUEST, 'Bugs', 'Looney Tunes',),
    #     ('Q18', 'Daffy Duck', AVATAR_TYPE_QUEST, 'Daffy', 'Looney Tunes',),
    #     ('Q19', 'Puss In Boots', AVATAR_TYPE_QUEST, 'PussInBoots', 'Shrek',),
    #     ('Q20', 'Bubsy', AVATAR_TYPE_QUEST, 'Bubsy', 'Bubsy',),
    #     ('Q21', 'Spider-Man', AVATAR_TYPE_QUEST, 'SpiderMan', 'Marvel',),
    #     ('Q22', 'Cynthia', AVATAR_TYPE_QUEST, 'Cynthia', 'Pokemon',),
    #     ('Q23', 'Marceline', AVATAR_TYPE_QUEST, 'Marceline', 'Adventure Time',),
    #     # WAVE 4
    #
    #     # ----SHOP AVATARS----
    #     # WAVE 4
    #     ('P1', 'Kasane Teto', AVATAR_TYPE_SHOP, 'KasaneTeto', 'Vocaloid', 250),
    #     ('P2', 'Moon', AVATAR_TYPE_SHOP, 'Moon', 'Soul Eater', 1000),
    #
    #     # Transcendant Avatars
    #     ('T1', 'Bigfoot', AVATAR_TYPE_TRANSCENDANT, 'Bigfoot', 'Cryptid',),
    #     ('T2', 'Mothman', AVATAR_TYPE_TRANSCENDANT, 'Mothman', 'Cryptid',),
    #     ('T3', 'Frogman', AVATAR_TYPE_TRANSCENDANT, 'Frogman', 'Cryptid',),
    #     ('T4', 'SkunkApe', AVATAR_TYPE_TRANSCENDANT, 'SkunkApe', 'Cryptid',),
    #
    #     # Fallback Avatars
    #     ('F1', 'Fallback-1', AVATAR_TYPE_FALLBACK, 'DefaultM', '',),
    #     ('F2', 'Fallback-2', AVATAR_TYPE_FALLBACK, 'DefaultF', '',),
    # ]

    for index, avatar in enumerate(avatar_data):
        avatar = (index + 1,) + avatar
        if len(avatar) == 6:
            avatar = avatar + (0,)
        if len(avatar) == 7:
            avatar = avatar + (False,)

        queryHandler.execute_query(TGOMMO_INSERT_NEW_USER_AVATAR, params=avatar)

        # for avatars unlocked server wide, insert a starter record into avatar link table
        if avatar[3] == AVATAR_TYPE_DEFAULT or avatar[3] == AVATAR_TYPE_SECRET:
            avatar_id = avatar[1]
            user_id = -1 if avatar[3] == AVATAR_TYPE_DEFAULT else 1
            queryHandler.execute_query(TGOMMO_INSERT_NEW_USER_AVATAR_LINK, params=(avatar_id, user_id))


# insert records for avatar quests.
def insert_user_avatar_unlock_condition_records(queryHandler):
    avatar_data = [
        # COLLECTION QUESTS
        ('Donkey Kong', ('Q1', AVATAR_DISTINCT_MAMMAL_QUEST_QUERY, 20)),
        ('Big Bird', ('Q2', AVATAR_DISTINCT_BIRD_QUEST_QUERY, 18)),
        ('Gex', ('Q3', AVATAR_DISTINCT_REPTILE_QUEST_QUERY, 3)),
        ('Kermit', ('Q4', AVATAR_DISTINCT_AMPHIBIAN_QUEST_QUERY, 2)),
        ('Hornet', ('Q5', AVATAR_DISTINCT_BUG_QUEST_QUERY, 5)),
        ('TMNT', ('Q6', AVATAR_VARIANTS_QUEST_1_QUERY, 10)),
        ('HGSS', ('Q7', AVATAR_MYTHICAL_QUEST_QUERY, 1)),
        ('Homer', ('Q8', AVATAR_MYTHICAL_QUEST_QUERY, 5)),
        # WAVE 2
        ('Mordecai', ('Q10', AVATAR_MORDECAI_QUEST_QUERY, AVATAR_QUEST_UNCOMMON_COUNT)),
        ('Rigby', ('Q11', AVATAR_RIGBY_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Squirrel Girl', ('Q12', AVTAR_SQUIRRELS_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Noko Shikanoko', ('Q13', AVATAR_DEER_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Huntrix', ('Q14', AVATAR_LEGENDARY_QUEST_QUERY, 3)),
        ('Shuma Gorath', ('Q15', AVATAR_TOTAL_EPIC_QUEST_QUERY, 10)),
        ('Gary', ('Q16', AVATAR_TOTAL_UNIQUE_CREATURES_CAUGHT_QUERY, AVATAR_QUEST_UNCOMMON_COUNT)),
        # WAVE 3
        ('Bugs', ('Q17', AVATAR_BUGS_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Daffy', ('Q18', AVATAR_DAFFY_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Puss in Boots', ('Q19', AVATAR_FELINES_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Bubsy', ('Q20', AVATAR_BUBSY_QUEST_QUERY, AVATAR_QUEST_RARE_COUNT)),
        ('Spider-Man', ('Q21', AVATAR_SPIDERS_QUEST_QUERY, AVATAR_QUEST_UNCOMMON_COUNT)),
        ('Cynthia', ('Q22', AVATAR_TOTAL_UNIQUE_CREATURES_CAUGHT_QUERY, 100)),
        ('Marceline', ('Q23', AVATAR_MARCELINE_QUEST_QUERY, 20)),
        # WAVE 4
        ('Mickey Mouse', ('Q24', AVATAR_MICKEY_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Betel Geuse', ('Q25', AVATAR_BEETLEJUICE_QUEST_QUERY, 33)),

        ('XLR8', ('Q26', AVATAR_TOTAL_REPTILE_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Stinkfly', ('Q27', AVATAR_TOTAL_INSECT_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Gray Matter', ('Q28', AVATAR_TOTAL_AMPHIBIAN_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),

        ('King K Rool', ('Q29', AVATAR_CROCODILIANS_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Funky Kong', ('Q30', AVATAR_DISTINCT_FL_QUERY, 500)),

        ('Edelgard', ('Q31', AVATAR_TOTAL_BIRD_QUEST_QUERY, 300)),
        ('Dimitri', ('Q32', AVATAR_FELINES_QUEST_QUERY, 300)),
        ('Claude', ('Q33', AVATAR_DEER_QUEST_QUERY, 300)),

        ('Fox McCloud', ('Q34', AVATAR_FOX_QUEST_QUERY, AVATAR_QUEST_RARE_COUNT)),
        ('Falco Lombardi', ('Q35', AVATAR_BIRDS_OF_PRAY_QUEST_QUERY, AVATAR_QUEST_RARE_COUNT)),

        ('Big Boss', ('Q36', AVATAR_SNAKES_QUEST_QUERY, 120, True)),
        ('Solid Snake', ('Q37', AVATAR_SNAKES_QUEST_QUERY, 85)),
        ('Buck Bumble', ('Q38', AVATAR_BUCK_BUMBLE_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Miss Piggy', ('Q39', AVATAR_MISS_PIGGY_QUEST_QUERY, 20)),
        ('Mr. Krabs', ('Q40', AVATAR_TOTAL_CRUSTACEAN_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Sandy Cheeks', ('Q41', AVTAR_SQUIRRELS_QUEST_QUERY, 200)),
        ('Felix the Cat', ('Q42', AVATAR_FELINES_QUEST_QUERY, 200)),
        ('Snoopy', ('Q43', AVATAR_SNOOPY_QUEST_QUERY, AVATAR_QUEST_UNCOMMON_COUNT)),
        ('Marmaduke', ('Q44', AVATAR_MARMADUKE_QUEST_QUERY, AVATAR_QUEST_RARE_COUNT)),
        ('Dwayne LaFontant', ('Q45', AVATAR_DWAYNE_LAFONTANT_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
        ('Marcus', ('Q46', AVATAR_MARCUS_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),

        # Transcendant Avatars
        ('Bigfoot', ('T1', AVATAR_BIGFOOT_QUEST_QUERY, 1, True)),
        ('Mothman', ('T2', AVATAR_MOTHMAN_QUEST_QUERY, 1, True)),
        ('Frogman', ('T3', AVATAR_FROGMAN_QUEST_QUERY, 1, True)),
        ('SkunkApe', ('T4', AVATAR_SKUNK_APE_QUEST_QUERY, 1, True)),
    ]

    for index, avatar in enumerate(avatar_data):
        avatar_params = avatar[1]
        if len(avatar_params) == 3:
            avatar_params = avatar_params + (False,)

        queryHandler.execute_query(TGOMMO_INSERT_NEW_AVATAR_UNLOCK_CONDITION, params=avatar_params)