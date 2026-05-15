TEST_QUERIES = [
    # ── FACTUAL ──
    {
        "id": "f1",
        "query": "How much garlic do I use in my chole recipe?",
        "family": "factual",
        "expected_recipe": "One Pot Chole/chickpea Curry",
        "expected_chunk_mode": "sections",
        "ground_truth_keywords": ["garlic", "cloves", "6", "six", "chole", "chickpea"]
    },
    {
        "id": "f2",
        "query": "How many whistles for my masala khichdi?",
        "family": "factual",
        "expected_recipe": "Masala Khicdi",
        "expected_chunk_mode": "sentences",
        "ground_truth_keywords": ["whistle", "four", "4", "khichdi", "pressure", "cooker"]
    },

    # ── CROSS MODAL ──
    {
        "id": "cm1",
        "query": "Recreate this pasta dish in my style",
        "family": "cross_modal",
        "image_path": "eval/test_images/pasta.jpg",
        "expected_recipe": "Vino Vedura",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["pasta", "garlic", "italian", "spice", "marinara"]
    },
    {
        "id": "cm2",
        "query": "What can I make for dinner with these ingredients?",
        "family": "cross_modal",
        "image_path": "eval/test_images/Pantry_2.jpg",
        "expected_recipe": "Hummus wraps",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["dinner", "recipe", "ingredients", "cook", "make"]
    },

    # ── ANALYTICAL ──
    {
        "id": "a1",
        "query": "What is my healthiest breakfast option?",
        "family": "analytical",
        "expected_recipe": "Cinnamon Overnight Oats",
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["oats", "breakfast", "healthy", "protein", "calories"]
    },
    {
        "id": "a2",
        "query": "Which of my pasta recipes has the most vegetables?",
        "family": "analytical",
        "expected_recipe": None,
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["pasta", "vegetables", "broccoli", "capsicum", "mushroom"]
    },

    # ── CONVERSATIONAL ──
    {
        "id": "conv1",
        "query": "What do I usually substitute if I don't want to use strawberries?",
        "family": "conversational",
        "expected_recipe": None,
        "expected_chunk_mode": "sections",
        "ground_truth_keywords": ["strawberry", "substitute", "blueberry", "compote", "alternative"]
    },
    {
        "id": "conv2",
        "query": "What desserts do I have that dont use milk chocolate?",
        "family": "conversational",
        "expected_recipe": None,
        "expected_chunk_mode": "whole",
        "ground_truth_keywords": ["dessert", "dark chocolate", "biscoff", "strawberry", "cheesecake"]
    },
]