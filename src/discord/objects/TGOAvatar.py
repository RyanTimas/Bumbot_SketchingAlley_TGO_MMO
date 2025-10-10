class TGOAvatar:
    def __init__(self, avatar_num:int =1, avatar_id:str ="", name:str ="", avatar_type:str ="Default", img_root:str ="", is_unlocked:bool =False):
        self.avatar_num = avatar_num
        self.avatar_id = avatar_id
        self.name = name
        self.avatar_type = avatar_type
        self.img_root = img_root
        self.is_unlocked = is_unlocked
