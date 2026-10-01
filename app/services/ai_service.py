"""
CreatorOS AI Service Engine (Enhanced v2.0)
Provides specialized AI generation algorithms for 7 Creator Tools:
1. Caption Generator
2. Script Generator
3. Hashtag Generator
4. Bio Generator
5. Rewrite Content
7. SEO Keywords Generator

Each tool uses randomized templates, dynamic structure, and varied output
to ensure every generation feels unique and fresh.
"""

import random
import re
from difflib import get_close_matches
from datetime import datetime

PROMPT_TEMPLATES = [
    {
        "id": "tpl_viral_hook",
        "name": "Viral Reel/TikTok Hook",
        "category": "Script & Video",
        "prompt": "Write 3 scroll-stopping opening hooks for a video about [Topic] targeting [Target Audience]."
    },
    {
        "id": "tpl_insta_story",
        "name": "High-Converting Instagram Caption",
        "category": "Captions",
        "prompt": "Create an engaging Instagram caption about [Topic] with a strong Call-To-Action (CTA) asking followers to save & share."
    },
    {
        "id": "tpl_youtube_intro",
        "name": "YouTube Video Intro (First 30 Seconds)",
        "category": "Script & Video",
        "prompt": "Draft a high-retention YouTube intro script introducing [Topic] and explaining why watching till the end is essential."
    },
    {
        "id": "tpl_linkedin_thought",
        "name": "LinkedIn Thought Leadership Post",
        "category": "Rewriting & SEO",
        "prompt": "Rewrite the following key insight into a professional LinkedIn post structured with short lines and bullet points: [Insight/Idea]."
    },
    {
        "id": "tpl_bio_creator",
        "name": "High-Impact Social Media Bio",
        "category": "Bio & Branding",
        "prompt": "Create 3 punchy, emoji-enhanced bio variations for a [Niche/Industry] creator emphasizing value proposition and link in bio."
    },
    {
        "id": "tpl_thread_post",
        "name": "Twitter/X Thread Starter",
        "category": "Captions",
        "prompt": "Write a viral Twitter/X thread (5 tweets) breaking down [Topic] with a hook, key insights, and a call-to-action."
    },
    {
        "id": "tpl_seo_blog",
        "name": "SEO Blog Outline + Keywords",
        "category": "Rewriting & SEO",
        "prompt": "Generate an SEO-optimized blog post outline for [Topic] including H2/H3 headings, target keywords, and a meta description."
    },
    {
        "id": "tpl_podcast_script",
        "name": "Podcast Episode Intro Script",
        "category": "Script & Video",
        "prompt": "Write a 60-second podcast intro script for an episode about [Topic] that hooks listeners and teases the key takeaway."
    }
]

class AIService:

    @staticmethod
    def clean_generated_output(text):
        """Remove markdown asterisks/decorative formatting from visible AI output."""
        text = str(text or '')
        text = text.replace('**', '').replace('__', '')
        text = re.sub(r'(?m)^\s*[-_=]{4,}\s*$', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return text

    @staticmethod
    def _topic_profile(topic):
        t=(topic or '').lower()
        profiles=[
            (('hotel','hospitality','resort','front office','housekeeping'), {'angles':['guest experience','front-office operations','housekeeping coordination','revenue and occupancy','service recovery'],'details':['smooth check-in and check-out','room readiness','handling guest complaints','upselling without being pushy','coordination between departments'],'hook':'A hotel can have beautiful rooms and still lose guests because the experience between those rooms is broken.'}),
            (('iphone','ios','apple phone','iphone 15','iphone 16','iphone 17'), {'angles':['camera workflow','battery habits','privacy settings','productivity shortcuts','ecosystem features'],'details':['camera controls','battery health','Focus modes','privacy permissions','iCloud and device continuity'],'hook':'Most people use only a small fraction of what their iPhone can actually do.'}),
            (('ai','artificial intelligence','chatgpt','machine learning','generative ai'), {'angles':['real use cases','prompt design','limitations','workflow automation','responsible use'],'details':['clear instructions','verification of outputs','repeatable workflows','privacy-aware use','human review'],'hook':'The useful AI skill is not asking for more words; it is asking for the right result.'}),
            (('fitness','workout','gym','weight loss','muscle'), {'angles':['consistency','training technique','recovery','nutrition basics','progress tracking'],'details':['progressive overload','sleep and recovery','form before load','protein and balanced meals','measurable weekly goals'],'hook':'The workout that looks impressive is not automatically the workout that gets results.'}),
            (('travel','tourism','trip','vacation','itinerary'), {'angles':['planning','budget control','local experiences','transport','common mistakes'],'details':['realistic travel time','neighborhood choice','weather backup plans','local transport','buffer time'],'hook':'A great trip is rarely about squeezing in more places; it is about making each move count.'}),
            (('coding','programming','python','java','javascript','software development'), {'angles':['problem solving','debugging','architecture','practice','shipping projects'],'details':['breaking problems into smaller parts','reading error messages','writing small test cases','choosing simple designs','building before overengineering'],'hook':'Most beginners do not need another tutorial; they need to get better at solving one small problem at a time.'}),
            (('marketing','social media','content marketing','branding','digital marketing'), {'angles':['audience pain points','positioning','content hooks','distribution','measurement'],'details':['clear positioning','specific audience problems','strong opening lines','consistent distribution','useful performance signals'],'hook':'Marketing gets easier when you stop trying to reach everyone and start solving one audience problem clearly.'}),
            (('fashion','clothing','outfit','style','beauty','skincare'), {'angles':['fit','routine','styling','product choice','personal expression'],'details':['fit and proportions','skin or fabric needs','occasion matching','ingredient or material awareness','repeatable styling combinations'],'hook':'Good style is less about owning more and more about knowing what actually works together.'}),
            (('artificial flower','artificial flowers','fake flower','fake flowers','silk flower','silk flowers','faux flower','faux flowers'), {'angles':['realistic styling','home decoration','colour combinations','maintenance','seasonal arrangements'],'details':['choosing realistic textures','matching flowers with the room','balancing colours and height','dust-free maintenance','creating arrangements that look natural'],'hook':'Artificial flowers can look surprisingly natural when the arrangement, colour and placement are right.'}),
            (('coffee shop','cafe','café','coffeehouse','coffee house'), {'angles':['ambience','coffee experience','menu choices','customer experience','quiet work spaces'],'details':['the aroma of freshly brewed coffee','warm lighting and comfortable seating','signature drinks and pastries','friendly service','the feeling of having a quiet moment'],'hook':'A good coffee shop is not only about coffee; it is about the feeling you carry out with you.'}),
            (('eye','eyes','gaze','look in your eyes'), {'angles':['mystery','emotion','unspoken feelings','memory','human connection'],'details':['what a gaze can reveal','feelings left unspoken','memories carried in a look','the silence between two people','the mystery behind a pair of eyes'],'hook':'Sometimes eyes say what words are too afraid to admit.'}),
        ]
        for keys, profile in profiles:
            if any(k in t for k in keys): return profile
        clean=re.sub(r'\s+',' ',(topic or 'your topic')).strip(' .,!?:;') or 'your topic'
        return {'angles':['what makes it interesting','key characteristics','real-life use','common misconceptions','practical ideas'],'details':[f'what makes {clean} distinctive',f'the details people often overlook about {clean}',f'a real-life example involving {clean}',f'a practical way to explore or use {clean}',f'why {clean} matters in everyday life'],'hook':f'There is more to {clean} than the first thing people notice.'}

    @staticmethod
    def generate_caption(topic, platform="Instagram", tone="Engaging", previous_output="", variation=0):
        """Generate a genuinely topic-specific caption; regeneration changes the angle."""
        topic=re.sub(r'\s+',' ',(topic or 'Content Creation')).strip(' .,!?:;') or 'Content Creation'
        platform=platform or 'Instagram'
        tone=tone or 'Engaging'
        profile=AIService._topic_profile(topic)
        hooks=AIService._creative_hooks(
            topic,
            funny='witty' in tone.lower() or 'funny' in tone.lower(),
            emotional='emotional' in tone.lower() or 'heartfelt' in tone.lower(),
            professional='professional' in tone.lower() or 'educational' in tone.lower(),
        )
        d=list(profile['details'])
        angles=list(profile['angles'])
        rng=random.Random(hash((topic.lower(),platform.lower(),tone.lower(),int(variation))) ^ random.randrange(1,10_000_000))
        rng.shuffle(d); rng.shuffle(angles)

        candidates=[]
        for i in range(5):
            hook = profile['hook'] if i == 0 else hooks[i % len(hooks)]
            detail1=d[i % len(d)]
            detail2=d[(i+1) % len(d)]
            angle=angles[i % len(angles)]
            cta=[
                f"What does {topic} make you feel or notice?",
                f"Which part of {topic} stands out to you?",
                f"Would you look at {topic} differently after noticing this?",
                f"Save this if you love {topic}.",
                f"Tell me your favourite thing about {topic}."
            ][i]
            candidates.append(
                f"{hook}\n\n"
                f"There is something interesting about {topic} when you look at {angle}. "
                f"From {detail1} to {detail2}, the small details are what make the experience memorable.\n\n"
                f"{cta}\n\n"
                f"#{re.sub(r'[^A-Za-z0-9]', '', topic.title()) or 'Content'} #{re.sub(r'[^A-Za-z0-9]', '', angle.title()) or 'Ideas'}"
            )

        previous=(previous_output or '').strip().lower()
        if previous:
            def overlap(a,b):
                aa=set(re.findall(r'\b\w+\b',a.lower())); bb=set(re.findall(r'\b\w+\b',b.lower()))
                return len(aa&bb)/max(1,len(aa|bb))
            fresh=[x for x in candidates if overlap(x,previous)<0.60]
            if fresh: candidates=fresh
        return rng.choice(candidates), 0

    @staticmethod
    def generate_script(topic, video_format="Reels / Shorts", length="60 Seconds", audience="General Creators", previous_output="", variation=0):
        """Generate a usable script around the exact topic supplied by the user."""
        topic = re.sub(r'\s+', ' ', (topic or 'your topic')).strip(' .,!?:;') or 'your topic'
        fmt = video_format or "Reels / Shorts"
        aud = audience or "General Creators"
        seconds = re.search(r'(\d+)', str(length or '60'))
        duration = int(seconds.group(1)) if seconds else 60

        # The generator is offline, so it must not invent facts about an unknown topic.
        # It builds a complete script around the user's exact subject and asks for
        # concrete examples rather than pretending they are verified facts.
        subject = topic[0].upper() + topic[1:] if topic else topic
        seed = hash((topic.lower(), fmt.lower(), int(variation))) & 0xffffffff
        rng = random.Random(seed)

        openings = [
            f"Most people hear about {topic}, but the real question is what you can actually do with it.",
            f"If {topic} is something you're trying to understand, start with this.",
            f"Let's make {topic} easy to understand in the next few seconds.",
            f"Here is a practical way to think about {topic} without overcomplicating it."
        ]
        hooks = [
            f"What is {topic} really about?",
            f"Why does {topic} matter?",
            f"How would you explain {topic} to a beginner?",
            f"What should you know about {topic} before you start?"
        ]
        close_lines = [
            f"That is the practical idea behind {topic}. Save this if you want to come back to it.",
            f"Start with one part of {topic}, apply it, and then build from there.",
            f"If you are learning {topic}, keep this framework and use it as your starting point."
        ]

        if "youtube" in fmt.lower() or "long" in fmt.lower() or duration >= 180:
            result = f"""🎬 {subject} — FULL VIDEO SCRIPT

OPENING
"{rng.choice(openings)}"

INTRODUCTION
"Hi everyone. Today we're looking at {topic}. I’ll break it down in a way that is useful for {aud}, without filling the video with unnecessary jargon."

SECTION 1 — THE CORE IDEA
"First, define the topic clearly. {topic} is the subject we are focusing on, so begin by explaining what it means in your own words and what problem or purpose it addresses."

SECTION 2 — HOW TO EXPLAIN IT
"Next, take the main idea and break it into two or three smaller points. For each point, give one concrete example that matches your actual experience, project, product, or source material."

SECTION 3 — PRACTICAL EXAMPLE
"Now show {topic} in a real situation. Walk the viewer through what happens first, what happens next, and what result they should look for. Avoid adding facts you have not verified."

SECTION 4 — COMMON MISTAKE
"A common content mistake is trying to explain everything at once. Keep the explanation focused on the one outcome this video promises."

TAKEAWAY
"If you remember only three things about {topic}: understand the core idea, show a concrete example, and give the viewer one useful next step."

OUTRO
"{rng.choice(close_lines)}"
"""
        elif "podcast" in fmt.lower():
            result = f"""🎙️ {subject} — PODCAST SCRIPT

OPEN
"{rng.choice(openings)}"

WELCOME
"Today we're talking about {topic}. Instead of giving you a random list of points, let's understand the subject from a practical point of view."

MAIN DISCUSSION
"To start, what exactly is {topic}? Explain the idea in plain language and connect it to a situation your audience already understands."

DEEPER POINT
"The interesting part is how {topic} works in practice. Take one real example and walk through the decision, process, or experience step by step."

AUDIENCE QUESTION
"{rng.choice(hooks)} What would you want a beginner to understand first?"

PRACTICAL TAKEAWAY
"The goal is not to make {topic} sound complicated. The goal is to make the next step obvious."

CLOSING
"{rng.choice(close_lines)}"
"""
        else:
            # Short-form script with actual spoken lines and visual cues.
            result = f"""🎬 {subject} — {fmt} SCRIPT

0:00–0:05 — HOOK
🗣️ "{rng.choice(openings)}"
🎥 Visual: Show the topic immediately on screen.

0:05–0:12 — SETUP
🗣️ "Today, we're breaking down {topic} and focusing on what a beginner actually needs to understand."
🎥 Visual: Display the topic and the one question this video will answer.

0:12–0:35 — VALUE
🗣️ "Start with the basic idea of {topic}. Then break it into the main steps or parts. For each part, show one real example from your own project, experience, product, or verified source."
🎥 Visual: Use 2–3 short examples, screenshots, clips, or labels that match the explanation.

0:35–0:50 — PRACTICAL POINT
🗣️ "The biggest mistake is trying to explain everything at once. Keep the video focused on one useful takeaway, then show the viewer what to do next."
🎥 Visual: Show a simple before-and-after, checklist, or demonstration.

0:50–0:60 — CTA
🗣️ "{rng.choice(close_lines)}"
🎥 Visual: Show the final takeaway and a simple Save/Follow prompt.
"""
        # On regeneration, change the hook/structure enough to avoid a duplicate.
        if previous_output:
            result = result.replace("THE CORE IDEA", "THE CORE IDEA — FRESH ANGLE")
        return result.strip(), len(result.split()) * 2

    @staticmethod
    def generate_hashtags(topic, platform="Instagram", niche="", previous_output="", variation=0):
        """Generate short, natural hashtags anchored to the supplied topic."""
        topic=re.sub(r'\s+',' ',(topic or 'Content')).strip(' .,!?:;') or 'Content'
        platform=platform or 'Instagram'
        niche=re.sub(r'\s+',' ',(niche or '').strip())
        low=topic.lower()
        base_words=[w for w in re.findall(r'[A-Za-z0-9]+',topic) if len(w)>1]
        base=''.join(w.title() for w in base_words) or 'Content'

        topic_sets=[
            (('graphic design','design'), ['#GraphicDesign','#GraphicDesignTips','#DesignInspiration','#DesignTips','#VisualDesign','#CreativeDesign','#Typography','#DesignIdeas']),
            (('artificial flower','artificial flowers','fake flower','fake flowers','silk flower','faux flower'), ['#ArtificialFlowers','#FlowerArrangement','#HomeDecor','#FloralDecor','#InteriorDecor','#FlowerDecor','#HomeStyling','#DecorIdeas']),
            (('coffee shop','cafe','café','coffeehouse'), ['#CoffeeShop','#CafeVibes','#CoffeeLovers','#CoffeeCulture','#CafeLife','#CoffeeTime','#CoffeeExperience','#CafeAesthetic']),
            (('eye','eyes','gaze'), ['#Eyes','#EyeContact','#EyesSpeak','#DeepGaze','#ExpressiveEyes','#EyeAesthetics','#SilentExpression','#EmotionalEyes']),
            (('iphone','ios','apple phone'), ['#iPhone','#iPhoneTips','#iPhonePhotography','#iPhoneTricks','#AppleTips','#iOS','#MobilePhotography','#TechTips']),
            (('fitness','workout','gym'), ['#Fitness','#WorkoutTips','#GymLife','#FitnessJourney','#Training','#HealthyHabits','#WorkoutMotivation','#FitnessGoals']),
            (('travel','tourism','vacation','trip'), ['#Travel','#TravelTips','#TravelIdeas','#TravelGuide','#Vacation','#TravelPlanning','#ExploreMore','#TravelInspiration']),
            (('fashion','outfit','clothing','style'), ['#Fashion','#StyleTips','#OutfitIdeas','#FashionStyle','#PersonalStyle','#StyleInspiration','#WardrobeIdeas','#FashionInspo']),
        ]
        selected=[]
        for keys,tags in topic_sets:
            if any(k in low for k in keys):
                selected=list(tags)
                break

        if not selected:
            selected=[
                f'#{base}', f'#{base}Tips', f'#{base}Ideas', f'#{base}Guide',
                f'#{base}Inspiration', f'#{base}Community', f'#{base}Daily', f'Learn{base}'
            ]
            # Add short topic words rather than entire sentences as hashtags.
            selected.extend('#'+w.title() for w in base_words[:4])

        platform_tag={'Instagram':'#Instagram','TikTok':'#TikTok','YouTube':'#YouTube','Twitter / X':'#TwitterX','YouTube Shorts':'#YouTubeShorts'}.get(platform,'#SocialMedia')
        if platform_tag not in selected: selected.append(platform_tag)

        if niche:
            niche_words=[w for w in re.findall(r'[A-Za-z0-9]+',niche) if len(w)>2]
            if niche_words:
                niche_tag='#'+''.join(w.title() for w in niche_words[:3])
                selected.append(niche_tag)

        # De-duplicate while preserving order and keep regeneration fresh.
        selected=list(dict.fromkeys(selected))
        previous=set(re.findall(r'#[A-Za-z0-9]+',previous_output or ''))
        fresh=[tag for tag in selected if tag.lower() not in {x.lower() for x in previous}]
        pool=fresh if len(fresh)>=6 else selected
        rng=random.Random(hash((low,platform.lower(),niche.lower(),int(variation))) ^ random.randrange(1,10_000_000))
        rng.shuffle(pool)
        focused=pool[:10]
        result=(f"{topic} — Hashtag Strategy\n\n"
                f"Platform: {platform}\n\n"
                f"Relevant hashtags\n{' '.join(focused)}\n\n"
                f"These tags are based on the exact topic and platform, not an unrelated category.")
        return result, len(result.split())*2

    @staticmethod
    def generate_bio(niche="Digital Marketing", personality="Professional yet Witty", cta="Download Free Guide", previous_output="", variation=0):
        niche=re.sub(r'\s+',' ',(niche or 'Content Creator')).strip(' .,!?:;') or 'Content Creator'
        cta=re.sub(r'\s+',' ',(cta or 'Follow for more')).strip()
        rng=random.Random(hash((niche.lower(),personality.lower(),cta.lower(),int(variation))) ^ random.randrange(1,10_000_000))
        options=[
            f'''**BIO 1 — Clear & Useful**
{niche} creator | Making complex ideas easier to use.
Practical lessons, honest experiments & useful resources.
👇 {cta}''',
            f'''**BIO 2 — Bold & Short**
{niche} • Ideas without the fluff.
Learn it → test it → share it.
✨ {cta}''',
            f'''**BIO 3 — Personal Brand**
Learning, building and creating around {niche}.
Real examples. Simple explanations. Fresh perspectives.
→ {cta}''',
            f'''**BIO 4 — Community Focused**
Helping curious people understand {niche}.
Tips • stories • practical takeaways
Join the conversation ↓
{cta}''',
            f'''**BIO 5 — Minimal**
{niche} creator & educator.
Clear ideas. Better content. Real practice.
{cta} ↓'''
        ]
        rng.shuffle(options)
        previous=(previous_output or '').strip().lower()
        chosen=next((x for x in options if x.lower()!=previous),options[0])
        rest=[x for x in options if x!=chosen][:2]
        result='\n\n'.join([chosen]+rest)
        return result, len(result.split())*2

    @staticmethod
    def rewrite_content(content, goal_style="Engaging & Persuasive"):
        """Rewrite the supplied text instead of echoing it back.

        The visible result contains only the rewritten copy. It deliberately avoids
        fake improvement percentages, timestamps, duplicated originals and canned
        'this has been changed' language.
        """
        source = re.sub(r'\s+', ' ', (content or '').strip())
        if not source or source.lower() == "sample text":
            source = "Content creation is important for growing online. You should post regularly and engage with your audience."

        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', source) if s.strip()]
        # Remove accidental report labels from an earlier CreatorOS result.
        source = re.sub(r'(?is)^(?:content rewrite|original text|rewritten version)\s*:?', '', source).strip()
        source = re.sub(r'(?is)generated:\s*\S+.*?(?=content creation|you |we |i )', '', source).strip() or source

        style = (goal_style or "Engaging & Persuasive").lower()
        persuasive = "persuasive" in style or "engaging" in style
        concise = "concise" in style or "punchy" in style
        formal = "formal" in style or "executive" in style

        # Phrase-level rewrites change wording without inventing facts.
        replacements = [
            (r'\bvery important\b', 'especially important'),
            (r'\bimportant\b', 'valuable'),
            (r'\bhelp\b', 'make it easier'),
            (r'\bhelps\b', 'makes it easier'),
            (r'\bgood\b', 'effective'),
            (r'\bbad\b', 'weak'),
            (r'\bthings\b', 'ideas'),
            (r'\bpeople\b', 'readers'),
            (r'\busing\b', 'working with'),
            (r'\bshould\b', 'can'),
            (r'\bneed to\b', 'can'),
            (r'\bnow\b', 'today'),
            (r'\bregularly\b', 'consistently'),
            (r'\bsimple\b', 'straightforward'),
        ]
        transformed=[]
        for s in sentences:
            line=s
            for pattern,repl in replacements:
                line=re.sub(pattern,repl,line,flags=re.I)
            line=line.strip()
            if line:
                transformed.append(line)

        if not transformed:
            transformed=[source]

        # Vary the structure on repeated calls.
        if len(transformed)>1:
            shift = random.randrange(len(transformed))
            transformed = transformed[shift:] + transformed[:shift]

        if concise:
            body = ' '.join(transformed)
            words = body.split()
            if len(words)>70:
                body=' '.join(words[:70]).rstrip('.,!?') + '.'
        elif formal:
            body = ' '.join(transformed)
            body = re.sub(r'^(And|But|So)\s+', '', body, flags=re.I)
            body = " ".join([body])
        else:
            bridges=["Here is the clearer way to look at it: ", "The main point is simple: ", "What matters most is this: "]
            body = random.choice(bridges) + ' '.join(transformed)
            if persuasive:
                body += " The message stays focused on the original idea while making the wording more direct."

        # Ensure the output is not effectively identical to the input.
        if re.sub(r'\W+', ' ', body.lower()).strip() == re.sub(r'\W+', ' ', source.lower()).strip():
            body = "A clearer way to express the same idea is: " + body

        return body.strip(), len(body.split()) * 2

    @staticmethod
    def check_grammar(text):
        """Offline grammar + spelling correction with an explicit before/after diff.

        No fake confidence/percentage score is returned. High-confidence grammar rules
        handle common sentence errors and TextBlob is used as an additional spelling
        pass when available. Unknown names/technical words are left alone.
        """
        if not text or not text.strip():
            return "Please enter text to check.", 0

        original = re.sub(r"\s+", " ", text.strip())
        fixed = original
        corrections = []

        phrase_rules = [
            (r"\bi\s+gone\b", "I went", "Past tense"),
            (r"\b(i|we|they|you)\s+go\s+home\s+(eat|study|work|sleep|rest|play)\b", lambda m: f"{m.group(1).capitalize()} go home to {m.group(2)}", "Infinitive after destination phrase"),
            (r"\b(i|we|they|you)\s+go\s+(school|college|office|home)\b", lambda m: f"{m.group(1).capitalize()} go to {m.group(2)}" if m.group(2).lower() != 'home' else f"{m.group(1).capitalize()} go home", "Preposition/destination"),
            (r"\bi\s+am\s+gone\b", "I am going", "Verb form"),
            (r"\bi\s+am\s+go\b", "I am going", "Verb form"),
            (r"\bi\s+am\s+eat\b", "I am eating", "Verb form"),
            (r"\bi\s+am\s+study\b", "I am studying", "Verb form"),
            (r"\bi\s+am\s+work\b", "I am working", "Verb form"),
            (r"\bi\s+was\s+go\b", "I was going", "Verb form"),
            (r"\bi\s+was\s+eat\b", "I was eating", "Verb form"),
            (r"\bi\s+have\s+went\b", "I have gone", "Past participle"),
            (r"\bi\s+didn['’]?t\s+went\b", "I didn't go", "Base verb after did not"),
            (r"\bhe\s+go\b", "he goes", "Subject-verb agreement"),
            (r"\bshe\s+go\b", "she goes", "Subject-verb agreement"),
            (r"\bit\s+go\b", "it goes", "Subject-verb agreement"),
            (r"\bhe\s+eat\b", "he eats", "Subject-verb agreement"),
            (r"\bshe\s+eat\b", "she eats", "Subject-verb agreement"),
            (r"\bhe\s+play\b", "he plays", "Subject-verb agreement"),
            (r"\bshe\s+play\b", "she plays", "Subject-verb agreement"),
            (r"\bthey\s+was\b", "they were", "Subject-verb agreement"),
            (r"\bwe\s+was\b", "we were", "Subject-verb agreement"),
            (r"\byou\s+was\b", "you were", "Subject-verb agreement"),
            (r"\bme\s+and\s+my\s+friend\b", "my friend and I", "Subject pronoun order"),
            (r"\btheir\s+is\b", "there is", "There/their"),
            (r"\btheir\s+are\b", "there are", "There/their"),
            (r"\bthere\s+is\s+many\b", "there are many", "Subject-verb agreement"),
            (r"\byour\s+a\b", "you're a", "Your/you're"),
            (r"\byour\s+not\b", "you're not", "Your/you're"),
            (r"\byour\s+going\b", "you're going", "Your/you're"),
            (r"\bmore\s+better\b", "better", "Double comparative"),
            (r"\bmore\s+easier\b", "easier", "Double comparative"),
            (r"\bdiscuss\s+about\b", "discuss", "Unnecessary preposition"),
            (r"\breturn\s+back\b", "return", "Unnecessary word"),
            (r"\brepeat\s+again\b", "repeat", "Unnecessary word"),
            (r"\bgo\s+to\s+home\b", "go home", "Unnecessary preposition"),
            (r"\bi\s+have\s+did\b", "I have done", "Past participle"),
            (r"\bi\s+did\s+not\s+went\b", "I did not go", "Base verb after did not"),
            (r"\bhe\s+don['’]?t\b", "he doesn't", "Subject-verb agreement"),
            (r"\bshe\s+don['’]?t\b", "she doesn't", "Subject-verb agreement"),
            (r"\bit\s+don['’]?t\b", "it doesn't", "Subject-verb agreement"),
            (r"\bhe\s+do\b", "he does", "Subject-verb agreement"),
            (r"\bshe\s+do\b", "she does", "Subject-verb agreement"),
            (r"\bit\s+do\b", "it does", "Subject-verb agreement"),
            (r"\bi\s+has\b", "I have", "Subject-verb agreement"),
            (r"\bthey\s+has\b", "they have", "Subject-verb agreement"),
            (r"\bwe\s+has\b", "we have", "Subject-verb agreement"),
            (r"\byou\s+has\b", "you have", "Subject-verb agreement"),
            (r"\bhe\s+have\b", "he has", "Subject-verb agreement"),
            (r"\bshe\s+have\b", "she has", "Subject-verb agreement"),
            (r"\bit\s+have\b", "it has", "Subject-verb agreement"),
            (r"\bi\s+is\b", "I am", "Subject-verb agreement"),
            (r"\bi\s+was\s+working\s+since\b", "I have been working since", "Present perfect continuous"),
            (r"\bcan\s+able\s+to\b", "can", "Remove redundant modal"),
            (r"\bmore\s+than\s+one\s+people\b", "more than one person", "Noun agreement"),
            (r"\bone\s+of\s+the\s+best\s+creator\b", "one of the best creators", "Plural noun after one of"),
        ]
        for pattern, replacement, reason in phrase_rules:
            updated = re.sub(pattern, replacement, fixed, flags=re.IGNORECASE)
            if updated != fixed:
                fixed = updated
                corrections.append(reason)

        # Common article, pronoun, preposition, adjective/adverb, and word-order rules.
        pos_rules = [
            (r"\ba ([aeiou][A-Za-z]+)", r"an \1", "Article: use 'an' before a vowel sound"),
            (r"\ban ([^aeiou\W][A-Za-z]+)", r"a \1", "Article: use 'a' before a consonant sound"),
            (r"\b(i|me) and (he|she)\b", lambda m: f"{m.group(2)} and {'I' if m.group(1).lower()=='i' else 'me'}", "Pronoun order"),
            (r"\bvery (good|bad|beautiful|quick|slow)\b", lambda m: {"very good":"excellent","very bad":"terrible","very beautiful":"beautiful","very quick":"quickly","very slow":"slowly"}.get(m.group(0).lower(),m.group(0)), "Adjective/adverb improvement"),
            (r"\bcan goes\b", "can go", "Modal verb takes base verb"),
            (r"\bwill goes\b", "will go", "Modal verb takes base verb"),
            (r"\bshould goes\b", "should go", "Modal verb takes base verb"),
            (r"\bmust goes\b", "must go", "Modal verb takes base verb"),
            (r"\bwant to going\b", "want to go", "Infinitive verb form"),
            (r"\bneed to going\b", "need to go", "Infinitive verb form"),
            (r"\bdoing good\b", "doing well", "Adverb form"),
            (r"\bfeel goodly\b", "feel good", "Adjective after linking verb"),
            (r"\bmore easier\b", "easier", "Comparative form"),
            (r"\bmost easiest\b", "easiest", "Superlative form"),
            (r"\bpeople is\b", "people are", "Noun-verb agreement"),
            (r"\bstudents is\b", "students are", "Noun-verb agreement"),
            (r"\bchildren is\b", "children are", "Noun-verb agreement"),
            (r"\beach students are\b", "each student is", "Determiner and noun agreement"),
            (r"\bevery people\b", "everyone", "Determiner and noun choice"),
        ]
        for pattern, replacement, reason in pos_rules:
            updated = re.sub(pattern, replacement, fixed, flags=re.IGNORECASE)
            if updated != fixed:
                fixed = updated
                corrections.append(reason)

        # Broader grammar, punctuation, duplicate-word and common usage rules.
        broader_rules = [
            (r'\b(a|an) ([A-Z][a-z]+)\b', lambda m: m.group(1).lower()+' '+m.group(2), 'Article/capitalization consistency'),
            (r'\b(i)\b', 'I', 'Pronoun capitalization'),
            (r'\b(i)\s+(am|was|have|will|can|should|need|want)\b', lambda m: 'I '+m.group(2), 'Pronoun capitalization'),
            (r'\b(can|could|should|would|will|may|might|must)\s+to\s+', lambda m: m.group(1)+' ', 'Modal verb + base form'),
            (r'\b(he|she|it)\s+(have|are|were)\b', lambda m: m.group(1)+' '+({'have':'has','are':'is','were':'was'}[m.group(2)]), 'Subject-verb agreement'),
            (r'\b(they|we)\s+(has|is|was)\b', lambda m: m.group(1)+' '+({'has':'have','is':'are','was':'were'}[m.group(2)]), 'Subject-verb agreement'),
            (r'\bthere\s+(is|was)\s+(many|several|two|three|four|five)\b', lambda m: 'there '+({'is':'are','was':'were'}[m.group(1)])+' '+m.group(2), 'Subject-verb agreement'),
            (r'\b(each|every)\s+(students|people|creators|users)\b', lambda m: m.group(1)+' '+m.group(2).rstrip('s'), 'Determiner + singular noun'),
            (r'\b(one of the best)\s+([A-Za-z]+)\b', lambda m: m.group(1)+' '+(m.group(2) if m.group(2).endswith('s') else m.group(2)+'s'), 'Plural noun after one of'),
            (r'\b(a lot of)\s+([A-Za-z]+)\b', lambda m: m.group(0), 'Quantifier check'),
            (r'\b(very)\s+(good|bad|quick|slow)\b', lambda m: m.group(1)+' '+m.group(2), 'Adverb + adjective/adverb check'),
            (r'\b(quick|slow|careful|beautiful)\s+(do|does|did|work|works|speak|speaks)\b', lambda m: {'quick':'quickly','slow':'slowly','careful':'carefully','beautiful':'beautifully'}[m.group(1)]+' '+m.group(2), 'Adverb form'),
            (r'\b(because|although|when|if|while)\s+([A-Z])', lambda m: m.group(1)+' '+m.group(2).lower(), 'Conjunction sentence flow'),
            (r'\b([A-Za-z]+)\s+\1\b', lambda m: m.group(1), 'Duplicate word removal'),
        ]
        for pattern, replacement, reason in broader_rules:
            updated = re.sub(pattern, replacement, fixed, flags=re.IGNORECASE)
            if updated != fixed:
                fixed = updated
                corrections.append(reason)

        # Fix common missing punctuation and normalize punctuation spacing.
        fixed = re.sub(r'\s+([,.;!?])', r'\1', fixed)
        fixed = re.sub(r'([,;:])(?=\S)', r'\1 ', fixed)
        fixed = re.sub(r'\?{2,}', '?', fixed)
        fixed = re.sub(r'!{2,}', '!', fixed)
        fixed = re.sub(r'\.{4,}', '...', fixed)

        # Capitalize standalone sentence starts even when the user entered multiple lines.
        fixed = re.sub(r'(^|(?<=[.!?])\s+|\n\s*)([a-z])', lambda m: m.group(1)+m.group(2).upper(), fixed)

        # If a line contains two independent short clauses, add a comma before a coordinating conjunction.
        fixed2 = re.sub(r'(?i)(\b(?:I|you|he|she|we|they|it)\s+[^.!?;,]{2,40})\s+(and|but|so)\s+((?:I|you|he|she|we|they|it)\b)', r'\1, \2 \3', fixed)
        if fixed2 != fixed:
            fixed = fixed2
            corrections.append('Punctuation: comma between independent clauses')

        # Common and user-requested spelling errors.
        word_rules = {
            "sucol":"school","scool":"school","shcool":"school","schol":"school","skool":"school","shool":"school",
            "recieve":"receive","seperate":"separate","definately":"definitely","occured":"occurred",
            "untill":"until","wich":"which","thier":"their","teh":"the","studing":"studying",
            "goverment":"government","enviroment":"environment","recieveing":"receiving","mesage":"message",
            "becuase":"because","langauge":"language","grammer":"grammar","adress":"address"
        }
        for wrong, right in word_rules.items():
            pattern = r"\b" + re.escape(wrong) + r"\b"
            updated = re.sub(pattern, right, fixed, flags=re.IGNORECASE)
            if updated != fixed:
                fixed = updated
                corrections.append(f"Spelling: {wrong} → {right}")

        # Proper-name and language capitalization. This is deliberately limited to
        # high-confidence names so ordinary words are not incorrectly title-cased.
        proper_case = {
            'english':'English', 'kannada':'Kannada', 'tamil':'Tamil',
            'telugu':'Telugu', 'hindi':'Hindi', 'python':'Python', 'java':'Java',
            'javascript':'JavaScript', 'html':'HTML', 'css':'CSS', 'sql':'SQL',
            'flask':'Flask', 'iphone':'iPhone', 'chatgpt':'ChatGPT',
            'instagram':'Instagram', 'youtube':'YouTube', 'tiktok':'TikTok',
            'linkedin':'LinkedIn', 'creatoros':'CreatorOS'
        }
        for wrong, right in proper_case.items():
            updated = re.sub(r'\b' + re.escape(wrong) + r'\b', right, fixed, flags=re.IGNORECASE)
            if updated != fixed:
                fixed = updated
                corrections.append(f"Capitalization: {right}")

        # General spelling pass. TextBlob is intentionally only used for words it
        # actually changes; high-confidence explicit rules above take precedence.
        try:
            from textblob import TextBlob
            corrected = str(TextBlob(fixed).correct())
            if corrected != fixed:
                # Keep only word-level changes and avoid replacing obvious names/URLs.
                before_words = fixed.split()
                after_words = corrected.split()
                if len(before_words) == len(after_words):
                    for bw, aw in zip(before_words, after_words):
                        bclean=re.sub(r"^[^\w]+|[^\w]+$","",bw)
                        aclean=re.sub(r"^[^\w]+|[^\w]+$","",aw)
                        if bclean and aclean and bclean.lower()!=aclean.lower() and len(bclean)>=4:
                            # Do not allow TextBlob to alter CreatorOS-specific vocabulary.
                            if bclean.lower() not in {"creatoros","creatorosai","instagram","youtube","tiktok","linkedin","python","flask","sql","html","css"}:
                                fixed = re.sub(r"\b"+re.escape(bclean)+r"\b", aw, fixed, count=1)
                                corrections.append(f"Spelling: {bclean} → {aw}")
        except Exception:
            pass

        # Normalize accidental ALL-CAPS writing while preserving acronyms and proper CreatorOS terms.
        def normalize_case(match):
            word=match.group(0)
            if word.upper() == word and len(word) > 1 and word not in {'AI','SEO','HTML','CSS','SQL','OS'}:
                return word.lower()
            return word
        fixed = re.sub(r"\b[A-Z]{2,}\b", normalize_case, fixed)
        fixed = re.sub(r"\b(i)\b", "I", fixed, flags=re.IGNORECASE)
        fixed = re.sub(r"[ \t]+", " ", fixed).strip()
        fixed = re.sub(r"\s+([,.!?;:])", r"\1", fixed)
        fixed = re.sub(r"([,.!?;:])([A-Za-z])", r"\1 \2", fixed)
        # Capitalize the beginning of every sentence.
        def cap_sentence(m): return m.group(1) + m.group(2).upper()
        capped = re.sub(r"(^|[.!?]\s+)([a-z])", cap_sentence, fixed)
        if capped != fixed:
            fixed = capped
            corrections.append("Capitalization: sentence beginnings")
        # Add commas before coordinating conjunctions when two independent clauses are obvious.
        punct_fixed = re.sub(r"\b([A-Za-z]+\s+[A-Za-z]+)\s+(and|but|so)\s+([A-Za-z]+\s+[A-Za-z]+)", r"\1, \2 \3", fixed)
        if punct_fixed != fixed:
            fixed = punct_fixed
            corrections.append("Punctuation: comma before coordinating conjunction")
        if fixed and fixed[-1] not in ".!?":
            fixed += "."
            corrections.append("Punctuation: added sentence ending")

        # Produce a real before/after word diff so the user can see exactly what changed.
        import difflib
        diff = list(difflib.ndiff(original.split(), fixed.split()))
        removed=[]; added=[]
        for item in diff:
            if item.startswith("- "): removed.append(item[2:])
            elif item.startswith("+ "): added.append(item[2:])
        changes = []
        for old, newword in zip(removed, added):
            changes.append(f"“{old}” → “{newword}”")
        if not changes and original != fixed:
            changes.append(f"Original → Corrected: “{original}” → “{fixed}”")

        # Lightweight parts-of-speech audit for the user: the checker actively handles
        # nouns, pronouns, verbs, adjectives, adverbs, articles/determiners, prepositions,
        # conjunctions and punctuation instead of only spell-checking.
        pos_areas = [
            ("Nouns", r"\b(?:person|people|student|students|creator|content|school|project|day|work|language|photo|calendar)\b"),
            ("Pronouns", r"\b(?:i|you|he|she|it|we|they|me|him|her|us|them|my|your|his|their|our)\b"),
            ("Verbs", r"\b(?:am|is|are|was|were|be|been|being|go|goes|went|make|makes|made|create|creates|created|have|has|had|do|does|did|can|will|should|must)\b"),
            ("Adjectives", r"\b(?:good|bad|great|beautiful|new|old|quick|slow|easy|easier|best|important)\b"),
            ("Adverbs", r"\b(?:quickly|slowly|well|very|really|always|never|often|today|tomorrow)\b"),
            ("Articles/Determiners", r"\b(?:a|an|the|this|that|these|those|each|every|some|many)\b"),
            ("Prepositions", r"\b(?:in|on|at|to|from|for|with|by|about|into|over|under|after|before)\b"),
            ("Conjunctions", r"\b(?:and|but|or|so|because|although|if|while)\b"),
        ]
        found_pos=[name for name,pattern in pos_areas if re.search(pattern, fixed, flags=re.IGNORECASE)]
        if re.search(r'[,.;:!?]', fixed): found_pos.append('Punctuation')
        pos_summary = ", ".join(found_pos) if found_pos else "General sentence structure"
        if original == fixed:
            result = f"""Corrected text:
{fixed}

Parts of speech checked:
• {pos_summary}

No high-confidence grammar or spelling errors were found."""
        else:
            unique_notes = list(dict.fromkeys(corrections))
            result = f"""Corrected text:
{fixed}

Parts of speech checked:
• {pos_summary}

Changes made:
{chr(10).join("• "+c for c in changes) if changes else "• Grammar/spelling correction applied."}

Why:
{chr(10).join("• "+c for c in unique_notes) if unique_notes else "• Grammar/spelling correction applied."}"""
        return result, len(result.split()) * 2

    @staticmethod
    def conversational_generate(question, current_output='', tool_type='caption', context=None, history=None):
        """Handle natural-language chat requests without requiring a paid API.

        This is the main conversational layer for the workspace. It treats the user's
        latest request, the current result, selected tool settings, and recent chat as
        context rather than matching only a few hard-coded commands.
        """
        question = re.sub(r'\s+', ' ', (question or '').strip())
        current_output = (current_output or '').strip()
        context = context or {}
        history = history or []
        low = question.lower()
        tool_type = (tool_type or 'caption').lower()

        topic = str(context.get('topic') or '').strip()
        platform = str(context.get('platform') or 'Instagram').strip()
        tone = str(context.get('tone') or 'Engaging & Viral').strip()

        # Recover useful context from the recent conversation when the form itself is blank.
        previous_user_messages = [
            str(item.get('content', '')).strip()
            for item in history[-8:]
            if isinstance(item, dict) and item.get('role') == 'user'
        ]
        previous_context = ' '.join(previous_user_messages)

        if not topic:
            topic = AIService._extract_topic(question, tool_type)
        if not topic:
            topic = AIService._extract_topic(previous_context, tool_type)
        if not topic:
            topic = 'your content'

        # Conversation intent. The important distinction is that vague requests such as
        # "give me relevant", "this is bad", or "something better" are treated as creative
        # requests instead of falling through to a generic help message.
        asks_rewrite = bool(re.search(r'\b(?:rewrite|re-write|rewritten|reword|rephrase|paraphrase)\b', low))
        asks_help = bool(re.search(r'\b(?:where|how do i|how can i|what is|explain|help me use)\b', low))
        asks_ideas = bool(re.search(r'\b(?:idea|ideas|options|variations|concepts|suggest|suggestions|examples|relevant|creative|inspiration)\b', low))
        rejects = bool(re.search(r"\b(?:don't like|dont like|didn't like|didnt like|not good|bad|boring|weak|generic|cringe|hate|improve|better|fix|redo|recreate|regenerate|again|different|fresh|change it|change this|not relevant)\b", low))
        asks_short = bool(re.search(r'\b(?:shorter|short|concise|brief|cut it down)\b', low))
        asks_long = bool(re.search(r'\b(?:longer|more detail|more detailed|expand|elaborate)\b', low))
        asks_funny = bool(re.search(r'\b(?:funny|humou?r|witty|playful)\b', low))
        asks_emotional = bool(re.search(r'\b(?:emotional|heartfelt|inspiring|personal|meaningful)\b', low))
        asks_professional = bool(re.search(r'\b(?:professional|formal|executive|polished)\b', low))
        asks_casual = bool(re.search(r'\b(?:casual|friendly|natural|human|conversational)\b', low))
        asks_hook = bool(re.search(r'\b(?:hook|opening|first line|headline|title)\b', low))
        remove_hashtags = bool(re.search(r'\b(?:remove|without|no)\s+(?:all\s+)?hashtags?\b', low))
        add_hashtags = bool(re.search(r'\b(?:add|give|include|more)\s+hashtags?\b', low))
        wants_many = re.search(r'\b(\d{1,2})\s+(?:ideas|options|versions|variations|hooks|captions)\b', low)
        count = max(2, min(10, int(wants_many.group(1)))) if wants_many else (5 if asks_ideas else 1)

        if asks_help and not (asks_ideas or rejects or current_output):
            return AIService._simple_creator_help(question, tool_type), 'Sure — here is how to use that part of CreatorOS.', 60

        # If the user asks to change the current result, preserve its subject and structure
        # where appropriate. If they ask for a new direction, deliberately create new material.
        if current_output:
            # "Rewrite" is a versioning action, not an instruction to overwrite the
            # existing result.  Return a materially different rewrite from the latest
            # result; the frontend will display it as a new version.
            if asks_rewrite:
                style = low
                result = AIService._creative_rewrite(current_output, topic, tool_type, style)
                return result, 'Done — I created a new rewritten version and kept the previous result.', len(result.split()) * 2

            if remove_hashtags:
                result = re.sub(r'#[A-Za-z0-9_]+', '', current_output)
                result = re.sub(r'\n{3,}', '\n\n', result).strip()
                return result, 'Done — I removed the hashtags and kept the rest of the content.', len(result.split()) * 2

            if asks_short:
                result = AIService._shorten_naturally(current_output, 70 if 'very' in low else 120)
                return result, 'Done — I tightened it without changing the main idea.', len(result.split()) * 2

            if asks_long:
                result = AIService._expand_naturally(current_output, topic)
                return result, 'Done — I expanded it with more useful detail instead of repeating the same lines.', len(result.split()) * 2

            if add_hashtags:
                base = re.sub(r'[^A-Za-z0-9]', '', topic.title()) or 'Content'
                tags = f'#{base} #ContentCreation #CreatorTips #ContentStrategy #AudienceGrowth #SocialMediaTips'
                result = current_output.rstrip() + '\n\n' + tags
                return result, 'Done — I added a relevant hashtag set.', len(result.split()) * 2

            if asks_hook:
                style_hooks = AIService._creative_hooks(topic, asks_funny, asks_emotional, asks_professional)
                result = '\n'.join(f'{i+1}. {h}' for i, h in enumerate(style_hooks[:count]))
                return result, 'Here are stronger opening options. Pick the direction you like and I can build the rest around it.', len(result.split()) * 2

        # Generate genuinely new material for ideas, vague dissatisfaction, or explicit recreation.
        if asks_ideas or rejects or not current_output:
            if tool_type == 'caption':
                variants = AIService._creative_caption_variants(topic, platform, tone, low, max(count, 3))
                result = '\n\n'.join(f'OPTION {i+1}\n{v}' for i, v in enumerate(variants[:max(count, 3)]))
                return result, 'Absolutely. I gave you different directions instead of minor edits. Tell me which one feels closest, and I’ll refine that one.', len(result.split()) * 2
            if tool_type == 'script':
                variants = AIService._creative_script_variants(topic, platform, tone, max(count, 3))
                result = '\n\n'.join(f'CONCEPT {i+1}\n{v}' for i, v in enumerate(variants[:max(count, 3)]))
                return result, 'Here are different creative directions. I can turn any one of them into the full script.', len(result.split()) * 2
            if tool_type == 'bio':
                variants = AIService._creative_bio_variants(topic, tone, max(count, 3))
                result = '\n\n'.join(f'OPTION {i+1}\n{v}' for i, v in enumerate(variants[:max(count, 3)]))
                return result, 'Here are distinct bio directions rather than small wording changes.', len(result.split()) * 2
            if tool_type == 'hashtag':
                result = AIService._creative_hashtag_set(topic, platform, max(count, 3))
                return result, 'I created a broader, more relevant set instead of recycling the same tags.', len(result.split()) * 2
            if tool_type == 'seo':
                result = AIService._creative_seo_ideas(topic, str(context.get('tone') or 'Creator Economy'))
                return result, 'Here are fresh SEO angles and keyword ideas for that topic.', len(result.split()) * 2
            result = AIService._creative_rewrite(current_output or question, topic, tool_type, low)
            return result, 'Done — I took a different angle rather than making a cosmetic edit.', len(result.split()) * 2

        # Style changes can be applied to an existing result even if the user did not use
        # a specific command phrase.
        if asks_professional or asks_casual or asks_funny or asks_emotional:
            style = 'professional' if asks_professional else 'casual' if asks_casual else 'funny' if asks_funny else 'emotional'
            result = AIService._creative_rewrite(current_output or question, topic, tool_type, style)
            return result, f'Done — I changed the voice to feel more {style}.', len(result.split()) * 2

        # Last resort: still do something useful. Never echo a canned "I can help" message
        # when the user is clearly asking for content.
        result = AIService._creative_rewrite(current_output or question, topic, tool_type, low)
        return result, 'Done — I used your request as the creative direction and generated a new version.', len(result.split()) * 2

    @staticmethod
    def _extract_topic(text, tool_type='caption'):
        """Pull a usable subject from free-form chat without requiring form fields."""
        text = (text or '').strip()
        if not text:
            return ''
        patterns = [
            r'\b(?:about|on|for|regarding)\s+(.+?)(?:\s+(?:for|on)\s+(?:instagram|tiktok|linkedin|youtube)|[.!?]|$)',
            r'\b(?:caption|script|post|bio|content)\s+(?:for|about|on)\s+(.+?)(?:[.!?]|$)',
            r'\b(?:topic|subject)\s*[:=-]\s*(.+?)(?:[.!?]|$)',
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.I)
            if m:
                value = m.group(1).strip(' "\'')
                if value and len(value) < 180:
                    return value
        cleaned = re.sub(r'\b(?:give me|create|make|write|generate|suggest|some|a|an|the|relevant|good|better|new|fresh)\b', ' ', text, flags=re.I)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip(' .,!?:;-')
        return cleaned[:120]

    @staticmethod
    def _shorten_naturally(text, max_words=120):
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        hashtags = [x for x in lines if '#' in x]
        body = [x for x in lines if '#' not in x]
        words = ' '.join(body).split()
        shortened = ' '.join(words[:max_words]).strip()
        if words and len(words) > max_words:
            shortened += '…'
        if hashtags:
            shortened += '\n\n' + ' '.join(hashtags[:1])
        return shortened

    @staticmethod
    def _expand_naturally(text, topic):
        clean = text.strip()
        addition = (
            f'\n\nWhy this matters: {topic} becomes much easier to communicate when the audience '
            'can immediately see the problem, the useful takeaway, and what they should do next. '
            'Keep the message specific and make each sentence earn its place.'
        )
        return clean + addition

    @staticmethod
    def _creative_script_variants(topic, platform, tone, count=3):
        ideas = [
            f'Open with a surprising mistake about {topic}, reveal the fix in three steps, and end with a quick challenge for the viewer.',
            f'Tell a short before/after story around {topic}: the problem, the turning point, what changed, and the lesson.',
            f'Use a myth-vs-reality format for {topic}. Start with the common belief, challenge it, prove the better approach, and close with one action.',
            f'Build a rapid tutorial on {topic} with one concrete example and a final checklist viewers can save.',
            f'Create a personal-confession angle on {topic}: what went wrong, what you learned, and what you would do differently now.'
        ]
        return ideas[:count]

    @staticmethod
    def _creative_bio_variants(niche, tone, count=3):
        return [
            f'{niche} creator | Practical ideas, real experiments, no unnecessary fluff.\nFollow for useful content you can actually use.',
            f'Helping people understand {niche} without making it complicated.\nNew ideas • Honest lessons • Useful resources',
            f'Building, learning and sharing around {niche}.\nIf you like clear ideas and better content, you’re in the right place.',
            f'{niche} | Learn it. Try it. Share it.\nFollow for fresh ideas and practical creator lessons.',
            f'Turning {niche} into simple, useful content.\nIdeas for creators who want substance, not noise.'
        ][:count]

    @staticmethod
    def _creative_hashtag_set(topic, platform, count=3):
        base = re.sub(r'[^A-Za-z0-9]', '', topic.title()) or 'Content'
        sets = [
            f'#{base} #ContentCreator #CreatorTips #ContentStrategy #AudienceGrowth #DigitalCreator',
            f'#{base} #SocialMediaTips #ContentMarketing #CreatorEconomy #ContentIdeas #GrowOnline',
            f'#{base} #CreativeProcess #PersonalBrand #ContentPlanning #OnlineCreator #CreatorCommunity'
        ]
        return '\n\n'.join(f'SET {i+1}\n{x}' for i, x in enumerate(sets[:count]))

    @staticmethod
    def _creative_seo_ideas(topic, industry='Creator Economy'):
        clean = topic.lower().strip()
        title = topic.title()
        return (
            f'PRIMARY\n1. {clean} guide\n2. how to use {clean}\n3. best {clean} strategies\n4. {clean} for beginners\n\n'
            f'LONG-TAIL\n• best {clean} tools for {industry.lower()}\n• {clean} tips and examples\n• common {clean} mistakes to avoid\n• how to improve {clean} step by step\n\n'
            f'CONTENT ANGLES\n• The beginner guide to {title}\n• 5 mistakes people make with {title}\n• {title}: what actually works\n• A practical {title} checklist'
        )

    @staticmethod
    def _simple_creator_help(question, tool_type):
        return (
            f'You are currently using the {tool_type.title()} workspace. Tell me what you want in plain language — '
            'for example, “this is boring, give me a completely different caption”, “give me 5 hooks”, '
            'or “keep this idea but make it funny”. I will use the current result and our recent conversation as context.'
        )

    @staticmethod
    def refine_output(previous_output, instruction, tool_type='caption', context=None):
        """Backward-compatible wrapper for older callers."""
        result, _answer, tokens = AIService.conversational_generate(
            instruction, previous_output, tool_type, context or {}, []
        )
        return result, tokens

    @staticmethod
    def _creative_hooks(topic, funny=False, emotional=False, professional=False):
        topic_low=(topic or '').lower()
        if any(x in topic_low for x in ('eye','eyes','gaze')):
            return [
                f"Some eyes do not just look at you — they tell you what words never could.",
                f"There is a kind of silence that only {topic} can speak.",
                f"You can hide a thought, but sometimes a gaze gives it away.",
                f"The darkest stories are sometimes reflected in a pair of {topic}.",
                f"What if {topic} could tell you everything the heart refuses to say?"
            ]
        if any(x in topic_low for x in ('coffee shop','cafe','café','coffeehouse')):
            return [
                f"A coffee shop can turn an ordinary hour into a memory.",
                f"Some places serve coffee. The best ones serve a feeling.",
                f"The aroma, the lights, the quiet — that is the real charm of a coffee shop.",
                f"A good coffee shop makes you want to stay five minutes longer.",
                f"There is something about coffee and a quiet corner that makes time slow down."
            ]
        if any(x in topic_low for x in ('artificial flower','artificial flowers','fake flower','fake flowers','silk flower','faux flower')):
            return [
                f"The secret to beautiful artificial flowers is making them feel almost real.",
                f"Artificial flowers do not need to look artificial — the arrangement changes everything.",
                f"A little colour, the right texture, and suddenly artificial flowers transform a room.",
                f"Not every beautiful flower needs watering.",
                f"The right artificial flower arrangement can make an empty corner feel alive."
            ]
        if funny:
            return [
                f"Me pretending I have {topic} figured out… until this happened 😂",
                f"Nobody warned me that {topic} could be this chaotic.",
                f"POV: you finally stop overthinking {topic}.",
                f"The internet made {topic} look easy. It isn't.",
                f"I tried the usual advice on {topic}. Here's what actually worked."
            ]
        if emotional:
            return [
                f"I wish someone had told me this about {topic} sooner.",
                f"Behind every result with {topic}, there's a part nobody sees.",
                f"If you're struggling with {topic}, this is for you.",
                f"One small shift changed how I look at {topic}.",
                f"You don't need to have {topic} figured out today."
            ]
        if professional:
            return [
                f"The practical truth about {topic}:",
                f"Three lessons every creator should know about {topic}:",
                f"A smarter way to approach {topic}:",
                f"What actually matters when working on {topic}:",
                f"A simple framework for improving {topic}:"]
        return [
            f"Here's the part about {topic} most people skip:",
            f"If I had to start {topic} again, I'd do this first:",
            f"The biggest mistake people make with {topic}:",
            f"You don't need more tips on {topic}. You need this:",
            f"Let's make {topic} much simpler."
        ]

    @staticmethod
    def _creative_caption_variants(topic, platform, tone, instruction, count=5):
        """Create captions that stay anchored to the actual subject."""
        topic = re.sub(r'\s+', ' ', (topic or 'your topic')).strip(' .,!?:;') or 'your topic'
        profile = AIService._topic_profile(topic)
        hooks = AIService._creative_hooks(
            topic,
            funny="funny" in instruction or "humor" in instruction,
            emotional="emotional" in instruction or "heartfelt" in instruction,
            professional="professional" in instruction or "formal" in instruction,
        )
        angles = profile['angles']
        details = profile['details']
        ctas = [
            f"What is your take on {topic}?",
            f"Would you experience {topic} this way?",
            f"Save this if {topic} caught your attention.",
            f"Which part of {topic} would you explore first?",
            f"Tell me the first thing you notice about {topic}."
        ]
        variants = []
        for i, hook in enumerate(hooks[:max(5, count)]):
            a = angles[i % len(angles)]
            d1 = details[i % len(details)]
            d2 = details[(i + 1) % len(details)]
            variants.append(
                f"{hook}\n\n"
                f"{topic} has its own story — especially when you look at {a}. "
                f"Think about {d1}, then notice {d2}. "
                f"That small detail can completely change the way you see {topic}.\n\n"
                f"{ctas[i % len(ctas)]}\n\n"
                f"#{re.sub(r'[^A-Za-z0-9]', '', topic.title()) or 'Content'}"
            )
        return variants[:count]

    @staticmethod
    def _creative_rewrite(text, topic, tool_type, instruction):
        """Create a materially different rewrite.

        A rewrite must NOT be a cosmetic edit of the previous result.  It should keep
        the core subject while changing the hook, sentence structure, phrasing and,
        for social content, the CTA/angle.  This is intentionally deterministic enough
        to work without a paid AI API, but uses several candidate variants and rejects
        candidates that are too similar to the source.
        """
        source = (text or '').strip()
        low = (instruction or '').lower()
        clean_topic = (topic or '').strip() or AIService._extract_topic(source, tool_type) or 'your topic'

        # Remove generated-report metadata if the Rewrite tool itself is being rewritten.
        source_core = re.sub(r'(?is)^.*?REWRITTEN VERSION\s*:?\s*', '', source, count=1)
        source_core = re.sub(r'(?is)━━━━━━━━.*$', '', source_core).strip()
        source_core = source_core.strip('"“”')
        if not source_core:
            source_core = source

        funny = bool(re.search(r'funny|humou?r|witty|playful', low))
        emotional = bool(re.search(r'emotional|heartfelt|personal|meaningful', low))
        professional = bool(re.search(r'professional|formal|executive|polished', low))
        concise = bool(re.search(r'short|concise|punchy|brief', low))

        # For captions, do not merely replace a few words in the old caption. Generate
        # several different angles and select one that is sufficiently different.
        if tool_type == 'caption':
            variants = AIService._creative_caption_variants(
                clean_topic,
                'Instagram',
                'Engaging & Viral',
                low,
                count=5,
            )
            source_norm = re.sub(r'\W+', ' ', source_core.lower()).strip()
            random.shuffle(variants)
            for candidate in variants:
                cand_norm = re.sub(r'\W+', ' ', candidate.lower()).strip()
                # Word-set overlap catches copies even when punctuation/emoji changes.
                a, b = set(source_norm.split()), set(cand_norm.split())
                overlap = len(a & b) / max(1, len(a | b))
                if overlap < 0.55 and cand_norm != source_norm:
                    return candidate
            return variants[0]

        if tool_type == 'script':
            hooks = AIService._creative_hooks(clean_topic, funny, emotional, professional)
            hook = random.choice(hooks)
            sentences = [x.strip() for x in re.split(r'(?<=[.!?])\s+', source_core) if x.strip()]
            core = ' '.join(sentences)
            # Reverse/reshape the source instead of preserving the same sentence order.
            chunks = [x.strip() for x in re.split(r'\n+|(?<=[.!?])\s+', core) if x.strip()]
            if chunks:
                chunks = list(reversed(chunks))
            body = ' '.join(chunks[:5]) if chunks else f'Let’s break {clean_topic} into a simple idea people can understand and use.'
            if concise:
                body = ' '.join(body.split()[:55]).rstrip('.,!?') + '.'
            return f'HOOK\n{hook}\n\nBODY\n{body}\n\nCTA\nSave this and share your biggest takeaway.'

        if tool_type == 'bio':
            options = [
                f'Helping creators get smarter about {clean_topic}.\nPractical ideas, useful tools, and lessons you can actually apply.\n👇 Follow for more.',
                f'{clean_topic}, made simple.\nIdeas that turn into better content — without the unnecessary fluff.\n✨ New creator insights regularly.',
                f'Creating around {clean_topic}.\nBreaking down complex ideas into clear, useful content.\n🚀 Follow along.'
            ]
            return random.choice(options)

        if tool_type == 'hashtag':
            base = re.sub(r'[^A-Za-z0-9]', '', clean_topic.title()) or 'Content'
            options = [
                f'#{base} #CreatorEducation #ContentStrategy #AudienceGrowth #DigitalCreator #SocialMediaTips',
                f'#{base} #TechCreators #ContentIdeas #PersonalBrand #CreatorCommunity #GrowthStrategy',
                f'#{base} #ContentMarketing #OnlineCreator #CreativeStrategy #SocialGrowth #CreatorTips'
            ]
            source_tags = set(re.findall(r'#[A-Za-z0-9_]+', source_core.lower()))
            choices = [x for x in options if len(source_tags & set(re.findall(r'#[A-Za-z0-9_]+', x.lower()))) < 3]
            return random.choice(choices or options)

        # Generic/rewrite-tool content: create a new sentence structure, not just word
        # substitutions. Use several lead patterns and rotate sentence order.
        replacements = {
            'important': 'essential', 'help': 'make it easier', 'good': 'effective',
            'things': 'ideas', 'people': 'creators', 'using': 'working with',
            'should': 'can', 'regularly': 'consistently', 'simple': 'straightforward'
        }
        sentences = [x.strip() for x in re.split(r'(?<=[.!?])\s+', source_core) if x.strip()]
        transformed = []
        for sentence in sentences:
            line = sentence
            for old_word, new_word in replacements.items():
                line = re.sub(rf'\b{re.escape(old_word)}\b', new_word, line, flags=re.I)
            transformed.append(line.rstrip('.!?'))
        if not transformed:
            transformed = [f'{clean_topic} becomes easier to understand when the main idea is clear and practical.']

        # A different order plus a different lead makes repeated rewrites visibly distinct.
        if len(transformed) > 1:
            transformed = transformed[1:] + transformed[:1]
        leads = [
            f'Here is a fresh way to frame {clean_topic}:',
            f'A stronger perspective on {clean_topic} is this:',
            f'Instead of approaching {clean_topic} the usual way, consider this:',
            f'The practical takeaway from {clean_topic} is:',
        ]
        lead = random.choice(leads)
        body = '. '.join(transformed).rstrip('.') + '.'
        if concise:
            body = ' '.join(body.split()[:60]).rstrip('.,!?') + '.'
        elif funny:
            body += ' The goal is clarity, not making it sound complicated.'
        elif emotional:
            body += ' What matters most is making the idea meaningful to the people reading it.'
        elif professional:
            body += ' This framing keeps the message clear, focused, and actionable.'
        else:
            body += ' The message stays the same, but the presentation is cleaner and more direct.'
        return f'{lead}\n\n{body}'

    @staticmethod
    def _simple_alternative(text, tool_type):
        body = re.sub(r"\*+", "", text)
        body = re.sub(r"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "", body)
        body = re.sub(r"\s{2,}", " ", body).strip()
        if tool_type == "hashtag":
            return "#ContentCreation #CreatorTips #DigitalContent #AudienceGrowth #SocialMediaGrowth"
        return "Here is a fresh version with a different structure and wording while keeping the same core idea.\n\n" + body[:900]

    @staticmethod
    def generate_seo_keywords(topic, industry="", previous_output="", variation=0):
        """Create topic-focused SEO keyword ideas without generic keyword dumping."""
        topic = re.sub(r'\s+', ' ', (topic or 'CreatorOS')).strip(' .,!?:;') or 'CreatorOS'
        industry = re.sub(r'\s+', ' ', (industry or '').strip())
        t = topic.lower()
        ind = industry.lower()

        # Build natural search phrases from the exact user topic.
        primary = [
            t,
            f"{t} guide",
            f"{t} tutorial",
            f"{t} tips",
            f"{t} for beginners",
        ]
        if ind:
            primary += [f"{t} {ind}", f"{t} for {ind}"]

        long_tail = [
            f"how to use {t}",
            f"how to learn {t}",
            f"how does {t} work",
            f"best way to use {t}",
            f"{t} step by step",
            f"{t} common mistakes",
            f"{t} examples",
        ]
        if ind:
            long_tail += [
                f"{t} for {ind} beginners",
                f"best {t} for {ind}",
            ]

        questions = [
            f"What is {t}?",
            f"How does {t} work?",
            f"How can I use {t}?",
            f"Who should use {t}?",
            f"What are the benefits of {t}?",
            f"What are the common mistakes with {t}?",
        ]

        # A second regeneration changes ordering and title angle.
        rng=random.Random(hash((t, ind, int(variation))) & 0xffffffff)
        rng.shuffle(primary)
        rng.shuffle(long_tail)
        rng.shuffle(questions)

        title_options = [
            f"{topic}: Complete Guide for Beginners",
            f"How to Use {topic}: Practical Guide",
            f"{topic}: Tips, Examples and Common Mistakes",
            f"{topic}: What You Need to Know",
        ]
        meta_options = [
            f"Learn about {topic}, how it works, practical uses, examples and common mistakes in this clear guide.",
            f"A practical guide to {topic} with beginner-friendly explanations, useful examples and actionable tips.",
            f"Explore {topic} through simple explanations, practical examples and steps you can apply.",
        ]

        result = f"""SEO KEYWORDS — {topic}

PRIMARY KEYWORDS
• {primary[0]}
• {primary[1]}
• {primary[2]}
• {primary[3]}
• {primary[4]}

LONG-TAIL KEYWORDS
• {long_tail[0]}
• {long_tail[1]}
• {long_tail[2]}
• {long_tail[3]}
• {long_tail[4]}
• {long_tail[5]}

SEARCH QUESTIONS
• {questions[0]}
• {questions[1]}
• {questions[2]}
• {questions[3]}
• {questions[4]}

SUGGESTED TITLE
{rng.choice(title_options)}

META DESCRIPTION
{rng.choice(meta_options)}
"""
        if industry:
            result += f"\nINDUSTRY CONTEXT\n{industry} — use this only where it genuinely matches the page or content."
        return result.strip(), len(result.split()) * 2




# ---------------------------------------------------------------------------
# CreatorOS Hub
# ---------------------------------------------------------------------------

def _hub_destination(message):
    # Resolve current CreatorOS module names and common/legacy terms.
    text = re.sub(r'[^a-z0-9& ]+', ' ', (message or '').lower())
    text = re.sub(r'\s+', ' ', text).strip()
    aliases = {
        'dashboard': ['launchpad', 'dashboard', 'home', 'main page', 'homepage', 'dashbord'],
        'workspace': ['idea flow', 'workspace', 'work space', 'ai workspace', 'copilot'],
        'caption': ['caption', 'captions', 'caption generator'],
        'script': ['script', 'scripts', 'script generator', 'reel script', 'youtube script'],
        'hashtag': ['hashtag', 'hashtags', 'hash tag'],
        'bio': ['bio', 'bios', 'biography', 'profile bio'],
        'seo': ['seo', 'keywords', 'search engine', 'search keywords'],
        'rewrite': ['rewrite', 'rewriting', 'rephrase', 'paraphrase'],
        'images': ['pick perfect', 'image editor', 'image', 'images', 'thumbnail', 'thumbnails', 'visual', 'picture'],
        'media': ['media bloom', 'media', 'assets', 'asset', 'media assets', 'files', 'upload'],
        'video': ['clip nest', 'video editor', 'video editing', 'video', 'reel editor', 'editor'],
        'calendar': ['day canvas', 'calendar', 'calender', 'calandar', 'schedule', 'scheduler', 'planning', 'planner'],
        'drafts': ['craft nest', 'draft', 'drafts', 'draft manager', 'saved content', 'recycle bin'],
        'analytics': ['growth lens', 'analytics', 'analysis', 'statistics', 'stats', 'performance', 'insights'],
        'profile': ['persona', 'profile', 'account', 'settings', 'avatar', 'language settings'],
        'hub': ['Nexus', 'creatoros hub', 'nexus', 'hub', 'help', 'assistant', 'creator hub'],
    }
    # Match longer module phrases first, so "image editor" is not mistaken for video editor.
    for dest, words in aliases.items():
        for word in sorted(words, key=len, reverse=True):
            if word in text:
                return dest
    tokens = text.split()
    vocabulary = {w: dest for dest, words in aliases.items() for w in words if ' ' not in w}
    for token in tokens:
        close = get_close_matches(token, list(vocabulary), n=1, cutoff=0.78)
        if close:
            return vocabulary[close[0]]
    return None


def _hub_link(destination):
    links = {
        'dashboard': ('/', 'Open Launchpad'),
        'workspace': ('/ai/workspace', 'Open Idea Flow'),
        'caption': ('/ai/workspace?tool=caption', 'Open Caption Generator'),
        'script': ('/ai/workspace?tool=script', 'Open Script Generator'),
        'hashtag': ('/ai/workspace?tool=hashtag', 'Open Hashtag Generator'),
        'bio': ('/ai/workspace?tool=bio', 'Open Bio Generator'),
        'seo': ('/ai/workspace?tool=seo', 'Open SEO Generator'),
        'rewrite': ('/ai/workspace?tool=rewrite', 'Open Rewrite Content'),
        'images': ('/pick-perfect', 'Open Pick Perfect'),
        'media': ('/media/assets', 'Open Media Bloom'),
        'video': ('/video-editor', 'Open Video Editor'),
        'calendar': ('/planner/calendar', 'Open Day Canvas'),
        'drafts': ('/drafts/manager', 'Open Craft Nest'),
        'analytics': ('/analytics', 'Open Growth Lens'),
        'profile': ('/profile/settings', 'Open Persona'),
        'hub': ('/ai/chatbot', 'Open Nexus'),
    }
    return links[destination]


def _creatoros_chat(message):
    # Explain how to use the user's current modules, then provide the matching link.
    text = (message or '').strip()
    lower = text.lower()
    destination = _hub_destination(text)

    if destination:
        path, label = _hub_link(destination)
        guides = {
            'dashboard': ('Launchpad', 'Your starting page for CreatorOS.', [
                'Open Launchpad to see your modules and recent activity.',
                'Choose the module for the task you want to do.',
                'Use the quick links to return to your work or plan your next task.']),
            'workspace': ('Idea Flow', 'Create and improve content with the available AI tools.', [
                'Open Idea Flow.', 'Choose Caption, Script, Hashtag, Bio, Rewrite or SEO.',
                'Enter your topic and the requested details.', 'Select Generate, review the result, and use the conversation bar to refine it.']),
            'caption': ('Caption Generator', 'Create a caption for a post or video.', [
                'Open Idea Flow and select Caption Generator.', 'Enter your topic or keyword.',
                'Choose the target platform and tone.', 'Select Generate Caption and review the result.']),
            'script': ('Script Generator', 'Prepare a script for your video.', [
                'Open Idea Flow and select Script Generator.', 'Enter your video concept or topic.',
                'Choose the video format and duration.', 'Select Generate Script, then review and edit the script.']),
            'hashtag': ('Hashtag Generator', 'Create a topic-related hashtag set.', [
                'Open Idea Flow and select Hashtag Generator.', 'Enter the main topic or keyword.',
                'Choose the platform and creator niche.', 'Select Generate Hashtags and review the suggestions.']),
            'bio': ('Bio Generator', 'Create profile bio variations.', [
                'Open Idea Flow and select Bio Generator.', 'Enter your industry or niche.',
                'Choose a personality and add a call to action.', 'Select Generate Bios and choose the version you want.']),
            'seo': ('SEO Generator', 'Create SEO keyword suggestions for your topic.', [
                'Open Idea Flow and select SEO.', 'Enter your topic or product and industry.',
                'Select Generate SEO Report.', 'Review the keywords and suggestions before using them.']),
            'rewrite': ('Rewrite Content', 'Improve the wording of a draft you provide.', [
                'Open Idea Flow and select Rewrite Content.', 'Paste your original draft.',
                'Choose the target tone.', 'Select Rewrite Text and review the revised version.']),
            'images': ('Pick Perfect', 'Edit an image using the image tools.', [
                'Open Pick Perfect.', 'Select Add Image and choose a picture.',
                'Choose a tool such as Clarity, Focus Veil, Tone Lab, Sticker Bloom, Crop, Frame, Text or Collage.',
                'Preview your changes, then select Download to save the edited image.']),
            'media': ('Media Bloom', 'Organize and manage your uploaded media files.', [
                'Open Media Bloom.', 'Choose the upload option and select your image, video or document.',
                'Wait for the upload to finish.', 'Find the file in the library; use its available open, download or delete action.']),
            'video': ('Video Editor', 'Edit and export a video.', [
                'Open Video Editor.', 'Add your video clip or clips.',
                'Arrange clips on the timeline and trim or split them as needed.',
                'Adjust available audio or effects and preview the result.',
                'Choose the export option to create the finished video.']),
            'calendar': ('Day Canvas', 'Plan and schedule content.', [
                'Open Day Canvas.', 'Choose Add Content.', 'Enter the title, date, time, platform and status.',
                'Add notes if needed, then select Save Content.', 'Return to the calendar to review the scheduled item.']),
            'drafts': ('Craft Nest', 'Keep unfinished content and files together.', [
                'Open Craft Nest.', 'Upload a file or open an existing draft.',
                'Continue editing and save your changes.', 'Use Recycle Bin to review or restore a removed draft.']),
            'analytics': ('Growth Lens', 'Review the performance information available in your account.', [
                'Open Growth Lens.', 'Choose the available reporting period or filter.',
                'Review the charts and activity summaries.', 'Use the results to understand your content activity.']),
            'profile': ('Persona', 'Manage your profile and account preferences.', [
                'Open Persona.', 'Update your display name or profile picture if needed.',
                'Choose your preferred language and other available settings.', 'Save your changes.']),
            'hub': ('Nexus', 'Get help navigating and using CreatorOS.', [
                'Type the name of a module or describe what you want to do.',
                'Ask “how do I…” for step-by-step guidance.', 'Select the Open link in the answer to go directly to that module.']),
        }
        title, summary, steps = guides[destination]
        lines = [f'{title} — {summary}', '']
        lines.extend(f'{i}. {step}' for i, step in enumerate(steps, 1))
        lines.extend(['', f'{label}: [{label}]({path})'])
        return '\n'.join(lines)

    if any(x in lower for x in ['hello', 'hi', 'hey', 'start', 'begin', 'getting started', 'what should i do first']):
        return '''Welcome to Nexus! 👋

Tell me what you want to do in CreatorOS. I will explain the steps and give you the link to the correct module.

Current modules: Launchpad, Idea Flow, Media Bloom, Pick Perfect, Clip Nest, Day Canvas, Craft Nest, Growth Lens and Persona.'''

    if any(x in lower for x in ['all modules', 'every module', 'modules', 'features']):
        return '''CreatorOS Modules 🧭

• Launchpad — your starting page
• Idea Flow — AI content creation and rewriting
• Media Bloom — uploaded media library
• Pick Perfect — image editing
• Clip Nest — video editing and export
• Day Canvas — content planning and scheduling
• Craft Nest — drafts and saved files
• Growth Lens — analytics and activity
• Persona — profile and account settings
• Nexus — help and navigation

Ask about any module and I will give you its steps and a direct Open link.'''

    return '''I can guide you through CreatorOS one step at a time.

Try asking:
• “How do I edit a video in Clip Nest?”
• “How do I upload files to Media Bloom?”
• “How do I crop and download an image in Pick Perfect?”
• “How do I schedule a post in Day Canvas?”'''


AIService.chat = staticmethod(_creatoros_chat)
