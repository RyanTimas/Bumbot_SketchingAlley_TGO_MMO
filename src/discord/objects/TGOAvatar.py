class TGOAvatar:
    def __init__(self,
                 avatar_num:int, avatar_id:str,
                 name:str, series:str,
                 avatar_type:str, is_parent_entry:bool,
                 img_root:str,
                 unlock_query:str ="", unlock_threshold:int =0, is_secret:bool =False
    ):
        self.avatar_num = avatar_num
        self.avatar_id = avatar_id

        self.name = name
        self.series = series

        self.avatar_type = avatar_type

        self.img_root = img_root
        self.is_parent_entry = is_parent_entry

        self.unlock_query = unlock_query if unlock_query else ""
        self.unlock_threshold = unlock_threshold if unlock_threshold else 0
        self.is_secret = is_secret if is_secret else False
