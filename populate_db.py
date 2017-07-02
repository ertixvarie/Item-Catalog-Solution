from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, Job, Weapon, User
from CRUD import makeSession, addEntry

session = makeSession()

deault_user = User(name = 'admin', email = 'dev@gmail.com')

addEntry(session, deault_user)

job_list = [Job(name = 'Warrior'),
            Job(name = 'Paladin'),
            Job(name = 'Bard'),
            Job(name = 'Dragoon'),
            Job(name = 'Monk'),
            Job(name = 'Black Mage'),
            Job(name = 'White Mage'),
            Job(name = 'Scholar'),
            Job(name = 'Summoner'),
            Job(name = 'Ninja'),
            Job(name = 'Astrologian'),
            Job(name = 'Dark Knight'),
            Job(name = 'Machinist'),
            Job(name = 'Archer'),
            Job(name = 'Gladiator'),
            Job(name = 'Lancer'),
            Job(name = 'Marauder'),
            Job(name = 'Pugilist'),
            Job(name = 'Arcanist'),
            Job(name = 'Conjurer'),
            Job(name = 'Thaumaturge'),
            Job(name = 'Rogue')]


wpn_list = [Weapon(name = "Coven Blade" , level = 60 , job_req = 'Gladiator', user_id = 1),
            Weapon(name = "Coven Fangs" , level = 60 , job_req = 'Pugilist', user_id = 1),
            Weapon(name = "Coven Battleaxe" , level = 60 , job_req = 'Marauder', user_id = 1),
            Weapon(name = "Coven Spear" , level = 60 , job_req = 'Lancer', user_id = 1),
            Weapon(name = "Coven Longbow" , level = 60 , job_req = 'Archer', user_id = 1),
            Weapon(name = "Coven Claws" , level = 60 , job_req = 'Rogue', user_id = 1),
            Weapon(name = "Coven Cane" , level = 60 , job_req = 'Conjurer', user_id = 1),
            Weapon(name = "Coven Rod" , level = 60 , job_req = 'Thaumaturge', user_id = 1),
            Weapon(name = "Coven Codex" , level = 60 , job_req = 'Arcanist', user_id = 1)
]


for job in job_list:
    addEntry(session, job)

for wpn in wpn_list:
    addEntry(session, wpn)
