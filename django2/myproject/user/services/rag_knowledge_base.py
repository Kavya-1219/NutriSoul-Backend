"""
NutriSoul RAG Knowledge Base
Curated nutrition and health documents for retrieval-augmented generation.
Each document has a title, content, and tags for fast pre-filtering.
"""

NUTRITION_KNOWLEDGE_BASE = [
    # ── Macronutrients ──────────────────────────────────────────────────
    {
        "title": "Protein Requirements and Sources",
        "content": (
            "Protein is essential for muscle repair, immune function, and enzyme production. "
            "The recommended daily allowance (RDA) is 0.8g per kg of body weight for sedentary adults. "
            "For muscle gain, aim for 1.6–2.2g per kg. For weight loss, 1.2–1.6g per kg helps preserve lean mass. "
            "High-quality sources: chicken breast (31g/100g), eggs (13g/100g), paneer (18g/100g), "
            "lentils/dal (9g/100g cooked), Greek yogurt (10g/100g), tofu (8g/100g), whey protein (25g/scoop). "
            "Spread protein intake across 4–5 meals for optimal muscle protein synthesis. "
            "Leucine-rich foods (eggs, dairy, soy) are especially effective at triggering muscle building."
        ),
        "tags": ["protein", "muscle", "macros", "diet", "strength", "gym", "bodybuilding"]
    },
    {
        "title": "Carbohydrates: Types and Timing",
        "content": (
            "Carbohydrates are the body's primary energy source. They are classified as simple (sugar, honey, fruit juice) "
            "and complex (whole grains, oats, brown rice, sweet potato, roti). "
            "Complex carbs provide sustained energy and are rich in fiber. "
            "Daily needs: 45–65% of total calories. For a 2000 kcal diet, that's 225–325g. "
            "For weight loss, moderate carb intake (40–45% of calories) paired with adequate protein works well. "
            "For athletic performance, carbs should be consumed pre-workout (2–3 hours before) and post-workout. "
            "Low-GI carbs (oats, brown rice, quinoa, sweet potato) are better for blood sugar control. "
            "High-GI carbs (white rice, white bread, sugary drinks) cause rapid blood sugar spikes."
        ),
        "tags": ["carbs", "carbohydrates", "energy", "sugar", "fiber", "glycemic", "diabetes"]
    },
    {
        "title": "Dietary Fats: Good vs Bad",
        "content": (
            "Fats are essential for hormone production, vitamin absorption (A, D, E, K), and brain function. "
            "Daily needs: 20–35% of total calories. For a 2000 kcal diet, that's 44–78g. "
            "Healthy fats: olive oil, avocado, nuts (almonds, walnuts), seeds (flax, chia), fatty fish (salmon, mackerel). "
            "Unhealthy fats: trans fats (fried foods, margarine, packaged snacks), excessive saturated fat (red meat, butter). "
            "Omega-3 fatty acids (found in fish, walnuts, flaxseeds) reduce inflammation and support heart health. "
            "For Indian diets, use cold-pressed groundnut oil, mustard oil, or coconut oil in moderation. "
            "Ghee in small amounts (1–2 tsp/day) is fine and provides conjugated linoleic acid (CLA)."
        ),
        "tags": ["fats", "omega3", "cholesterol", "heart", "oil", "ghee", "healthy fats"]
    },
    {
        "title": "Fiber and Digestive Health",
        "content": (
            "Fiber is crucial for digestive health, blood sugar control, and cholesterol management. "
            "Daily recommendation: 25–30g for adults. Most people consume only 15g. "
            "Soluble fiber (oats, beans, apples, psyllium/isabgol) lowers cholesterol and stabilizes blood sugar. "
            "Insoluble fiber (whole wheat, vegetables, bran) promotes regular bowel movements. "
            "High-fiber Indian foods: rajma (15g/cup), chana (12g/cup), palak (4g/cup), guava (5g/fruit). "
            "Increase fiber gradually to avoid bloating. Always drink plenty of water with high-fiber foods. "
            "Probiotics (curd, buttermilk, fermented pickles) combined with fiber (prebiotics) optimize gut health."
        ),
        "tags": ["fiber", "digestion", "gut", "constipation", "prebiotics", "probiotics"]
    },

    # ── Vitamins & Minerals ─────────────────────────────────────────────
    {
        "title": "Essential Vitamins and Their Food Sources",
        "content": (
            "Vitamin A: carrots, sweet potato, spinach, mango — supports vision and immunity. "
            "Vitamin B12: eggs, dairy, fish, fortified cereals — critical for nerve function and red blood cells. "
            "Deficiency common in vegetarians/vegans. "
            "Vitamin C: amla (Indian gooseberry, 600mg/100g), guava, oranges, bell peppers — boosts immunity and iron absorption. "
            "Vitamin D: sunlight exposure (15–20 min daily), fortified milk, egg yolks, fatty fish. "
            "Deficiency is extremely common in India (70–80% of population). "
            "Vitamin E: almonds, sunflower seeds, spinach — antioxidant protecting cell membranes. "
            "Vitamin K: green leafy vegetables, broccoli — essential for blood clotting and bone health."
        ),
        "tags": ["vitamins", "micronutrients", "deficiency", "immunity", "b12", "vitamin d"]
    },
    {
        "title": "Minerals: Iron, Calcium, Zinc, and Magnesium",
        "content": (
            "Iron: men need 8mg/day, women 18mg/day. Sources: spinach, lentils, jaggery, red meat, liver. "
            "Pair iron with vitamin C (lemon, amla) for better absorption. Tea/coffee inhibit iron absorption. "
            "Calcium: 1000mg/day for adults. Sources: milk, curd, paneer, ragi (finger millet, 344mg/100g), sesame seeds. "
            "Zinc: 11mg/day (men), 8mg (women). Sources: pumpkin seeds, chickpeas, cashews, meat. "
            "Supports immunity and wound healing. "
            "Magnesium: 400mg/day. Sources: bananas, dark chocolate, spinach, almonds, pumpkin seeds. "
            "Deficiency causes muscle cramps, poor sleep, and anxiety."
        ),
        "tags": ["minerals", "iron", "calcium", "anemia", "bones", "zinc", "magnesium"]
    },

    # ── Weight Management ────────────────────────────────────────────────
    {
        "title": "Calorie Deficit for Weight Loss",
        "content": (
            "Weight loss requires a calorie deficit: consuming fewer calories than your body burns. "
            "A safe deficit is 500 kcal/day, leading to ~0.5 kg loss per week. "
            "TDEE (Total Daily Energy Expenditure) = BMR × Activity Factor. "
            "Activity factors: Sedentary (1.2), Lightly active (1.375), Moderately active (1.55), Very active (1.725). "
            "Never go below 1200 kcal/day (women) or 1500 kcal/day (men) without medical supervision. "
            "High-protein diets (25–30% of calories) preserve muscle during weight loss. "
            "Track food intake consistently — studies show tracking improves weight loss outcomes by 50%. "
            "Avoid crash diets: they slow metabolism and lead to muscle loss and nutrient deficiencies."
        ),
        "tags": ["weight loss", "calorie deficit", "tdee", "bmr", "diet", "fat loss"]
    },
    {
        "title": "Calorie Surplus for Weight/Muscle Gain",
        "content": (
            "Muscle gain requires a calorie surplus of 250–500 kcal/day above TDEE. "
            "Aim for 0.25–0.5 kg weight gain per week to minimize fat gain. "
            "Protein target: 1.6–2.2g per kg bodyweight. Spread across 4–6 meals. "
            "Carbs fuel workouts: aim for 4–7g per kg bodyweight. "
            "Healthy surplus foods: oats, banana shakes, peanut butter, rice, dal, chicken, eggs, paneer. "
            "Progressive overload in resistance training is essential — without it, excess calories become fat. "
            "Post-workout nutrition: 20–40g protein + fast carbs within 2 hours of training. "
            "Sleep 7–9 hours for optimal growth hormone release and muscle recovery."
        ),
        "tags": ["weight gain", "muscle gain", "calorie surplus", "bulk", "strength", "gym"]
    },
    {
        "title": "BMI and Body Composition",
        "content": (
            "BMI = weight(kg) / height(m)². Categories: Underweight (<18.5), Normal (18.5–24.9), "
            "Overweight (25–29.9), Obese (≥30). "
            "BMI is a rough screening tool — it doesn't distinguish muscle from fat. "
            "For Indian/Asian populations, health risks increase at lower BMI thresholds (≥23 is overweight). "
            "Body composition (muscle-to-fat ratio) is more useful than BMI alone. "
            "Waist circumference >90cm (men) or >80cm (women) indicates central obesity risk. "
            "Focus on building lean muscle through resistance training and adequate protein intake."
        ),
        "tags": ["bmi", "body composition", "obesity", "weight", "fat", "muscle"]
    },

    # ── Diet Types ───────────────────────────────────────────────────────
    {
        "title": "Vegetarian Diet Planning",
        "content": (
            "A well-planned vegetarian diet provides all essential nutrients. "
            "Key protein sources: paneer (18g/100g), dal/lentils (9g/100g), chole/chickpeas (19g/100g dry), "
            "soy chunks (52g/100g), tofu (8g/100g), milk (3.4g/100ml), curd (11g/cup). "
            "Combine cereals with pulses (rice + dal, roti + rajma) for complete amino acid profiles. "
            "Watch for deficiencies: Vitamin B12 (consider supplements), Iron (pair with vitamin C), "
            "Omega-3 (flaxseeds, walnuts). "
            "Indian vegetarian thali is naturally balanced: roti/rice + dal + sabzi + curd + salad."
        ),
        "tags": ["vegetarian", "veg", "plant-based", "protein", "indian diet"]
    },
    {
        "title": "Vegan Diet Essentials",
        "content": (
            "Vegan diets exclude all animal products including dairy and eggs. "
            "Critical supplements: Vitamin B12 (must supplement), Vitamin D, Omega-3 (algae-based). "
            "Protein sources: soy (tofu, tempeh, soy milk), legumes, quinoa, seitan, peanuts. "
            "Calcium: fortified plant milks, ragi, sesame seeds, broccoli. "
            "Iron: spinach, lentils, kidney beans, jaggery — always pair with vitamin C. "
            "A vegan Indian diet can include: chole, rajma, dal, soy chunks, tofu paneer, coconut milk curries, "
            "vegetable biryanis, peanut chutneys, ragi porridge."
        ),
        "tags": ["vegan", "plant-based", "dairy-free", "b12", "supplement"]
    },
    {
        "title": "Non-Vegetarian Diet Benefits and Guidelines",
        "content": (
            "Non-vegetarian diets provide complete proteins, heme iron, and B12 naturally. "
            "Lean protein sources: chicken breast (165 kcal/100g), fish (salmon 208 kcal/100g), eggs (155 kcal/100g). "
            "Limit red meat to 2–3 servings per week due to saturated fat and cancer risk. "
            "Processed meats (sausages, bacon, ham) should be minimized — linked to colorectal cancer. "
            "Fish is excellent: omega-3 from fatty fish (salmon, mackerel, sardine) supports heart and brain health. "
            "Eggs are a superfood: 6g protein, choline, lutein, and vitamin D per egg. "
            "For Indian non-veg diets, prefer grilled/tandoori over deep-fried preparations."
        ),
        "tags": ["non-vegetarian", "nonveg", "chicken", "fish", "eggs", "meat"]
    },

    # ── Health Conditions ────────────────────────────────────────────────
    {
        "title": "Diabetes Management Through Diet",
        "content": (
            "For Type 2 diabetes, diet is the most powerful intervention. "
            "Focus on low glycemic index (GI) foods: oats (GI 55), brown rice (GI 50), sweet potato (GI 54), "
            "whole wheat roti (GI 62), most vegetables (GI <20). "
            "Avoid high-GI foods: white rice (GI 73), white bread (GI 75), sugary drinks, maida-based foods. "
            "The plate method: 50% non-starchy vegetables, 25% lean protein, 25% complex carbs. "
            "Eat small, frequent meals (every 3–4 hours) to prevent blood sugar spikes. "
            "Cinnamon (1/2 tsp daily), fenugreek seeds (methi), and bitter gourd (karela) may help regulate blood sugar. "
            "Fiber intake should be ≥25g/day. Monitor carb portions — not all carbs are equal."
        ),
        "tags": ["diabetes", "blood sugar", "glycemic index", "type 2", "insulin"]
    },
    {
        "title": "PCOS Diet and Nutrition",
        "content": (
            "PCOS (Polycystic Ovary Syndrome) affects 1 in 10 women. Diet plays a crucial role in management. "
            "Anti-inflammatory foods: turmeric, ginger, fatty fish, leafy greens, berries, nuts. "
            "Reduce refined carbs and sugar — they worsen insulin resistance, a core PCOS issue. "
            "Protein at every meal helps stabilize blood sugar and reduce cravings. "
            "Recommended: 40% carbs, 30% protein, 30% fat. "
            "Inositol (found in citrus fruits, beans, nuts) may improve insulin sensitivity. "
            "Avoid: sugary drinks, white bread, pastries, deep-fried foods, excessive dairy (may worsen acne). "
            "Regular exercise (150 min/week) is as important as diet for PCOS management."
        ),
        "tags": ["pcos", "hormonal", "women", "insulin resistance", "anti-inflammatory"]
    },
    {
        "title": "Thyroid Diet Guidelines",
        "content": (
            "Hypothyroidism (underactive thyroid) slows metabolism. "
            "Iodine-rich foods: iodized salt, seaweed, dairy, eggs — essential for thyroid hormone production. "
            "Selenium-rich foods: Brazil nuts (1–2/day provides full daily need), eggs, tuna, mushrooms. "
            "Zinc-rich foods: pumpkin seeds, chickpeas, cashews — support thyroid function. "
            "Foods to limit with hypothyroidism: raw cruciferous vegetables (broccoli, cabbage, cauliflower) "
            "in excess — cooking reduces goitrogenic effects. Soy products in excess may interfere with medication absorption. "
            "Hyperthyroidism (overactive): limit iodine, increase calcium-rich foods. "
            "Take thyroid medication 30–60 minutes before eating for optimal absorption."
        ),
        "tags": ["thyroid", "hypothyroid", "hyperthyroid", "iodine", "selenium", "metabolism"]
    },
    {
        "title": "Heart Health and Cholesterol Management",
        "content": (
            "High cholesterol increases cardiovascular disease risk. "
            "LDL ('bad') cholesterol: reduce with soluble fiber (oats, beans, apples), omega-3 fats, and plant sterols. "
            "HDL ('good') cholesterol: increase with exercise, healthy fats (olive oil, nuts), and moderate alcohol. "
            "DASH diet is clinically proven: rich in fruits, vegetables, whole grains, lean protein, low-fat dairy. "
            "Limit sodium to <2300mg/day (ideally <1500mg for high BP). "
            "Heart-healthy Indian foods: oats upma, moong dal khichdi, grilled fish, flaxseed chutney, walnuts. "
            "Avoid: deep-fried snacks (samosa, pakora regularly), excessive ghee, coconut cream, organ meats. "
            "Potassium-rich foods help lower BP: bananas, coconut water, spinach, sweet potatoes, oranges."
        ),
        "tags": ["cholesterol", "heart", "blood pressure", "cardiovascular", "dash diet", "sodium"]
    },
    {
        "title": "Anemia Prevention and Iron-Rich Diet",
        "content": (
            "Iron-deficiency anemia is common in India, especially among women and vegetarians. "
            "Heme iron (better absorbed): red meat, liver, chicken, fish. "
            "Non-heme iron: spinach, lentils, chickpeas, jaggery (gur), dates, raisins, beetroot, pomegranate. "
            "Vitamin C dramatically improves iron absorption: squeeze lemon on dal, eat amla, guava, or oranges with meals. "
            "Iron absorption inhibitors: tea, coffee (wait 1 hour after meals), excess calcium, phytates. "
            "Cooking in cast-iron vessels increases iron content of food. "
            "Daily iron needs: men 8mg, women 18mg (27mg during pregnancy). "
            "Symptoms of deficiency: fatigue, pale skin, shortness of breath, cold hands/feet, brittle nails."
        ),
        "tags": ["anemia", "iron", "deficiency", "fatigue", "blood", "hemoglobin"]
    },
    {
        "title": "Digestive Health and Gut-Friendly Foods",
        "content": (
            "A healthy gut microbiome is linked to better immunity, mood, and weight management. "
            "Probiotics (beneficial bacteria): curd/yogurt, buttermilk (chaas), fermented pickles, idli/dosa batter. "
            "Prebiotics (food for good bacteria): bananas, garlic, onions, oats, asparagus. "
            "For bloating/gas: avoid carbonated drinks, eat slowly, reduce raw cruciferous vegetables. "
            "For acid reflux: avoid lying down after meals, reduce spicy/oily food, have smaller meals. "
            "For constipation: increase fiber (isabgol/psyllium husk), drink 8+ glasses of water, stay active. "
            "Ginger, ajwain (carom seeds), and fennel (saunf) are traditional Indian digestive aids."
        ),
        "tags": ["gut", "digestion", "bloating", "constipation", "probiotics", "acid reflux"]
    },

    # ── Hydration & Sleep ────────────────────────────────────────────────
    {
        "title": "Hydration and Water Intake",
        "content": (
            "Water is essential: makes up 60% of body weight and affects every body function. "
            "General recommendation: 35ml per kg of body weight. For a 70kg person, that's ~2.5 liters/day. "
            "Increase intake during exercise, hot weather, illness, and high-protein diets. "
            "Signs of dehydration: dark yellow urine, headaches, fatigue, dry mouth, dizziness. "
            "Ideal urine color: pale straw/light yellow. "
            "Water-rich foods: cucumber (96%), watermelon (92%), oranges (87%), curd, buttermilk. "
            "Coconut water is an excellent natural electrolyte drink (low calories, high potassium). "
            "Avoid excessive caffeine (>400mg/day) as it has mild diuretic effects. "
            "Drink water 30 minutes before meals to support digestion and reduce overeating."
        ),
        "tags": ["water", "hydration", "dehydration", "electrolytes", "fluid"]
    },
    {
        "title": "Sleep, Recovery, and Nutrition",
        "content": (
            "Sleep is critical for weight management, muscle recovery, and metabolic health. "
            "Adults need 7–9 hours of quality sleep per night. "
            "Sleep deprivation increases ghrelin (hunger hormone) and decreases leptin (satiety hormone), "
            "leading to increased appetite and weight gain. "
            "Foods that promote sleep: warm milk (tryptophan), almonds (magnesium), chamomile tea, "
            "tart cherries (melatonin), bananas (magnesium + potassium). "
            "Avoid large meals, caffeine (6+ hours before bed), and alcohol close to bedtime. "
            "Consistent sleep/wake times regulate circadian rhythm. "
            "Poor sleep increases cortisol (stress hormone), which promotes belly fat storage. "
            "Screen time before bed disrupts melatonin production — use night mode or stop screens 1 hour before sleep."
        ),
        "tags": ["sleep", "recovery", "insomnia", "melatonin", "cortisol", "rest"]
    },

    # ── Meal Planning & Timing ───────────────────────────────────────────
    {
        "title": "Meal Timing and Frequency",
        "content": (
            "Meal timing can influence metabolism, energy levels, and body composition. "
            "3 meals + 1–2 snacks is a good baseline for most people. "
            "Don't skip breakfast — it kickstarts metabolism and prevents overeating later. "
            "Ideal meal spacing: every 3–4 hours to maintain stable blood sugar. "
            "Pre-workout meal (2–3 hours before): complex carbs + moderate protein (e.g., banana + peanut butter toast). "
            "Post-workout meal (within 2 hours): protein + carbs (e.g., eggs + toast, or protein shake + banana). "
            "Evening meals should be lighter — heavy dinners impair sleep quality and digestion. "
            "Intermittent fasting (16:8 pattern) can help with weight loss but isn't necessary for everyone. "
            "Listen to hunger cues — forced eating schedules aren't better than intuitive eating for most people."
        ),
        "tags": ["meal timing", "frequency", "breakfast", "intermittent fasting", "pre-workout", "post-workout"]
    },
    {
        "title": "Indian Diet Meal Planning",
        "content": (
            "A balanced Indian thali naturally covers all food groups. "
            "Standard composition: 2 rotis/1 cup rice + 1 cup dal/curry + 1 cup sabzi + curd + salad. "
            "Approximate calories: breakfast 300–400 kcal, lunch 500–600 kcal, dinner 400–500 kcal, snacks 200–300 kcal. "
            "Healthy breakfast options: poha (250 kcal), upma (280 kcal), idli-sambar (300 kcal), "
            "oats porridge (250 kcal), besan chilla (200 kcal), dalia (220 kcal). "
            "Healthy lunch: roti + dal + sabzi (500 kcal), khichdi + raita (400 kcal), "
            "rajma chawal (550 kcal), curd rice + pickle (350 kcal). "
            "Healthy snacks: roasted chana (120 kcal/30g), makhana (90 kcal/30g), fruit + nuts (150 kcal). "
            "Regional cuisines (South Indian, Punjabi, Bengali, etc.) all have healthy traditional options."
        ),
        "tags": ["indian diet", "thali", "meal plan", "roti", "dal", "rice", "indian food"]
    },

    # ── Food Allergies ───────────────────────────────────────────────────
    {
        "title": "Managing Food Allergies",
        "content": (
            "Common food allergens: milk/dairy, eggs, peanuts, tree nuts, wheat/gluten, soy, fish, shellfish. "
            "For dairy allergy: use fortified plant milks (almond, soy, oat), ragi for calcium, tofu for protein. "
            "For gluten intolerance/celiac: avoid wheat, barley, rye. Safe grains: rice, jowar, bajra, ragi, amaranth. "
            "For nut allergy: seeds (sunflower, pumpkin, flax) are usually safe alternatives. "
            "For egg allergy: use flax egg (1 tbsp ground flax + 3 tbsp water) in baking. "
            "Always read food labels for hidden allergens. Cross-contamination is a real risk in restaurants. "
            "Keep an allergy card in your wallet listing your allergies. "
            "Epinephrine auto-injectors should be carried by those with severe (anaphylactic) allergies."
        ),
        "tags": ["allergy", "allergies", "gluten", "dairy", "nuts", "intolerance", "celiac"]
    },

    # ── Supplements ──────────────────────────────────────────────────────
    {
        "title": "Common Nutritional Supplements",
        "content": (
            "Supplements should complement, not replace, a balanced diet. "
            "Whey protein: convenient post-workout, 25g protein per scoop. Not necessary if diet is adequate. "
            "Creatine monohydrate: 3–5g/day, proven to increase strength and muscle mass. Safe for long-term use. "
            "Vitamin D3: 1000–2000 IU/day if deficient (very common in India). Get blood test to confirm. "
            "Vitamin B12: essential supplement for vegetarians/vegans. 1000mcg/week or daily sublinguals. "
            "Omega-3 (fish oil): 1000–2000mg/day for heart health. Vegans use algae-based DHA/EPA. "
            "Multivitamins: useful as insurance but cannot fix a poor diet. "
            "Iron supplements: only take if prescribed — excess iron is toxic. "
            "Probiotics: consider after antibiotics or for persistent gut issues."
        ),
        "tags": ["supplements", "whey", "creatine", "vitamin d", "b12", "omega3", "fish oil"]
    },

    # ── Specific Nutrient Questions ──────────────────────────────────────
    {
        "title": "Understanding Calories and Energy Balance",
        "content": (
            "A calorie is a unit of energy. 1 kcal = the energy needed to raise 1kg of water by 1°C. "
            "BMR (Basal Metabolic Rate) is calories burned at rest — accounts for 60–70% of daily expenditure. "
            "Mifflin-St Jeor equation: Men: 10×weight(kg) + 6.25×height(cm) - 5×age - 5. "
            "Women: 10×weight(kg) + 6.25×height(cm) - 5×age - 161. "
            "TDEE = BMR × activity multiplier. This is your maintenance calories. "
            "To lose 0.5kg/week: eat 500 kcal below TDEE. To gain 0.5kg/week: eat 500 kcal above. "
            "Macronutrient calories: Protein = 4 kcal/g, Carbs = 4 kcal/g, Fat = 9 kcal/g, Alcohol = 7 kcal/g. "
            "Not all calories are equal — 200 kcal of almonds is more satiating than 200 kcal of candy."
        ),
        "tags": ["calories", "energy", "bmr", "tdee", "metabolism", "energy balance"]
    },
    {
        "title": "Healthy Snacking Options",
        "content": (
            "Smart snacking prevents overeating at meals and maintains stable blood sugar. "
            "Protein-rich snacks: boiled eggs, paneer cubes, roasted chickpeas, Greek yogurt, peanut butter. "
            "Fiber-rich snacks: fruit (apple, guava, pear), makhana (foxnuts), sprouts chaat, dhokla. "
            "Healthy fat snacks: mixed nuts (20–30g), seeds (pumpkin, sunflower), dark chocolate (70%+, 1–2 squares). "
            "Indian snack options under 150 kcal: 1 cup buttermilk (40 kcal), 30g makhana (90 kcal), "
            "1 small banana (90 kcal), 1 cup sprout salad (120 kcal), 2 khakhra (120 kcal). "
            "Avoid: packaged chips, biscuits, namkeens (high in trans fats and sodium), sugary juices. "
            "Time snacks between main meals — mid-morning (10–11 AM) and mid-afternoon (3–4 PM)."
        ),
        "tags": ["snacks", "snacking", "healthy snacks", "mid-meal", "makhana", "nuts"]
    },
    {
        "title": "Post-Workout Nutrition",
        "content": (
            "After exercise, the body needs to replenish glycogen stores and repair muscle tissue. "
            "The 'anabolic window' is roughly 2 hours post-workout — protein synthesis is elevated. "
            "Ideal post-workout: 20–40g protein + 40–80g carbs. "
            "Quick options: whey protein shake + banana, eggs + toast, paneer sandwich, chicken + rice. "
            "Indian options: sprouts chaat + buttermilk, egg bhurji + 2 rotis, curd + muesli, soy chunks curry. "
            "Hydration: drink 500ml water for every 0.5kg lost during exercise. "
            "For weight loss: keep post-workout meal moderate (focus on protein, moderate carbs). "
            "For muscle gain: larger post-workout meal with ample carbs to drive insulin and recovery."
        ),
        "tags": ["post-workout", "workout", "recovery", "gym", "exercise", "protein", "anabolic"]
    },

    # ── Emotional & Behavioral ───────────────────────────────────────────
    {
        "title": "Emotional Eating and Mindful Eating",
        "content": (
            "Emotional eating uses food to cope with stress, boredom, sadness, or anxiety — not physical hunger. "
            "Signs: eating when not hungry, eating rapidly, guilt after eating, craving specific comfort foods. "
            "HALT method: before eating, ask — am I Hungry, Angry, Lonely, or Tired? "
            "Mindful eating practices: eat without screens, chew 20–30 times per bite, taste and enjoy each meal. "
            "Eating slowly (20+ minutes per meal) allows satiety hormones to signal fullness. "
            "Keep trigger foods out of the house. Replace emotional eating with: walking, journaling, calling a friend. "
            "No food is 'good' or 'bad' — restriction often leads to binge cycles. Practice moderation instead. "
            "Professional support (therapist, dietitian) is valuable for persistent emotional eating patterns."
        ),
        "tags": ["emotional eating", "mindful eating", "stress eating", "binge", "mental health"]
    },
    {
        "title": "Portion Control Strategies",
        "content": (
            "Portion control is key to managing calorie intake without strict calorie counting. "
            "Hand-based portions: palm = protein serving, fist = carb serving, thumb = fat serving, "
            "two cupped hands = vegetable serving. "
            "Use smaller plates (9-inch instead of 12-inch) — studies show this reduces intake by 20–25%. "
            "Pre-portion snacks instead of eating from packages. "
            "Restaurant portions are typically 2–3x recommended serving sizes — consider sharing or boxing half. "
            "Fill half your plate with vegetables, quarter with protein, quarter with whole grains. "
            "Drinking water before meals reduces intake by 75–90 calories per meal. "
            "Serving sizes in India: 1 roti = ~80 kcal, 1 cup cooked rice = ~200 kcal, 1 cup dal = ~150 kcal."
        ),
        "tags": ["portion control", "serving size", "plate method", "mindful eating", "overeating"]
    },

    # ── Special Topics ───────────────────────────────────────────────────
    {
        "title": "Blood Pressure and DASH Diet",
        "content": (
            "The DASH diet (Dietary Approaches to Stop Hypertension) is clinically proven to lower blood pressure. "
            "Key principles: high potassium, calcium, magnesium; low sodium, saturated fat, cholesterol. "
            "Daily sodium limit: <2300mg (ideally <1500mg for hypertension). 1 tsp salt = ~2300mg sodium. "
            "Potassium-rich foods: bananas, coconut water, sweet potatoes, spinach, oranges, yogurt. "
            "Calcium sources: milk, curd, paneer, ragi, fortified plant milks. "
            "Magnesium sources: dark leafy greens, nuts, seeds, bananas, dark chocolate. "
            "Indian DASH-friendly meals: dal with minimum salt, grilled fish, vegetable raita, "
            "cucumber salad, steamed idli, ragi dosa, moong dal soup."
        ),
        "tags": ["blood pressure", "hypertension", "dash diet", "sodium", "potassium", "heart"]
    },
    {
        "title": "Low Blood Pressure Management",
        "content": (
            "Low blood pressure (hypotension) causes dizziness, fainting, and fatigue. "
            "Increase salt intake slightly (if not contraindicated). Drink more fluids — aim for 3+ liters/day. "
            "Eat small, frequent meals to prevent post-meal drops in blood pressure. "
            "Avoid standing up too quickly. Compression stockings can help. "
            "Caffeine (1–2 cups coffee/day) can temporarily raise blood pressure. "
            "Foods that help: salted nuts, pickles (in moderation), olives, cheese, beetroot juice. "
            "Avoid alcohol — it lowers blood pressure further. "
            "Stay hydrated during hot weather and exercise. Coconut water with a pinch of salt works well."
        ),
        "tags": ["low blood pressure", "hypotension", "dizziness", "fainting", "salt"]
    },
]
