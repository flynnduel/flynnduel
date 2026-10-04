// Word bank (spec §5) and secret easter-egg categories (spec §6.1–6.2).
// Every entry is a widely known noun or name of 1–3 words.

const CATEGORIES = {
  Food: [
    'Pizza', 'Sushi', 'Taco', 'Burrito', 'Pancakes', 'Waffles', 'Spaghetti', 'Lasagna', 'Hamburger', 'Hot Dog',
    'French Fries', 'Ice Cream', 'Chocolate', 'Popcorn', 'Pretzel', 'Bacon', 'Cheesecake', 'Donut', 'Cupcake', 'Nachos',
    'Mac and Cheese', 'Fried Chicken', 'Salad', 'Soup', 'Avocado', 'Watermelon', 'Pineapple', 'Banana', 'Strawberry', 'Peanut Butter',
    'Grilled Cheese', 'Ramen', 'Dumplings', 'Cereal', 'Popsicle', 'Burrito Bowl', 'Corn Dog',
  ],
  Animals: [
    'Elephant', 'Giraffe', 'Penguin', 'Kangaroo', 'Dolphin', 'Shark', 'Octopus', 'Lion', 'Tiger', 'Zebra',
    'Monkey', 'Gorilla', 'Panda', 'Koala', 'Sloth', 'Flamingo', 'Owl', 'Eagle', 'Parrot', 'Peacock',
    'Snake', 'Crocodile', 'Turtle', 'Frog', 'Hippo', 'Rhino', 'Camel', 'Llama', 'Raccoon', 'Squirrel',
    'Hedgehog', 'Bat', 'Jellyfish', 'Goat', 'Chicken', 'Pig',
  ],
  Jobs: [
    'Doctor', 'Nurse', 'Teacher', 'Firefighter', 'Police Officer', 'Chef', 'Pilot', 'Astronaut', 'Dentist', 'Lawyer',
    'Plumber', 'Electrician', 'Farmer', 'Mail Carrier', 'Barber', 'Mechanic', 'Lifeguard', 'Librarian', 'Waiter', 'Bartender',
    'DJ', 'Magician', 'Clown', 'Detective', 'Scientist', 'Photographer', 'Architect', 'Veterinarian', 'Personal Trainer', 'Influencer',
    'Uber Driver', 'Construction Worker', 'Zookeeper', 'Judge', 'Cashier',
  ],
  Places: [
    'Beach', 'Airport', 'Hospital', 'Library', 'Casino', 'Zoo', 'Museum', 'Movie Theater', 'Gym', 'Supermarket',
    'Bowling Alley', 'Church', 'Prison', 'Castle', 'Farm', 'Desert', 'Jungle', 'Volcano', 'Space Station', 'Submarine',
    'Train Station', 'Hotel', 'Haunted House', 'Water Park', 'Amusement Park', 'Mall', 'Gas Station', 'Laundromat', 'Stadium', 'Igloo',
    'Treehouse', 'Lighthouse', 'Ski Resort', 'Pyramid', 'Waterfall',
  ],
  Sports: [
    'Soccer', 'Basketball', 'Football', 'Baseball', 'Tennis', 'Golf', 'Hockey', 'Volleyball', 'Swimming', 'Boxing',
    'Wrestling', 'Skateboarding', 'Surfing', 'Snowboarding', 'Skiing', 'Bowling', 'Cricket', 'Rugby', 'Table Tennis', 'Badminton',
    'Gymnastics', 'Cycling', 'Marathon', 'Archery', 'Fencing', 'Karate', 'Rock Climbing', 'Dodgeball', 'Pickleball', 'Lacrosse',
    'Figure Skating', 'Darts', 'Cornhole', 'Kickball', 'Horse Racing',
  ],
  'Movies & TV': [
    'Titanic', 'Star Wars', 'Harry Potter', 'Shrek', 'Frozen', 'Toy Story', 'Finding Nemo', 'The Lion King', 'Jurassic Park', 'Spider-Man',
    'Batman', 'The Avengers', 'Stranger Things', 'The Office', 'Friends', 'SpongeBob', 'The Simpsons', 'Squid Game', 'Barbie', 'Home Alone',
    'Jaws', 'Rocky', 'Ghostbusters', 'Mean Girls', 'Cars', 'Up', 'Moana', 'Avatar', 'Breaking Bad', 'Game of Thrones',
    'Wednesday', 'Despicable Me', 'Top Gun', 'Grease', 'Scooby-Doo',
  ],
  'Famous Characters': [
    'Mickey Mouse', 'Mario', 'Pikachu', 'Sonic', 'Darth Vader', 'Yoda', 'Elsa', 'Shrek', 'Batman', 'Superman',
    'Wonder Woman', 'Spider-Man', 'Hulk', 'Iron Man', 'Harry Potter', 'Gandalf', 'Sherlock Holmes', 'Cinderella', 'Santa Claus', 'Easter Bunny',
    'Tooth Fairy', 'Dracula', 'Frankenstein', 'Garfield', 'Scooby-Doo', 'Homer Simpson', 'SpongeBob', 'Winnie the Pooh', 'Buzz Lightyear', 'Kermit',
    'Barbie', 'Grinch', 'Hello Kitty', 'Pac-Man', 'Shaggy',
  ],
  'Things at a Party': [
    'Balloons', 'Cake', 'Candles', 'Confetti', 'Pinata', 'Karaoke', 'Speaker', 'Disco Ball', 'Red Cups', 'Chips',
    'Dip', 'Pizza Boxes', 'Party Hat', 'Streamers', 'Playlist', 'Dance Floor', 'Photo Booth', 'Ice', 'Cooler', 'Beer Pong',
    'Glow Sticks', 'Presents', 'Birthday Card', 'Neighbors', 'Uninvited Guest', 'Selfie', 'Group Photo', 'Snacks', 'Punch Bowl', 'Costume',
    'Fog Machine', 'Fairy Lights', 'Charades', 'Sparklers', 'Party Bus',
  ],
  Superpowers: [
    'Flying', 'Invisibility', 'Super Strength', 'Teleportation', 'Time Travel', 'Mind Reading', 'Telekinesis', 'Super Speed', 'Shapeshifting', 'Healing',
    'X-Ray Vision', 'Laser Eyes', 'Immortality', 'Fire Breathing', 'Freezing', 'Shrinking', 'Growing', 'Weather Control', 'Talking to Animals', 'Breathing Underwater',
    'Night Vision', 'Force Field', 'Cloning', 'Lie Detection', 'Super Hearing', 'Elasticity', 'Wall Climbing', 'Mind Control', 'Lightning', 'Rewind Time',
    'Pause Time', 'Super Luck', 'Walking Through Walls', 'Glowing', 'Web Shooting',
  ],
  'Things in a Bathroom': [
    'Toilet', 'Toilet Paper', 'Toothbrush', 'Toothpaste', 'Shampoo', 'Conditioner', 'Soap', 'Towel', 'Mirror', 'Shower',
    'Bathtub', 'Rubber Duck', 'Plunger', 'Hair Dryer', 'Razor', 'Floss', 'Mouthwash', 'Deodorant', 'Bath Mat', 'Shower Curtain',
    'Scale', 'Sink', 'Faucet', 'Loofah', 'Cotton Swabs', 'Bath Bomb', 'Tweezers', 'Hairbrush', 'Lotion', 'Air Freshener',
    'Toilet Brush', 'Medicine Cabinet', 'Bubble Bath', 'Face Mask', 'Nail Clippers',
  ],
  Vacation: [
    'Passport', 'Suitcase', 'Sunscreen', 'Flip Flops', 'Sunglasses', 'Hotel', 'Cruise', 'Road Trip', 'Camping', 'Tent',
    'Souvenir', 'Postcard', 'Beach Towel', 'Snorkel', 'Airplane', 'Jet Lag', 'Tour Guide', 'Map', 'Swimsuit', 'Hammock',
    'Resort', 'Cabin', 'Theme Park', 'Boarding Pass', 'Selfie Stick', 'Sandcastle', 'Campfire', 'Sunburn', 'Rental Car', 'Pool',
    'Room Service', 'Backpack', 'Hostel', 'Island', 'Luggage Carousel',
  ],
  Holidays: [
    'Christmas', 'Halloween', 'Thanksgiving', 'Easter', 'New Year', "Valentine's Day", 'Fourth of July', 'Hanukkah', 'Diwali', 'Ramadan',
    'Eid', 'Kwanzaa', 'Lunar New Year', "St. Patrick's Day", "Mother's Day", "Father's Day", 'Birthday', 'Mardi Gras', 'Cinco de Mayo', 'Labor Day',
    "April Fools' Day", 'Christmas Tree', 'Jack-o-Lantern', 'Turkey', 'Fireworks', 'Easter Egg', 'Mistletoe', 'Stocking', 'Trick or Treat', 'Candy Cane',
    'Gingerbread Man', 'Snowman', 'Reindeer', 'Menorah', 'Wedding',
  ],
  School: [
    'Teacher', 'Homework', 'Backpack', 'Pencil', 'Eraser', 'Notebook', 'Calculator', 'Chalkboard', 'Locker', 'Cafeteria',
    'Recess', 'Detention', 'Principal', 'School Bus', 'Report Card', 'Field Trip', 'Science Fair', 'Gym Class', 'Prom', 'Graduation',
    'Yearbook', 'Spelling Bee', 'Library', 'Hall Pass', 'Pop Quiz', 'Final Exam', 'Group Project', 'Substitute Teacher', 'Fire Drill', 'Lunchbox',
    'Glue Stick', 'Crayons', 'Ruler', 'Dorm', 'Snow Day',
  ],
  Music: [
    'Guitar', 'Piano', 'Drums', 'Violin', 'Trumpet', 'Saxophone', 'Flute', 'Microphone', 'Headphones', 'Concert',
    'Festival', 'Karaoke', 'DJ', 'Rap', 'Rock', 'Jazz', 'Country', 'Opera', 'Choir', 'Boy Band',
    'Taylor Swift', 'Beyonce', 'Drake', 'Michael Jackson', 'Elvis', 'The Beatles', 'Bad Bunny', 'Rihanna', 'Ed Sheeran', 'Lady Gaga',
    'Spotify', 'Vinyl', 'Mosh Pit', 'Encore', 'Ukulele',
  ],
  'Fast Food Chains': [
    "McDonald's", 'Burger King', "Wendy's", 'Taco Bell', 'Chick-fil-A', 'KFC', 'Subway', 'Starbucks', "Dunkin'", 'Chipotle',
    "Domino's", 'Pizza Hut', "Papa John's", 'Five Guys', 'In-N-Out', 'Shake Shack', 'Popeyes', 'Panda Express', 'Sonic', "Arby's",
    'Jollibee', 'Dairy Queen', 'Whataburger', "Culver's", "Raising Cane's", 'Panera', 'Wingstop', "Zaxby's", "Hardee's", "Carl's Jr",
    'Krispy Kreme', 'White Castle', 'Little Caesars', "Jersey Mike's", 'Waffle House',
  ],
};

const SECRET = {
  gambia: {
    name: 'The Gambia',
    words: [
      'Benachin', 'Domoda', 'Kora', 'Banjul', 'Attaya', 'Wrestling', 'Ferry', 'Mango', 'Djembe', 'Baobab',
      'Serrekunda', 'Yassa', 'Cashew', 'Hippo', 'Gele', 'Bush Taxi', 'Kankurang', 'Peanuts', 'Crocodile Pool', 'Fishing Boat',
    ],
  },
  insideJokes: {
    name: 'Inside Jokes',
    // Swap these for your friends' own references.
    words: [
      'Group Chat', 'Aux Cord', 'Brunch', 'Road Trip', 'Late Fee', 'Ex', 'Group Photo', 'Hangover', 'Dad Joke', 'Read Receipts',
    ],
  },
};

const GAMBIA_CHANCE = 0.04; // 1 in 25
const INSIDE_JOKES_CHANCE = 0.025; // 1 in 40

const key = (category, word) => `${category}|${word}`;

function pickFrom(rng, category, words, used) {
  const available = words.filter((w) => !used.has(key(category, w)));
  if (available.length === 0) return null;
  return available[Math.floor(rng() * available.length)];
}

function pickNormal(rng, used) {
  const names = Object.keys(CATEGORIES);
  const first = names[Math.floor(rng() * names.length)];
  const word = pickFrom(rng, first, CATEGORIES[first], used);
  if (word) return { category: first, word, secret: null };

  const open = names.filter((n) => pickFrom(rng, n, CATEGORIES[n], used));
  if (open.length === 0) return null;
  const category = open[Math.floor(rng() * open.length)];
  return { category, word: pickFrom(rng, category, CATEGORIES[category], used), secret: null };
}

function pickWord(rng, used) {
  const r = rng();
  let secret = null;
  if (r < GAMBIA_CHANCE) secret = 'gambia';
  else if (r < GAMBIA_CHANCE + INSIDE_JOKES_CHANCE) secret = 'insideJokes';

  let pick = null;
  if (secret) {
    const { name, words } = SECRET[secret];
    const word = pickFrom(rng, name, words, used);
    if (word) pick = { category: name, word, secret };
  }
  if (!pick) pick = pickNormal(rng, used);
  if (!pick) {
    used.clear();
    pick = pickNormal(rng, used);
  }
  used.add(key(pick.category, pick.word));
  return pick;
}

module.exports = { CATEGORIES, SECRET, pickWord };
