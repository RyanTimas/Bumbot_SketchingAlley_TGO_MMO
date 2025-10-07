class TGOCollection:
    def __init__(self, collection_id, title, description, image_path, background_color_path, total_count_query, caught_count_query, completion_reward_1, completion_reward_2, completion_reward_3, is_active = 1):
        self.collection_id = collection_id

        self.title = title
        self.description = description

        self.image_path = image_path
        self.background_color_path = background_color_path

        self.total_count_query = total_count_query
        self.caught_count_query = caught_count_query

        self.completion_reward_1 = completion_reward_1
        self.completion_reward_2 = completion_reward_2
        self.completion_reward_3 = completion_reward_3

        self.is_active = is_active