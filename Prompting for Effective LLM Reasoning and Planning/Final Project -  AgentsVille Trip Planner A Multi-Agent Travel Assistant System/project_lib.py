"""Provides utility functions for the project."""

from enum import Enum

SINGLE_TAB_LEVEL = 4


class Interest(str, Enum):
    ART = "art"
    COOKING = "cooking"
    COMEDY = "comedy"
    DANCING = "dancing"
    FITNESS = "fitness"
    GARDENING = "gardening"
    HIKING = "hiking"
    MOVIES = "movies"
    MUSIC = "music"
    PHOTOGRAPHY = "photography"
    READING = "reading"
    SPORTS = "sports"
    TECHNOLOGY = "technology"
    THEATRE = "theatre"
    TENNIS = "tennis"
    WRITING = "writing"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ChatAgent:
    """A chat agent that interacts with OpenAI's API to facilitate conversations.

    This class manages chat history, formats system prompts, and handles
    communication with OpenAI's chat completion API. It provides methods to
    add messages, get responses, and maintain conversation context.

    Attributes:
        system_prompt_template (str): Template for the system prompt using {variable_name} placeholders.
    """
    system_prompt = "You are a helpful assistant."
    messages = []

    def __init__(self, name=None, system_prompt=None, client=None, model=None):
        self.name = name or self.__class__.__name__
        if system_prompt:
            self.system_prompt = system_prompt
        self.client = client
        self.model = model
        self.reset()

    def add_message(self, role, content):
        """Add a message to the chat history.

        Args:
            role (str): The role of the message ("system", "user", or "assistant").
            content (str): The content of the message.

        Raises:
            ValueError: If the role is not one of "system", "user", or "assistant".
        """
        if role not in ["system", "user", "assistant"]:
            raise ValueError(f"Invalid role: {role}")
        self.messages.append({"role": role, "content": content})
        if role == "system":
            print_in_box(
                content,
                f"{self.name} - System Prompt",
            )
        elif role == "user":
            print_in_box(
                content,
                f"{self.name} - User Prompt",
            )
        elif role == "assistant":
            print_in_box(
                content,
                f"{self.name} - Assistant Response",
            )

    def reset(self):
        """Reset the chat history and re-initialize with the system prompt.

        This method clears all existing messages and adds the system prompt
        formatted with the template_kwargs.
        """
        from textwrap import dedent

        system_prompt = dedent(self.system_prompt).strip()

        # Clear previous messages and add the system prompt
        self.messages = []
        self.add_message(
            "system",
            system_prompt,
        )

    def get_response(self, add_to_messages=True, model=None, client=None, **kwargs):
        """Get a response from the OpenAI API.

        Args:
            add_to_messages (bool, optional): Whether to add the response to the chat history
            using the add_message method and the assistant role. Defaults to True.

        Returns:
            str: The response from the OpenAI API.


        """
        response = do_chat_completion(
            messages=self.messages,
            model=model or self.model,
            client=client or self.client,
            **kwargs
        )
        if add_to_messages:
            self.add_message("assistant", response)
        return response

    def chat(self, user_message, add_to_messages=True, model=None, **kwargs):
        """Send a message to the chat and get a response.

        Args:
            user_message (str): The message to send to the chat.

        Returns:
            str: The response from the OpenAI API.
        """
        self.add_message("user", user_message)
        return self.get_response(add_to_messages=add_to_messages, model=model, **kwargs)


def print_in_box(text, title="", cols=120, tab_level=0):
    """
    Prints the given text in a box with the specified title and dimensions.

    Args:
        text: The text to print in the box.
        title: The title of the box.
        cols: The width of the box.
        tab_level: The level of indentation for the box.
    """
    import textwrap

    text = str(text)

    # Make a box using extended ASCII characters
    if cols < 4 + tab_level * SINGLE_TAB_LEVEL:
        cols = 4 + tab_level * SINGLE_TAB_LEVEL

    tabs = " " * tab_level * SINGLE_TAB_LEVEL

    top = (
        tabs
        + "\u2554"
        + "\u2550" * (cols - 2 - tab_level * SINGLE_TAB_LEVEL)
        + "\u2557"
    )
    if tab_level == 0:
        print()  # Print a newline before any box at level 0

    if title:
        # replace the middle of the top with the title
        title = "[ " + title + " ]"
        top = top[: (cols - len(title)) // 2] + title + top[(cols + len(title)) // 2 :]
    print(top)

    for line in text.split("\n"):
        for wrapped_line in textwrap.wrap(
            line, cols - 4 - tab_level * SINGLE_TAB_LEVEL
        ):
            print(
                f"{tabs}\u2551 {wrapped_line:<{cols - 4 - tab_level * SINGLE_TAB_LEVEL}} \u2551"
            )

    print(
        f"{tabs}\u255a"
        + "\u2550" * (cols - 2 - tab_level * SINGLE_TAB_LEVEL)
        + "\u255d"
    )


def do_chat_completion(messages: list[dict[str, str]], model=None, client=None, **kwargs):
    """A simple wrapper around OpenAI's chat completion API.

    Args:
        messages: A list of messages to send to the chat completion API.

    Returns:
        str: The response from the chat completion API.

    Raises:
        openai.OpenAIError: If the chat completion API returns an error.

    Examples:
        >>> messages = [
        ...     {"role": "user", "content": "Hello, how are you?"},
        ...     {"role": "assistant", "content": "I'm good, thanks!"},
        ... ]
        >>> from unittest.mock import patch
        >>> with patch('openai.OpenAI') as mock_openai:
        ...     # Setup mock response
        ...     mock_client = mock_openai.return_value
        ...     mock_chat = mock_client.chat
        ...     mock_completions = mock_chat.completions
        ...     mock_create = mock_completions.create
        ...     mock_response = mock_create.return_value
        ...     mock_response.choices = [type('obj', (object,), {'message': type('msg', (object,), {'content': "I'm good, thanks!"})()})]
        ...     response = do_chat_completion(messages)
        >>> response
        "I'm good, thanks!"
    """
    if client is None:
        raise ValueError("A valid OpenAI client must be provided.")
    
    if model is None:
        raise ValueError("A valid model must be provided.")

    if "response_format" not in kwargs:
        response = client.chat.completions.create(  # type: ignore
            model=model,
            messages=messages,  # type: ignore
            **kwargs,  # type: ignore
        )
    else:
        response = client.beta.chat.completions.parse(  # type: ignore
            model=model,
            messages=messages,  # type: ignore
            **kwargs,  # type: ignore
        )

    if hasattr(response, "error"):
        raise RuntimeError(
            f"OpenAI API returned an error: {str(response.error)}"
        )

    return response.choices[0].message.content


ACTIVITY_CALENDAR = [
    {
        "activity_id": "event-2025-06-10-0",
        "name": "FutureTech Breakfast Meet-Up",
        "start_time": "2025-06-10 09:00",
        "end_time": "2025-06-10 11:00",
        "location": "The Innovation Atrium, Tech District, AgentsVille",
        "description": "Join fellow technology enthusiasts for a dynamic morning at the FutureTech Breakfast Meet-Up! Dive into the latest trends in tech, gadget demos, and networking opportunities over coffee and fresh pastries. Held indoors at the spacious Innovation Atrium, this event is perfect for tech lovers eager to exchange ideas and discover new possibilities in a comfortable, modern setting.",
        "price": 20,
        "related_interests": ["technology"],
    },
    {
        "activity_id": "event-2025-06-10-1",
        "name": "Serve & Savor: Tennis and Taste Luncheon",
        "start_time": "2025-06-10 12:00",
        "end_time": "2025-06-10 13:30",
        "location": "The Grand Racquet Terrace, AgentsVille",
        "description": "Join us for 'Serve & Savor,' the ultimate crossover event for cooking and tennis enthusiasts in AgentsVille! Kick off your lunch hour with a friendly round of doubles on our outdoor courts, then unwind with a hands-on cooking workshop led by a local chef, where you'll prepare and enjoy delicious energy-boosting recipes. Whether you come for the sport or the flavors, this energizing luncheon celebrates both passions in a lively outdoor setting. Ideal for anyone who loves to play, cook, or simply savor fresh food and fun!",
        "price": 20,
        "related_interests": ["cooking", "tennis"],
    },
    {
        "activity_id": "event-2025-06-10-2",
        "name": "Artful Athletics: Paint & Play Extravaganza",
        "start_time": "2025-06-10 15:00",
        "end_time": "2025-06-10 17:00",
        "location": "Creative Courts Park, AgentsVille",
        "description": "Join us for an exciting afternoon at Creative Courts Park, where the worlds of art and sports collide! At 'Artful Athletics: Paint & Play Extravaganza', you'll participate in collaborative outdoor murals inspired by your favorite sports, and then get moving with fun, friendly sports mini-games. Whether you love painting or playing, this event celebrates creativity, teamwork, and the joy of movement under the open sky. Perfect for art lovers and sports enthusiasts alike—come ready to express yourself and get active! (Event is held outdoors; in case of rain, we move indoors to the Community Gym nearby.)",
        "price": 15,
        "related_interests": ["art", "sports"],
    },
    {
        "activity_id": "event-2025-06-10-3",
        "name": "AgentsVille Twilight Writing Escape",
        "start_time": "2025-06-10 19:00",
        "end_time": "2025-06-10 21:00",
        "location": "The Ink Loft, 12 Quill Lane, AgentsVille",
        "description": "Join fellow writers for an inspiring evening at The Ink Loft, where words flow as freely as the coffee! This writing-themed event welcomes all—novelists, poets, bloggers, or anyone with a passion for storytelling. Set indoors in AgentsVille's coziest lounge, enjoy writing games, group prompts, and opportunities to read your work aloud. Connect, create, and celebrate the art of writing in this creative indoor haven.",
        "price": 15,
        "related_interests": ["writing", "reading", "art"],
    },
    {
        "activity_id": "event-2025-06-11-0",
        "name": "Morning Groove Dance Party",
        "start_time": "2025-06-11 09:00",
        "end_time": "2025-06-11 10:30",
        "location": "Rhythm Hall, Center Plaza, AgentsVille",
        "description": "Start your day with energy and joy at the Morning Groove Dance Party! This lively event welcomes dancers of all levels to join a vibrant indoor session filled with upbeat music and fun routines. Whether you love modern pop, Latin beats, or classic disco, our dance instructors will guide you to move and groove. Connect with fellow dance lovers in the colorful atmosphere of Rhythm Hall. Perfect for fans of dancing, music, and fitness. Let the rhythm move you! (Indoor event.)",
        "price": 15,
        "related_interests": ["dancing", "music", "fitness"],
    },
    {
        "activity_id": "event-2025-06-11-1",
        "name": "Tech Lunch & Learn: AI Frontiers",
        "start_time": "2025-06-11 12:00",
        "end_time": "2025-06-11 13:30",
        "location": "The Digital Atrium, AgentsVille",
        "description": "Join fellow tech enthusiasts for a dynamic lunchtime event exploring the future of artificial intelligence! Held indoors at The Digital Atrium, this Tech Lunch & Learn features engaging lightning talks, interactive demos, and networking opportunities all centered around technology and innovation. Enjoy light lunch fare as you connect with others passionate about technology, AI, and the digital world. Whether you're a seasoned developer or just curious about tech, this event is for you! Related interests: technology, music (sound tech demos), photography (AI imaging), writing (AI creativity).",
        "price": 20,
        "related_interests": ["technology", "music", "photography", "writing"],
    },
    {
        "activity_id": "event-2025-06-11-2",
        "name": "AgentsVille Art & Music Fusion Fest",
        "start_time": "2025-06-11 15:00",
        "end_time": "2025-06-11 17:30",
        "location": "The Echo Gardens Amphitheater, AgentsVille",
        "description": "Immerse yourself in an unforgettable afternoon at the Echo Gardens Amphitheater, where the vibrant worlds of art and music collide! Surrounded by lush gardens under the open sky, enjoy live performances from talented local musicians while exploring an interactive outdoor art gallery featuring works from AgentsVille's creative community. This engaging outdoor event is perfect for art and music enthusiasts who love to be inspired and connect with fellow creatives. Don't miss out on the fusion of melodies and colors in a relaxing, friendly atmosphere!",
        "price": 18,
        "related_interests": ["art", "music"],
    },
    {
        "activity_id": "event-2025-06-11-3",
        "name": "Palette & Palate: Art Meets Cooking Experience",
        "start_time": "2025-06-11 18:30",
        "end_time": "2025-06-11 20:30",
        "location": "The Creative Canvas Studio, Artisanal Lane, AgentsVille",
        "description": "Immerse yourself in a colorful evening where art and cooking blend together! At 'Palette & Palate,' participants will begin indoors at The Creative Canvas Studio with a guided session to paint their own culinary-inspired masterpiece. Afterwards, a local chef will lead an interactive cooking class, teaching you how to craft vibrant, edible works of art. Whether you're an art enthusiast, a food lover, or both, this creative night is perfect for socializing and expressing yourself through color and flavor! All materials and ingredients are provided. This event is held indoors and welcomes all experience levels in art and cooking.",
        "price": 25,
        "related_interests": ["art", "cooking"],
    },
    {
        "activity_id": "event-2025-06-12-0",
        "name": "AgentsVille Nature & Green Thumb Adventure",
        "start_time": "2025-06-12 08:00",
        "end_time": "2025-06-12 10:00",
        "location": "Echo Ridge Botanical Trails, AgentsVille",
        "description": "Join fellow nature enthusiasts for a morning of outdoor adventure that blends hiking and gardening! Explore the picturesque Echo Ridge trails on a gentle hike while expert guides introduce you to local plant life and teach hands-on gardening tips along the way. Get your hands dirty with mini-plantings and learn how to cultivate native species. Perfect for lovers of both hiking and gardening, this outdoor event promises fresh air, community, and green inspiration.",
        "price": 15,
        "related_interests": ["hiking", "gardening"],
    },
    {
        "activity_id": "event-2025-06-12-1",
        "name": "Soundtrack Picnic: Lunchtime Movies & Melodies",
        "start_time": "2025-06-12 12:00",
        "end_time": "2025-06-12 13:30",
        "location": "Starlight Amphitheater, AgentsVille",
        "description": "Experience the magic of classic movie scenes paired with live music at the outdoor Starlight Amphitheater! Bring your lunch and relax on the lawn as musicians perform iconic film soundtracks while selected clips light up our open-air screen. Perfect for movie buffs and music lovers alike, this engaging event celebrates both arts in a sunny lunchtime setting. In case of rain, the event will move indoors to the adjacent Harmony Hall. Come for the tunes, stay for the cinematic wonder!",
        "price": 15,
        "related_interests": ["movies", "music"],
    },
    {
        "activity_id": "event-2025-06-12-2",
        "name": "Trail Tales: Writing & Hiking Adventure",
        "start_time": "2025-06-12 14:00",
        "end_time": "2025-06-12 16:30",
        "location": "Whispering Pines Trailhead, AgentsVille",
        "description": "Embark on an outdoor writing journey with fellow enthusiasts on the scenic trails of AgentsVille! Trail Tales is a unique event that combines hiking through beautiful pine forests and creative writing activities inspired by nature. Whether you love writing poetry, stories, or journal entries, this event is perfect for those who enjoy both writing and hiking. You'll have guided prompts, collaborative exercises, and plenty of fresh air. Suitable for writers of all levels who want to fuel their creativity while exploring the outdoors.",
        "price": 20,
        "related_interests": ["writing", "hiking"],
    },
    {
        "activity_id": "event-2025-06-12-3",
        "name": "Tech & Film Fusion Night",
        "start_time": "2025-06-12 19:00",
        "end_time": "2025-06-12 21:30",
        "location": "Virtual Reality Theater, Silicon Plaza, AgentsVille",
        "description": "Dive into an immersive evening where the magic of movies meets the latest in technology! Join fellow movie buffs and tech enthusiasts for a special screening of cutting-edge sci-fi short films, followed by an interactive panel with local filmmakers and VR technologists. Experience the future of entertainment and discuss how technology is transforming the world of cinema. This exciting, indoor event at the Virtual Reality Theater is perfect for anyone interested in technology and movies.",
        "price": 15,
        "related_interests": ["technology", "movies"],
    },
    {
        "activity_id": "event-2025-06-13-0",
        "name": "Laugh & Groove: Morning Comedy Dance Bash",
        "start_time": "2025-06-13 09:00",
        "end_time": "2025-06-13 10:30",
        "location": "The Jiving Parlor, Central Plaza, AgentsVille",
        "description": "Start your day with big laughs and even bigger moves at the Laugh & Groove Morning Comedy Dance Bash! Hosted indoors at The Jiving Parlor in the heart of AgentsVille, this lively event blends hilarious stand-up performances with upbeat group dance sessions. Whether you love to dance, enjoy comedy, or just want a fun way to kick off your day, you'll find your place here. Perfect for fans of dancing and comedy alike—come ready to laugh, groove, and connect!",
        "price": 15,
        "related_interests": ["dancing", "comedy"],
    },
    {
        "activity_id": "event-2025-06-13-1",
        "name": "Trails & Tales: Lunchtime Hiking and Writing Retreat",
        "start_time": "2025-06-13 12:00",
        "end_time": "2025-06-13 13:30",
        "location": "Whispering Pines Trailhead, AgentsVille",
        "description": "Step into the great outdoors for Trails & Tales, a unique lunchtime event combining invigorating hiking and creative writing in the beautiful forests of AgentsVille. Take in the scenery on a guided hike, pausing at scenic spots to reflect and write with fellow nature-loving writers. Whether you're an avid hiker, passionate about writing, or want to creatively recharge in nature, this outdoor adventure is for you! Please note: This event is outdoors. All writing materials and a light snack provided.",
        "price": 15,
        "related_interests": ["hiking", "writing"],
    },
    {
        "activity_id": "event-2025-06-13-2",
        "name": "Art & Lens: Outdoor Creative Walk",
        "start_time": "2025-06-13 15:00",
        "end_time": "2025-06-13 17:00",
        "location": "Sunset Promenade Art Park, AgentsVille",
        "description": "Join us for 'Art & Lens: Outdoor Creative Walk', where art lovers and photography enthusiasts unite! Explore the vibrant scenery of Sunset Promenade Art Park in AgentsVille, capturing inspiring moments and sketching as you go. Bring your camera, sketchbook, or both, and enjoy a guided creative journey with plenty of opportunities to connect, learn, and create. This engaging event is held entirely outdoors and is perfect for anyone passionate about art and photography.",
        "price": 15,
        "related_interests": ["art", "photography"],
    },
    {
        "activity_id": "event-2025-06-13-3",
        "name": "Sunset Groove Hike",
        "start_time": "2025-06-13 18:00",
        "end_time": "2025-06-13 20:00",
        "location": "Starlit Ridge, AgentsVille",
        "description": "Experience the perfect fusion of adventure and rhythm at the Sunset Groove Hike! Join fellow hiking and dancing enthusiasts as we traverse the scenic trails of Starlit Ridge just as the sun sets. Halfway through our energizing hike, we'll stop at a panoramic viewpoint for a lively group dance session led by a professional instructor, with music and views to inspire all. This outdoor event combines the joy of hiking with the fun of dancing, offering a memorable evening in nature. All experience levels are welcome—let's move and groove under the open sky!",
        "price": 15,
        "related_interests": ["hiking", "dancing"],
    },    
    {
        "activity_id": "event-2025-06-14-0",
        "name": "Sunrise Nature & Plant Walk",
        "start_time": "2025-06-14 08:00",
        "end_time": "2025-06-14 10:00",
        "location": "Emerald Meadows Park, AgentsVille",
        "description": "Experience the perfect blend of hiking and gardening! Join us for a refreshing outdoor morning hike through scenic Emerald Meadows Park, where we'll stop along the way to learn about local plants and do hands-on gardening activities. Whether you're a hiking enthusiast or a plant lover, this outdoor adventure is tailored for you. Come connect with nature and fellow enthusiasts while nurturing both your body and the local flora.",
        "price": 15,
        "related_interests": ["hiking", "gardening"],
    },
    {
        "activity_id": "event-2025-06-14-1",
        "name": "Lunchtime Bloom: Community Garden Party",
        "start_time": "2025-06-14 12:00",
        "end_time": "2025-06-14 13:30",
        "location": "Green Haven Park, AgentsVille",
        "description": "Join us for a vibrant outdoor gardening event in the heart of AgentsVille! 'Lunchtime Bloom' is the perfect gathering for plant lovers and nature enthusiasts. Learn hands-on gardening tips, participate in a flower-planting session, and connect with fellow green thumbs. Enjoy light refreshments in the fresh air while exploring the world of gardening. Whether you're a seasoned gardener or just getting started, this lively outdoor event promises inspiration and fun for all ages.",
        "price": 15,
        "related_interests": ["gardening", "fitness"],
    },
    {
        "activity_id": "event-2025-06-14-2",
        "name": "AgentsVille Summer Garden Party",
        "start_time": "2025-06-14 14:00",
        "end_time": "2025-06-14 16:30",
        "location": "The Blooming Courtyard, AgentsVille",
        "description": "Join us for an afternoon of blossoming fun at the AgentsVille Summer Garden Party! Whether you're a seasoned gardener or just getting started, this outdoor event invites everyone to dig in and grow together. Explore hands-on workshops, plant your own flowers to take home, enjoy garden games, and connect with fellow plant enthusiasts. The event will celebrate all things green, combining education, creativity, and relaxation for anyone interested in gardening and nature. Perfect for families, friends, and solo adventurers who love the outdoors and greenery!",
        "price": 15,
        "related_interests": ["gardening", "art", "fitness"],
    },
    {
        "activity_id": "event-2025-06-14-3",
        "name": "Dancing Through Prose: A Creative Movement & Writing Evening",
        "start_time": "2025-06-14 19:00",
        "end_time": "2025-06-14 21:00",
        "location": "Writers' Waltz Hall, AgentsVille",
        "description": "Join us for 'Dancing Through Prose,' a lively evening where the worlds of dance and writing beautifully intersect! Guided by local choreographers and creative writers, you'll be inspired by movement to spark your written words, and then let the rhythm of your prose take you back to the dance floor. This event is perfect for anyone who loves dancing and writing, no matter your experience level. Held indoors at the charming Writers' Waltz Hall, you'll enjoy a vibrant and supportive atmosphere where your imagination can truly move. Don't miss this unique celebration of movement and storytelling!",
        "price": 15,
        "related_interests": ["dancing", "writing"],
    },
    {
        "activity_id": "event-2025-06-15-0",
        "name": "Writers' Sunrise Workshop",
        "start_time": "2025-06-15 09:00",
        "end_time": "2025-06-15 11:00",
        "location": "Starlight Literary Cafe, AgentsVille",
        "description": "Kickstart your morning creativity at the Starlight Literary Cafe! Join fellow writers for an inspiring writing workshop surrounded by the cozy ambiance of our indoor cafe. Whether you're working on a novel, exploring poetry, or journaling, this event is perfect for connecting with like-minded enthusiasts. Enjoy writing prompts, group discussions, and plenty of coffee. Ideal for anyone interested in writing, reading, and art. (Indoors event)",
        "price": 15,
        "related_interests": ["writing", "reading", "art"],
    },
    {
        "activity_id": "event-2025-06-15-1",
        "name": "Lunchtime Groove: AgentsVille Dance Social",
        "start_time": "2025-06-15 12:00",
        "end_time": "2025-06-15 13:30",
        "location": "Sunbeam Community Hall, Downtown AgentsVille",
        "description": "Join us for Lunchtime Groove, AgentsVille's exciting indoor dance social! Shake off your midday blues with an hour and a half of energetic dancing, fun choreography, and great music. Whether you're a beginner or a seasoned dancer, enjoy learning new moves and meeting fellow dance lovers. Related interests: dancing, music, fitness.",
        "price": 15,
        "related_interests": ["dancing", "music", "fitness"],
    },
    {
        "activity_id": "event-2025-06-15-2",
        "name": "AgentsVille Summer Dance Jam",
        "start_time": "2025-06-15 15:00",
        "end_time": "2025-06-15 17:00",
        "location": "The Groove Pavilion, Central Park, AgentsVille",
        "description": "Get ready to dance the afternoon away at AgentsVille's Summer Dance Jam! Whether you're a dancing enthusiast or just looking to bust a move, join us at the spacious, open-air Groove Pavilion in Central Park. Expect a lively mix of pop, salsa, and swing tunes, interactive group lessons, and fun dance-offs. This outdoor event welcomes dancers of all levels and ages. Make new friends, learn new moves, and celebrate your love for music and dancing!",
        "price": 15,
        "related_interests": ["dancing", "music", "fitness"],
    },
    {
        "activity_id": "event-2025-06-15-3",
        "name": "Twilight Tennis Rally",
        "start_time": "2025-06-15 18:00",
        "end_time": "2025-06-15 20:00",
        "location": "Grand Courts at Sunfield Park, AgentsVille",
        "description": "Join us for a thrilling outdoor evening of tennis under the setting sun at the Grand Courts! Whether you're a beginner or a seasoned player, this event offers friendly matches, skill challenges, and social time with fellow tennis enthusiasts. Embrace the fresh air, lively music, and exciting giveaways all themed around the love of tennis. Don't miss your chance to rally, serve, and have fun! Perfect for those passionate about tennis, fitness, and meeting new people.",
        "price": 15,
        "related_interests": ["tennis", "fitness", "music"],
    },
]


INCLIMATE_WEATHER_CONDITIONS = ["thunderstorm", "rainy"]

WEATHER_FORECAST = [
    {
        "date": "2025-06-10",
        "city": "AgentsVille",
        "temperature": 31,
        "temperature_unit": "celsius",
        "condition": "clear",
        "description": "A bright and sunny day in AgentsVille with clear skies and warm temperatures. Perfect weather for outdoor activities!",
    },
    {
        "date": "2025-06-11",
        "city": "AgentsVille",
        "temperature": 34,
        "temperature_unit": "celsius",
        "condition": "partly cloudy",
        "description": "A warm day with periods of sunshine and mixed clouds, making it a perfect opportunity for outdoor activities.",
    },
    {
        "date": "2025-06-12",
        "city": "AgentsVille",
        "temperature": 28,
        "temperature_unit": "celsius",
        "condition": "thunderstorm",
        "description": "A thunderstorm is expected to roll in during the afternoon, bringing heavy rain and gusty winds. The atmosphere will feel charged with humidity, creating a sultry and dramatic setting as clouds build in the sky.",
    },
    {
        "date": "2025-06-13",
        "city": "AgentsVille",
        "temperature": 15,
        "temperature_unit": "celsius",
        "condition": "rainy",
        "description": "Cloudy skies with intermittent rain showers throughout the day, accompanied by a cool breeze and a chance of occasional thunderstorms.",
    },
    {
        "date": "2025-06-14",
        "city": "AgentsVille",
        "temperature": 14,
        "temperature_unit": "celsius",
        "condition": "rainy",
        "description": "A steady rain is expected throughout the day with overcast skies and cool temperatures. Residents should be prepared for slick roads and carry umbrellas.",
    },
    {
        "date": "2025-06-15",
        "city": "AgentsVille",
        "temperature": 31,
        "temperature_unit": "celsius",
        "condition": "sunny",
        "description": "A bright and sunny day perfect for outdoor activities with no chance of rain.",
    },
]


def call_activities_api_mocked(
    date: str | None = None, city: str | None = None, activity_ids: list[str] | None = None
) -> list[dict[str, str | int]]:
    """Calls the mocked activities API to get a list of activities for a given date and city.

    This function simulates an API call to retrieve activities based on the provided date and city.

    Args:
        date: The date to get activities for. Must be in the format YYYY-MM-DD.
        city: The city to get activities for. Only "AgentsVille" is supported.
        activity_ids: A list of activity IDs to filter the results. If None, all activities for the date and city will be returned.

    Returns:
        A list of activities for the given date and city. Currently only returns activities
        for AgentsVille between 2025-06-10 and 2025-06-15.
    """
    import datetime

    # If the city is not AgentsVille, return an empty list
    if city and city != "AgentsVille":
        return []

    # Verify the date format
    if date:
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format: {date}")
            return []

    # If the date is not between 2025-06-10 and 2025-06-15, return an empty list
    if date and (date < "2025-06-10" or date > "2025-06-15"):
        print(f"Date {date} is outside the valid range (2025-06-10 - 2025-06-15)")
        return []

    activities = ACTIVITY_CALENDAR

    if date:
        activities = [event for event in activities if event["start_time"].startswith(date)]

    if activity_ids:
        activities = [event for event in activities if event["activity_id"] in activity_ids]

    if not activities:
        print(f"No activities found for {date} in {city}.")
    return activities


def call_activity_by_id_api_mocked(activity_id: str):
    """Calls the mocked activity API to get an activity by its ID.

    Args:
        activity_id: The ID of the event to retrieve.

    Returns:
        A dictionary containing the event details, or an empty dictionary if not found.
    """
    for event in ACTIVITY_CALENDAR:
        if event["activity_id"] == activity_id:
            return event
    print(f"Event with ID {activity_id} not found.")
    return None


def call_weather_api_mocked(date: str, city: str) -> dict[str, str | int]:
    """
    Returns the weather forecast for a given date and city.

    Args:
        date: The date to get weather for. Must be in the format YYYY-MM-DD.
        city: The city to get weather for.

    Returns:
        A dictionary containing the weather forecast for the given date and city.
    """
    import datetime

    # If the city is not AgentsVille, return an empty dictionary
    if city != "AgentsVille":
        return {}

    # Verify the date format
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {date}")
        return {}

    # If the date is not between 2025-06-10 and 2025-06-15, return an empty dictionary
    if date < "2025-06-10" or date > "2025-06-15":
        print(f"Date {date} is outside the valid range (2025-06-10 - 2025-06-15)")
        return {}

    return next(
        (forecast for forecast in WEATHER_FORECAST if forecast["date"] == date), {}
    )


def narrate_my_trip(vacation_info, itinerary, client, model, filename="/tmp/my_trip_narration.mp3"):
    from IPython.display import Audio, Markdown, display
    from openai import OpenAI

    resp = do_chat_completion(
        messages=[
            {
                "role": "user",
                "content": f"""
                Here is information on the trip collected by the Onboarding Agent:
                {vacation_info}.

                Here is the final itinerary:
                {itinerary}
                
                Introduce the trip (travelers, interests, restrictions, and total cost) and
                then discuss each day of the itinerary.

                Do not specify the cost of each activity.

                Do not reference the the narrative itself in the response.
                """,
            }
        ],
        client=client,
        model=model,
    )
    display(Markdown(resp))

    try:
        if resp:
            with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice="coral",
                input=resp,
                instructions="Speak in a cheerful and positive tone.",
            ) as response:
                response.stream_to_file(filename)

            display(Audio(filename))
        else:
            print("No response from the chat completion API.")
    except Exception:
        pass
