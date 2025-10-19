class TGOAvatar:
    def __init__(self, avatar_num:int =1, avatar_id:str ="", name:str ="", avatar_type:str ="Default", img_root:str ="", series:str ="", unlock_query:str ="", unlock_threshold:int =0, is_parent_entry:bool =False):
        self.avatar_num = avatar_num

        self.avatar_id = avatar_id
        self.name = name
        self.series = series

        self.avatar_type = avatar_type
        self.img_root = img_root

        self.unlock_query = unlock_query
        self.unlock_threshold = unlock_threshold

        self.is_parent_entry = is_parent_entry
