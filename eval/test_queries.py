TEST_QUERIES = [
    {
        "id": "f1",
        "query": "How much garlic do I use in my chole recipe?",
        "family": "factual",
        "expected_recipe": "One Pot Chole/chickpea Curry",
        "expected_chunk_mode": "sections",
        "ground_truth_keywords": ["garlic", "cloves", "6", "7", "chole"]
    },
    {
        "id": "f2",
        "query": "What spice level is my dal tadka?",
        "family": "factual",
        "expected_recipe": "Dal Tadka",
        "expected_chunk_mode": "sections",
        "ground_truth_keywords": ["spice", "5", "dal", "tadka"]
    },
    {
        "id": "f3",
        "query": "How many whistles for my masala khichdi?",
        "family": "factual",
        "expected_recipe": "Masala Khicdi",
        "expected_chunk_mode": "sentences",
        "ground_truth_keywords": ["whistle", "4", "khichdi", "pressure"]
    },
    {
        "id": "f4",
        "query": "What alternatives do I have for strawberry?",
        "family": "factual",
        "expected_recipe": "Quick Hummus",
        "expected_chunk_mode": "sections",
        "ground_truth_keywords": ["hummus", "alternative", "olive"]
    },
    {
        "id": "f5",
        "query": "What is the combined cook and prep time for my banana bread?",
        "family": "factual",
        "expected_recipe": "Banana Bread",
        "expected_chunk_mode": "sections",
        "ground_truth_keywords": ["50", "mins", "banana", "180"]
    },

    # ── CROSS MODAL ──
    {
        "id": "cm1",
        "query": "Recreate this pasta dish in my style",
        "family": "cross_modal",
        "image_path": "eval/test_images/pasta.jpg",
        "expected_recipe": "White base pasta Pasta",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["pasta", "garlic", "italian", "spice"]
    },
    {
        "id": "cm2",
        "query": "What can I make for dinner with these ingredients?",
        "family": "cross_modal",
        "image_path": "eval/test_images/Pantry_2.jpg",
        "expected_recipe": "Hummus Wraps",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["recipe", "ingredients", "dinner"]
    },
    {
        "id": "cm3",
        "query": "Before going to the gym I want to make something light with these ingredients",
        "family": "cross_modal",
        "image_path": "eval/test_images/Pantry_1.jpg",
        "expected_recipe": "Dark chocolate oats",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["Breakfast", "oats", "light"]
    },

    # ── ANALYTICAL ──
    {
        "id": "a1",
        "query": "Which of my dessert recipes is the quickest to cook?",
        "family": "analytical",
        "expected_recipe": "Oreo Cheesecake bites",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["mins", "quick", "fast", "time"]
    },
    {
        "id": "a2",
        "query": "What is my healthiest breakfast option?",
        "family": "analytical",
        "expected_recipe": "Cinnamon Overnight Oats",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["oats", "breakfast", "healthy", "protein"]
    },
    {
        "id": "a3",
        "query": "I have to bake a cake for someone who loves fruit, give me a recipe that uses a fruit",
        "family": "analytical",
        "expected_recipe": "Strawberry cheesecake",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["fruits", "fruit", "cake", "bake"]
    },
    {
        "id": "a4",
        "query": "Compare my two hummus recipes",
        "family": "analytical",
        "expected_recipe": "Quick Hummus",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["hummus", "traditional", "quick", "difference"]
    },
    {
        "id": "a5",
        "query": "Which of my pasta recipe uses wine?",
        "family": "analytical",
        "expected_recipe": "Vino Vedura",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["pasta", "wine", "white"]
    },

    # ── CONVERSATIONAL ──
    {
        "id": "conv1",
        "query": "What do I usually substitute as my source of protein when I dont have paneer?",
        "family": "conversational",
        "expected_recipe": None,
        "expected_chunk_mode": "sections",
        "ground_truth_keywords": ["paneer", "substitute", "protein"]
    },
    {
        "id": "conv2",
        "query": "I am going on a high protein based diet, what changes should I make in my current recipes",
        "family": "conversational",
        "expected_recipe": None,
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["chicken", "paneer", "chickpeas", "protein"]
    },
    {
        "id": "conv3",
        "query": "Make me dal tadka again but less salty",
        "family": "conversational",
        "expected_recipe": "Dal Tadka",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["dal", "tadka", "salt", "reduce"]
    },
    {
        "id": "conv4",
        "query": "What desserts do I have that dont use milk chocolate?",
        "family": "conversational",
        "expected_recipe": None,
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["dessert", "dark chocolate", "biscoff", "strawberry"]
    },
    {
        "id": "conv5",
        "query": "I want something spicy for dinner tonight under 30 mins",
        "family": "conversational",
        "expected_recipe": None,
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["spicy", "dinner", "mins", "quick"]
    },
]