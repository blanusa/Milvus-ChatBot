import pandas as pd
from faker import Faker
import random

# Initialize faker
fake = Faker('en_US')

# List of streets and landmarks
streets = [
    'Bulevar Oslobođenja', 'Cara Dušana', 'Narodnog Fronta', 'Zmaj Jovina', 
    'Jovana Cvijića', 'Futoška', 'Bulevar Evrope', 'Maksima Gorkog', 
    'Stražilovska', 'Dunavska', 'Kisacka', 'Temerinska', 'Pariske Komune', 
    'Balzakova', 'Somborska Rampa', 'Lasla Gala', 'Feješ Klare', 
    'Mihajla Pupina', 'Jovana Dučića', 'Cara Lazara', 'Jevrejska', 
    'Petefi Šandora', 'Miše Dimitrijevića', 'Žarka Zrenjanina', 'Pavla Papa',
    'Veternik', 'Futog', 'Sajlovo', 'Stepanovići', 'Adice', 'Telep', 'Klisa',
    'Salajka', 'Podbara', 'Detelinara', 'Grbavica', 'Limani', 'Banatić',
    'Partizanska', 'Branka Radičevića', 'Nova 1', 'Nova 2', 'Karađorđeva', 
    'Beogradska', 'Miloša Obilića', 'Vojvode Putnika', 'Braće Krkljuš', 
    'Jevrejska', 'Jovana Cvijića', 'Stevana Sremca', 'Novosadska', 
    'Vuka Karadžića', 'Njegoševa', 'Braće Jerković', 'Braće Kovač', 
    'Stevana Sinđelića', 'Vukašinovićeva', 'Zlatiborska', 'Milovana Glišića', 
    'Braće Stefanović', 'Vojvode Mišića', 'Svetozara Miletića', 
    'Jovana Subotića', 'Svetosavska', 'Železnička', 'Bulevar Jaše Tomića', 
    'Narodnih Heroja', 'Slobodana Bajica', 'Miletićeva', 'Ive Lole Ribara', 
    'Trg Republike', 'Trg Slobode', 'Omladinska', 'Novosadska 1', 
    'Novosadska 2', 'Novosadska 3', 'Laze Telečkog', 'Nikole Tesle', 
    'Braće Ribnikar', 'Gogoljeva', 'Bulevar Patrijarha Pavla', 
    'Stevana Mokranjca', 'Braće Dronjak', 'Braće Grulović', 
    'Braće Novaković', 'Braće Krkljuš', 'Majke Jugovića', 'Svetosavska', 
    'Njegoševa', 'Petefi Šandora', 'Đorđa Jovanovića', 'Sonje Marinković', 
    'Dositejeva', 'Bulevar Mihajla Pupina', 'Bulevar cara Lazara', 
    'Bulevar kralja Petra I', 'Bulevar kralja Aleksandra', 
    'Narodnog Fronta', 'Kralja Aleksandra', 'Kralja Petra I', 'Kraljice Marije',
    'Carice Milice', 'Vladimira Perića', 'Jug Bogdana', 'Radnički', 
    'Partizanska', 'Kneza Miloša', 'Vojvode Mišića', 'Živojina Mišića', 
    'Kralja Milana', 'Vuka Karadžića', 'Kneza Lazara', 'Kneza Mihaila', 
    'Vuka Karadžića', 'Kneza Višeslava', 'Petra Kočića', 'Laze Kostića', 
    'Milutina Milankovića', 'Aleksandra Vulina', 'Stefana Dečanskog', 
    'Vojislava Ilića', 'Kneza Mihailova', 'Kralja Aleksandra I Karađorđevića',
    'Nikole Tesle', 'Kneza Pavla', 'Svetosavska', 'Svetog Save', 
    'Đure Đakovića', 'Zmaj Jovina', 'Njegoševa', 'Svetog Save', 
    'Maršala Tita', 'Petra Drapšina', 'Milana Tepić', 'Bulevar Slobodana Jovanovića', 
    'Braće Popović', 'Braće Ribnikar', 'Braće Janjić', 'Braće Krsmanović', 
    'Braće Vujić', 'Braće Penić', 'Braće Đukić', 'Braće Milić', 'Braće Radić', 
    'Braće Brkić', 'Braće Jovanović', 'Braće Čolaković', 'Braće Ilić'
]

# List of landmarks or notable sights in Novi Sad
landmarks = [
    'Petrovaradin Fortress', 'Danube Park', 'Novi Sad Synagogue', 
    'Serbian National Theatre', 'Museum of Vojvodina', 'Liberty Square', 
    'Cathedral of Saint George', 'University of Novi Sad', 
    'Fruška Gora National Park', 'Strand Beach', 'Spens Sports Center', 
    'Big Shopping Mall', 'City Hall', 'Danube River', 'Freedom Square', 
    'Stari Grad', 'Žeželj Bridge', 'Fish Market', 'Matica Srpska Gallery', 
    'Svetozar Miletić Monument', 'Novi Sad Fair', 'Limanski Park'
]

# Generate bus lines
bus_lines = [f"Bus Line {i}" for i in range(1, 101)]

# Facilities list
facilities = ["Benches", "Shelter", "Information Board", "Ticket Machine", "Wi-Fi"]

# Generate bus stops
def generate_bus_stops(num_stops):
    stops = []
    for stop_id in range(1, num_stops + 1):
        name = fake.random.choice(landmarks)
        lines = fake.random.sample(bus_lines, k=fake.random_int(min=1, max=5))
        stop_facilities = fake.random.sample(facilities, k=fake.random_int(min=1, max=len(facilities)))
        nearby_landmarks = fake.random.sample(landmarks, k=fake.random_int(min=1, max=3))
        special_features = f"{name}, historical significance"

        stops.append({
            "stop_id": str(stop_id),
            "name": str(name),
            "latitude": str(round(fake.latitude(), 6)),
            "longitude": str(round(fake.longitude(), 6)),
            "bus_lines": str(lines),
            "facilities": str(stop_facilities),
            "nearby_landmarks": str(nearby_landmarks),
            "special_features": str(special_features)
        })
    
    return stops

# Generate data for 100 bus stops
bus_stops = generate_bus_stops(200)

# Convert to DataFrame and save to CSV
df_stops = pd.DataFrame(bus_stops)
csv_filename_stops = 'novi_sad_bus_stops.csv'
df_stops.to_csv(csv_filename_stops, index=False)

print(f"CSV file '{csv_filename_stops}' generated successfully!")
