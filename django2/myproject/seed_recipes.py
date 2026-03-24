import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.models import Recipe

def seed_recipes():
    recipes_data = [
        # -------------------- BREAKFAST --------------------
        {
            "id": 1, "name": "Masala Oats Upma", "category": "breakfast", "cook_time": "15 mins",
            "calories": 180, "servings": 2, "difficulty": "Easy", "protein": 6, "carbs": 28, "fats": 4, "fiber": 5,
            "image": "🥣",
            "ingredients": ["1 cup rolled oats","1 onion, chopped","1 tomato, chopped","1 green chili, chopped","1/2 tsp mustard seeds","Curry leaves","1/2 tsp turmeric","Salt","2 cups water","Fresh coriander"],
            "instructions": ["Dry roast oats 3-4 minutes.","Temper mustard + curry leaves.","Sauté onion + chili.","Add tomatoes + turmeric + salt.","Add water; boil.","Add oats; cook 3-4 minutes.","Garnish and serve."]
        },
        {
            "id": 2, "name": "Moong Dal Cheela", "category": "breakfast", "cook_time": "20 mins",
            "calories": 220, "servings": 2, "difficulty": "Easy", "protein": 12, "carbs": 30, "fats": 5, "fiber": 8,
            "image": "🥞",
            "ingredients": ["1 cup moong dal (soaked)","1 onion, chopped","1 green chili","1 inch ginger","1/2 tsp cumin","Salt","Coriander","Oil"],
            "instructions": ["Grind dal with ginger + chili.","Add onion, cumin, salt, coriander.","Cook on pan both sides.","Serve with chutney/yogurt."]
        },
        {
            "id": 3, "name": "Vegetable Poha", "category": "breakfast", "cook_time": "15 mins",
            "calories": 200, "servings": 2, "difficulty": "Easy", "protein": 4, "carbs": 35, "fats": 6, "fiber": 3,
            "image": "🍚",
            "ingredients": ["2 cups poha","1 onion","1 potato","1/2 cup peas","1 green chili","mustard","turmeric","curry leaves","peanuts","lemon","coriander"],
            "instructions": ["Rinse poha; drain.","Temper mustard + curry leaves + peanuts.","Cook onion + veggies.","Add turmeric + salt.","Mix poha gently.","Finish with lemon + coriander."]
        },
        {
            "id": 13, "name": "Idli Sambar (Light & Protein)", "category": "breakfast", "cook_time": "25 mins",
            "calories": 240, "servings": 2, "difficulty": "Medium", "protein": 10, "carbs": 40, "fats": 3, "fiber": 6,
            "image": "🍘",
            "ingredients": ["4 idlis","1 cup sambar","Mixed veggies","Mustard","Curry leaves","Salt"],
            "instructions": ["Steam/prepare idlis.","Heat sambar and simmer.","Temper mustard + curry leaves.","Serve hot."]
        },
        {
            "id": 14, "name": "Ragi Dosa with Veg Filling", "category": "breakfast", "cook_time": "20 mins",
            "calories": 260, "servings": 2, "difficulty": "Medium", "protein": 8, "carbs": 42, "fats": 6, "fiber": 7,
            "image": "🫓",
            "ingredients": ["1 cup ragi flour","Salt","Water","Onion, carrot, capsicum","1 tsp oil"],
            "instructions": ["Make thin batter.","Spread on pan.","Add veg filling; fold.","Serve with chutney."]
        },

        # -------------------- LUNCH --------------------
        {
            "id": 4, "name": "Dal Tadka", "category": "lunch", "cook_time": "30 mins",
            "calories": 180, "servings": 4, "difficulty": "Medium", "protein": 10, "carbs": 28, "fats": 4, "fiber": 12,
            "image": "🍲",
            "ingredients": ["1 cup toor dal","tomatoes","onion","chilies","cumin","garlic","turmeric","chili powder","garam masala","coriander","ghee"],
            "instructions": ["Cook dal.","Make tadka.","Mix and simmer.","Garnish and serve."]
        },
        {
            "id": 6, "name": "Rajma Masala", "category": "lunch", "cook_time": "40 mins",
            "calories": 240, "servings": 4, "difficulty": "Medium", "protein": 14, "carbs": 38, "fats": 4, "fiber": 11,
            "image": "🫘",
            "ingredients": ["1 cup rajma","onion","tomato","ginger-garlic","cumin","spices","coriander"],
            "instructions": ["Cook rajma.","Cook masala base.","Simmer with rajma 15-20 min.","Serve."]
        },
        {
            "id": 15, "name": "Quinoa Veg Pulao", "category": "lunch", "cook_time": "25 mins",
            "calories": 280, "servings": 2, "difficulty": "Easy", "protein": 10, "carbs": 45, "fats": 6, "fiber": 8,
            "image": "🥘",
            "ingredients": ["1 cup quinoa","mixed veggies","jeera","ginger","chili","salt","1 tsp oil"],
            "instructions": ["Rinse quinoa.","Temper jeera; add ginger/chili.","Sauté veggies.","Cook quinoa 1:2 water.","Serve with curd."]
        },
        {
            "id": 16, "name": "Chole (Healthy Chickpea Curry)", "category": "lunch", "cook_time": "35 mins",
            "calories": 290, "servings": 3, "difficulty": "Medium", "protein": 14, "carbs": 42, "fats": 7, "fiber": 11,
            "image": "🫛",
            "ingredients": ["1 cup chickpeas","onion","tomato","ginger-garlic","chole masala","cumin","lemon","coriander"],
            "instructions": ["Cook chickpeas.","Cook masala.","Simmer 10-12 min.","Finish with lemon + coriander."]
        },

        # -------------------- SNACKS --------------------
        {
            "id": 7, "name": "Sprouts Chaat", "category": "snack", "cook_time": "10 mins",
            "calories": 150, "servings": 2, "difficulty": "Easy", "protein": 8, "carbs": 22, "fats": 3, "fiber": 6,
            "image": "🥗",
            "ingredients": ["sprouts","onion","tomato","cucumber","chili","chaat masala","lemon","coriander"],
            "instructions": ["Boil sprouts 5 minutes.","Mix everything.","Add lemon and serve."]
        },
        {
            "id": 8, "name": "Masala Roasted Makhana", "category": "snack", "cook_time": "10 mins",
            "calories": 120, "servings": 2, "difficulty": "Easy", "protein": 4, "carbs": 18, "fats": 4, "fiber": 2,
            "image": "🍿",
            "ingredients": ["makhana","1 tsp ghee","chaat masala","turmeric","chili powder","salt"],
            "instructions": ["Roast 6-7 minutes.","Add spices.","Cool and eat."]
        },
        {
            "id": 17, "name": "Greek Yogurt Fruit Bowl", "category": "snack", "cook_time": "5 mins",
            "calories": 190, "servings": 1, "difficulty": "Easy", "protein": 12, "carbs": 22, "fats": 5, "fiber": 4,
            "image": "🍓",
            "ingredients": ["1 cup Greek yogurt","fruits","chia/flax seeds","honey (optional)"],
            "instructions": ["Add yogurt.","Top with fruits + seeds.","Optional honey."]
        },
        {
            "id": 18, "name": "Paneer & Cucumber Sandwich", "category": "snack", "cook_time": "10 mins",
            "calories": 260, "servings": 1, "difficulty": "Easy", "protein": 16, "carbs": 26, "fats": 10, "fiber": 5,
            "image": "🥪",
            "ingredients": ["whole wheat bread","paneer","cucumber","mint chutney","salt/pepper"],
            "instructions": ["Season paneer.","Layer cucumber + paneer.","Toast optional; serve."]
        },

        # -------------------- DINNER --------------------
        {
            "id": 10, "name": "Palak Paneer", "category": "dinner", "cook_time": "30 mins",
            "calories": 280, "servings": 3, "difficulty": "Medium", "protein": 16, "carbs": 10, "fats": 20, "fiber": 4,
            "image": "🥬",
            "ingredients": ["paneer","spinach","onion","tomato","ginger-garlic","cumin","garam masala","salt"],
            "instructions": ["Blanch spinach; blend.","Cook masala.","Add spinach; simmer.","Add paneer; finish spices."]
        },
        {
            "id": 11, "name": "Chicken Curry (Home Style)", "category": "dinner", "cook_time": "40 mins",
            "calories": 320, "servings": 4, "difficulty": "Medium", "protein": 35, "carbs": 8, "fats": 18, "fiber": 2,
            "image": "🍗",
            "ingredients": ["chicken","onion","tomato","ginger-garlic","spices","curry leaves","coriander"],
            "instructions": ["Cook onion masala.","Add chicken.","Simmer covered until tender.","Garnish and serve."]
        },
        {
            "id": 12, "name": "Vegetable Khichdi", "category": "dinner", "cook_time": "25 mins",
            "calories": 210, "servings": 3, "difficulty": "Easy", "protein": 8, "carbs": 38, "fats": 4, "fiber": 6,
            "image": "🍛",
            "ingredients": ["rice","moong dal","veggies","jeera","turmeric","ginger","salt","ghee"],
            "instructions": ["Wash rice+dal.","Cook with veggies and spices.","Pressure cook soft.","Finish with ghee."]
        },
        {
            "id": 19, "name": "Tandoori Fish (Pan/OTG)", "category": "dinner", "cook_time": "25 mins",
            "calories": 260, "servings": 2, "difficulty": "Easy", "protein": 30, "carbs": 6, "fats": 12, "fiber": 1,
            "image": "🐟",
            "ingredients": ["fish fillet","curd","tandoori masala","lemon","salt","1 tsp oil"],
            "instructions": ["Marinate 15 minutes.","Pan grill or bake.","Serve with salad."]
        },
        {
            "id": 20, "name": "Mixed Veg Soup (Light Dinner)", "category": "dinner", "cook_time": "20 mins",
            "calories": 140, "servings": 2, "difficulty": "Easy", "protein": 6, "carbs": 22, "fats": 3, "fiber": 5,
            "image": "🥣",
            "ingredients": ["carrot","beans","tomato","garlic","salt","pepper","water/stock"],
            "instructions": ["Sauté garlic.","Add veggies + stock.","Boil 12-15 minutes.","Season and serve."]
        }
    ]

    for data in recipes_data:
        recipe_id = data.pop('id')
        Recipe.objects.update_or_create(id=recipe_id, defaults=data)
    
    print(f"Successfully seeded {len(recipes_data)} recipes.")

if __name__ == "__main__":
    seed_recipes()
